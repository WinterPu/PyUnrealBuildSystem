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

        plugin_list = os.listdir(plugin_root_path)
        for one_plugin in plugin_list:
            plugin_path = os.path.join(plugin_root_path, one_plugin)
            for folder in UETmpFolderList:
                folder_path = os.path.join(plugin_path, folder)
                PrintLog("CleanPluginProject %s " % (folder_path))
                FileUtility.DeleteDir(folder_path)

    def GenerateProject(host_platform,path_uproject_file):
        host_platform.GenerateProject(path_uproject_file)
        PrintLog("Generate Project")

    def GenerateIOSProject(host_platform,path):
        if host_platform.GetHostPlatform() == "Mac":
            host_platform.GenerateIOSProject(path)
            PrintLog("Generate Project")
        else:
            PrintErr("Host Platform doesn't support to generate ios project for now.")

    

