
from Platform.PlatformBase import *
from Command.GenerateProjectFilesCommand import *
from pathlib import Path

class MacPlatformPathUtility:
    @staticmethod
    def GetDefaultEnginePath():
        return Path("/Users/Shared/Epic Games")
    
    @staticmethod
    def GetRunUATPath():
        return Path("Engine/Build/BatchFiles/RunUAT.sh") 
    
    @staticmethod
    def GetGenerateProjectScriptPath():
        return Path("Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh") 


class MacPlatformBase(PlatformBase):
    def GenHostPlatformParams(args):
        ret,val = PlatformBase.GenHostPlatformParams(args)

        key = "uat_path"
        ## if a path starts with '/', it would be treated as starting from the root path.
        val[key] = Path(val["engine_path"]) / MacPlatformPathUtility.GetRunUATPath()

        key = "genprojfiles_path"
        val[key] = Path(val["engine_path"])/ MacPlatformPathUtility.GetGenerateProjectScriptPath()

        return ret,val
    
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)

        key = "platform"
        val[key] = "Mac"

        # key = "project_path"
        # val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        PrintLog("PlatformBase - GenParams")
        return ret,val



class MacHostPlatform(BaseHostPlatform):
    def GenerateProject(self,project_file_path):
        genproj_script = self.GetParamVal("genprojfiles_path")
        one_command = GenerateProjectFilesCommand(genproj_script)
        
        one_command.GenerateProjectFiles(self.Params)
        PrintLog("BaseHostPlatform - GenerateProject")


class MacTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - Mac Platform")

    def Package(self):
        self.SetupEnvironment()
        print("Package - Mac Platform")
        self.RunUAT().BuildCookRun(self.Params)