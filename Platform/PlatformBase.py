from Logger.Logger import *
from Command.CommandBase import *
from Command.UATCommand import *


class PlatformBase:
    def GetRunUATPath():
        PrintLog("PlatformBase - GetUATPath")

    def GenHostPlatformParams(args):
        PrintLog("PlatformBase - GenParams")
        val = {}
        
        # key = "platform"
        # val[key] = args.HostMachineOS 
        
        return True,val

    def GenTargetPlatformParams(args):
        PrintLog("PlatformBase - GenParams")
        val = {}

        return True,val


class BaseHostPlatform:
    Params = None
    OneUATCommand = None
    def __init__(self,host_params) -> None:
        self.Params = host_params
        self.OneUATCommand = UATCommand(self.Params['uat_path'])

    def GetHostPlatform(self):
        return SystemHelper.Get().GetHostPlatform()
    
    def SetupEnvironment(self):
       PrintLog("BaseHostPlatform - SetupEnvironment")

    def GetParamVal(self,key):
        return self.Params[key]

    def RunUAT(self):
        PrintLog("BaseHostPlatform - RunUAT")
        return self.OneUATCommand

    def BuildPlugin(self,uplugin_file,target_platform, output_path = "./output"):
        
        params = ParamsUAT()
        params.path_uplugin_file = uplugin_file
        params.target_platform = target_platform
        params.path_plugin_output_dir = output_path
        
        self.RunUAT().BuildPlugin(params)


    def GenerateProject(self,path):
        PrintLog("BaseHostPlatform - GenerateProject paht %s " % path)
    
class BaseTargetPlatform:
    HostPlatform = None
    Params = None
    def __init__(self,host_platform,target_params) -> None:
        self.HostPlatform = host_platform
        self.Params = target_params
    
    def GetParamVal(self,key):
        return self.Params[key]
    

    def RunUAT(self):
        return self.HostPlatform.RunUAT()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Base Platform")

    def Package():
        print("Package - Base Platform")

    def PostPackaged():
        print("PostPackaged - Base Platform")

    def GetHostPlatform(self):
        return SystemHelper.Get().GetHostPlatform()
    
    def GetTargetPlatform(self):
        print("SystemBase - GetTargetPlatform")
