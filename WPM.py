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
        ArgParser.add_argument('-wwisepluginname',default="AgoraWwiseRTCSDK")
        ArgParser.add_argument('-wwise_xcode_generated_teamid',default="BCB4VLKTK5")
        ArgParser.add_argument('-wwise_windows_toolset',default="vc150+vc160+vc170")
        ArgParser.add_argument('-wwise_windows_toolset_not_build',default="vc150")
        ArgParser.add_argument('-authoring', action='store_true')

        ## For Authoring Default Build Args
        ArgParser.add_argument('-authoring_toolset', default="vc170")
        ArgParser.add_argument('-authoring_build_config', default="Release")
        ArgParser.add_argument('-authoring_build_arch', default="x64")
        ArgParser.add_argument('-android16kb_disable', action='store_true')
        ArgParser.add_argument('-android16kb_search_line', default = "LOCAL_LDFLAGS := -Wl,--as-needed -Wl,--export-dynamic") ## add 16kb compile options under this line

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
        if WPMHelper.Get().IsBuildWwiseAuthoring():
            PrintLog("WPMHelper - Build Wwise Authoring")
            self.BuildWwisePluginAuthoring()
        
        else:
            self.BuildWwisePluginSDK()

    
    def BuildWwisePluginSDK(self):
        Args = WPMHelper.Get().GetArgs()
        target_platform_type_list = ParsePlatformArg(Args.targetplatform)
        for target_platform_type in target_platform_type_list:
            ret_target,target_platform = CreateTargetPlatform(None,target_platform_type,Args)
            if ret_target == True:
                target_platform.Package_Wwise()
            else: 
                PrintErr("Invalid TargetPlatform Creation")

    
    def BuildWwisePluginAuthoring(self):

        WPMHelper.Get().CleanWwiseProject()

        Args = WPMHelper.Get().GetArgs()
        one_config = Args.authoring_build_config
        arch = Args.authoring_build_arch
        toolset = Args.authoring_toolset
        
        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()


        ### python "%WWISEROOT%/Scripts/Build/Plugins/wp.py" premake Authoring
        one_param_premake = ParamsWwisePluginPremake()
        ## Authoring would generate all platforms
        one_param_premake.platform = "Authoring"
        OneWwiseCommand.Premake(one_param_premake)


        ## Clean First
        path_authoring = WPMHelper.Get().GetPath_WwiseAuthoringPathBase()
        path_tmp_obj = path_authoring / arch / one_config / "obj"
        FileUtility.DeleteDir(path_tmp_obj)


        ## python "%WWISEROOT%/Scripts/Build/Plugins/wp.py" build -c Release -x x64 -t vc160 Authoring
        one_param_build = ParamsWwisePluginBuild()
        one_param_build.config = one_config
        one_param_build.arch = arch
        one_param_build.toolset = toolset
        one_param_build.platform = "Authoring"
        OneWwiseCommand.Build(one_param_build)


if __name__ == '__main__':
    WwisePluginManager.Get().Start()