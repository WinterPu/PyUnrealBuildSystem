from Platform.PlatformBase import *
from Command.UBTCommand import *
from Command.WwiseCommand import *
from WPMHelper import * 
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
        WPMHelper.Get().CleanWwiseProject()

        list_config = ["Debug","Profile","Release"]
        arch = "x64"
        toolset = WPMHelper.Get().GetWindowsToolsetList()
        not_build_black_list = WPMHelper.Get().GetWindowsToolsetBuildBlackList()
       
        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()
        
        one_param_premake = ParamsWwisePluginPremake()
        ## Authoring would generate all platforms
        one_param_premake.platform = "Authoring"
        OneWwiseCommand.Premake(one_param_premake)

        for one_config in list_config:
            one_param = ParamsWwisePluginBuild()
            one_param.config = one_config
            one_param.arch = arch

            for one_toolset in toolset:
                if one_toolset in not_build_black_list:
                    PrintLog("Skip Build - %s" % one_toolset)
                    continue
                one_param.toolset = one_toolset
                one_param.platform = "Windows_" + one_toolset
                OneWwiseCommand.Build(one_param)
        
        PrintStageLog("Win64 - Package_Wwise Build Complete")
        
        ## Archive
        ## Final Product 
        for one_config in list_config:
            for one_toolset in toolset:
                OneArchiveInfo = ArchiveInfo_WwisePlugin(
                    WPMHelper.Get().GetName_WwisePluginName(),
                    WPMHelper.Get().GetVer_Wwise(),
                    SystemHelper.Mac_TargetName(),
                    one_config,
                    arch,
                    one_toolset
                )
                extension = "dll"
                name_final_product = OneArchiveInfo.GetArchiveName()   + "."  + extension
                path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() / OneArchiveInfo.GetArchiveSubDirBasedOnInfo() / "bin" / name_final_product
                PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
                bshould_clean_others_when_archving = False
                ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

                extension = "lib"
                name_final_product = OneArchiveInfo.GetArchiveName()  + "."   + extension
                path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() /OneArchiveInfo.GetArchiveSubDirBasedOnInfo() / "bin" / name_final_product
                PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
                bshould_clean_others_when_archving = False
                ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

        PrintStageLog("Win64 - Package_Wwise Archive Complete")