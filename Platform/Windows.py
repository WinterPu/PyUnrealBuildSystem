from Platform.PlatformBase import *
from Command.UBTCommand import *
from Command.WwiseCommand import *
from pathlib import Path

from UBSHelper import *

class WinPlatformPathUtility:
    def GetRunUATPath():
        ## if you start with '/', it would be treated as starting from the root path
        return Path("Engine/Build/BatchFiles/RunUAT.bat")

    def GetRunIOSPackager():
        return Path("Engine/Binaries/DotNET/IOS/IPhonePackager.exe")

    def GetUBTPath():
        path  = Path("Engine/Binaries/DotNET/UnrealBuildTool.exe")

        if UBSHelper.Get().Is_UE53_Or_Later():
            path = Path("Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.exe")

        return path


class WinPlatformBase(PlatformBase):
    def GenHostPlatformParams(args):
        ret, val = PlatformBase.GenHostPlatformParams(args)

        key = "uat_path"
        val["uat_path"] = UBSHelper.Get().GetPath_UEEngine() / WinPlatformPathUtility.GetRunUATPath()

        return ret, val

    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        # key = "target_platform"
        # val[key] = "Win64"
        
        PrintLog("PlatformBase - GenParams")
        return ret, val


class WinHostPlatform(BaseHostPlatform):
    def GenerateProject(self, path_uproject_file):
        ## uproject file could be any uproject file, not only the target project
        ubt_path = Path(UBSHelper.Get().GetPath_UEEngine()) / Path(WinPlatformPathUtility.GetUBTPath())

        one_command = UBTCommand(ubt_path)

        params = ParamsUBT()
        params.path_uproject_file = path_uproject_file

        one_command.GenerateProjectFiles(params)
        PrintLog("BaseHostPlatform - GenerateProject")


class WinTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.Win64_TargetName()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Win Platform")

    def Package(self):
        self.SetupEnvironment()
        PrintStageLog("Package - %s Platform" % self.GetTargetPlatform())

        params = ParamsUAT()
        params.target_platform = self.GetTargetPlatform()
        params.path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        params.path_engine = UBSHelper.Get().GetPath_UEEngine()
        params.path_archive = UBSHelper.Get().GetPath_ArchiveDirBase()
        params.skip_build_editor = UBSHelper.Get().ShouldSkipBuildEditor()
        
        self.RunUAT().BuildCookRun(params)

        self.PostPackaged()

        self.ArchiveProduct()

    
    def PostPackaged(self):
        PrintStageLog("PostPackaged - Win")

        path_archive_dir = UBSHelper.Get().GetPath_ArchiveDir(self.GetTargetPlatform())
        self.SetArchivePath_FinalProductDir(path_archive_dir)
    




#####################################################################################
#################################### Wwise ##########################################
    def Package_Wwise(self):
        list_config = ["Debug","Profile","Release"]
        arch = "x64"
        toolset = ["vc_160","vc170"]
       
        OneWwiseCommand = WwiseCommand()

        for one_config in list_config:
            one_param = ParamsWwisePluginBuild()
            one_param.configuration = one_config
            one_param.architecture = arch

            for one_toolset in toolset:
                one_param.toolset = one_toolset
                one_param.platform = "Windows_" + one_toolset
                OneWwiseCommand.Build(one_param)
        
