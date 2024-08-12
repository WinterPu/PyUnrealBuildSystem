from FileIO.FileUtility import *
from Utility.HeaderBase import *


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

    

