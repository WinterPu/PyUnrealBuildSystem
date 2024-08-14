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

    


    def UpdateXcodeProject(path_project_root,src_root_path_resources):
        path_project = Path(path_project_root)
        for xcworkspace_dir in path_project.glob("*.xcworkspace"):
            try:
                FileUtility.DeleteDir(xcworkspace_dir)
            except PermissionError as error:
                PrintErr("[UpdateXcodeProject] Delete xcworksapce dir [%s] Failed! - PermissionError [%s]" %(xcworkspace_dir.name,error.strerror + "  " + error.filename),error.errno)
            PrintLog("[UpdateXcodeProject] Delete xcworksapce [%s]" %xcworkspace_dir.name )

        for xcworkspace_dir in src_root_path_resources.glob("*.xcworkspace"):
            FileUtility.CopyDir(xcworkspace_dir,path_project/xcworkspace_dir.name,True,bmac_use_shutil=True)
        
        path_intermediate = path_project / "Intermediate"
        path_projectfiles = path_intermediate / "ProjectFiles"

        if path_projectfiles.exists():
            FileUtility.DeleteDir(path_projectfiles)

        src_path_projectfiles = src_root_path_resources / "ProjectFiles"
        dst_path_projectfiles = path_projectfiles
        PrintLog(f"Copy: {src_path_projectfiles} -> {dst_path_projectfiles}")
        FileUtility.CopyDir(src_path_projectfiles,dst_path_projectfiles)




