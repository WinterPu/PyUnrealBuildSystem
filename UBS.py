from Utility.HeaderBase import *
from Utility.ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *

from Command.GitCommand import *

import argparse

import platform

version_info = {}
class PyUnrealBuildSystem:
    version = "1.""0.""0"
    
    def Start():
        PrintLog("Start Build System")
        PyUnrealBuildSystem.Init()


        ## 
        args = PyUnrealBuildSystem.ParseCMDArgs()
        PyUnrealBuildSystem.CreateTask(args)

    def Init():
        ## Init System Info
        PyUnrealBuildSystem.InitBuildSystemInfo()


    def InitBuildSystemInfo():
        version_info['BuildSystemVersion'] = PyUnrealBuildSystem.version
        version_info['PythonVersion'] = platform.python_version()
        ossystem = platform.platform().lower()
        if 'windows' in ossystem:
            version_info['HostMachineOS'] = "Win"
        elif 'macos' in ossystem:
            version_info['HostMachineOS'] = "Mac"
        else:
            version_info['HostMachineOS'] = ossystem
        
        PrintLog(version_info)

    def ParseCMDArgs():
        ArgParser = argparse.ArgumentParser(description="Parse Package Args")
        default_targetsystem = version_info['HostMachineOS']
        if default_targetsystem == "Win":
            default_targetsystem = "Win64"
        
        ArgParser.add_argument("-enginepath", default=Path("/Users/Shared/Epic Games/UE_4.27/"))
        ArgParser.add_argument("-enginever", default="4.27")
        ArgParser.add_argument("-projectpath", default=Path("/Users/admin/Documents/Unreal Projects/Agora-Unreal-RTC-SDK-dev-4.2.1/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject"))   
        ArgParser.add_argument("-pluginpath", default="") ## if "": use the plugin under the plugins file
        ArgParser.add_argument("-targetplatform", default=default_targetsystem)
        ArgParser.add_argument("-agorasdktype", default="RTC")
        ArgParser.add_argument("-agorasdk", default="4.2.1")
        
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

    def InitConfig():
        PrintLog("Init Log")
        ## Host Machine
        

    def CreateTask(Args):
        ## Init Host Platform
        type_hostplatform = version_info['HostMachineOS']
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

if __name__ == '__main__':
    PyUnrealBuildSystem.Start()