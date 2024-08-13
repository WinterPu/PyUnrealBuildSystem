from pathlib import Path
from Logger.Logger import *
from ConfigParser import *
from SystemHelper import *

class ABSHelper():
    __instance = None

    __Args = None
    __bIs_AudioOnly = False

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ABSHelper()
    
    def Init(self,Args):
        self.__Args = Args
        self.__InitInner_IsAudioOnly(Args)
        

    def __InitInner_IsAudioOnly(self,Args):
        self.__bIs_AudioOnly = Args.sdkisaudioonly

    def IsAgoraUEProject(self):
        ## it means this is an ue project with agora sdk
        return True
    

    def IsAgoraSDKAudioOnly(self):
        return self.__bIs_AudioOnly
