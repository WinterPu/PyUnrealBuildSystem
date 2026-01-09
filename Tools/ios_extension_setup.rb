require 'xcodeproj'
require 'fileutils'

# Usage: ruby ios_extension_setup.rb <ProjectPath> <ProjectRoot> <MainTargetName> <ExtensionName> <ExtensionBundleID>

project_path = ARGV[0]
project_root = ARGV[1]
main_target_name = ARGV[2]
extension_target_name = ARGV[3]
extension_bundle_id = ARGV[4]
team_id = ARGV[5]
provisioning_profile_specifier = ARGV[6]

puts "--- Ruby Script Start ---"
puts "Project: #{project_path}"
puts "Target: #{main_target_name}"

project = Xcodeproj::Project.open(project_path)

# 1. Find Main Target
main_target = project.targets.find { |t| t.name == main_target_name }
if main_target.nil?
  puts "Error: Main target '#{main_target_name}' not found. Available targets: #{project.targets.map(&:name).join(', ')}"
  exit 1
end

# 2. Get or Create Extension Target
extension_target = project.targets.find { |t| t.name == extension_target_name }

if extension_target
    puts "Target #{extension_target_name} already exists."
else
    # Create target
    # Type: app_extension
    # Platform: ios
    extension_target = project.new_target(:app_extension, extension_target_name, :ios)
    puts "Created new target: #{extension_target_name}"
    
    # Force creation of build configurations (Debug/Release/etc to match project)
    # new_target usually creates default configs.
end

# 3. Add Source Files
# Calculate relative path from .xcodeproj folder to Extension folder
# We know project_root is where extension folder lives.
# We know project_path is the .xcodeproj file.
require 'pathname'
project_dir_path = File.dirname(project_path)
extension_dir_path = File.join(project_root, extension_target_name)

# Make sure extension directory exists
unless File.directory?(extension_dir_path)
    puts "Error: Extension directory not found at #{extension_dir_path}"
    exit 1
end

# Calculate relative path: e.g. ../../../AgoraBCExtension
# This path is what we put in the PBXGroup so it resolves correctly relative to the project.
relative_group_path = Pathname.new(extension_dir_path).relative_path_from(Pathname.new(project_dir_path)).to_s
puts "Extension Relative Path: #{relative_group_path}"

# Get or Create Group
extension_group = project.main_group.find_subpath(extension_target_name) || project.main_group[extension_target_name]

unless extension_group
    # Create group with the relative path
    extension_group = project.main_group.new_group(extension_target_name, relative_group_path)
    
    # Add files recursively
    Dir.glob(File.join(extension_dir_path, "*")).each do |file_path|
      next if file_path.include?(".DS_Store")
      file_name = File.basename(file_path)
      
      # For files inside the folder, we can add them to the group.
      # If the group has a path set, new_reference(file_name) adds it relative to the group path.
      file_ref = extension_group.new_reference(file_name)
      
      if file_name.end_with?(".h", ".m", ".swift", ".c", ".cpp", ".mm")
         extension_target.add_file_references([file_ref])
      elsif file_name.end_with?(".plist")
         # Plist doesn't go to compile sources
      end
    end
end

# 4. Configure Build Settings

# Retrieve Main Target Signing Info
main_dev_team = ""
# main_sign_identity = "" 
# main_prov_profile = ""
unless main_target.build_configurations.empty?
    main_config = main_target.build_configurations.first
    main_dev_team = main_config.build_settings['DEVELOPMENT_TEAM']
    # main_sign_identity = main_config.build_settings['CODE_SIGN_IDENTITY']
end

extension_target.build_configurations.each do |config|
    config.build_settings['PRODUCT_BUNDLE_IDENTIFIER'] = extension_bundle_id
    
    # Info.plist path relative to the PROJECT FILE (not the group)
    config.build_settings['INFOPLIST_FILE'] = "#{relative_group_path}/Info.plist"
    
    config.build_settings['PRODUCT_NAME'] = extension_target_name
    config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
    config.build_settings['SKIP_INSTALL'] = 'YES'
    config.build_settings['TARGETED_DEVICE_FAMILY'] = "1,2" # iPhone, iPad
    
    # Apply Main Target Signing
    if team_id && !team_id.empty?
        config.build_settings['DEVELOPMENT_TEAM'] = team_id
        
        if provisioning_profile_specifier && !provisioning_profile_specifier.empty?
             config.build_settings['CODE_SIGN_STYLE'] = 'Manual'
             config.build_settings['PROVISIONING_PROFILE_SPECIFIER'] = provisioning_profile_specifier
             puts "Manual Signing Configured: Team #{team_id}, Profile #{provisioning_profile_specifier}"
        else
             config.build_settings['CODE_SIGN_STYLE'] = 'Automatic' 
             puts "Automatic Signing Configured: Team #{team_id}"
        end

    elsif main_dev_team && !main_dev_team.empty?
        config.build_settings['DEVELOPMENT_TEAM'] = main_dev_team
        config.build_settings['CODE_SIGN_STYLE'] = 'Automatic' 
    else
        config.build_settings['CODE_SIGN_STYLE'] = 'Automatic'
    end
