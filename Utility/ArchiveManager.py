from Utility.HeaderBase import *
from FileIO.FileUtility import *
from Command.ZipCommand import *

class ArchiveInfoBase:
    __path_root = ""

    def __init__(self) -> None:
        pass

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
    def __init__(self,build_platform,bis_audioonly_sdk,bis_cpp,ue_ver,sdk_ver,ioscert = "",extra_info = "") -> None:
        self.build_platform = build_platform
        self.bis_audioonly_sdk = bis_audioonly_sdk
        self.bis_cpp = bis_cpp
        self.ue_ver = ue_ver
        self.sdk_ver = sdk_ver
        self.ioscert = ioscert
        self.extra_info = extra_info

    def GetPath_CurRootArchiveDir(self):
        return Path("Archive_Example")
    
    def GetArchiveName(self):
        ## UnrealAPIExample_Full_Cpp_UE5.4_SDK_IOSCert_D_Extra
        str_sdktype = "RTC"
        str_platform = self.build_platform
        str_sdkaudioonly = "Full" if not self.bis_audioonly_sdk else "AudioOnly"
        str_ueprojecttype = "Cpp" if self.bis_cpp else "Blueprint"
        str_ue_ver = f"UE{self.ue_ver}"
        str_sdk_ver = f"SDK{self.sdk_ver}"
        str_ioscert = f"_IOSCert{self.ioscert}" if self.ioscert != "" else ""
        str_extra = f"_{self.extra_info}" if self.extra_info != "" else ""

        return f"UEDemo_{str_platform}_{str_sdktype}_{str_sdkaudioonly}_{str_ueprojecttype}_{str_ue_ver}_{str_sdk_ver}{str_ioscert}{str_extra}"

    # Override
    def GetArchivePath(self):
        path_root = self.GetPath_CurRootArchiveDir()
        path = Path(f"{self.sdk_ver}")
        path = path / (Path("Full") if not self.bis_audioonly_sdk else Path("AudioOnly"))
        path = path / ("Cpp" if self.bis_cpp else "Blueprint")
        path = path / (f"UE_{self.ue_ver}")
        return path_root / path

class ArchiveInfo_AgoraPlugin(ArchiveInfoBase):
    def __init__(self,bis_audioonly_sdk,sdk_ver) -> None:
        self.bis_audioonly_sdk = bis_audioonly_sdk
        self.sdk_ver = sdk_ver

    def GetPath_CurRootArchiveDir(self):
        return Path("Archive_AgoraPlugin")
    
    def GetArchiveName(self):
        ## Agora_RTC_FULL_SDK_#_Unreal
        str_sdktype = "RTC"
        str_sdkaudioonly = "FULL" if not self.bis_audioonly_sdk else "VOICE"
        str_sdkver = self.sdk_ver
        return f"Agora_{str_sdktype}_{str_sdkaudioonly}_SDK_{str_sdkver}_Unreal"

    # Override
    def GetArchivePath(self):
        path_root = self.GetPath_CurRootArchiveDir()
        str_sdkaudioonly = "FULLSDK" if not self.bis_audioonly_sdk else "VOICESDK"
        str_sdkver = self.sdk_ver
        return path_root / str_sdkver / str_sdkaudioonly


class ArchiveManager:
    __instance = None
    
    __Args = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ArchiveManager()
    
    def Init(self,Args):
        ## Init with Args from UBS
        self.__Args = Args


    def GetName_DefaultArchiveDir(self):
        return "ArchiveBuildsUnreal"
    
    def GetName_TmpZipDir(self):
        return "TmpZip"
    

    def GetPath_ArchiveRootDir(self):
        cur_path = Path(__file__).parent.parent.absolute()
        cur_path = cur_path.parent
        PrintLog("[ArchiveRootDir] Cur PWD %s " %(str(cur_path)))
        return cur_path / self.GetName_DefaultArchiveDir()

    ## Unreal_Cpp

    ## kept_extension: copy to archive dir with [kept_extension] file
    def ArchiveBuild(self,path_src_file,archive_info : ArchiveInfoBase,kept_extension = ""):
        PrintStageLog("PyUnrealBuildSystem --- Archive Start")

        path_archive_root = self.GetPath_ArchiveRootDir()
        path_archive_root.mkdir(parents=True,exist_ok= True)

        archive_info.SetRootPath(path_archive_root)
        PrintLog(f"Archive Root Path {path_archive_root}")

        path_target_archive_dir = path_archive_root / Path(archive_info.GetArchivePath())
        # if path_target_archive_dir.exists():
        #     FileUtility.DeleteDir(path_target_archive_dir)
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

