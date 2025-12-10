from Utility.HeaderBase import *
from FileIO.FileUtility import *
from Command.ZipCommand import *
from Base.AgoraSDKInfo import *

class ArchiveInfoBase:
    __path_root = ""

    def __init__(self) -> None:
        pass

    def GetPath_CurRootArchiveDirBase(self):
        return Path("Undefined")
    
    ## For Clean Archive Dir
    def GetPath_CurRootArchiveDir(self):
        return Path("Undefined")

    def GetArchiveName(self):
        return "unknown"

    ## Relative Path
    def GetArchivePath(self):
        return Path("")

    def GetRootPath(self):
        return self.__path_root
    
    def SetRootPath(self,path_root):
        self.__path_root = path_root

    ## Full Path With Root
    def GetFullPath_FinalProduct(self,extension = "zip"):
        filename = f"{self.GetArchiveName()}.{extension}"
        return Path(self.__path_root) / Path(self.GetArchivePath()) / filename


class ArchiveInfo_AgoraExample(ArchiveInfoBase):
    def __init__(self,build_platform,bis_audioonly_sdk,bis_cpp,ue_ver,sdk_ver,buse_all_ioscerts,ioscert = "",extra_info = "") -> None:
        self.build_platform = build_platform
        self.bis_audioonly_sdk = bis_audioonly_sdk
        self.bis_cpp = bis_cpp
        self.ue_ver = ue_ver
        self.sdk_ver = sdk_ver
        self.buse_all_ios_certs = buse_all_ioscerts
        self.ioscert = ioscert
        self.extra_info = extra_info

    def GetPath_CurRootArchiveDirBase(self):
        return Path("Archive_Example")
    
    def GetPath_CurRootArchiveDir(self):
        return self.GetPath_CurRootArchiveDirBase() / Path(f"{self.sdk_ver}")
    
    def GetArchiveName(self):
        ## UnrealAPIExample_Full_Cpp_UE5.4_SDK_IOSCert_D_Extra
        str_sdktype = "RTC"
        str_platform = self.build_platform
        str_sdkaudioonly = "Full" if not self.bis_audioonly_sdk else "AudioOnly"
        str_ueprojecttype = "Cpp" if self.bis_cpp else "Blueprint"
        str_ue_ver = f"UE{self.ue_ver}"
        str_sdk_ver = f"SDK{self.sdk_ver}"
        str_ioscert = f"_IOSCert{self.ioscert}" if self.ioscert != "" else ""
        if self.buse_all_ios_certs:
            str_ioscert = f"_AllIOSCerts"
        str_extra = f"_{self.extra_info}" if self.extra_info != "" else ""

        return f"UEDemo_{str_platform}_{str_sdktype}_{str_sdkaudioonly}_{str_ueprojecttype}_{str_ue_ver}_{str_sdk_ver}{str_ioscert}{str_extra}"

    # Override
    def GetArchivePath(self):
        path_root = self.GetPath_CurRootArchiveDir()
        path = (Path("Full") if not self.bis_audioonly_sdk else Path("AudioOnly"))
        path = path / ("Cpp" if self.bis_cpp else "Blueprint")
        path = path / (f"UE_{self.ue_ver}")
        return path_root / path

class ArchiveInfo_AgoraPlugin(ArchiveInfoBase):
    def __init__(self, sdkinfo:AgoraSDKInfo) -> None:
        self.sdkinfo = sdkinfo
        self.bis_audioonly_sdk = sdkinfo.Get_SDKIsAudioOnly()
        self.native_sdk_ver = sdkinfo.Get_NativeSDKVer()
        self.sdk_type = sdkinfo.Get_SDKType()
        self.plugin_ver = sdkinfo.Get_PluginVer()

    def GetPath_CurRootArchiveDirBase(self):
        company_name = self.sdkinfo.Get_AtlasName()
        name_base = f"Archive_{company_name}Plugin"
        if self.sdk_type != "RTC":
            name_base = f"{name_base}_{self.sdk_type}"
        return Path(name_base)
    
    def GetPath_CurRootArchiveDir(self):
        return self.GetPath_CurRootArchiveDirBase() / self.plugin_ver
    
    def GetArchiveName(self):
        ## Agora_RTC_FULL_SDK_#_Unreal
        str_sdktype = "RTC"
        str_sdkaudioonly = "FULL" if not self.bis_audioonly_sdk else "VOICE"
        str_sdkver = self.native_sdk_ver
        str_pluginver = self.plugin_ver
        str_companyname = self.sdkinfo.Get_AtlasName()
        return f"{str_companyname}_{str_sdktype}_{str_sdkaudioonly}_SDK_Unreal_{str_pluginver}"

    # Override
    def GetArchivePath(self):
        path_root = self.GetPath_CurRootArchiveDir()
        str_sdkaudioonly = "FULLSDK" if not self.bis_audioonly_sdk else "VOICESDK"
        return path_root / str_sdkaudioonly

