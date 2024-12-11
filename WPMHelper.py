from SystemHelper import *
from pathlib import Path
class WPMHelper:
    __instance = None
    __initialized = False
    __Args = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__initialized = False
        return cls.__instance
    
    def __init__(self) -> None:
        if not self.__initialized: 
            super().__init__()

            ## Init

            self.__initialized = True

    
    def Get():
        return WPMHelper()
    
    def Init(self,Args):
        self.__Args = Args

    
    def GetArgs(self):
        return self.__Args

    def GetPath_WPProject(self):
        return Path(self.__Args.wpprojectpath)

    def GetPath_WwiseBase(self):
        path_wwise_base = self.__Args.pathwwisebase
        if path_wwise_base == "":
            if SystemHelper.Get().GetHostPlatform() == SystemHelper.Mac_HostName():
                path_wwise_base = Path("/Applications/Audiokinetic")

            elif SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName():
                path_wwise_base = Path("C:\Program Files (x86)\Audiokinetic")
        
        ver_wwise = self.__Args.wwisever

        path_wwise_ver = str("Wwise") +  str(ver_wwise)

        path_final = path_wwise_base / path_wwise_ver

        if not path_final.exists():
            path_wwise_ver =  str("Wwise ") + str(ver_wwise)
            path_final = path_wwise_base / path_wwise_ver

        return path_final
    

    def GetPath_WwiseWPScript(self):
        return self.GetPath_WwiseBase() / Path("Scripts/Build/Plugins/wp.py")
    

    def GetPath_WwiseSDKBase(self):
        return self.GetPath_WwiseBase() / Path("SDK")

                
           
