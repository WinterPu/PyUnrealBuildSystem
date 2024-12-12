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
        ArgParser.add_argument('-wwisever',default="2021.1.14.8108")
        ArgParser.add_argument('-pathwwisebase',default="")
        ArgParser.add_argument('-wpprojectpath',default="")
        ArgParser.add_argument('-wwisepluginname',default="AgoraWWiseRTCSDK")
        ArgParser.add_argument('-wwise_xcode_generated_teamid',default="BCB4VLKTK5")
        ArgParser.add_argument('-wwise_windows_toolset',default="vc150+vc160+vc170")
        ArgParser.add_argument('-wwise_windows_toolset_not_build',default="vc150")
        if bIncludeConflictArgs:
            ArgParser.add_argument("-targetplatform", default=SystemHelper.Get().GetTargetPlatform_BasedOnHostPlatform())
            ArgParser.add_argument("-ioscert", default="D")
    
    def Init(self):
        PrintStageLog("WwisePluginManager Init")

    def Start(self):
        WwisePluginManager.Get().Init()
        args = self.ParseCMDArgs()
        WPMHelper.Get().Init(args)
        self.CreateTask()

    def CreateTask(self):
        self.BuildWwisePlugin()

    
    def BuildWwisePlugin(self):
        Args = WPMHelper.Get().GetArgs()
        target_platform_type_list = ParsePlatformArg(Args.targetplatform)
        for target_platform_type in target_platform_type_list:
            ret_target,target_platform = CreateTargetPlatform(None,target_platform_type,Args)
            if ret_target == True:
                target_platform.Package_Wwise()
            else: 
                PrintErr("Invalid TargetPlatform Creation")



if __name__ == '__main__':
    WwisePluginManager.Get().Start()