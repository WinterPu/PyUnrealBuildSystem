
from Platform.PlatformBase import *
from CommandBase.GenerateProjectFilesCommand import *
import os

class MacPlatformBase(PlatformBase):
    def GetRunUATPath():
        return "/Engine/Build/BatchFiles/RunUAT.sh"
    
    def GetGenerateProjectScriptPath():
        return "/Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh"

    def GenHostPlatformParams(params):
        ret = True
        val = {}

        key = "engine_path"
        val[key] = params.enginepath


        key = "uat_path"
        val[key] = "%s"%(val["engine_path"] + MacPlatformBase.GetRunUATPath())

        key = "genprojfiles_path"
        val[key] = "%s"%(val["engine_path"] + MacPlatformBase.GetGenerateProjectScriptPath())
        
        return ret,val
    
    def GenTargetPlatformParams(params):
        ret = True
        val = {}

        key = "platform"
        val[key] = "Mac"

        key = "project_path"
        val[key] = params[key] if key in params else None
        ### [TBD]
        ## validate project

        PrintLog("PlatformBase - GenParams")
        return ret,val



class MacHostPlatform(BaseHostPlatform):
    def GetDefaultEnginePath(self):
        return "/Users/Shared/Epic Games"
    
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