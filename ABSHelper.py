from pathlib import Path
from Logger.Logger import *
from ConfigParser import *
from SystemHelper import *

class ABSHelper():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return ABSHelper()
    
    def Init(self,Args):
        pass


    def IsAgoraUEProject(self):
        ## it means this is an ue project with agora sdk
        return True