end

# 5. Add Frameworks
puts "Adding Framework Search Paths and Linking..."

# Framework path: [ProjectRoot]/IOSFramework/AgoraReplayKitExtension.framework
# ProjectRoot is passed as ARGV[1]
framework_root = File.join(project_root, "IOSFramework")
framework_name = "AgoraReplayKitExtension.framework"
framework_fullpath = File.join(framework_root, framework_name)

if File.exist?(framework_fullpath)
    # 1. Add File Reference to Project
    # We want to add it to a group, maybe "IOSFramework" group or "Frameworks" group?
    # Let's create/find IOSFramework group in project root 
    
    # Calculate relative path to framework
    # Project: [Root]/Intermediate/ProjectFiles/[Project].xcodeproj
    # Framework: [Root]/IOSFramework/...
    # Relative: ../../IOSFramework/...
    
    require 'pathname'
    project_dir_path = File.dirname(project_path)
    framework_relative_path = Pathname.new(framework_fullpath).relative_path_from(Pathname.new(project_dir_path)).to_s
    
    puts "Framework Relative Path: #{framework_relative_path}"

    # Find or Create Group "IOSFramework"
    framework_group = project.main_group.find_subpath("IOSFramework") || project.main_group.new_group("IOSFramework", "../../IOSFramework")
    
    # Check if ref exists
    framework_ref = framework_group.files.find { |f| f.path == framework_name }
    unless framework_ref
        # add_reference expects path relative to group if group has path, or absolute?
        # If group path is "../../IOSFramework", then adding "AgoraReplayKitExtension.framework" works if it's inside.
        framework_ref = framework_group.new_reference(framework_name)
    end
    
    # 2. Add to Frameworks Build Phase
    unless extension_target.frameworks_build_phase.files_references.include?(framework_ref)
        extension_target.frameworks_build_phase.add_file_reference(framework_ref)
        puts "Linked #{framework_name} to extension target."
    end
    
    # 3. Add Framework Search Paths
    extension_target.build_configurations.each do |config|
        paths = config.build_settings['FRAMEWORK_SEARCH_PATHS']
        paths = [paths] if paths.is_a?(String)
        paths = [] if paths.nil?
        
        # Add path relative to project
        # If the group logic above used "../../IOSFramework", let's use that.
        search_path = "$(PROJECT_DIR)/../../IOSFramework"
        
        unless paths.include?(search_path)
             paths << search_path
             config.build_settings['FRAMEWORK_SEARCH_PATHS'] = paths
             puts "Added Framework Search Path: #{search_path}"
        end
    end

else
    puts "Warning: Framework not found at #{framework_fullpath}"
end

# (Framework logic removed)



# 6. Add Dependency to Main Target
unless main_target.dependencies.any? { |dep| dep.target == extension_target }
    main_target.add_dependency(extension_target)
    puts "Added dependency to main target"
end
# 6. Add Extension to Main Target's Embed App Extensions Phase
# Build Phase: Copy Files (PlugIns)
# 7. Embed Extension in Main App
# Look for 'Embed App Extensions' phase or create it
# symbol_dst_subfolder_spec :plugins is 13
# Xcodeproj enum: :frameworks, :shared_frameworks, :resources, :plugins, :java_resources, :products, :xpc_services ...
# Xcodeproj expects the raw integer value for dst_subfolder_spec.
# 13 corresponds to the 'PlugIns' folder, which is the standard location for App Extensions in an iOS App Bundle.

embed_phase = main_target.copy_files_build_phases.find { |p| p.symbol_dst_subfolder_spec == :plugins } 
if embed_phase.nil?
    embed_phase = main_target.new_copy_files_build_phase("Embed App Extensions")
    # Set dst_subfolder_spec to 13 (PlugIns)
    embed_phase.dst_subfolder_spec = "13"
end

product_ref = extension_target.product_reference
if product_ref
    # Check if already added
    already_embedded = embed_phase.files_references.any? { |f| f.path == product_ref.path }
    unless already_embedded
        build_file = embed_phase.add_file_reference(product_ref)
        build_file.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
        puts "Added extension to Embed App Extensions phase"
    end
end

project.save
puts "Project saved."
