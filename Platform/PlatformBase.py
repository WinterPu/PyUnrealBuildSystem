from Logger.Logger import *
from Command.CommandBase import *
from Command.UATCommand import *


class PlatformBase:
    def GetRunUATPath():
        PrintLog("PlatformBase - GetUATPath")

    def GenHostPlatformParams(params):
        PrintLog("PlatformBase - GenParams")
        return False,None

    def GenTargetPlatformParams(params):
        PrintLog("PlatformBase - GenParams")
        return False,None


class BaseHostPlatform:
    Params = None
    OneUATCommand = None
    def __init__(self,host_params) -> None:
        self.Params = host_params
        self.OneUATCommand = UATCommand(self.Params['uat_path'])

    def SetupEnvironment(self):
       PrintLog("BaseHostPlatform - SetupEnvironment")

    def GetParamVal(self,key):
        return self.Params[key]

    def RunUAT(self):
        PrintLog("BaseHostPlatform - RunUAT")
        return self.OneUATCommand

    def BuildPlugin(self,uplugin_file,target_platform, output_path = "./output"):
        
        params = {}

        params["plugin_path"] = uplugin_file
        params["platform"] = target_platform
        params["output_path"] = output_path
        params["extra_commands"] = ""

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
    
    def GetTargetPlatform(self):
        return self.Params['platform']

    def RunUAT(self):
        return self.HostPlatform.RunUAT()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Base Platform")

    def Package():
        print("Package - Base Platform")
