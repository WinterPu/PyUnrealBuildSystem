from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *

from Command.GitCommand import *
from Command.MacRATrustCommand import *
from Command.ZipCommand import *
from Utility.Downloader import *

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
        PrintLog("Start Build System")
        PyUnrealBuildSystem.Get().Init()


        ## 
        args = PyUnrealBuildSystem.Get().ParseCMDArgs()
        PyUnrealBuildSystem.Get().CreateTask(args)

    def Init(self):
        ## Init System Info
        PyUnrealBuildSystem.Get().InitBuildSystemInfo()

        ConfigParser.Get().Init()

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
        default_targetsystem = version_info['HostMachineOS']
        if default_targetsystem == "Win":
            default_targetsystem = "Win64"
        
        ArgParser.add_argument("-enginepath", default="")
        ArgParser.add_argument("-enginever", default="4.27")
        ArgParser.add_argument("-projectpath", default=Path("/Users/admin/Documents/LLS/AgoraExample/AgoraExample.uproject"))   
        ArgParser.add_argument("-pluginpath", default="") ## if "": use the plugin under the plugins file
        ArgParser.add_argument("-targetplatform", default=default_targetsystem)
        ArgParser.add_argument("-agorasdktype", default="RTC")
        ArgParser.add_argument("-agorasdk", default="4.2.1")
        ArgParser.add_argument("-CopySDKType",default="None")
        ArgParser.add_argument("-RedownloadSDK",action='store_true')
        
        ## Build Command
        ArgParser.add_argument("-BuildCookRun", action='store_true')
        ArgParser.add_argument("-BuildPlugin", action='store_true')


        ## Utility Command
        ArgParser.add_argument("-GitClone", action='store_true')
        ArgParser.add_argument("-GitRevert", action='store_true')
        ArgParser.add_argument("-Clean", action='store_true')
        ArgParser.add_argument("-GenProject", action='store_true')
        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args

    def InitConfig(self):
        PrintLog("Init Log")
        ## Host Machine
        

    def CreateTask(self,Args):
        ## Init Host Platform
        type_hostplatform = version_info['HostMachineOS']

        PrintLog("Check EnginePath " + str(Args.enginepath) + str(Args.enginepath == ""))
        ## Handle Engine Version
        if Args.enginepath == "":
            Args.enginepath = Path(ConfigParser.Get().GetDefaultEnginePath(Args.enginever))
            PrintLog("Check EnginePath " + str(Args.enginepath))

        ret_host,host_platform = CreateHostPlatform(type_hostplatform,Args)

        if ret_host == False:
            PrintErr(sys._getframe())
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
        
        if Args.BuildCookRun == True:
            target_platform_type_list = ParsePlatformArg(Args.targetplatform)
            for target_platform_type in target_platform_type_list:
                ret_target,target_platform = CreateTargetPlatform(host_platform,target_platform_type,Args)
                if ret_target == True:
                    target_platform.SetupEnvironment()
                    target_platform.Package()
                else: 
                    PrintErr(sys._getframe(),"Invalid TargetPlatform Creation")

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

        


        if Args.CopySDKType != "None":
            ## Create Plugin Repo
            default_plugin_repo_path = Path(ConfigParser.Get().GetDefaultPluginRepo())
            default_plugin_repo_path.mkdir(parents= True, exist_ok= True)

            bUseAudioOnlySDK = Args.CopySDKType == "AudioOnly"
            url = ConfigParser.Get().GetRTCSDKURL(Args.agorasdk,bUseAudioOnlySDK)
            PrintLog(url)
            plugin_name = url.split('/')[-1]
            plugin_path = default_plugin_repo_path / plugin_name

            PrintLog(plugin_path)

            ## Download Plugin
            if Args.RedownloadSDK:
                if plugin_path.exists() == True:
                    plugin_path.unlink()
                FileDownloader.DownloadWithRequests(url,plugin_path)

            ## Copy Plugin
            dst_project_path = Args.projectpath
            dst_plugin_path = dst_project_path.parent.joinpath("Plugins")
            dst_plugin_path.mkdir(parents= True, exist_ok= True)
            dst_plugin_path = dst_plugin_path / Path("AgoraPlugin")
            if dst_plugin_path.exists() == True:
                FileUtility.DeleteDir(str(dst_plugin_path))
            
            dst_plugin_path.mkdir(parents= True, exist_ok= True)
            
            OneZipCommand =ZipCommand(self.GetHostPlatform())
            unzip_path = default_plugin_repo_path / Path("UnzipPlugin")
            OneZipCommand.UnZipFile(plugin_path ,unzip_path)
            src_plugin_path = unzip_path / Path("AgoraPlugin")
            shutil.copytree(str(src_plugin_path),str(dst_plugin_path),dirs_exist_ok= True)

            FileUtility.DeleteDir(str(unzip_path))

            ## MacRATrust
            OneMacRATrustCommand= MacRATrustCommand()
            OneMacRATrustCommand.DoMacTrust(Args.projectpath.parent);


if __name__ == '__main__':
    PyUnrealBuildSystem.Get().Start()