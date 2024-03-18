import json
import os
from Utility.HeaderBase import *
from pathlib import Path
from SystemBase import *

path_val = Path("/Users/admin/Documents/PyUnrealBuildSystem/Config/Config.json")

class ConfigParser(BaseSystem):
    _instance = None
    _initialized = False
    SDKTYPE="RTC"
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
        self.SDKTYPE = SDKLoadType
        self.ParseConfig()

    def ParseConfig(self):
        self.ParseUEConfig()
        self.ParseSDKConfig()
        self.ParseIOSCertConfig()

    def ParseUEConfig(self):
        base_config_path=Path("Config/UEConfig/Config.json")
        base_config_file = open(base_config_path)
        base_config_json_data = json.load(base_config_file)

        platform_config_path = base_config_path.parent.joinpath("Platforms",self.GetHostPlatform(),"Config.json")
        platform_config_file = open(platform_config_path)
        platform_config_json_data = json.load(platform_config_file)
        base_config_json_data.update(platform_config_json_data)

        PrintLog("UE Config: " + str(base_config_json_data))

        self.UEConfigData = base_config_json_data

    def ParseSDKConfig(self):
        SDKTYPELIST = self.SDKTYPE.split('+')

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

    def GetRTCSDKURL(self,sdkver,bUseAudioOnlySDK):
        key_type = "url_full"
        if bUseAudioOnlySDK == True:
            key_type = "url_audioonly"
        return self.SDKConfigData[sdkver][key_type]
    
    def GetRTCSDKNativeURL_IOS(self,sdkver):
        key_type = "url_native_ios"
        return self.SDKConfigData[sdkver][key_type]
    def GetRTCSDKNativeURL_Android(self,sdkver):
        key_type = "url_native_android"
        return self.SDKConfigData[sdkver][key_type]
    def GetRTCSDKNativeURL_Win(self,sdkver):
        key_type = "url_native_win"
        return self.SDKConfigData[sdkver][key_type]
    def GetRTCSDKNativeURL_Mac(self,sdkver):
        key_type = "url_native_mac"
        return self.SDKConfigData[sdkver][key_type]
    

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


    def GetOneIOSCertificate(self,tag_name):
        base_path = Path("Config/UEConfig/Platforms/IOS/Certs")
        return {
            "signing_identity": self.IOSCertData[tag_name]["signing_identity"],
            "provisioning_profile": self.IOSCertData[tag_name]["provisioning_profile"],
            "name_mobileprovision": self.IOSCertData[tag_name]["mobileprovision_filename"],
            "path_mobileprovision" : str(base_path / self.IOSCertData[tag_name]["mobileprovision_filename"])
        }

    