from Utility.HeaderBase import *
from SystemBase import *

from APM import *
from UBS import *
## Combine UBS + APM
class AgoraBuildSystem(BaseSystem):

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized: 
            super().__init__()
            self._initialized = True
    
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
        #ArgParser.add_argument("-NeedCopySDKWhenBuilding",action = "store_true")
        ArgParser.add_argument("-MacTrust",action = "store_true")
        ArgParser.add_argument("-Password",default="")
        # ArgParser.add_argument("-MacTrust",action = "store_true")
        ArgParser.add_argument("-TestPlugin",action = "store_true")
        ArgParser.add_argument("-NotTestAgoraPlugin",action = "store_true")
        ArgParser.add_argument("-TestPluginPath",default = "/Users/admin/Documents/PluginWorkDir/PluginArchive/AgoraPlugin.zip")
        ArgParser.add_argument("-TestBlackList",default = "")

        ArgParser.add_argument("-GenPlugin",action = "store_true")

        if bIncludeConflictArgs:
            pass

    def CreateTask(self,Args):
        if Args.GenPlugin == True:
            AgoraPluginManager.Get().StartGenPlugin(Args)

        if Args.BuildUEProject == True:
            
            self.CopySDKToUEProject(Args)
            Args.Clean = True
            PyUnrealBuildSystem.Get().CreateTask(Args)
            Args.Clean = False
            Args.BuildCookRun = True
            PyUnrealBuildSystem.Get().CreateTask(Args)
            Args.BuildCookRun = False
        
        if Args.TestPlugin == True:

            btest_is_agora_plugin = not Args.NotTestAgoraPlugin
            plugin_name = Args.pluginname
            path_test_plugin_zipfile = Path(Args.TestPluginPath)
            path_working_dir = path_test_plugin_zipfile.parent
            path_output_dir = path_working_dir / Path("TestPluginOutput")
            path_test_plugin_dir = path_working_dir / plugin_name

            ## Clean First
            if path_test_plugin_dir.exists():
                FileUtility.DeleteDir(path_test_plugin_dir)
            
            if path_output_dir.exists():
                FileUtility.DeleteDir(path_output_dir)
        
            ## Prepare 
            OneZipCommand =ZipCommand(self.GetHostPlatform())
            OneZipCommand.UnZipFile(path_test_plugin_zipfile,path_test_plugin_zipfile.parent)
 
            path_uplugin_file =  path_test_plugin_dir / Path(plugin_name+".uplugin")
        
            path_output_dir.mkdir(parents=True,exist_ok=True)

            if btest_is_agora_plugin:
                AgoraPluginManager.Get().RemoveSymbolicLink(path_test_plugin_dir/ Path("Source/ThirdParty/AgoraPluginLibrary") / Path("Mac") / Path("Release"))

            cur_enginever  = Args.enginever

            all_engine_list = ConfigParser.Get().GetAllAvailableEngineList()
            test_complete_log_keyword = "Test Plugin Complete"
            for engine_ver in all_engine_list:
                PrintStageLog("Test Use Engine Ver [%s]" % engine_ver)
                Args = PyUnrealBuildSystem.Get().SetUEEngine(engine_ver,Args)  
             
                arg_targetplatform = Args.targetplatform
                ret_host,tmp_host_platform = CreateHostPlatform(self.GetHostPlatform(),Args)
                tmp_host_platform.BuildPlugin(path_uplugin_file,arg_targetplatform,path_output_dir)
                PrintStageLog(test_complete_log_keyword + " Engine Ver[%s]" %engine_ver)

            ## Recover UE Engine
            Args = PyUnrealBuildSystem.Get().SetUEEngine(cur_enginever,Args)

            PrintStageLog("Test Plugin Complete --- Use keyword [%s] to search in your log" %test_complete_log_keyword )

    def CopySDKToUEProject(self,Args):
        dst_project_path = Args.projectpath.parent
        plugin_name = Args.pluginname
        sdk_type = Args.agorasdktype
        sdk_ver = Args.agorasdk
        sdk_is_audio_only = Args.sdkisaudioonly
        bdo_macratrust = Args.MacTrust
        dst_plugin_path = dst_project_path.joinpath("Plugins")
        dst_plugin_path.mkdir(parents= True, exist_ok= True)

        AgoraPluginManager.Get().CopySDKToDstPath(plugin_name,sdk_type,sdk_ver,sdk_is_audio_only,dst_plugin_path)
        
        if bdo_macratrust and self.GetHostPlatform() == "Mac":
            AgoraPluginManager.Get().DoMacRATrustTask(dst_project_path,Args.Password)


    

if __name__ == '__main__':
    AgoraBuildSystem.Get().Start()
