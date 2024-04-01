
from Platform.PlatformBase import *
from Command.GenerateProjectFilesWithShellCommand import *
from Command.IPhonePackagerCommand import *
from Command.UBTCommand import * 
from pathlib import Path
from FileIO.FileUtility import FileUtility

from UBSHelper import *

import shutil

class MacPlatformPathUtility:
    @staticmethod
    def GetDefaultEnginePath():
        return Path("/Users/Shared/Epic Games")
    
    @staticmethod
    def GetRunUATPath():
        return Path("Engine/Build/BatchFiles/RunUAT.sh")
    
    def GetMonoScriptPath():
        return Path("Engine/Build/BatchFiles/Mac/RunMono.sh")

    def GetIPhonePackagerPath():
        return Path("Engine/Binaries/DotNET/IOS/IPhonePackager.exe")
    
    @staticmethod
    def GetGenerateProjectScriptPath():
        return Path("Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh") 

    def GetFrameworkDstPathInApplication():
        return Path("Contents/MacOS")
    
    def GetFrameworkSrcPathFromSDK():
        return Path("Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/Mac/Release/")
    
    def GetUBTPath():
        return Path("Engine/Binaries/DotNET/UnrealBuildTool.exe")
    


class MacPlatformBase(PlatformBase):
    def GenHostPlatformParams(args):
        ret,val = PlatformBase.GenHostPlatformParams(args)
        
        path_engine = UBSHelper.Get().GetPath_UEEngine()

        key = "uat_path"
        ## if a path starts with '/', it would be treated as starting from the root path.
        val[key] = Path(path_engine) / MacPlatformPathUtility.GetRunUATPath()

        key = "genprojfiles_path"
        val[key] = Path(path_engine)/ MacPlatformPathUtility.GetGenerateProjectScriptPath()


        key = "bundlename"
        val[key] = args.bundlename if 'bundlename' in args else ""

        key = "mono_path"
        val[key] = Path(path_engine) / MacPlatformPathUtility.GetMonoScriptPath()

        key = "iphonepackager_path"
        val[key] = Path(path_engine) / MacPlatformPathUtility.GetIPhonePackagerPath()


        return ret,val
    
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)

        # key = "target_platform"
        # val[key] = "Mac"

        PrintLog("PlatformBase - GenParams")
        return ret,val



class MacHostPlatform(BaseHostPlatform):
    def __init__(self,host_params) -> None:
        self.Params = host_params
        path_script_genproj = Path(UBSHelper.Get().GetPath_UEEngine()) / MacPlatformPathUtility.GetGenerateProjectScriptPath()
        self.OneUATCommand = UATCommand(self.Params['uat_path'],path_script_genproj)

    def GenerateProject(self,path_uproject_file):
        ## uproject file could be any uproject file, not only the target project
        genproj_script = self.GetParamVal("genprojfiles_path")
        one_command = GenerateProjectFilesWithShellCommand(genproj_script)

        params = ParamsGenProjectWithShell()
        params.path_uproject_file = path_uproject_file
    
        one_command.GenerateProjectFiles(params)
        PrintLog("BaseHostPlatform - GenerateProject")
    
    def GenerateIOSProject(self,path_uproject):
        ubt_path = Path(UBSHelper.Get().GetPath_UEEngine()) / Path(MacPlatformPathUtility.GetUBTPath())

        one_command = UBTCommand(ubt_path,self.Params["mono_path"])

        params = ParamsUBT()
        params.path_uproject_file = path_uproject
        
        one_command.GenerateIOSProject(params)
        PrintLog("BaseHostPlatform - GenerateProject")

    
    def IOSSign(self,path_uproject_file,bundlename):
        path_mono =  self.GetParamVal("mono_path")
        path_iphonerpackager =  self.GetParamVal("iphonepackager_path")

        OneIPhonePackagerCommand = IPhonePackagerCommand(path_mono,path_iphonerpackager)

        params = ParamsIPhonePacakger()
        params.path_uproject_file = path_uproject_file
        params.bunndle_name = bundlename

        OneIPhonePackagerCommand.Sign(params)


class MacTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.Mac_TargetName()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Mac Platform")

    def PostPackaged(self):
        PrintStageLog("PostPackaged")
        app_name = "AgoraExample.app"

        platform_folder = "Mac"
        if UBSHelper.Get().GetVer_UEEngine() == '4.27':
            platform_folder = "MacNoEditor"
        
        project_folder_path = UBSHelper.Get().GetPath_ProjectRoot()
        app_dst_achieve_folder = project_folder_path / "ArchivedBuilds" / platform_folder / app_name
        src_path = project_folder_path / MacPlatformPathUtility.GetFrameworkSrcPathFromSDK()
        dst_path = app_dst_achieve_folder / MacPlatformPathUtility.GetFrameworkDstPathInApplication()
        PrintLog("Copy Framework: src: [ " + str(src_path) + "] dst: [ " + str(dst_path)+"]")
        #PrintLog(str(dst_path))
        #shutil.copytree(src_path,dst_path,dirs_exist_ok= True)
        FileUtility.CopyFilesWithSymbolicLink(src_path,dst_path)

    def Package(self):
        self.SetupEnvironment()
        PrintStageLog("Package - %s Platform" % self.GetTargetPlatform())

        params = ParamsUAT()
        params.target_platform = self.GetTargetPlatform()
        params.path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        params.path_engine = UBSHelper.Get().GetPath_UEEngine()
        params.path_archive = UBSHelper.Get().GetPath_ArchiveDirBase()
        self.RunUAT().BuildCookRun(params)

        self.PostPackaged()
