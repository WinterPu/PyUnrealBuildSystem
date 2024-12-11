from Utility.HeaderBase import *
import argparse
from WPMHelper import *

class WwisePluginManager():
    __instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__initialized = False
        return cls.__instance
    
    def __init__(self) -> None:
        if not self.__initialized: 
            super().__init__()
            self.__initialized = True
    
    def Get():
        return WwisePluginManager()


    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse Wwise Plugin Manager Args")
        
        self.AddArgsToParser(ArgParser)

        Args = ArgParser.parse_args()

        PrintLog(Args)
        return Args
    
    def AddArgsToParser(self,ArgParser, bIncludeConflictArgs = True):
        default_targetsystem = self.GetHostPlatform()
        if default_targetsystem == SystemHelper.Win_HostName():
            default_targetsystem = SystemHelper.Win64_TargetName()

        ArgParser.add_argument('-wwisever',default="2021.1.14.8108")
        ArgParser.add_argument('-pathwwisebase',default="")
        ArgParser.add_argument('-wpprojectpath',default="")
        if bIncludeConflictArgs:
            ArgParser.add_argument("-targetplatform", default=SystemHelper.Get().GetTargetPlatform_BasedOnHostPlatform())
    
    def Init(self):
        PrintStageLog("WwisePluginManager Init")

    def Start(self):
        WwisePluginManager.Get().Init()
        args = self.ParseCMDArgs()
        WPMHelper.Get().Init(args)
        self.CreateTask(args)

    def CreateTask(self):
        self.BuildWwisePlugin()

    
    def BuildWwisePlugin(self):
        Args = WPMHelper.Get().GetArgs()
        type_hostplatform = SystemHelper.Get().GetHostPlatform()
        ret_host,host_platform = CreateHostPlatform(type_hostplatform,Args)
        target_platform_type_list = ParsePlatformArg(Args.targetplatform)
        for target_platform_type in target_platform_type_list:
            ret_target,target_platform = CreateTargetPlatform(host_platform,target_platform_type,Args)
            if ret_target == True:
                target_platform.Package_Wwwise()
            else: 
                PrintErr("Invalid TargetPlatform Creation")


if __name__ == '__main__':
    WwisePluginManager.Get().Start()