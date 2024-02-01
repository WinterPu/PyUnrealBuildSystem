from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *

from Command.GitCommand import *
from Command.MacRATrustCommand import *
from Command.ZipCommand import *
from Utility.Downloader import *

from APM import *

from SystemBase import *

import argparse

import platform

version_info = {}
class PyUnrealBuildSystem(BaseSystem):
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
        return PyUnrealBuildSystem()
    
    
    def Start(self):
        PrintStageLog("Start Build System")
        PyUnrealBuildSystem.Get().Init()


        ## 
        args = PyUnrealBuildSystem.Get().ParseCMDArgs()
        PyUnrealBuildSystem.Get().CreateTask(args)

    def Init(self):
        ## Init System Info
        PrintStageLog("PyUnrealBuildSystem Init")
        PyUnrealBuildSystem.Get().InitBuildSystemInfo()

        ConfigParser.Get().Init()

        AgoraPluginManager.Get().Init()

    def InitBuildSystemInfo(self):
        version_info['BuildSystemVersion'] = self.version
        version_info['PythonVersion'] = platform.python_version()
        ossystem = platform.platform().lower()
        if 'windows' in ossystem:
            version_info['HostMachineOS'] = "Win"
        elif 'macos' in ossystem:
            version_info['HostMachineOS'] = "Mac"
        else:
            version_info['HostMachineOS'] = ossystem
        
        PrintLog(version_info)

    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse Package Args")
        self.AddArgsToParser(ArgParser)
        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args

    def AddArgsToParser(self,ArgParser, bIncludeConflictArgs = True):
        #bIncludeConflictArgs: Some Args used in this file would have conflicts with args which have the same name in the other files
        ## because [add_argument] cannot add the same arguments twice
        default_targetsystem = version_info['HostMachineOS']
        if default_targetsystem == "Win":
            default_targetsystem = "Win64"

        ArgParser.add_argument("-enginepath", default="")
        ArgParser.add_argument("-enginever", default="4.27")
        ArgParser.add_argument("-projectpath", default=Path("/Users/admin/Documents/Agora-Unreal-RTC-SDK-main/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject"))   
        ArgParser.add_argument("-pluginpath", default="") ## if "": use the plugin under the plugins file
        ArgParser.add_argument("-targetplatform", default=default_targetsystem)
        
        ## Build Command
        ArgParser.add_argument("-BuildCookRun", action='store_true')
        ArgParser.add_argument("-BuildPlugin", action='store_true')
        


        ## Utility Command
        ArgParser.add_argument("-GitClone", action='store_true')
        ArgParser.add_argument("-GitRevert", action='store_true')
        ArgParser.add_argument("-Clean", action='store_true')
        ArgParser.add_argument("-GenProject", action='store_true')

        if bIncludeConflictArgs:
            ArgParser.add_argument("-TestPlugin", action='store_true')
            ArgParser.add_argument("-agorasdktype", default="RTC")
            ArgParser.add_argument("-agorasdk", default="4.2.1")
            ArgParser.add_argument("-CopySDKType",default="None")
            ArgParser.add_argument("-RedownloadSDK",action='store_true')

    def InitConfig(self):
        PrintLog("Init Log")
        ## Host Machine
        

    def CreateTask(self,Args):
        ## Init Host Platform
        type_hostplatform = version_info['HostMachineOS']

        ## Combine 2 Args
        Args.HostMachineOS = type_hostplatform


        PrintLog("Check EnginePath " + str(Args.enginepath) + str(Args.enginepath == ""))
        ## Handle Engine Version
        if Args.enginepath == "":
            Args.enginepath = Path(ConfigParser.Get().GetDefaultEnginePath(Args.enginever))
            PrintLog("Check EnginePath " + str(Args.enginepath))

        ret_host,host_platform = CreateHostPlatform(type_hostplatform,Args)

        if ret_host == False:
            PrintErrWithFrame(sys._getframe())
            return

        if Args.BuildPlugin == True:
            arg_targetplatform = Args.targetplatform
            arg_project_file_path = Args.projectpath
            arg_project_path = arg_project_file_path.parent
            plugin_path = arg_project_path  / Path("Plugins/AgoraVoicePlugin/AgoraVoicePlugin.uplugin")
            output_path = arg_project_path  / Path("Saved/PluginOutput/")
            if Args.pluginpath != "":
                plugin_path = Path(Args.pluginpath)
                output_path = plugin_path.parent.parent / Path("output/")
            host_platform.BuildPlugin(plugin_path,arg_targetplatform,output_path)

        # if Args.TestPlugin == True:
        #     PrintStageLog("Test Plugin")
            
        #     ## Clean
        #     path_plugin_archive_dir = Path("/Users/admin/Documents/PluginWorkDir/PluginArchive/")
        #     path_target_plugin = path_plugin_archive_dir/ Path("AgoraPlugin.zip")
        #     path_output_dir = path_plugin_archive_dir / Path("Output")
            
        #     path_target_plugin_dir = path_plugin_archive_dir/path_target_plugin.stem
        #     if path_target_plugin_dir.exists():
        #         FileUtility.DeleteDir(path_target_plugin_dir)
            
        #     if path_output_dir.exists():
        #         FileUtility.DeleteDir(path_output_dir)


        #     ## Prepare 
        #     OneZipCommand =ZipCommand(self.GetHostPlatform())
        #     OneZipCommand.UnZipFile(path_target_plugin,path_plugin_archive_dir)
        #     plugin_name = "AgoraPlugin"
        #     path_uplugin_file =  path_plugin_archive_dir / plugin_name / Path(plugin_name+".uplugin")
            
        #     path_output_dir.mkdir(parents=True,exist_ok=True)

        #     AgoraPluginManager.Get().RemoveSymbolicLink(path_target_plugin_dir/ Path("Source/ThirdParty/AgoraPluginLibrary") / Path("Mac") / Path("Release"))

        #     cur_enginever  = Args.enginever

        #     all_engine_list = ConfigParser.Get().GetAllAvailableEngineList()
        #     for engine_ver in all_engine_list:
        #         PrintStageLog("Build Use Engine Ver [%s]" % engine_ver)
        #         Args = self.SetUEEngine(engine_ver,Args)  
             
        #         arg_targetplatform = Args.targetplatform
        #         ret_host,tmp_host_platform = CreateHostPlatform(type_hostplatform,Args)
        #         tmp_host_platform.BuildPlugin(path_uplugin_file,arg_targetplatform,path_output_dir)

        #     ## Recover UE Engine
        #     Args = self.SetUEEngine(cur_enginever,Args)

        if Args.BuildCookRun == True:
            target_platform_type_list = ParsePlatformArg(Args.targetplatform)
            for target_platform_type in target_platform_type_list:
                ret_target,target_platform = CreateTargetPlatform(host_platform,target_platform_type,Args)
                if ret_target == True:
                    target_platform.SetupEnvironment()
                    target_platform.Package()
                else: 
                    PrintErr("Invalid TargetPlatform Creation")

        if Args.Clean == True:
            path_project = Path(Args.projectpath)
            project_folder_path = path_project.parent
            ## Path \ or not

            ## [TBD] clean xcproject
            UnrealProjectManager.CleanProject(project_folder_path)

        if Args.GenProject == True:
            path_project = Path(Args.projectpath)
            project_folder_path = Args.projectpath
            ## [TBD] some needs \ and some doesn't need \
            UnrealProjectManager.GenerateProject(host_platform,project_folder_path)

        if Args.GitClone == True:
            url = ""
            OneGitCommand = GitCommand()
            VersionControlTool.Init(OneGitCommand)
            VersionControlTool.CheckOutOneRepo(url)

        

    def SetUEEngine(self,engine_ver,Args):
        Args.enginever = engine_ver
        Args.enginepath = Path(ConfigParser.Get().GetDefaultEnginePath(Args.enginever))
        return Args

if __name__ == '__main__':
    PyUnrealBuildSystem.Get().Start()