class ArchiveInfo_AgoraPluginMarketplace(ArchiveInfoBase):
    def __init__(self, sdk_ver) -> None:
        self.sdk_ver = sdk_ver
        pass

    def GetPath_CurRootArchiveDirBase(self):
        return Path("Archive_UEMarketplace")
    
    def GetPath_CurRootArchiveDir(self):
        return self.GetPath_CurRootArchiveDirBase()/ self.sdk_ver
    
    def GetArchivePath(self):
        return self.GetPath_CurRootArchiveDir()


class ArchiveInfo_WwisePlugin(ArchiveInfoBase):
    def __init__(self,PLUGIN_NAME, val_wwisever,val_platform, val_config,val_arch = "",val_toolset = "") -> None:
        self.name_plugin = PLUGIN_NAME
        self.wwisever = val_wwisever
        self.platform = val_platform
        self.config = val_config
        self.arch = val_arch
        self.toolset = val_toolset

    def GetPath_CurRootArchiveDirBase(self):
        return Path("Archive_WwisePlugin")
    
    def GetPath_CurRootArchiveDir(self):
        return self.GetPath_CurRootArchiveDirBase()/ self.wwisever / "ThirdParty"
    
    def GetArchivePath(self):
        return self.GetPath_CurRootArchiveDir() / self.GetArchiveSubDirBasedOnInfo()

    def GetArchiveSubDirBasedOnInfo(self):
        path = ""
        if self.platform == SystemHelper.Win64_TargetName():
            path = Path("Win64")
            path = path / ( self.arch + "_" + self.toolset) / self.config
        elif self.platform == SystemHelper.Mac_TargetName():
            path = Path("Mac") / self.config
        elif self.platform == SystemHelper.IOS_TargetName():
            path = Path("IOS") / (self.config + "-iphoneos")
        elif self.platform == SystemHelper.Android_TargetName():
            path = Path("Android") / self.arch / self.config
        return path
    
    def GetArchiveName(self):
        name = ""
        if self.platform == SystemHelper.Win64_TargetName():
            name = self.name_plugin
        elif self.platform == SystemHelper.Mac_TargetName():
            name = "lib" + self.name_plugin + "Source"
        elif self.platform == SystemHelper.IOS_TargetName():
            name = "lib" + self.name_plugin + "Source"
        elif self.platform == SystemHelper.Android_TargetName():
            name = "lib" + self.name_plugin

        return name

