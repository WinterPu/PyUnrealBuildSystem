import json
from Utility.HeaderBase import *
from pathlib import Path
from SystemBase import *
from Base.AgoraSDKInfo import *
from Utility.PathConfiger import *
from FileIO.FileUtility import *

path_val = Path("/Users/admin/Documents/PyUnrealBuildSystem/Config/Config.json")


class IOSCertInfo:
    def __init__(self,signing_identity,provisioning_profile,name_mobileprovision,path_mobileprovision,provisioning_profile_specifier):
        self.__signing_identity = signing_identity
        self.__provisioning_profile = provisioning_profile
        self.__name_mobileprovision = name_mobileprovision
        self.__path_mobileprovision = Path(path_mobileprovision)
        self.__provisioning_profile_specifier = provisioning_profile_specifier

    @property
    def get_signing_identity(self):
        return self.__signing_identity
    
    ## currently get it from UE Config
    @property
    def get_provisioning_profile(self):
        return self.__provisioning_profile
    
    @property
    def get_filename_mobileprovision(self):
        return self.__name_mobileprovision
    
    @property
    def get_filepath_mobileprovision(self):
        return self.__path_mobileprovision
    

    ## use security cms -D -i [path_mobile_provision]
    ## to check UUID
    ## could be used in Xcode[provisioning_profile_specifier]
    @property
    def get_provisioning_profile_specifier(self):
        return self.__provisioning_profile_specifier





