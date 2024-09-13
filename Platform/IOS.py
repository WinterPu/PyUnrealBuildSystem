from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
from ConfigParser import *

from Utility.VersionControlTool import *
from Command.ZipCommand import *

from FileIO.FileUtility import *

from UBSHelper import *
from ABSHelper import *

from Utility.UnrealProjectManager import *


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
        val[key] = args.ioscert

        key = "iosbundleidentifier"
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

        bUseMordenXcodeSetting = UBSHelper.Get().Is_UE53_Or_Later()
        bRet = UnrealConfigIniManager.SetConfig_IOSCert(path_uproject_file,self.Params['ioscert'],bUseMordenXcodeSetting)
        if bRet:
            PrintLog("IOSTargetPlatform - SetupEnvironment Certificate %s Set Done!" % self.Params['ioscert'] )
        else:
            PrintErr("IOSTargetPlatform - SetupEnvironment Certificate Set Failed")

        
        UnrealConfigIniManager.SetConfig_BundleIdentifier(path_uproject_file,self.Params['iosbundleidentifier'])

        ## Agora
        self.PrepareMannualOp_BCExtension()

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

        self.PostPackaged_DoXcodeBuild()

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

            
            
