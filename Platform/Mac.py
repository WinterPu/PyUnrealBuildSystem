
from Platform.PlatformBase import *
from Command.GenerateProjectFilesWithShellCommand import *
from Command.IPhonePackagerCommand import *
from Command.UBTCommand import * 
from pathlib import Path
from FileIO.FileUtility import *

from UBSHelper import *
from ABSHelper import *

import shutil

from Utility.UnrealProjectManager import *

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
    

    def GetBuildFolderName():
        if UBSHelper.Get().Is_UE5_Or_Later():
            return "Mac"
        else:
            return "MacNoEditor"
        
    

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

    def SetupEnvironment(self):
        self.SetEngineInfoPlistTmpl()

    def SetEngineInfoPlistTmpl(self):
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        if bis_agora_ue_project:

            # Ex. "/Users/Shared/Epic Games/UE_4.27"
            path_engine_root = UBSHelper.Get().GetPath_UEEngine()
            path_mac_infoplist_tmpl = path_engine_root / Path("Engine/Source/Runtime/Launch/Resources/Mac/Info.plist")

            OneXcodeCommand = XcodeCommand()
            OneXcodeCommand.PlistBuddy("Add :NSCameraUsageDescription string 'AgoraVideoCall'",path_mac_infoplist_tmpl,True)
            OneXcodeCommand.PlistBuddy("Add :NSMicrophoneUsageDescription string 'AgoraMicrophoneCall'",path_mac_infoplist_tmpl,True)

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
        PrintStageLog("PostPackaged - Mac")

        ## Set Final Product
        path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform())
        self.SetArchivePath_FinalProduct(path_final_product)

        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        if bis_agora_ue_project:
            
            PrintLog("IsAgoraUEProject [%s] " %(str(bis_agora_ue_project)))

            ## Ex. "AgoraExample.app"
            app_name = UBSHelper.Get().GetName_PackagedApp(self.GetTargetPlatform())
            ## Ex."/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/"
            project_folder_path = UBSHelper.Get().GetPath_ProjectRoot()
            ## Ex. for 4.27 "/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/ArchiveBuilds/MacNoEditor/AgoraExample.app"
            app_dst_achieve_folder = Path(UBSHelper.Get().GetPath_ArchiveDir(self.GetTargetPlatform())) / app_name
            src_path = project_folder_path / MacPlatformPathUtility.GetFrameworkSrcPathFromSDK()
            dst_path = app_dst_achieve_folder / MacPlatformPathUtility.GetFrameworkDstPathInApplication()
            PrintLog("Copy Framework: src: [ " + str(src_path) + "] dst: [ " + str(dst_path)+"]")
            FileUtility.CopyDir(src_path,dst_path)
        
        self.PostPackaged_DoXcodeBuild()

        path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform(),bInBinaries=True)
        self.SetArchivePath_FinalProduct(path_final_product)
    
    def PostPackaged_DoXcodeBuild(self):
        ## The Morden Xcode Project Feature was introduced in UE53
        bis_ue53_or_later = UBSHelper.Get().Is_UE53_Or_Later()
        if bis_ue53_or_later:
            self.PostPackaged_UseMordenXcodeProject()
        else:
            self.PostPackaged_UseLegencyXcodeProject()



    def PostPackaged_UseMordenXcodeProject(self):
        PrintSubStageLog("Mac - PostPackaged_UseMordenXcodeProject")

        ## Make sure the previous build is successful
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        bis_sdkaudioonly = ABSHelper.Get().IsAgoraSDKAudioOnly()
        path_project_root = Path(UBSHelper.Get().GetPath_ProjectRoot())
        uproject_name = UBSHelper.Get().GetName_ProjectName()

        bhas_add_postxcodebuild = ABSHelper.Get().HasPostXcodeBuildAdded()

        if bis_agora_ue_project and bhas_add_postxcodebuild:
            ## Ex. AgoraExample_UE5
            resource_index_key = uproject_name + "_UE5"
            resource_tag_name = ABSHelper.Get().GetResourceTagName()
            src_root_path_resource = ConfigParser.Get().GetResourcesRootPath(resource_index_key,resource_tag_name)

            if not src_root_path_resource.exists():
                PrintErr(f"Cannot find resource root path {src_root_path_resource}")
                return 

            UnrealProjectManager.ReplaceXcodeProject(path_project_root,src_root_path_resource)
            OneXcodeCommand = XcodeCommand()
            params = ParamsXcodebuild()

            name_workspace = uproject_name + " (Mac).xcworkspace"
            params.scheme = uproject_name
            params.workspace =  path_project_root / name_workspace
            params.destination = "generic/platform=macOS"
            OneXcodeCommand.XcodeBuild(params)

    def PostPackaged_UseLegencyXcodeProject(self):
        ## for now, no need further actions
        pass



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