class ConfigParser(BaseSystem):
    _instance = None
    _initialized = False
    ## RTC+RTM
    SDKLOADTYPELIST="RTC"
    UEConfigData = None
    SDKConfigData = None
    IOSCertData = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized: 
            super().__init__()
            self._initialized = True
    
    def Get():
        return ConfigParser()
    
    def Init(self,SDKLoadType = "RTC"):
        self.SDKLOADTYPELIST = SDKLoadType
        self.ParseConfig()

    def ParseConfig(self):
        self.ParseUEConfig()
        self.ParseSDKConfig()
        self.ParseIOSCertConfig()

    def ParseUEConfig(self):
        ## Load Basic Config
        base_config_path=Path("Config/UEConfig/Config.json")
        base_config_file = open(base_config_path)
        base_config_json_data = json.load(base_config_file)

        ## Load Platforms Config
        platform_config_path = base_config_path.parent.joinpath("Platforms",self.GetHostPlatform(),"Config.json")
        platform_config_file = open(platform_config_path)
        platform_config_json_data = json.load(platform_config_file)
        base_config_json_data.update(platform_config_json_data)

        PrintLog("UE Config: " + str(base_config_json_data))

        self.UEConfigData = base_config_json_data

    def ParseSDKConfig(self):
        SDKTYPELIST = self.SDKLOADTYPELIST.split('+')

        base_config_json_data = None
        for SDKTYPE in SDKTYPELIST:
            one_type_config_path=Path("Config/SDKConfig").joinpath(SDKTYPE,"Config.json")
            one_type_config_file = open(one_type_config_path)
            one_type_config_json_data = json.load(one_type_config_file)
            if base_config_json_data == None:
                base_config_json_data = one_type_config_json_data
            else:
                base_config_json_data.update(one_type_config_json_data)


        platform_config_path = Path("Config/SDKConfig").joinpath("Platforms",self.GetHostPlatform(),"Config.json")
        platform_config_file = open(platform_config_path)
        platform_config_json_data = json.load(platform_config_file)
        base_config_json_data.update(platform_config_json_data)

        PrintLog("SDK Config: " + str(base_config_json_data))

        self.SDKConfigData = base_config_json_data


    def ParseIOSCertConfig(self):
        ios_cert_config_path = Path("Config/UEConfig/Platforms/IOS/Certificate.json")
        ios_cert_config_path = open(ios_cert_config_path)
        config_path_json_data = json.load(ios_cert_config_path)
        PrintLog("Available IOS Certificate: " + str(config_path_json_data))
        self.IOSCertData = config_path_json_data

    def GetAllAvailableEngineList(self):
        available_list = []
        for engine_ver in self.UEConfigData["EngineList"]:
            available_list.append(engine_ver)
        return available_list

    def GetDefaultEnginePath(self,ver):
        return self.UEConfigData["EngineList"][ver]["Path"]

    def GetDefaultPluginRepo(self):
        return self.SDKConfigData["defaultpluginrepo"]

    def GetRTCSDKURL(self,sdkinfo:AgoraSDKInfo):
        key_type = "url_full"
        if sdkinfo.Get_SDKIsAudioOnly() == True:
            key_type = "url_audioonly"
        return self.SDKConfigData[sdkinfo.Get_SDKVer()][key_type]
    
    def GetRTCSDKNativeURL_IOS(self,sdkinfo:AgoraSDKInfo):
        key_type = "url_native_ios"
        if sdkinfo.Get_SDKIsAudioOnly():
            key_type = "url_native_ios_audioonly"
        return self.SDKConfigData[sdkinfo.Get_SDKVer()][key_type]
    def GetRTCSDKNativeURL_Android(self,sdkinfo:AgoraSDKInfo):
        key_type = "url_native_android"
        if sdkinfo.Get_SDKIsAudioOnly():
            key_type = "url_native_android_audioonly"
        return self.SDKConfigData[sdkinfo.Get_SDKVer()][key_type]
    def GetRTCSDKNativeURL_Win(self,sdkinfo:AgoraSDKInfo):
        key_type = "url_native_win"
        return self.SDKConfigData[sdkinfo.Get_SDKVer()][key_type]
    def GetRTCSDKNativeURL_Mac(self,sdkinfo:AgoraSDKInfo):
        key_type = "url_native_mac"
        return self.SDKConfigData[sdkinfo.Get_SDKVer()][key_type]
    

    ## IOS Certificate
    def GetAllIOSCertificates(self):
        return self.IOSCertData.items()
    
    def IsIOSCertValid(self,tag_name):
        bIsValid = False
        if self.IOSCertData and self.IOSCertData[tag_name]:
            cert = self.IOSCertData[tag_name]["signing_identity"]
            mobileprovision = self.IOSCertData[tag_name]["provisioning_profile"]
            if cert and len(cert) > 0 and mobileprovision and len(mobileprovision) > 0:
                bIsValid = True
            else:
                PrintErr("[Cert %s] is not a valid certificate" % tag_name)
        return bIsValid


    def GetOneIOSCertificate(self,tag_name) -> IOSCertInfo:
        ## Get current script working dir
        
        if not self.IsIOSCertValid(tag_name):
            return None
        
        current_dir = Path(__file__).parent
        base_path = current_dir / Path("Config/UEConfig/Platforms/IOS/Certs")

        return IOSCertInfo(
            signing_identity = self.IOSCertData[tag_name]["signing_identity"],
            provisioning_profile = self.IOSCertData[tag_name]["provisioning_profile"],
            name_mobileprovision = self.IOSCertData[tag_name]["mobileprovision_filename"],
            path_mobileprovision = str(base_path / self.IOSCertData[tag_name]["mobileprovision_filename"]),
            provisioning_profile_specifier = self.IOSCertData[tag_name]["provisioning_profile_specifier"]
        )


    def CopyAllMobileProvisionsToDstPath(self):
        if SystemHelper.Get().GetHostPlatform() == SystemHelper.Mac_HostName():
            current_dir = Path(__file__).parent
            src_path = current_dir / Path("Config/UEConfig/Platforms/IOS/Certs")
            dst_path = Path(PathConfiger.GetMobileProvisionCachePath())

            
            if dst_path.exists():
                for file in src_path.glob("*.mobileprovision"):
                    dst_file = dst_path / file.name
                    FileUtility.CopyFile(file, dst_file)


    


    ### For Resources Related
    def GetResourcesRootPath(self,resource_index_key,resource_tag_name):
        current_dir = Path(__file__).parent
        final_path = current_dir / Path("Config/UEConfig/Resources") / resource_index_key / resource_tag_name
        return final_path
    


