
from Platform.PlatformBase import *
from Command.GenerateProjectFilesWithShellCommand import *
from Command.IPhonePackagerCommand import *
from Command.UBTCommand import * 
from Command.MacUtilityCommand import *
from pathlib import Path
from FileIO.FileUtility import *

from UBSHelper import *
from ABSHelper import *

import shutil

from Utility.UnrealProjectManager import *

## Wwise
from Command.WwiseCommand import * 
from WPMHelper import * 

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
        self.SetupEnvironment()

    def SetupEnvironment(self):
        PrintStageLog("Mac Host Platform: SetupEnvironment Begin")
        
        self.SetEngineInfoPlistTmpl()
        self.SetEngineEntitlementsTmpl()
        
        PrintStageLog("Mac Host Platform: SetupEnvironment End")

    def CallCMD_PlistBuddy(self,one_command,target_file,error_msg_when_failed):
        OneXcodeCommand = XcodeCommand()
        try:
            OneXcodeCommand.PlistBuddy(one_command,target_file,False)
        except:
            PrintWarn(error_msg_when_failed)
                


    def SetEngineInfoPlistTmpl(self):
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        if bis_agora_ue_project:
            
            ## Legency Xcode Project Infoplist
            # Ex. "/Users/Shared/Epic Games/UE_4.27"
            path_engine_root = UBSHelper.Get().GetPath_UEEngine()
            path_mac_infoplist_tmpl = path_engine_root / Path("Engine/Source/Runtime/Launch/Resources/Mac/Info.plist")

            PrintLog(f"Mac Host Machine: Add [Camera] and [Microphone] permissions to UE Engine[{UBSHelper.Get().GetVer_UEEngine()}] 's (Launch Module) info plists")

            error_msg_when_failed_legency = "PlistBuddy Failed to add permission to infoplist (in Launch module): maybe it has already been added."
            self.CallCMD_PlistBuddy("Add :NSCameraUsageDescription string 'AgoraVideoCall'",path_mac_infoplist_tmpl,error_msg_when_failed_legency)
            self.CallCMD_PlistBuddy("Add :NSMicrophoneUsageDescription string 'AgoraMicrophoneCall'",path_mac_infoplist_tmpl,error_msg_when_failed_legency)



            ## For Morden Xcode Project Infoplist
            path_mac_infoplist_tmpl = UBSHelper.Get().GetPath_UEEngine() / Path("Engine/Build/Mac/Resources/Info.Template.plist")
            if path_mac_infoplist_tmpl.exists():
                PrintLog(f"Mac Host Machine: Add [Camera] and [Microphone] permissions to UE Engine[{UBSHelper.Get().GetVer_UEEngine()}] 's (Build) info plists")

                error_msg_when_failed_modern = "PlistBuddy Failed to add permission to infoplist (in Build): maybe it has already been added."
                self.CallCMD_PlistBuddy("Add :NSCameraUsageDescription string 'AgoraVideoCall'",path_mac_infoplist_tmpl,error_msg_when_failed_modern)
                self.CallCMD_PlistBuddy("Add :NSMicrophoneUsageDescription string 'AgoraMicrophoneCall'",path_mac_infoplist_tmpl,error_msg_when_failed_modern)


    
    def SetEngineEntitlementsTmpl(self):
        
        ## For Morden Xcode Project Entitlements
        ## Default：For [DebugGame] or [Development] 
        bshould_modify_debug_development = True
        filename_mac_entitlements_dev = "Sandbox.Server.entitlements"
        if bshould_modify_debug_development:
            self.SetEngineEntitlementsTmpl_Inner(filename_mac_entitlements_dev)
        else:
            PrintLog(f"Mac Host Machine: do nothing to [{filename_mac_entitlements_dev}], should modify [{bshould_modify_debug_development}] ")


        ## For Morden Xcode Project Entitlements
        ## Default：For [Shipping]
        bshould_modify_shipping = True
        filename_mac_entitlements_shipping = "Sandbox.NoNet.entitlements"
        if bshould_modify_shipping:
            self.SetEngineEntitlementsTmpl_Inner(filename_mac_entitlements_shipping)
        else:
            PrintLog(f"Mac Host Machine: do nothing to [{filename_mac_entitlements_shipping}], should modify [{bshould_modify_shipping}] ")



    def SetEngineEntitlementsTmpl_Inner(self,filename_entitlements:str):
        path_mac_entitlements_file = UBSHelper.Get().GetPath_UEEngine() / Path(f"Engine/Build/Mac/Resources/{filename_entitlements}")
        if path_mac_entitlements_file.exists():
            PrintLog(f"Mac Host Machine: add permissiones to [{filename_entitlements}]")

            error_msg_when_failed =f"PlistBuddy Failed to add permission to [{filename_entitlements}]: maybe it has already been added."
            if filename_entitlements == "Sandbox.Server.entitlements":
                ## Default: For [DebugGame] or [Development]
                self.CallCMD_PlistBuddy("Add :com.apple.security.app-sandbox bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.audio-input bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.bluetooth bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.camera bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.usb bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.network.client bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.network.server bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.personal-information.addressbook bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.personal-information.calendars bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.personal-information.location bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.print bool true",path_mac_entitlements_file,error_msg_when_failed)

            elif filename_entitlements == "Sandbox.NoNet.entitlements":
                ## Default: For [Shipping]
                self.CallCMD_PlistBuddy("Add :com.apple.security.app-sandbox bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.audio-input bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.device.camera bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.network.client bool true",path_mac_entitlements_file,error_msg_when_failed)
                self.CallCMD_PlistBuddy("Add :com.apple.security.network.server bool true",path_mac_entitlements_file,error_msg_when_failed)


        else:
            PrintLog(f"Mac Host Machine: do nothing to [{filename_entitlements}] file exists {path_mac_entitlements_file.exists()} path {path_mac_entitlements_file}")


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
        self.CleanPreviousArchivedBuild()
        

    def PostPackaged(self):
        PrintStageLog("PostPackaged - Mac")

        ## Set Final Product
        path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform())
        self.SetArchivePath_FinalProduct(path_final_product)

        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        if bis_agora_ue_project:
            
            PrintLog("IsAgoraUEProject [%s] " %(str(bis_agora_ue_project)))

            dst_path_app_archive_dir = Path(UBSHelper.Get().GetPath_ArchiveDir(self.GetTargetPlatform()))
            self.CopyFrameworkToApplication(dst_path_app_archive_dir)

        
        self.PostPackaged_DoXcodeBuild()

        bis_ue53_or_later = UBSHelper.Get().Is_UE53_Or_Later()
        if bis_ue53_or_later:
            path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform(),bInBinaries=True)
            self.SetArchivePath_FinalProduct(path_final_product)
        else:
            ### no need to do anything 
            pass
    
    def PostPackaged_DoXcodeBuild(self):
        ## The Morden Xcode Project Feature was introduced in UE53
        bis_ue53_or_later = UBSHelper.Get().Is_UE53_Or_Later()
        if bis_ue53_or_later:
            self.PostPackaged_UseMordenXcodeProject()

            ## Copy Framework
            dst_path_app_archive_dir = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform(),bInBinaries=True) / ".."
            self.CopyFrameworkToApplication(dst_path_app_archive_dir)

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
            params.sdk = "macosx"
            OneXcodeCommand.XcodeBuild(params)

    def PostPackaged_UseLegencyXcodeProject(self):
        ## for now, no need further actions
        pass


    def CopyFrameworkToApplication(self,dst_path_app_archive_dir):

        ## Ex."/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/"
        project_folder_path = UBSHelper.Get().GetPath_ProjectRoot()
        ## Ex. for 4.27 "/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/ArchiveBuilds/MacNoEditor/AgoraExample.app"
        src_path = project_folder_path / MacPlatformPathUtility.GetFrameworkSrcPathFromSDK()

        ## Ex. "AgoraExample.app"
        app_name = UBSHelper.Get().GetName_PackagedApp(self.GetTargetPlatform())
        ## Ex. "xxx/AgoraExample.app"
        app_dst_achive_folder = dst_path_app_archive_dir / app_name
        ## Ex. "xxx/AgoraExample.app/Contents/MacOS"
        dst_path = app_dst_achive_folder / MacPlatformPathUtility.GetFrameworkDstPathInApplication()

        PrintLog("Copy Framework: src: [ " + str(src_path) + "] dst: [ " + str(dst_path)+"]")
        FileUtility.CopyDir(src_path,dst_path)

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



    def CleanPreviousArchivedBuild(self):
        ## Delete Default ArchiveBuild
        PrintLog(f"CleanPreviousArchivedBuild - {self.GetTargetPlatform()}")
        path_default_archive_build = UBSHelper.Get().GetPath_DefaultArchiveDir(self.GetTargetPlatform())
        if path_default_archive_build.exists():
            FileUtility.DeleteDir(path_default_archive_build)







