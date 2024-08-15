from Utility.HeaderBase import *
from SystemBase import *

from APM import *
from UBS import *

from UBSHelper import *
from ABSHelper import *

## Combine UBS + APM
class AgoraBuildSystem(BaseSystem):

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
        return AgoraBuildSystem()
    
    def Init(self):
        PrintStageLog("AgoraBuildSystem Init")
        PyUnrealBuildSystem.Get().Init()
        AgoraPluginManager.Get().Init()

    def Start(self):
        AgoraBuildSystem.Get().Init()
        args = self.ParseCMDArgs()
        self.CreateTask(args)
    
    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse Package Args")

        bIncludeConflictArgs = False
        PyUnrealBuildSystem.Get().AddArgsToParser(ArgParser,bIncludeConflictArgs)
        AgoraPluginManager.Get().AddArgsToParser(ArgParser,bIncludeConflictArgs)

        bUseSubParser = False
        if bUseSubParser:
            Subparsers = ArgParser.add_subparsers(help='commands')
            UBSArgParser = Subparsers.add_parser(name='UBS', help='unreal build system')
            PyUnrealBuildSystem.Get().AddArgsToParser(UBSArgParser)
            
            APMArgParser = Subparsers.add_parser(name='APM', help='agora plugin manager')
            AgoraPluginManager.Get().AddArgsToParser(APMArgParser)


        self.AddArgsToParser(ArgParser)
        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args

    def AddArgsToParser(self,ArgParser,bIncludeConflictArgs = True):

        ArgParser.add_argument("-BuildUEProject",action = "store_true")

        ArgParser.add_argument("-AddPostXcodeBuild",action = "store_true") ## after packaging, updated Xcode project and use 'xcodebuild' to build again

        #ArgParser.add_argument("-NeedCopySDKWhenBuilding",action = "store_true")
        ArgParser.add_argument("-MacTrust",action = "store_true")
        ArgParser.add_argument("-Password",default="")
        
        
        ArgParser.add_argument("-TestUEPlugin",action = "store_true")
        ArgParser.add_argument("-TestPluginPath",default = "/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1/AgoraPlugin.zip")
        ArgParser.add_argument("-TestAgoraPlugin",action = "store_true") ## Test Agora Plugin
        ArgParser.add_argument("-QuerySDK",action = "store_true") ## Query Agora SDK to find the tested plugin file

        ArgParser.add_argument("-TestBlackList",default = "")

        ArgParser.add_argument("-GenPlugin",action = "store_true")
        ArgParser.add_argument("-SkipCopySDKToProject",action = "store_true")
        ArgParser.add_argument("-SkipClean",action = "store_true")



        ArgParser.add_argument("-AppToIPA",action="store_true")
        ArgParser.add_argument("-AppPath",default="")

        if bIncludeConflictArgs:
            pass

    def CreateTask(self,Args):
        ABSHelper.Get().Init(Args)

        if Args.GenPlugin == True:
            AgoraPluginManager.Get().StartGenPlugin(Args)

        if Args.BuildUEProject == True:
            
            if Args.SkipCopySDKToProject != True:
                self.CopySDKToUEProject(Args)

            if Args.SkipClean != True:
                Args.Clean = True
                PyUnrealBuildSystem.Get().CreateTask(Args)
                Args.Clean = False
            
            Args.BuildCookRun = True
            PyUnrealBuildSystem.Get().CreateTask(Args)
            Args.BuildCookRun = False
        

        if Args.TestUEPlugin == True:
            PyUnrealBuildSystem.Get().BuildPlugin(Args,Args.TestPluginPath)

        if Args.TestAgoraPlugin == True:
            
            btest_use_agora_sdk_info = Args.QuerySDK
            if btest_use_agora_sdk_info:
                sdkinfo = AgoraSDKInfo(Args.agorasdk,Args.sdkisaudioonly)
                path_plugin_zipfile = AgoraPluginManager.Get().GetPath_QueryPluginZipFile(sdkinfo,False,True)
                if path_plugin_zipfile.exists():
                    self.TestAgoraPlugin(Args,path_plugin_zipfile)
                else:
                    PrintErr("[TestPlugin] not found agora sdk")
            else:
                self.TestAgoraPlugin(Args,Args.TestPluginPath)

        if Args.AppToIPA == True:
            UnrealProjectManager.ConvertMacAppToIPA(Args.AppPath)

    def CopySDKToUEProject(self,Args):
        
        bdo_macratrust = Args.MacTrust
        sdkinfo = AgoraSDKInfo(Args.agorasdk, Args.sdkisaudioonly, Args.agorasdktype)
        
        dst_project_path = Path(Args.uprojectpath).parent
        dst_plugin_path = dst_project_path.joinpath("Plugins")
        dst_plugin_path.mkdir(parents= True, exist_ok= True)

        AgoraPluginManager.Get().QueryAndCopySDKToDstPath(sdkinfo,dst_plugin_path)
        
        if bdo_macratrust and self.GetHostPlatform() == "Mac":
            AgoraPluginManager.Get().DoMacRATrustTask(dst_project_path,Args.Password)


    def TestAgoraPlugin(self,Args,path_plugin_zipfile):

        path_working_dir = Path(path_plugin_zipfile).parent
        path_unzip = path_working_dir / Path(PyUnrealBuildSystem.Get().GetName_TestPluginUnzipDir())

        ## Clean First
        if path_unzip.exists():
            FileUtility.DeleteDir(path_unzip)

        ## Prepare :
        ## Unzip the plugin to get uplugin file path
        OneZipCommand =ZipCommand()
        OneZipCommand.UnZipFile(path_plugin_zipfile,path_unzip)
        name_plugin,path_uplugin_file = UBSHelper.Get().GetInfo_PluginNameAndUPluginFilePath(path_unzip)
        path_plugin = Path(path_uplugin_file).parent
    
        ### Agora Modfication
        AgoraPluginManager.Get().RemoveSymbolicLink(path_plugin / Path("Source/ThirdParty/AgoraPluginLibrary") / Path("Mac") / Path("Release"))

        ## Start Testing
        PyUnrealBuildSystem.Get().BuildPluginInner(Args,path_uplugin_file)
    
        ### [After Build] Clean Environment
        if path_unzip.exists():
            FileUtility.DeleteDir(path_unzip)




if __name__ == '__main__':
    AgoraBuildSystem.Get().Start()
