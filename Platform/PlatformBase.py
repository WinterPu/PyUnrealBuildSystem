from Logger.Logger import *
from Command.CommandBase import *
from Command.UATCommand import *

from UBSHelper import *
from ABSHelper import *
from Utility.ArchiveManager import *

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
    
class BaseTargetPlatform:
    HostPlatform = None
    Params = None
    __target_platform_type = ""
    __path_final_product = ""
    def __init__(self,host_platform,target_params,target_platform_type) -> None:
        self.HostPlatform = host_platform
        self.Params = target_params
        self.__target_platform_type = target_platform_type
        self.__path_final_product = ""
    
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


    def ArchiveProduct(self):
        print("SystemBase - ArchiveProduct")
        bshould_archive = UBSHelper.Get().should_archive_product()

        if bshould_archive:
            self.Archive_AgoraExample()



    def Archive_AgoraExample(self):
        bisagora_example = ABSHelper.Get().IsAgoraUEProject()
        if bisagora_example:
            
            val_platform = self.__target_platform_type
            val_bis_audioonly_sdk = ABSHelper.Get().IsAgoraSDKAudioOnly()
            val_bis_cpp = not ABSHelper.Get().IsExampleTypeUEBlueprint()
            val_ue_ver = UBSHelper.Get().GetVer_UEEngine()
            val_sdk_ver = ABSHelper.Get().GetAgoraSDKVer()
            val_ioscert = ABSHelper.Get().GetIOSCert() if str(val_platform).lower() == SystemHelper.IOS_TargetName().lower() else "" 
            val_extra_info = ""
            OneArchiveInfo = ArchiveInfo_AgoraExample(
                val_platform,
                val_bis_audioonly_sdk,
                val_bis_cpp,
                val_ue_ver,
                val_sdk_ver,
                val_ioscert,
                val_extra_info)
            
            ArchiveManager.Get().ArchiveBuild(self.__path_final_product,OneArchiveInfo)