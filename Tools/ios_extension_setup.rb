require 'xcodeproj'
require 'fileutils'

# Usage: ruby ios_extension_setup.rb <ProjectPath> <ProjectRoot> <MainTargetName> <ExtensionName> <ExtensionBundleID>

project_path = ARGV[0]
project_root = ARGV[1]
main_target_name = ARGV[2]
extension_target_name = ARGV[3]
extension_bundle_id = ARGV[4]

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
# Assumes files are in [ProjectRoot]/[ExtensionName]
extension_group_path = File.join(project_root, extension_target_name)
extension_rel_path = extension_target_name # Relative to project root

# Xcodeproj has group[] access via [name], but find_sub_group isn't standard in older versions or some forks?
# Standard Xcodeproj::Project::Object::PBXGroup usage:
extension_group = project.main_group.find_subpath(extension_target_name) || project.main_group[extension_target_name]

unless extension_group
  # If the folder exists on disk, we can add it
  if File.directory?(extension_group_path)
    extension_group = project.main_group.new_group(extension_target_name, extension_rel_path)
    # Add files recursively
    Dir.glob(File.join(extension_group_path, "*")).each do |file_path|
      next if file_path.include?(".DS_Store")
      file_name = File.basename(file_path)
      file_ref = extension_group.new_reference(file_name)
      
      if file_name.end_with?(".h", ".m", ".swift", ".c", ".cpp")
         extension_target.add_file_references([file_ref])
      elsif file_name.end_with?(".plist")
         # Plist doesn't go to compile sources
      end
    end
  else
    puts "Warning: Extension directory #{extension_group_path} does not exist."
  end
end

# 4. Configure Build Settings
extension_target.build_configurations.each do |config|
    config.build_settings['PRODUCT_BUNDLE_IDENTIFIER'] = extension_bundle_id
    # Assuming Info.plist is at [ExtensionName]/Info.plist relative to project file or project root?
    # Xcodeproj paths are relative to project file usually.
    # If project file is in [Root]/Intermediate/ProjectFiles/..., and source is in [Root]/Extension...
    config.build_settings['INFOPLIST_FILE'] = "$(PROJECT_DIR)/../../#{extension_target_name}/Info.plist" 
    # Adjust this path logic based on where .xcodeproj is vs where source files are
    
    config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
    config.build_settings['SKIP_INSTALL'] = 'YES'
end

# 5. Add Frameworks
# Framework path: [ProjectRoot]/IOSFramework/AgoraReplayKitExtension.framework
framework_root = File.join(project_root, "IOSFramework")
framework_name = "AgoraReplayKitExtension.framework"
framework_path = File.join(framework_root, framework_name)

if File.exist?(framework_path)
    # framework_group = project.main_group.find_sub_group("IOSFramework")
    framework_group = project.main_group.find_subpath("IOSFramework") || project.main_group["IOSFramework"]
    unless framework_group
        framework_group = project.main_group.new_group("IOSFramework", "IOSFramework") # path relative to project root usually
    end

    framework_ref = framework_group.find_file_by_path(framework_name)
    unless framework_ref
        framework_ref = framework_group.new_reference(framework_name)
    end

    # Add to Extension Frameworks Build Phase
    unless extension_target.frameworks_build_phase.files_references.include?(framework_ref)
        extension_target.frameworks_build_phase.add_file_reference(framework_ref)
        puts "Added framework to extension target."
    end
    
    # Add Framework Search Paths
    extension_target.build_configurations.each do |config|
        paths = config.build_settings['FRAMEWORK_SEARCH_PATHS']
        paths = [paths] if paths.is_a?(String)
        paths = [] if paths.nil?
        
        # Add path relative to project or absolute
        new_path = "$(PROJECT_DIR)/../../IOSFramework"
        unless paths.include?(new_path)
             paths << new_path
             config.build_settings['FRAMEWORK_SEARCH_PATHS'] = paths
        end
    end
else
    puts "Warning: Framework not found at #{framework_path}"
end


# 6. Add Dependency to Main Target
unless main_target.dependencies.any? { |dep| dep.target == extension_target }
    main_target.add_dependency(extension_target)
    puts "Added dependency to main target"
end

# 7. Embed Extension in Main App
# Look for 'Embed App Extensions' phase or create it
# symbol_dst_subfolder_spec :plugins is 13
embed_phase = main_target.copy_files_build_phases.find { |p| p.symbol_dst_subfolder_spec == :plugins } # :plugins mapping might verify
if embed_phase.nil?
    embed_phase = main_target.new_copy_files_build_phase("Embed App Extensions")
    embed_phase.symbol_dst_subfolder_spec = :plugins 
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
