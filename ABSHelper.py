from pathlib import Path
from Logger.Logger import *
from ConfigParser import *
from SystemHelper import *

class ABSHelper():
    __instance = None

    __Args = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ABSHelper()
    
    def Init(self,Args):
        self.__Args = Args


    def IsAgoraUEProject(self):
        ## it means this is an ue project with agora sdk
        return True
    

    def IsAgoraSDKAudioOnly(self):
        return self.__Args.sdkisaudioonly if self.__Args else None
    

    def HasPostXcodeBuildAdded(self):
        return self.__Args.AddPostXcodeBuild if self.__Args else None
    

    def GetResourceTagName(self):
        return self.__Args.ResourceTagName if self.__Args else None
    
    def GetAgoraSDKVer(self):
        return self.__Args.agorasdk if self.__Args else None
    
    def GetIOSCert(self):
        return self.__Args.ioscert if self.__Args else None
    

    def IsExampleTypeUEBlueprint(self):
        path_uproject_file = Path(self.__Args.uprojectpath)
        uproject_name = path_uproject_file.stem
        
        bRet = True
        if uproject_name == "AgoraBPExample":
            bRet = True
        else:
            bRet = False
        return bRet
