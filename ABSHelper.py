from pathlib import Path
from Logger.Logger import *
from ConfigParser import *
from SystemHelper import *

class ABSHelper():
    __instance = None

    __Args = None
    __bIs_AudioOnly = False
    __bHas_PostXcodeBuild = False
    __ResourceTagName = ""

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ABSHelper()
    
    def Init(self,Args):
        self.__Args = Args
        self.__InitInner_IsAudioOnly(Args)
        self.__InitInner_AddPostXcodeBuild(Args)
        self.__InitInner_ResourceTagName(Args)
        

    def __InitInner_IsAudioOnly(self,Args):
        self.__bIs_AudioOnly = Args.sdkisaudioonly

    def __InitInner_AddPostXcodeBuild(self,Args):
        self.__bHas_PostXcodeBuild = Args.AddPostXcodeBuild

    def __InitInner_ResourceTagName(self,Args):
        self.__ResourceTagName = Args.ResourceTagName
    

    def IsAgoraUEProject(self):
        ## it means this is an ue project with agora sdk
        return True
    

    def IsAgoraSDKAudioOnly(self):
        return self.__bIs_AudioOnly
    

    def HasPostXcodeBuildAdded(self):
        return self.__bHas_PostXcodeBuild
    

    def GetResourceTagName(self):
        return self.__ResourceTagName
