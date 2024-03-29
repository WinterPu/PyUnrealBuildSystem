
from Logger.Logger import *
class AgoraSDKInfo:

    _sdk_type = "RTC"
    _sdk_ver = ""
    _bis_audio_only = False

    def __init__(self,sdk_ver,is_audio_only,sdk_type = "RTC"):
        self._sdk_ver = sdk_ver
        self._bis_audio_only = is_audio_only
        self._sdk_type = sdk_type

    def Get_SDKVer(self):
        return self._sdk_ver
    
    def Get_SDKType(self):
        return self._sdk_type
    
    def Get_SDKIsAudioOnly(self):
        return self._bis_audio_only
    
    def GetName_SDKFull():
        return "Full"
    
    def GetName_SDKAudioOnly():
        return "AudioOnly"
    
    def ToString(self):
        return "[SDKInfo] SDKType[%s] SDKVer[%s] Category[%s]" %(self._sdk_type,self._sdk_ver,(AgoraSDKInfo.GetName_SDKAudioOnly() if self._bis_audio_only else AgoraSDKInfo.GetName_SDKFull()))



