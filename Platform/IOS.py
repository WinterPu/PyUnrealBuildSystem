from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
from ConfigParser import *

from Utility.VersionControlTool import *
from Command.ZipCommand import *

from FileIO.FileUtility import *

from UBSHelper import *
from ABSHelper import *

from Utility.UnrealProjectManager import *
from Command.FastLaneCommand import * 

## Wwise
from Command.WwiseCommand import * 
from WPMHelper import * 

class IOSPlatformPathUtility:
    @staticmethod
    def GetBCExtensionFrameworkDir():
        return Path("IOSFramework")
    
    def GetSrcReplayKitExtensionZipFilePath():
        return Path("Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/IOS/Release/AgoraReplayKitExtension.embeddedframework.zip")
    
class IOSPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)
        
        # key = "target_platform"
        # val[key] = "IOS"

        key = "ioscert"
        val[key] = args.ioscert if "ioscert" in args  else ""

        if "enginever" in args:
            bUseMordenXcodeSetting = UBSHelper.Get().DoesUseModernXcodeProject()
            key = "iosbundleval"
            if bUseMordenXcodeSetting:
                ## for now, it would set [moderniosbundleidprefix] to str_bundlename.rsplit('.',1)[0]
                ## Example. [io.agora.AgoraExample], it would be [io.agora]
                str_bundlename = str(args.iosbundlename)
                # val[key] = args.moderniosbundleidprefix
                val[key] = str_bundlename.rsplit('.',1)[0]
            else:
                val[key] = args.iosbundlename

        return ret,val
    

class IOSTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.IOS_TargetName()
    
    def SetupEnvironment(self):
        PrintLog("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

        path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()

        PrintLog("IOSTargetPlatform - SetupEnvironment: Copying Mobile Provisions To Environment")
        ConfigParser.Get().CopyAllMobileProvisionsToDstPath()

        bUseMordenXcodeSetting = UBSHelper.Get().DoesUseModernXcodeProject()
        bRet = UnrealConfigIniManager.SetConfig_IOSCert(path_uproject_file,self.Params['ioscert'],bUseMordenXcodeSetting)
        if bRet:
            PrintLog("IOSTargetPlatform - SetupEnvironment Certificate %s Set Done!" % self.Params['ioscert'] )
        else:
            PrintErr("IOSTargetPlatform - SetupEnvironment Certificate Set Failed")


        UnrealConfigIniManager.SetConfig_BundleIdentifier(path_uproject_file,self.Params['iosbundleval'],bUseMordenXcodeSetting)

        ## Agora
        self.PrepareMannualOp_BCExtension()

        self.CleanEmbdededFrameworks()

        ## Clean Previous ArchiveBuild
        self.CleanPreviousArchiveBuild()


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
        
    
    def PrepareMannualOp_BCExtension(self):
        path_project_root = Path(UBSHelper.Get().GetPath_ProjectRoot())
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        bis_audioonly = ABSHelper.Get().IsAgoraSDKAudioOnly()
        
        if bis_agora_ue_project and not bis_audioonly:

            # Ex. [Project] / IOSFramework
            root_path_framework_dir = path_project_root / IOSPlatformPathUtility.GetBCExtensionFrameworkDir()
            if not root_path_framework_dir.exists():
                root_path_framework_dir.mkdir(parents=True)
            

            extension_folder_name = "AgoraReplayKitExtension.framework"
            # Ex. [Project] / IOSFramework / AgoraReplayKitExtension.framework
            path_target_extension = root_path_framework_dir / extension_folder_name 

            if path_target_extension.exists():
                FileUtility.DeleteDir(path_target_extension)

            # Ex. Src: [Project] /Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/IOS/Release/AgoraReplayKitExtension.embeddedframework.zip
            #     Dst: [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework.zip
            src_zip_file_path_replay_kit = path_project_root / IOSPlatformPathUtility.GetSrcReplayKitExtensionZipFilePath()
            dst_zip_file_path_replay_kit  = root_path_framework_dir / src_zip_file_path_replay_kit.name
            FileUtility.CopyFile(src_zip_file_path_replay_kit,dst_zip_file_path_replay_kit)

            OneZipCommand = ZipCommand()
            OneZipCommand.UnZipFile(dst_zip_file_path_replay_kit,root_path_framework_dir)
            # Ex. [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework
            target_unzip_path = root_path_framework_dir / dst_zip_file_path_replay_kit.stem

            # Ex. [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework / AgoraReplayKitExtension.framework
            # --> [Project] / IOSFramework / AgoraReplayKitExtension.framework
            unzipped_folder = target_unzip_path / extension_folder_name
            if unzipped_folder.exists():
                    unzipped_folder.rename(target_unzip_path.parent/ extension_folder_name)

            # Del: [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework.zip
            # Del: [Project] / IOSFramework / AgoraReplayKitExtension.embeddedframework
            FileUtility.DeleteFile(dst_zip_file_path_replay_kit)
            FileUtility.DeleteDir(target_unzip_path)


    def PostPackaged(self):
        PrintStageLog("PostPackaged - IOS")
        
        path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform(),bInBinaries= False)


        ## Convert App To IPA
        bUseMordenXcodeProject = UBSHelper.Get().DoesUseModernXcodeProject()
        if bUseMordenXcodeProject:
            path_app = Path(path_final_product).with_suffix('.app')
            UnrealProjectManager.ConvertMacAppToIPA(path_app)


        self.SetArchivePath_FinalProduct(path_final_product)

        bHasPostXcodeBuildAdded = ABSHelper.Get().HasPostXcodeBuildAdded()

        if bHasPostXcodeBuildAdded:

            self.PostPackaged_DoXcodeBuild()
            
            path_final_product = UBSHelper.Get().GetPath_FinalProduct(self.GetTargetPlatform(),bInBinaries=True)
            self.SetArchivePath_FinalProduct(path_final_product)


        bshould_gen_with_all_ios_certs = UBSHelper.Get().ShouldPackageWithAllIOSCerts()

        if bshould_gen_with_all_ios_certs:
            name_final_ipa = path_final_product.stem
            path_archive_all_ios_dir = path_final_product.parent / Path(UBSHelper.Get().GetName_AllIOSCertsArchiveDir())
            if path_archive_all_ios_dir.exists():
                FileUtility.DeleteDir(path_archive_all_ios_dir)
            path_archive_all_ios_dir.mkdir(parents=True,exist_ok=True)
            iocerts_items = ConfigParser.Get().GetAllIOSCertificates()

            for tag_name, one_ioscert in iocerts_items:
                path_app_with_target_ioscert = path_archive_all_ios_dir / (f"{name_final_ipa}_{tag_name}.ipa")
                FileUtility.CopyFile(path_final_product,path_app_with_target_ioscert)
                if ConfigParser.Get().IsIOSCertValid(tag_name) :
                    PrintLog("[IPAResign] Use IOS Certificate %s " %tag_name)
                    OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(tag_name)
                    OneFastLaneCommand = FastLaneCommand()
                    OneFastLaneCommand.IPAResign(
                        path_app_with_target_ioscert,
                        OneIOSCert.get_signing_identity,
                        OneIOSCert.get_filepath_mobileprovision
                    )
                    PrintLog(f"Resign Complete ===> Path [{path_app_with_target_ioscert}]")

                self.SetArchivePath_FinalProductDir(path_archive_all_ios_dir)


    def PostPackaged_DoXcodeBuild(self):
        ## The Morden Xcode Project Feature was introduced in UE53
        bis_ue53_or_later = UBSHelper.Get().Is_UE53_Or_Later()
        if bis_ue53_or_later:
            self.PostPackaged_UseMordenXcodeProject()
        else:
            self.PostPackaged_UseLegencyXcodeProject()
            
    def PostPackaged_UseMordenXcodeProject(self):
        PrintSubStageLog("IOS - PostPackaged_UseMordenXcodeProject")

        ## Make sure the previous build is successful
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        bis_audioonly = ABSHelper.Get().IsAgoraSDKAudioOnly()
        path_project_root = Path(UBSHelper.Get().GetPath_ProjectRoot())
        uproject_name = UBSHelper.Get().GetName_ProjectName()

        bhas_add_postxcodebuild = ABSHelper.Get().HasPostXcodeBuildAdded()

        PrintLog(f"Status: IsAgoraProject: {bis_agora_ue_project} NeedAddPostXcodeBuild {bhas_add_postxcodebuild}")
        if bis_agora_ue_project and bhas_add_postxcodebuild:
            
            ## Ex. AgoraExample_UE5
            resource_index_key = uproject_name + "_UE5"
            resource_tag_name = ABSHelper.Get().GetResourceTagName()
            src_root_path_resource = ConfigParser.Get().GetResourcesRootPath(resource_index_key,resource_tag_name)
            
            PrintLog(f"ResourcePath: [{src_root_path_resource}]")

            if not src_root_path_resource.exists():
                PrintErr(f"Cannot find resource root path {src_root_path_resource}")
                return 


            UnrealProjectManager.ReplaceXcodeProject(path_project_root,src_root_path_resource)
            OneXcodeCommand = XcodeCommand()
            params = ParamsXcodebuild()

            name_workspace = uproject_name + " (IOS).xcworkspace"
            params.scheme = uproject_name
            params.workspace =  path_project_root / name_workspace

            ioscert_tag_name = self.Params['ioscert']
            OneIOSCert:IOSCertInfo = ConfigParser.Get().GetOneIOSCertificate(ioscert_tag_name)
            if OneIOSCert != None:
                params.codesign_identity = OneIOSCert.get_signing_identity
                params.provisioning_profile_specifier = OneIOSCert.get_provisioning_profile_specifier
            
            OneXcodeCommand.XcodeBuild(params)

            ## Ex. [project_root_path] /  "Binaries" / "IOS" / "AgoraExample.app"
            name_app =  uproject_name + ".app"
            path_app = path_project_root / "Binaries" / "IOS" / name_app
            UnrealProjectManager.ConvertMacAppToIPA(path_app)


    def PostPackaged_UseLegencyXcodeProject(self):
        PrintSubStageLog("IOS - PostPackaged_UseLegencyXcodeProject")

        ## Make sure the previous build is successful
        bis_agora_ue_project = ABSHelper.Get().IsAgoraUEProject()
        bis_audioonly = ABSHelper.Get().IsAgoraSDKAudioOnly()
        path_project_root = Path(UBSHelper.Get().GetPath_ProjectRoot())
        uproject_name = UBSHelper.Get().GetName_ProjectName()

        bhas_add_postxcodebuild = ABSHelper.Get().HasPostXcodeBuildAdded()

        PrintLog(f"Status: IsAgoraProject: {bis_agora_ue_project} NeedAddPostXcodeBuild {bhas_add_postxcodebuild}")
        if bis_agora_ue_project and bhas_add_postxcodebuild:
            ## Ex. AgoraExample_UE4
            resource_index_key = uproject_name + "_UE4"
            resource_tag_name = ABSHelper.Get().GetResourceTagName()
            src_root_path_resource = ConfigParser.Get().GetResourcesRootPath(resource_index_key,resource_tag_name)
            PrintLog(f"ResourcePath: [{src_root_path_resource}]")


            if not src_root_path_resource.exists():
                PrintErr(f"Cannot find resource root path {src_root_path_resource}")
                return 


            UnrealProjectManager.ReplaceXcodeProject(path_project_root,src_root_path_resource,"ProjectFilesIOS")
            OneXcodeCommand = XcodeCommand()

            params = ParamsXcodebuild()
            name_workspace = uproject_name + "_IOS.xcworkspace"
            params.workspace =  path_project_root / name_workspace
            params.scheme = uproject_name
            
            ioscert_tag_name = self.Params['ioscert']
            OneIOSCert:IOSCertInfo = ConfigParser.Get().GetOneIOSCertificate(ioscert_tag_name)
            if OneIOSCert != None:
                params.codesign_identity = OneIOSCert.get_signing_identity
                params.provisioning_profile_specifier = OneIOSCert.get_provisioning_profile_specifier
            
            OneXcodeCommand.XcodeBuild(params)

            ## Ex. [project_root_path] /  "Binaries" / "IOS" / "AgoraExample.app"
            name_app =  uproject_name + ".app"
            path_app = path_project_root / "Binaries" / "IOS" / "Payload" / name_app
            UnrealProjectManager.ConvertMacAppToIPA(path_app)

    def  CleanEmbdededFrameworks(self):
        path_engine = UBSHelper.Get().GetPath_UEEngine()
        path_unzipped_framework = path_engine / "Engine" / "Intermediate" / "UnzippedFrameworks"
        if path_unzipped_framework.exists():
            FileUtility.DeleteDir(path_unzipped_framework)
            PrintLog(f"Cleaned Unzipped Frameworks, path {path_unzipped_framework}")
        else:
            PrintLog("No Unzipped Frameworks Found")

        path_unzipped_framework.mkdir(parents=True,exist_ok=True)

    def CleanPreviousArchiveBuild(self):
        ## founded: when you packaging audio-only example app:
        ## it would use the previous full-app, so that audio-only example app has a full plugin framework
        ## Here, just use a simple way: delete the previous app

        ## Delete Default ArchiveBuild
        PrintLog(f"CleanPreviousArchivedBuild - {self.GetTargetPlatform()}")
        path_default_archive_build = UBSHelper.Get().GetPath_DefaultArchiveDir(self.GetTargetPlatform())
        if path_default_archive_build.exists():
            FileUtility.DeleteDir(path_default_archive_build)

        ## Delete Binaries
        ## did it in [Project Clean] Command
        
            
            


