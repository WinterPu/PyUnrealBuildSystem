from Platform.PlatformBase import *
import os 

class WinPlatformBase(PlatformBase):
    def GetRunUATPath():
        return "/Engine/Build/BatchFiles/RunUAT.bat"

    def GenHostPlatformParams(params):
        ret = True
        val = {}

        key = "engine_path"
        val["engine_path"] = params.enginepath

        key = "uat_path"
        val["uat_path"] ="%s"%(val["engine_path"] + WinPlatformBase.GetRunUATPath())

        return ret,val
    
    def GenTargetPlatformParams(params):
        ret = True
        val = {}

        key = "platform"
        val[key] = "Win"

        key = "project_path"
        val[key] = params[key] if key in params else None
        ### [TBD]
        ## validate project

        PrintLog("PlatformBase - GenParams")
        return ret,val

class WinHostPlatform(BaseHostPlatform):
    def GetRunUATPath():
        return "/Engine/Build/BatchFiles/RunUAT.bat"
    


class WinTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - Win Platform")

    def Package(self):
        self.SetupEnvironment()
        print("Package - Win Platform")

        params = {}
        params["platform"] = self.GetParamVal("platform")
        params["project_path"] = self.GetParamVal("project_path")
        self.RunUAT().BuildCookRun(params)
