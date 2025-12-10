
from Logger.Logger import *
class AgoraSDKInfo:

    _sdk_type = "RTC"
    _bis_audio_only = False
    _native_sdk_ver = ""
    _plugin_ver = ""
    _ue_plugin_name = "AgoraPlugin"
    _agora_build_config = "Release"
    _company_name = "Agora"
  
    def __init__(self,
                sdk_ver,
                is_audio_only,
                sdk_type = "RTC",
                plugin_ver = "", 
                ue_plugin_name = "AgoraPlugin", 
                agora_build_config = "Release",
                company_name = "Agora"):
        
        ## sdk_ver: equal to native sdk ver:
        ### Ex. 4.2.1

        ## plugin_ver: equal to plugin ver:
        ### Ex. 4.2.1-build.1

    
        val_native_sdk_ver = sdk_ver
        if plugin_ver != "":
            val_native_sdk_ver = plugin_ver.split("-")[0]
        
        self._native_sdk_ver = val_native_sdk_ver
        self._plugin_ver = plugin_ver
        self._bis_audio_only = is_audio_only
        self._sdk_type = sdk_type
        self._ue_plugin_name = ue_plugin_name 
        self._agora_build_config = agora_build_config
        self._company_name = company_name

    def Get_UEPluginName(self):
        return self._ue_plugin_name

    def Get_AgoraBuildConfig(self):
        return self._agora_build_config

    def Get_NativeSDKVer(self):
        return self._native_sdk_ver

    def Get_PluginVer(self):
        return self._plugin_ver
    
    def Get_SDKType(self):
        return self._sdk_type
    
    def Get_SDKIsAudioOnly(self):
        return self._bis_audio_only

    def Get_SDKProfile(self):
        return AgoraSDKInfo.GetName_SDKFull() if not self._bis_audio_only else AgoraSDKInfo.GetName_SDKAudioOnly()
    
    def HasAtlasName(self):
        return self._company_name.lower() != "agora"

    def Get_AtlasName(self,bFirstLetterCapital = False):
        if bFirstLetterCapital:
            return self._company_name.lower().capitalize()
        else:
            return self._company_name

    @staticmethod
    def GetName_SDKFull():
        return "Full"
    
    @staticmethod
    def GetName_SDKAudioOnly():
        return "AudioOnly"
    
    def ToString(self):
        return "[SDKInfo] SDKType[%s] PluginVer[%s]  NativeSDKVer[%s] Category[%s]" %(self._sdk_type,self._plugin_ver,self._native_sdk_ver, self.Get_SDKProfile())



