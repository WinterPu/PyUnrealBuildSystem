from Platform.Windows import *
from Platform.Mac import *
from Platform.Android import *
from Platform.IOS import *
from Logger.Logger import *

## Example: Win+Mac+Android+IOS
def ParsePlatformArg(str):
    return str.split('+')



def CreateHostPlatform(type,original_args):
    if type == "Win":
        ret,params = WinPlatformBase.GenHostPlatformParams(original_args)
        val = WinHostPlatform(params) if ret == True else None
        return ret,val
    elif type == "Mac":
        ret,params = MacPlatformBase.GenHostPlatformParams(original_args)
        val = MacHostPlatform(params) if ret == True else None
        return ret,val
    else:
        PrintErr(sys._getframe(),"Invalid HostPlatform")
        return False,None
    
    return False,None


def CreateTargetPlatform(host_platform,type,original_args):
    if type == "Win":
        ret,params = WinPlatformBase.GenTargetPlatformParams(original_args)
        val = WinTargetPlatform(host_platform,params) if ret == True else None
        return ret,val
    elif type == "Mac":
        ret,params = MacPlatformBase.GenTargetPlatformParams(original_args)
        val = MacTargetPlatform(host_platform,params) if ret == True else None
        return ret,val
    elif type == "Android":
        ret,params = AndroidPlatformBase.GenTargetPlatformParams(original_args)
        val = AndroidTargetPlatform(host_platform,params) if ret == True else None
        return ret,val
    elif type == "IOS":
        ret,params = IOSPlatformBase.GenTargetPlatformParams(original_args)
        val = IOSTargetPlatform(host_platform,params) if ret == True else None
        return ret,val
    
    return False,None