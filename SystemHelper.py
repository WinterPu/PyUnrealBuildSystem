from pathlib import Path
import platform
from Logger.Logger import *

class SystemHelper():
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return SystemHelper()
    
    def GetHostPlatform(self):
        ossystem = platform.platform().lower()
        if 'windows' in ossystem:
            return SystemHelper.Win_HostName()
        elif 'macos' in ossystem:
            return SystemHelper.Mac_HostName()
        else:
            PrintErr("HostPlatform [%s] currently is not supported" %(str(ossystem)))
            return "NotSupportPlatform"
        

    def GetTargetPlatform_BasedOnHostPlatform(self):
        platform = self.GetHostPlatform()
        if platform == SystemHelper.Win_HostName():
            platform = SystemHelper.Win64_TargetName()
        return platform

    ## Host Platforms
    def Win_HostName():
        return "Win"
    
    def Mac_HostName():
        return "Mac"

    ## ====== Target Platforms ======  
    def Win64_TargetName():
        return "Win64"
    
    def Mac_TargetName():
        return "Mac"
    
    def IOS_TargetName():
        return "IOS"
    
    def Android_TargetName():
        return "Android"
    
    ## Win_SpecialRequestName() if needed
    def Win_InArgsTargetName():
        ## In Args: Win64 == Win
        return "Win"
    



    