
from Platform.PlatformBase import *
from Command.GenerateProjectFilesCommand import *
from Command.IPhonePackagerCommand import *
from Command.UBTCommand import * 
from pathlib import Path
from FileIO.FileUtility import FileUtility

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

        key = "uat_path"
        ## if a path starts with '/', it would be treated as starting from the root path.
        val[key] = Path(val["engine_path"]) / MacPlatformPathUtility.GetRunUATPath()

        key = "genprojfiles_path"
        val[key] = Path(val["engine_path"])/ MacPlatformPathUtility.GetGenerateProjectScriptPath()


        key = "bundlename"
        val[key] = args.bundlename if 'bundlename' in args else ""

        key = "mono_path"
        val[key] = Path(val["engine_path"]) / MacPlatformPathUtility.GetMonoScriptPath()

        key = "iphonepackager_path"
        val[key] = Path(val["engine_path"]) / MacPlatformPathUtility.GetIPhonePackagerPath()


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
        
        self.Params['project_file_path'] = project_file_path

        one_command.GenerateProjectFiles(self.Params)
        PrintLog("BaseHostPlatform - GenerateProject")
    
    def GenerateIOSProject(self,path_uproject):
        engine_path = self.GetParamVal("engine_path")
        ubt_path = Path(engine_path) / Path(MacPlatformPathUtility.GetUBTPath())

        one_command = UBTCommand(ubt_path)

        self.Params["project_file_path"] = path_uproject

        one_command.GenerateIOSProject(self.Params)
        PrintLog("BaseHostPlatform - GenerateProject")

    
    def IOSSign(self,project_file_path,bundlename):
        path_mono =  self.GetParamVal("mono_path")
        path_iphonerpackager =  self.GetParamVal("iphonepackager_path")
        self.Params['project_path'] = project_file_path
        self.Params['bundlename'] = bundlename
        OneIPhonePackagerCommand = IPhonePackagerCommand(path_mono,path_iphonerpackager)
        OneIPhonePackagerCommand.Sign(self.Params)


class MacTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - Mac Platform")

    def PostPackaged(self):
        PrintStageLog("PostPackaged")
        app_name = "AgoraExample.app"

        platform_folder = "Mac"
        if self.GetParamVal('engine_ver') == '4.27':
            platform_folder = "MacNoEditor"
        
        project_path = Path(self.GetParamVal('project_path'))
        project_folder_path = project_path.parent
        app_dst_achieve_folder = project_folder_path / "ArchivedBuilds" / platform_folder / app_name
        src_path = project_folder_path / MacPlatformPathUtility.GetFrameworkSrcPathFromSDK()
        dst_path = app_dst_achieve_folder / MacPlatformPathUtility.GetFrameworkDstPathInApplication()
        PrintLog("Copy Framework: src: [ " + str(src_path) + "] dst: [ " + str(dst_path)+"]")
        #PrintLog(str(dst_path))
        #shutil.copytree(src_path,dst_path,dirs_exist_ok= True)
        FileUtility.CopyFilesWithSymbolicLink(src_path,dst_path)

    def Package(self):
        self.SetupEnvironment()
        PrintStageLog("Package - Mac Platform")
        self.RunUAT().BuildCookRun(self.Params)
        self.PostPackaged()
