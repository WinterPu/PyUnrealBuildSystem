from FileIO.FileUtility import *
from Utility.HeaderBase import *

from Command.ZipCommand import *
from Command.XcodeCommand import *

from ConfigParser import *
from UBSHelper import *

class UnrealProjectManager:
    def ValidateProject(path):
        PrintLog("Validate Project")

    def CleanProject(project_path):
        
        path_project = Path(project_path)
        for xcworkspace_dir in path_project.glob("*.xcworkspace"):
            try:
                FileUtility.DeleteDir(xcworkspace_dir)
            except PermissionError as error:
                PrintErr("[CleanProject] Delete xcworksapce dir [%s] Failed! - PermissionError [%s]" %(xcworkspace_dir.name,error.strerror + "  " + error.filename),error.errno)
            PrintLog("[CleanProject] Delete xcworksapce [%s]" %xcworkspace_dir.name )
            
        
        UETmpFolderList = ["Binaries", "Build", "Intermediate", "Saved","DerivedDataCache"]
        for folder in UETmpFolderList:
            folder_path = os.path.join(project_path, folder)
            PrintLog("CleanProject %s" % str(folder_path))
            FileUtility.DeleteDir(folder_path)
        plugin_root_path = os.path.join(project_path, "Plugins")

        if os.path.exists(plugin_root_path):
            plugin_list = os.listdir(plugin_root_path)
            for one_plugin in plugin_list:
                plugin_path = os.path.join(plugin_root_path, one_plugin)
                for folder in UETmpFolderList:
                    folder_path = os.path.join(plugin_path, folder)
                    PrintLog("CleanPluginProject %s " % (folder_path))
                    FileUtility.DeleteDir(folder_path)

        ### Handle UE5 new Config Ini
        config_path = Path(project_path) / "Config"
        original_defaultinput_ini_filename = "DefaultInput.ini"
        bak_defaultinput_ini_filename = "DefaultInput_bak.ini"
        if UBSHelper.Get().Is_UE5_Or_Later():

            ## Restore
            # ini_defaultinput_file = config_path / original_defaultinput_ini_filename
            # bak_ini_defaultinput_file = config_path / bak_defaultinput_ini_filename
            # if ini_defaultinput_file.exists() == False and  bak_ini_defaultinput_file.exists():
            #     bak_ini_defaultinput_file.rename( config_path / original_defaultinput_ini_filename)
            
            pass 
        else:
            ini_defaultinput_file = config_path / original_defaultinput_ini_filename
            if ini_defaultinput_file.exists():
                ini_defaultinput_file.rename( config_path / bak_defaultinput_ini_filename )


    def GenerateProject(host_platform,path_uproject_file):
        host_platform.GenerateProject(path_uproject_file)
        PrintLog("Generate Project")

    def GenerateIOSProject(host_platform,path):
        if host_platform.GetHostPlatform() == "Mac":
            host_platform.GenerateIOSProject(path)
            PrintLog("Generate Project")
        else:
            PrintErr("Host Platform doesn't support to generate ios project for now.")

    

    ## UE5 Packaging IOS would generate app rather than ipa
    def ConvertMacAppToIPA(path_app):

        ## Ex. [Root] / AgoraExample.app
        path_app = Path(path_app)
        if not path_app.exists():
            PrintErr(f"Target App {path_app} doesn't exist.")
            return
        
        root_path = path_app.parent
        tmp_payload_name = "Payload"
        
        ## Ex. [Root] / Payload
        path_payload = root_path / tmp_payload_name
        if path_payload.exists():
            FileUtility.DeleteDir(path_payload)
        path_payload.mkdir(parents=True)
        
        ##FileUtility.CopyFile(path_app, path_payload / path_app.name)
        ## App is a directory
        FileUtility.CopyDir(path_app,path_payload / path_app.name,bkeep_symlink=True,bmac_use_shutil=True)


        OneZipCommand = ZipCommand()
        
        dst_framework_path = root_path / (tmp_payload_name + ".zip")
        src_framework_path = root_path / tmp_payload_name
        OneZipCommand.ZipFile(src_framework_path,dst_framework_path)
        
        ## Ex. [Root] / Payload.zip -> AgoraExample.zip
        path_final_product = path_app.parent / (path_app.stem + ".ipa")
        if path_final_product.exists():
            FileUtility.DeleteFile(path_final_product)
            
        PrintLog(f"Final Product ==> {path_final_product}")
        dst_framework_path.rename(path_final_product)

        FileUtility.DeleteDir(path_payload)

    


    def ReplaceXcodeProject(path_project_root,src_root_path_resources,dir_name_projectfiles = "ProjectFiles"):
        ## It requires the project has the same directory: which means: 
        ### * it should have the same user account [ Ex. admin ]

        path_project = Path(path_project_root)
        for xcworkspace_dir in path_project.glob("*.xcworkspace"):
            try:
                FileUtility.DeleteDir(xcworkspace_dir)
            except PermissionError as error:
                PrintErr("[ReplaceXcodeProject] Delete xcworksapce dir [%s] Failed! - PermissionError [%s]" %(xcworkspace_dir.name,error.strerror + "  " + error.filename),error.errno)
            PrintLog("[ReplaceXcodeProject] Delete xcworksapce [%s]" %xcworkspace_dir.name )

        for xcworkspace_dir in src_root_path_resources.glob("*.xcworkspace"):
            FileUtility.CopyDir(xcworkspace_dir,path_project/xcworkspace_dir.name,True,bmac_use_shutil=True)
        
        path_intermediate = path_project / "Intermediate"
        path_projectfiles = path_intermediate / dir_name_projectfiles

        if path_projectfiles.exists():
            FileUtility.DeleteDir(path_projectfiles)

        src_path_projectfiles = src_root_path_resources / dir_name_projectfiles
        dst_path_projectfiles = path_projectfiles
        PrintLog(f"Copy: {src_path_projectfiles} -> {dst_path_projectfiles}")
        FileUtility.CopyDir(src_path_projectfiles,dst_path_projectfiles)

    def AddMacSandboxPermissions(path_project_root):
        path_project = Path(path_project_root)
        files_entitlements = list(path_project.rglob("*.entitlements"))
        
        if len(files_entitlements) == 0:
             PrintLog(f"[AddMacSandboxPermissions] No Entitlements found in {path_project_root} ")

        OneXcodeCommand = XcodeCommand()
        for file_entitlements in files_entitlements:
            PrintLog(f"[AddMacSandboxPermissions] Add Permissions to {file_entitlements}")
            
            permissions = [
                "com.apple.security.device.camera",
                "com.apple.security.device.microphone",
                "com.apple.security.network.server",
                "com.apple.security.network.client"
            ]

            for permission in permissions:
                 # Try adding first (fails if exists)
                 cmd_add = f"Add :{permission} bool true"
                 OneXcodeCommand.PlistBuddy(cmd_add, file_entitlements)
                 # Then set to ensure correct value (fails if doesn't exist)
                 cmd_set = f"Set :{permission} true"
                 OneXcodeCommand.PlistBuddy(cmd_set, file_entitlements)

    def AddIOSBroadcastExtension(path_project_root, src_root_path_resource):
        # 1. Copy Source Files
        path_project = Path(path_project_root)
        src_extension_path = src_root_path_resource / "AgoraBCExtension"
        dst_extension_path = path_project / "AgoraBCExtension"
        
        if src_extension_path.exists():
            PrintLog(f"[AddIOSBroadcastExtension] Copying source files from {src_extension_path} to {dst_extension_path}")
            if dst_extension_path.exists():
                FileUtility.DeleteDir(dst_extension_path)
            FileUtility.CopyDir(src_extension_path, dst_extension_path)
        else:
            PrintErr(f"[AddIOSBroadcastExtension] Source path {src_extension_path} does not exist!")

        # 2. Prepare Frameworks
        PrintLog("[AddIOSBroadcastExtension] Preparing Frameworks")
        
        # Ex. [Project] / IOSFramework
        root_path_framework_dir = path_project / "IOSFramework"
        if not root_path_framework_dir.exists():
            root_path_framework_dir.mkdir(parents=True)
            
        extension_folder_name = "AgoraReplayKitExtension.framework"
        path_target_extension = root_path_framework_dir / extension_folder_name 

        if path_target_extension.exists():
            FileUtility.DeleteDir(path_target_extension)

        # Src: [Project] /Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/IOS/Release/AgoraReplayKitExtension.embeddedframework.zip
        src_zip_relative = Path("Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/IOS/Release/AgoraReplayKitExtension.embeddedframework.zip")
        src_zip_file_path_replay_kit = path_project / src_zip_relative
        dst_zip_file_path_replay_kit  = root_path_framework_dir / src_zip_file_path_replay_kit.name
        
        if src_zip_file_path_replay_kit.exists():
            FileUtility.CopyFile(src_zip_file_path_replay_kit, dst_zip_file_path_replay_kit)

            OneZipCommand = ZipCommand()
            OneZipCommand.UnZipFile(dst_zip_file_path_replay_kit, root_path_framework_dir)
            
            target_unzip_path = root_path_framework_dir / dst_zip_file_path_replay_kit.stem
            
            # Ex. [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework / AgoraReplayKitExtension.framework
            unzipped_folder = target_unzip_path / extension_folder_name
            if unzipped_folder.exists():
                    unzipped_folder.rename(target_unzip_path.parent / extension_folder_name)

            FileUtility.DeleteFile(dst_zip_file_path_replay_kit)
            FileUtility.DeleteDir(target_unzip_path)
            PrintLog("[AddIOSBroadcastExtension] Framework preparation done.")
        else:
             PrintWarn(f"[AddIOSBroadcastExtension] Framework zip not found at {src_zip_file_path_replay_kit}")

        # 3. Configure Xcode Project via Ruby Script
        PrintLog("[AddIOSBroadcastExtension] Configuring Xcode Project via Ruby...")

        # Find .xcodeproj
        # Assuming UE structure: [ProjectRoot]/Intermediate/ProjectFiles/[ProjectName].xcodeproj
        # Or checking what exists.
        project_name = UBSHelper.Get().GetName_ProjectName()
        path_xcodeproj = path_project / "Intermediate" / "ProjectFiles" / (project_name + "_IOS.xcodeproj")
        
        # In UE5 Modern Xcode, it might be different structure or name?
        # Based on logs: "UnrealGame (IOS).xcodeproj" or "AgoraExample_IOS.xcworkspace"
        # Since we are modifying the project file that generates the workspace logic or the one used inside it.
        # But UE often regenerates these.
        # If modern Xcode: [ProjectRoot]/Intermediate/ProjectFiles/[ProjectName].xcodeproj matches?
        
        # Fallback check
        if not path_xcodeproj.exists():
             # Try Mac/IOS pattern
             path_xcodeproj = path_project / "Intermediate" / "ProjectFiles" / (project_name + ".xcodeproj")
        
        if not path_xcodeproj.exists():
             # Try IOS specific naming if distinct
             files = list((path_project / "Intermediate" / "ProjectFiles").glob("*IOS.xcodeproj"))
             if len(files) > 0:
                 path_xcodeproj = files[0]

        if not path_xcodeproj.exists():
             # Try ProjectName (IOS).xcodeproj pattern (seen in modern UE5 logs)
             path_temp = path_project / "Intermediate" / "ProjectFiles" / (project_name + "(IOS).xcodeproj")
             if path_temp.exists():
                 path_xcodeproj = path_temp

        if path_xcodeproj.exists():
             # Params
             script_path = Path("Tools/ios_extension_setup.rb").resolve()
             # Targets
             main_target_name = project_name 
             extension_name = "AgoraBCExtension"
             # Construct Bundle ID: [AppBundleID].AgoraBCExtension
             # We need to fetch App Bundle ID. 
             # Simplified: passed from upstream or read config?
             # For now, let's construct it from Config or args if available.
             # Hardcoding a pattern or fetching via ConfigParser could work.
             # Re-reading Config might be needed.
             
             # Assuming we can get it from UBSHelper or passed args not easily available here without signature change.
             # Let's try to get it from ConfigParser
             # But ConfigParser needs uProject path.
             bundle_id_prefix = "io.agora.AgoraExample" # Default/Fallback
             # In a real scenario, retrieve this properly.
             extension_bundle_id = f"{bundle_id_prefix}.{extension_name}"

             cmd = f"ruby {script_path} '{path_xcodeproj}' '{path_project}' '{main_target_name}' '{extension_name}' '{extension_bundle_id}'"
             
             PrintLog(f"Running: {cmd}")
             RUNCMD(cmd)
        else:
             PrintErr(f"[AddIOSBroadcastExtension] Could not find .xcodeproj at {path_xcodeproj}")




