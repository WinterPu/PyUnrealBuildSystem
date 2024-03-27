from Platform.PlatformBase import *
from Command.UBTCommand import *
from pathlib import Path


class WinPlatformPathUtility:
    def GetRunUATPath():
        ## if you start with '/', it would be treated as starting from the root path
        return Path("Engine/Build/BatchFiles/RunUAT.bat")

    def GetRunIOSPackager():
        return Path("Engine/Binaries/DotNET/IOS/IPhonePackager.exe")

    def GetUBTPath():
        return Path("Engine/Binaries/DotNET/UnrealBuildTool.exe")


class WinPlatformBase(PlatformBase):
    def GenHostPlatformParams(args):
        ret, val = PlatformBase.GenHostPlatformParams(args)

        key = "uat_path"
        val["uat_path"] = val["engine_path"] / WinPlatformPathUtility.GetRunUATPath()

        return ret, val

    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        key = "platform"
        val[key] = "Win64"

        # key = "project_path"
        # val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        PrintLog("PlatformBase - GenParams")
        return ret, val


class WinHostPlatform(BaseHostPlatform):
    def GenerateProject(self, project_file_path):
        engine_path = self.GetParamVal("engine_path")
        ubt_path = Path(engine_path) / Path(WinPlatformPathUtility.GetUBTPath())

        one_command = UBTCommand(ubt_path)

        self.Params["project_file_path"] = project_file_path

        one_command.GenerateProjectFiles(self.Params)
        PrintLog("BaseHostPlatform - GenerateProject")


class WinTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - Win Platform")

    def Package(self):
        self.SetupEnvironment()
        print("Package - Win Platform")

        self.RunUAT().BuildCookRun(self.Params)
