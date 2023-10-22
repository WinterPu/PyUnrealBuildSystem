from FileIO.FileUtility import *
from Utility.HeaderBase import *


class UnrealProjectManager:
    def ValidateProject(path):
        PrintLog("Validate Project")

    def CleanProject(project_path):
        UETmpFolderList = ["Binaries", "Build", "Intermediate", "Saved"]
        for folder in UETmpFolderList:
            folder_path = os.path.join(project_path, folder)
            print("CleanProject", folder_path)
            FileUtility.DeleteDir(folder_path)
        plugin_root_path = os.path.join(project_path, "Plugins")

        plugin_list = os.listdir(plugin_root_path)
        for one_plugin in plugin_list:
            plugin_path = os.path.join(plugin_root_path, one_plugin)
            for folder in UETmpFolderList:
                folder_path = os.path.join(plugin_path, folder)
                print("CleanPluginProject", folder_path)
                FileUtility.DeleteDir(folder_path)

    def GenerateProject(path):
        print("Generate Project")
