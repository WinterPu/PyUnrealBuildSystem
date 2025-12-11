from Logger.Logger import *
from Command.CommandBase import *
from Command.UATCommand import *
from Command.ZipCommand import *

from UBSHelper import *
from ABSHelper import *
from Utility.ArchiveManager import *

from enum import Enum

class PlatformBase:
    def GetRunUATPath():
        PrintLog("PlatformBase - GetUATPath")

    def GenHostPlatformParams(args):
        PrintLog("PlatformBase - GenParams")
        val = {}
        
        # key = "platform"
        # val[key] = args.HostMachineOS 
        
        return True,val

    def GenTargetPlatformParams(args):
        PrintLog("PlatformBase - GenParams")
        val = {}

        return True,val


class BaseHostPlatform:
    Params = None
    OneUATCommand = None
    def __init__(self,host_params) -> None:
        self.Params = host_params
        self.OneUATCommand = UATCommand(self.Params['uat_path'])

    def GetHostPlatform(self):
        return SystemHelper.Get().GetHostPlatform()
        
    def SetupEnvironment(self):
       PrintLog("BaseHostPlatform - SetupEnvironment (Usually do sth once which requires like: sudo permission)")

    def GetParamVal(self,key):
        return self.Params[key]

    def RunUAT(self):
        PrintLog("BaseHostPlatform - RunUAT")
        return self.OneUATCommand

    def BuildPlugin(self,uplugin_file,target_platform, output_path = "./output"):
        
        params = ParamsUAT()
        params.path_uplugin_file = uplugin_file
        params.target_platform = target_platform
        params.path_plugin_output_dir = output_path
        
        self.RunUAT().BuildPlugin(params)


    def GenerateProject(self,path):
        PrintLog("BaseHostPlatform - GenerateProject paht %s " % path)
    
class ArchiveType(Enum):
    NotSet = 0
    ArchiveSingleFile = 1
    ArchiveWithDir = 2

class BaseTargetPlatform:
    HostPlatform = None
    Params = None
    __target_platform_type = ""
    __path_final_product = ""
    __path_final_product_dir = ""
    __flag_archive_final_product = ArchiveType.NotSet 
    def __init__(self,host_platform,target_params,target_platform_type) -> None:
        self.HostPlatform = host_platform
        self.Params = target_params
        self.__target_platform_type = target_platform_type
        self.__path_final_product = ""
        self.__path_final_product_dir = ""
        self.__flag_archive_final_product = ArchiveType.NotSet
    
    def GetParamVal(self,key):
        return self.Params[key]
    

    def RunUAT(self):
        return self.HostPlatform.RunUAT()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Base Platform")

    def Package(self):
        print("Package - Base Platform")

    def PostPackaged(self):
        print("PostPackaged - Base Platform")

    def GetHostPlatform(self):
        return SystemHelper.Get().GetHostPlatform()
    
    def GetTargetPlatform(self):
        print("SystemBase - GetTargetPlatform")


    ## Require to set [SetArchivePath_FinalProduct] or [SetArchivePath_FinalProductDir] first
    def ArchiveProduct(self):
        print("SystemBase - ArchiveProduct")

        flag,path = self.GetStatus_ArchiveFinalProduct()
        PrintLog(f"ArchiveStatus: flag{flag} - path{path}")

        bshould_archive = UBSHelper.Get().should_archive_product()

        if bshould_archive:
            self.Archive_AgoraExample()

    def SetArchivePath_FinalProduct(self,path):
        self.__flag_archive_final_product = ArchiveType.ArchiveSingleFile
        self.__path_final_product = path

    def SetArchivePath_FinalProductDir(self,path):
        self.__flag_archive_final_product = ArchiveType.ArchiveWithDir
        self.__path_final_product_dir = path

    
    def GetStatus_ArchiveFinalProduct(self):
        path = ""
        if self.__flag_archive_final_product == ArchiveType.ArchiveSingleFile:
            path = self.__path_final_product
        elif self.__flag_archive_final_product == ArchiveType.ArchiveWithDir:
            path = self.__path_final_product_dir

        return self.__flag_archive_final_product , path
        


    def GetPath_FinalProduct(self):
        return self.__path_final_product
    

    def Archive_AgoraExample(self):
        bisagora_example = ABSHelper.Get().IsAgoraUEProject()
        if bisagora_example:
            
            flag_archive_status,path = self.GetStatus_ArchiveFinalProduct()
            bArchiveWithDir = flag_archive_status == ArchiveType.ArchiveWithDir

            val_platform = self.__target_platform_type
            val_bis_cpp = not ABSHelper.Get().IsExampleTypeUEBlueprint()
            val_ue_ver = UBSHelper.Get().GetVer_UEEngine()
            val_sdkinfo = ABSHelper.Get().GetAgoraSDKInfo()
            val_use_all_ioscerts = UBSHelper.Get().ShouldPackageWithAllIOSCerts()
            val_ioscert = ABSHelper.Get().GetIOSCert() if str(val_platform).lower() == SystemHelper.IOS_TargetName().lower() else "" 
            val_extra_info = ""
            OneArchiveInfo = ArchiveInfo_AgoraExample(
                val_platform,
                val_sdkinfo,
                val_bis_cpp,
                val_ue_ver,
                val_use_all_ioscerts,
                val_ioscert,
                val_extra_info)
            
            path_target_archive_file = Path(path)

            if bArchiveWithDir:
                path_src_dir = Path(path)
                path_target_archive_file = path_src_dir
                if not path_src_dir.exists() or path_src_dir == Path(""):
                    PrintErr(f"Archive-SrcDir does not exists! {path_src_dir}")
                    return
                
                OneZipCommand = ZipCommand()
                path_dst_zip_file =  path_target_archive_file.parent / f"{path_target_archive_file.stem}.zip"
                OneZipCommand.ZipFile(path_src_dir,path_dst_zip_file)
                path_target_archive_file = path_dst_zip_file
            
            if  not path_target_archive_file.exists() or path_target_archive_file == Path(""):
                PrintErr(f"Target Archive File not founded {path_target_archive_file}")
                return 

            bshould_clean = UBSHelper.Get().should_clean_dir_before_archiving()
            ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean)

            if bArchiveWithDir:
                FileUtility.DeleteFile(path_target_archive_file)