#####################################################################################
#################################### Wwise ##########################################
    def Package_Wwise(self):
        WPMHelper.Get().CleanWwiseProject()

        list_config = ["Debug","Profile","Release"]
        arch = "iOS"
        platform =  "iOS"

        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()

        one_param_premake = ParamsWwisePluginPremake()
        one_param_premake.platform = platform
        OneWwiseCommand.Premake(one_param_premake)

        path_xcode_workspace_static = WPMHelper.Get().GetPath_WPProject() / "SoundEnginePlugin/AgoraWwiseRTCSDK_iOS_static.xcodeproj/project.pbxproj"
        default_generated_apple_team_id = WPMHelper.Get().GetWwiseDefaultTeamID()
        apple_team_id = WPMHelper.Get().GetAppleTeamID()
        FileUtility.ReplaceFileContent(path_xcode_workspace_static,default_generated_apple_team_id,apple_team_id)

        path_xcode_workspace_shared = WPMHelper.Get().GetPath_WPProject() / "SoundEnginePlugin/AgoraWwiseRTCSDK_iOS_shared.xcodeproj/project.pbxproj"
        FileUtility.ReplaceFileContent(path_xcode_workspace_shared,default_generated_apple_team_id,apple_team_id)

        for one_config in list_config:
            ### Clean First
            ## need to be cleaned first, otherwise, the final product may be incorrect:
            ## Ex. lake some new exposed functions
            path_wwise_objs = WPMHelper.Get().GetPath_WwiseSDKBase() / "iOS" / (one_config + "-iphoneos") / "obj"
            FileUtility.DeleteDir(path_wwise_objs)
            PrintLog("Clean Wwise Objs Dir [%s]" % path_wwise_objs)

            one_param_build = ParamsWwisePluginBuild()
            one_param_build.config = one_config
            one_param_build.arch = arch
            one_param_build.platform = platform
            OneWwiseCommand.Build(one_param_build)

        PrintStageLog("iOS - Package_Wwise Build Complete")

        ## Archive
        ## Final Product 
        for one_config in list_config:
            OneArchiveInfo = ArchiveInfo_WwisePlugin(
                WPMHelper.Get().GetName_WwisePluginName(),
                WPMHelper.Get().GetVer_Wwise(),
                SystemHelper.IOS_TargetName(),
                one_config
            )
            extension = "a"
            name_final_product = OneArchiveInfo.GetArchiveName() + "." + extension
            path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() / "iOS" /(one_config +"-iphoneos") / "lib" / name_final_product
            PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
            bshould_clean_others_when_archving = False
            ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

        PrintStageLog("IOS - Package_Wwise Archive Complete")