#####################################################################################
#################################### Wwise ##########################################


    def Package_Wwise(self):
        WPMHelper.Get().CleanWwiseProject()

        list_config = ["Debug","Profile","Release"]

        arch_list = ["x86_64","arm64"]
        ## arch = SystemHelper.Get().GetHostPlatformArchitechture()
        platform =  "Mac"

        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()

        one_param_premake = ParamsWwisePluginPremake()
        one_param_premake.platform = "Mac"
        OneWwiseCommand.Premake(one_param_premake)

        path_xcode_workspace_static = WPMHelper.Get().GetPath_WPProject() / "SoundEnginePlugin/AgoraWwiseRTCSDK_Mac_static.xcodeproj/project.pbxproj"
        # default_generated_apple_team_id = WPMHelper.Get().GetWwiseDefaultTeamID()
        # apple_team_id = WPMHelper.Get().GetAppleTeamID()
        # FileUtility.ReplaceFileContent(path_xcode_workspace_static,default_generated_apple_team_id,apple_team_id)

        # FileUtility.ReplaceFileLineContent(path_xcode_workspace_static,"CODE_SIGN_IDENTITY =",' "-";')
        
        ## CODE_SIGN_IDENTITY = "-": means: Sign to run locally
        FileUtility.InsertLineToFileBeforePrefix(path_xcode_workspace_static,"CONFIGURATION_BUILD_DIR = /Applications/",'CODE_SIGN_IDENTITY = "-";')



        path_xcode_workspace_shared = WPMHelper.Get().GetPath_WPProject() / "SoundEnginePlugin/AgoraWwiseRTCSDK_Mac_shared.xcodeproj/project.pbxproj"
        # FileUtility.ReplaceFileContent(path_xcode_workspace_shared,default_generated_apple_team_id,apple_team_id)
        # FileUtility.ReplaceFileLineContent(path_xcode_workspace_shared,"CODE_SIGN_IDENTITY =",' "-";')
        
        ## CODE_SIGN_IDENTITY = "-": means: Sign to run locally
        FileUtility.InsertLineToFileBeforePrefix(path_xcode_workspace_shared,"CONFIGURATION_BUILD_DIR = /Applications/",'CODE_SIGN_IDENTITY = "-";')



        ## BuildTmpDir
        ## need to combine x86_64 and arm64 to be a universal lib
        ### Ex. AgoraWwiseRTCSDK_BuildTmp
        NAME_BUILD_TMP_DIR = WPMHelper.Get().GetName_WwisePluginName()+ "_" + "BuildTmp"



        for one_config in list_config:
            ## Ex. /Applications/Audiokinetic/Wwise2021.1.14.8108/SDK/Mac/Debug/lib
            ### Clean tmp build folder
            path_build_arch_tmp_base = WPMHelper.Get().GetPath_WwiseSDKBase() / Path("Mac") / one_config / "lib" / NAME_BUILD_TMP_DIR
            if path_build_arch_tmp_base.exists():
                FileUtility.DeleteDir(path_build_arch_tmp_base)
            path_build_arch_tmp_base.mkdir(parents=True,exist_ok=True)

            for one_arch  in arch_list:
                ## Clean
                ### Clean the product in Ex. /Applications/Audiokinetic/Wwise2021.1.14.8108/SDK/Mac/Debug/lib
                OneArchiveInfo = ArchiveInfo_WwisePlugin(
                    WPMHelper.Get().GetName_WwisePluginName(),
                    WPMHelper.Get().GetVer_Wwise(),
                    SystemHelper.Mac_TargetName(),
                    one_config
                )
                extension = "a"
                name_final_product = OneArchiveInfo.GetArchiveName()  + "."   + extension
                path_final_build_tmp = path_build_arch_tmp_base.parent / name_final_product
                FileUtility.DeleteFile(path_final_build_tmp)

                ## Build
                ### Build the product in Ex. /Applications/Audiokinetic/Wwise2021.1.14.8108/SDK/Mac/Debug/lib
                one_param_build = ParamsWwisePluginBuild()
                one_param_build.config = one_config
                one_param_build.arch = one_arch
                one_param_build.platform = platform
                OneWwiseCommand.Build(one_param_build)

                ### Create Tmp Dir to save the build result
                path_final_arch_tmp = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_"+ one_arch)
                path_final_arch_tmp.mkdir(parents=True,exist_ok=True)

                FileUtility.CopyFile(path_build_arch_tmp_base.parent / name_final_product,path_final_arch_tmp / name_final_product)
            
            ## Combine x86_64 and arm64 to be a universal lib
            ## In /Applications/Audiokinetic/Wwise2021.1.14.8108/SDK/Mac/Debug/lib/[NAME_BUILD_TMP_DIR] there would be 3 libs
            ## Ex. AgoraWwiseRTCSDK_x86_64
            ## Ex. AgoraWwiseRTCSDK_arm64
            ## Ex. AgoraWwiseRTCSDK_universal
            OneLipoCommand = LipoCommand()
            path_tmp_x86_64 = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_x86_64") / name_final_product
            path_tmp_arm64 = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_arm64") / name_final_product
            path_tmp_dir_universal = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_universal") 
            path_tmp_dir_universal.mkdir(parents=True,exist_ok=True)
            path_tmp_universal = path_tmp_dir_universal / name_final_product
            OneLipoCommand.CreateUniversalArch(path_tmp_universal,path_tmp_x86_64,path_tmp_arm64)


        PrintStageLog("Mac - Package_Wwise Build Complete")
        
        ## Archive
        ## Final Product 
        for one_config in list_config:
            path_build_arch_tmp_base = WPMHelper.Get().GetPath_WwiseSDKBase() / Path("Mac") / one_config / "lib" / NAME_BUILD_TMP_DIR
            OneArchiveInfo = ArchiveInfo_WwisePlugin(
                WPMHelper.Get().GetName_WwisePluginName(),
                WPMHelper.Get().GetVer_Wwise(),
                SystemHelper.Mac_TargetName(),
                one_config
            )
            extension = "a"
            name_final_product = OneArchiveInfo.GetArchiveName()  + "."   + extension
            
            path_tmp_x86_64 = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_x86_64") / name_final_product
            path_tmp_arm64 = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_arm64") / name_final_product
            path_tmp_universal = path_build_arch_tmp_base / (WPMHelper.Get().GetName_WwisePluginName()+ "_universal") / name_final_product

            ## For now, we only need the universal lib
            ## [TBD] support to archive other arch libs
            path_target_archive_file = path_tmp_universal

            PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
            bshould_clean_others_when_archving = False
            ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

            FileUtility.DeleteDir(path_build_arch_tmp_base)

        PrintStageLog("Mac - Package_Wwise Archive Complete")



      