class ArchiveManager:
    __instance = None
    
    __Args = None

    __path_mannual_set_archive_root = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ArchiveManager()
    
    def Init(self,Args):
        ## Init with Args from UBS
        self.__Args = Args
        self.__path_mannual_set_archive_root = None


    def GetName_DefaultArchiveDir(self):
        return "ArchiveBuildsUnreal"
    
    def GetName_TmpZipDir(self):
        return "TmpZip"
    

    def GetPath_ArchiveRootDir(self):
        path_archive_root = None

        ## Mannually Set
        if self.__path_mannual_set_archive_root != None:
            path_archive_root = Path(self.__path_mannual_set_archive_root)
            if not path_archive_root.exists():
                PrintWarn(f"[ArchiveRootDir] mannually set path doesn't exist == create path {path_archive_root}")
                path_archive_root.mkdir(parents=True,exist_ok=True)

        if path_archive_root == None:
            cur_path = Path(__file__).parent.parent.absolute()
            cur_path = cur_path.parent
            PrintLog("[ArchiveRootDir] Cur PWD %s " %(str(cur_path)))
            path_archive_root = cur_path / self.GetName_DefaultArchiveDir()

        PrintLog(f"[ArchiveRootDir] {path_archive_root}")
        return path_archive_root
    
    def SetPath_ArchiveRootDir(self,path):
        self.__path_mannual_set_archive_root = path


    def GetPath_TargetArchiveDir(self,archive_info : ArchiveInfoBase):
        path_archive_root = self.GetPath_ArchiveRootDir()
        path_archive_root.mkdir(parents=True,exist_ok= True)

        path_target_archive_dir = Path(path_archive_root) / archive_info.GetArchivePath()
        path_target_archive_dir.mkdir(parents=True,exist_ok= True)
        return path_target_archive_dir

    ## Unreal_Cpp

    ## kept_extension: copy to archive dir with [kept_extension] file
    def ArchiveBuild(self,path_src_file,archive_info : ArchiveInfoBase,bCleanTargetArchiveDir = False,kept_extension = ""):
        PrintStageLog("PyUnrealBuildSystem --- Archive Start")

        path_archive_root = self.GetPath_ArchiveRootDir()
        path_archive_root.mkdir(parents=True,exist_ok= True)

        archive_info.SetRootPath(path_archive_root)
        PrintLog(f"Archive Root Path {path_archive_root}")

        path_target_archive_dir = path_archive_root / Path(archive_info.GetArchivePath())
        
        if bCleanTargetArchiveDir == True:
            path_clean_old_archives_dir = path_archive_root / Path(archive_info.GetPath_CurRootArchiveDir())
            PrintLog(f"Need to clean target archive dir: {path_clean_old_archives_dir}")
            FileUtility.DeleteDir(path_clean_old_archives_dir)

        path_target_archive_dir.mkdir(parents=True,exist_ok= True)

        bNeedToDelteTmpFile = False 
        path_src_archive_file = Path(path_src_file)

        kept_extension = "zip" if kept_extension == "" or str(kept_extension).lower() == "zip" else kept_extension
        bNeedToZipFile = kept_extension == "zip" and path_src_archive_file.suffix != ".zip"
        PrintLog(f"Archive NeedZipFile [{bNeedToZipFile}]: kept_extension [{kept_extension}]  src_archive_file suffix [{path_src_archive_file.suffix}] path [{path_src_archive_file}] ")
        if bNeedToZipFile:
            OneZipCommand = ZipCommand()


            # ## Create Tmp Dir For Zipping...
            # ## Ex. [...Agora-Unreal-SDK-Blueprint-Example/ArchivedBuilds/Mac] / [TmpZip]
            # tmp_dir = path_src_file.parent / self.GetName_TmpZipDir()
            # if tmp_dir.exists():
            #     FileUtility.DeleteDir(tmp_dir)
            # tmp_dir.mkdir(parents=True,exist_ok=True)
            ## Ex. [...Agora-Unreal-SDK-Blueprint-Example/ArchivedBuilds/Mac] / [TmpZip] / [SrcFile]
            ## tmp_dst_zip_src_file = tmp_dir / path_src_archive_file.name



            ## Ex. [...Agora-Unreal-SDK-Blueprint-Example/ArchivedBuilds/Mac] / AgoraBPExample.app
            tmp_dst_zip_src_file = Path(path_src_file)

            ## Ex. [...Agora-Unreal-SDK-Blueprint-Example/ArchivedBuilds/Mac] / AgoraBPExample.zip
            tmp_dst_zip_file = tmp_dst_zip_src_file.parent /f"{path_src_archive_file.stem}.zip"
            if tmp_dst_zip_file.exists():
                FileUtility.DeleteFile(tmp_dst_zip_file)
            
            # FileUtility.SimpleCopy(path_src_archive_file,tmp_dst_zip_src_file)
            OneZipCommand.ZipFile(tmp_dst_zip_src_file,tmp_dst_zip_file)
            PrintLog(f"Gened Tmp Zip File {tmp_dst_zip_file}")
            # FileUtility.DeleteDir(tmp_dir)
            path_src_archive_file = tmp_dst_zip_file
            bNeedToDelteTmpFile = True
        
        path_dst_archive_file = archive_info.GetFullPath_FinalProduct(kept_extension)
        ## Have been done
        if path_dst_archive_file.exists():
            FileUtility.DeleteFile(path_dst_archive_file)

        PrintLog(f"Archive SrcPath[{path_src_archive_file}]  ==>  DstPath[{path_dst_archive_file}]")
        FileUtility.SimpleCopy(path_src_archive_file,path_dst_archive_file)

        if bNeedToDelteTmpFile:
            PrintLog(f"[Clear] Gened Tmp Zip File ... Path{path_src_archive_file}")
            FileUtility.DeleteFile(path_src_archive_file)


        PrintLog(f"[Success!] Final Archive Product Path =====> {path_dst_archive_file} ")
        PrintStageLog("PyUnrealBuildSystem --- Archive End")

