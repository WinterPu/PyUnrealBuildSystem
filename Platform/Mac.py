
from Platform.PlatformBase import *
from CommandBase.GenerateProjectFilesCommand import *
from pathlib import Path

class MacPlatformBase(PlatformBase):
    def GetRunUATPath():
        return Path("Engine/Build/BatchFiles/RunUAT.sh") 
    
    def GetGenerateProjectScriptPath():
        return Path("Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh") 

    def GenHostPlatformParams(args):
        ret = True
        val = {}

        key = "engine_path"
        val[key] = args.enginepath



        key = "uat_path"
        ## if a path starts with '/', it would be treated as starting from the root path.
        val[key] = Path(val["engine_path"]) / Path(MacPlatformBase.GetRunUATPath())

        key = "genprojfiles_path"
        val[key] = Path(val["engine_path"])/ Path(MacPlatformBase.GetGenerateProjectScriptPath())

        return ret,val
    
    def GenTargetPlatformParams(args):
        ret = True
        val = {}

        key = "platform"
        val[key] = "Mac"

        key = "project_path"
        val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        PrintLog("PlatformBase - GenParams")
        return ret,val



class MacHostPlatform(BaseHostPlatform):
    def GetDefaultEnginePath(self):
        return Path("/Users/Shared/Epic Games")
    
    def GenerateProject(self,project_file_path):
        genproj_script = self.GetParamVal("genprojfiles_path")
        one_command = GenerateProjectFilesCommand(genproj_script)
        
        params = {}
        params["project_file_path"] = project_file_path
        one_command.GenerateProjectFiles(params)
        PrintLog("BaseHostPlatform - GenerateProject")


class MacTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - Mac Platform")

    def Package(self):
        self.SetupEnvironment()
        print("Package - Mac Platform")

        params = {}
        params["platform"] = self.GetParamVal("platform")
        params["project_path"] = self.GetParamVal("project_path")
        self.RunUAT().BuildCookRun(params)