from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *
from Utility.UnrealConfigIniManager import *

from Command.GitCommand import *
from Command.MacRATrustCommand import *
from Command.ZipCommand import *
from Command.FastLaneCommand import * 
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
        ArgParser.add_argument("-projectpath", default=Path("/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject"))   
        ArgParser.add_argument("-pluginpath", default="") ## if "": use the plugin under the plugins file
        ArgParser.add_argument("-targetplatform", default=default_targetsystem)
        ArgParser.add_argument("-iosbundlename", default="com.YourCompany.AgoraExample")
        ArgParser.add_argument("-ioscert",default = "MediaLab")
        ## CreateTask handles it to be the base dir under the project dir
        ## otherwise it would be under the engine dir
        ArgParser.add_argument("-archive_dir",default = "")
    
        
        ## Config Set
        ArgParser.add_argument("-SetUEConfigIni", action='store_true')
        ArgParser.add_argument("-IniFile", default="")
        ArgParser.add_argument("-IniSection", default="")
        ArgParser.add_argument("-IniKey", default="")
        ArgParser.add_argument("-IniVal", default="")

        ## Build Command
        ArgParser.add_argument("-BuildCookRun", action='store_true')
        ArgParser.add_argument("-BuildPlugin", action='store_true')
        
        ## IOS Resign
        ## Use -ioscert specify the certificate
        ArgParser.add_argument("-IPAResign", action='store_true')
        
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

    def GetName_TestPluginOutputDir(self):
        return "TestPluginOutput"
    
    def GetName_TestPluginUnzipDir(self):
        return "TestPluginUnzip"
    
    def GetInfo_PluginNameAndUPluginFilePath(self,path_plugin_folder):
        ## search in path_plugin_folder to find upluign file. 
        ## get the plugin name the same as the uplugin file

        uplugin_files = list(Path(path_plugin_folder).rglob("*.uplugin"))
        path_uplugin_file = ""
        name_plugin = ""
        for uplugin_file in uplugin_files:
            if "__MACOSX" in str(uplugin_file):
                    ## not the target one
                    pass
            else:
                path_uplugin_file = Path(uplugin_file)
                name_plugin = Path(path_uplugin_file).stem
                PrintLog("[GetPluginInfo] plugin name [%s] uplugin file path: [%s] " % (name_plugin , str(path_uplugin_file)))
                if name_plugin != path_uplugin_file.parent.name:
                    PrintErr("[GetPluginInfo] the plugin folder name [%s] is not equal to uplugin file name [%s]" %( path_uplugin_file.parent.name,name_plugin))
        
        return name_plugin, path_uplugin_file

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

        if Args.archive_dir != "":
            Args.archive_dir = str(Path(Args.projectpath).parent / Args.archive_dir)

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
                    ## target_platform.SetupEnvironment() did it in [Package]
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

        bTestCommand = False
        if bTestCommand:
            if self.GetHostPlatform() == "Mac":
                project_folder_path = Args.projectpath
                bundlename = Args.iosbundlename
                host_platform.IOSSign(project_folder_path,bundlename)           

        if Args.IPAResign == True:
            OneFastLaneCommand = FastLaneCommand()
            path_uproject = Path(Args.projectpath)
            name_app = path_uproject.stem + ".ipa"

            path_ipa = Path(Args.projectpath).parent / "ArchivedBuilds"/ "IOS" / name_app
            
            tag_name_ios_cert = Args.ioscert
            if ConfigParser.Get().IsIOSCertValid(tag_name_ios_cert) :
                PrintLog("[IPAResign] Use IOS Certificate %s " %tag_name_ios_cert)
                OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(tag_name_ios_cert)
                OneFastLaneCommand.IPAResign(path_ipa,OneIOSCert["signing_identity"],OneIOSCert["path_mobileprovision"])
            
        
        if Args.SetUEConfigIni == True:
            UnrealConfigIniManager.SetConfig(Args.IniFile,Args.IniSection,Args.IniKey,Args.IniVal,True)
            
            #OneIOSCert = ConfigParser.Get().GetOneIOSCertificate("D")
            #UnrealConfigIniManager.SetConfig_IOSCert(Args.projectpath,OneIOSCert["signing_identity"],OneIOSCert["provisioning_profile"])
        

    def BuildPlugin(self,Args,path_plugin_zipfile):

        path_working_dir = Path(path_plugin_zipfile).parent
        path_unzip = path_working_dir / Path(self.GetName_TestPluginUnzipDir())

        ## Clean First
        if path_unzip.exists():
            FileUtility.DeleteDir(path_unzip)
    
        ## Prepare :
        ## Unzip the plugin to get uplugin file path
        OneZipCommand =ZipCommand(self.GetHostPlatform())
        OneZipCommand.UnZipFile(path_plugin_zipfile,path_unzip)
        name_plugin,path_uplugin_file = self.GetInfo_PluginNameAndUPluginFilePath(path_unzip)
        
        ## Start Testing
        self.BuildPluginInner(Args,path_uplugin_file)
    
        ### [After Build] Clean Environment
        if path_unzip.exists():
            FileUtility.DeleteDir(path_unzip)



    def BuildPluginInner(self,Args,path_uplugin_file):
        ## Ex. /Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1/AgoraPlugin/AgoraPlugin.uplugin
        ## -> /Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1/TestPluginOutput
        path_output_dir = Path(path_uplugin_file).parent.parent / Path(self.GetName_TestPluginOutputDir())
        
        if path_output_dir.exists():
            FileUtility.DeleteDir(path_output_dir)
        path_output_dir.mkdir(parents=True,exist_ok=True)
        
        cur_enginever  = Args.enginever
        arg_targetplatform = Args.targetplatform

        all_engine_list = ConfigParser.Get().GetAllAvailableEngineList()
        test_complete_log_keyword = "Test Plugin Complete"
        for engine_ver in all_engine_list:
            PrintStageLog("Test Use Engine Ver [%s]" % engine_ver)
            Args = PyUnrealBuildSystem.Get().SetUEEngine(engine_ver,Args)  
            
            ret_host,tmp_host_platform = CreateHostPlatform(self.GetHostPlatform(),Args)
            tmp_host_platform.BuildPlugin(path_uplugin_file,arg_targetplatform,path_output_dir)
            PrintStageLog(test_complete_log_keyword + " Engine Ver[%s]" %engine_ver)

        PrintStageLog("Test Plugin Complete --- Use keyword [%s] to search in your log" %test_complete_log_keyword )

        ## [Ater Test] Recover UE Engine
        Args = PyUnrealBuildSystem.Get().SetUEEngine(cur_enginever,Args)

        if path_output_dir.exists():
            FileUtility.DeleteDir(path_output_dir)
    

    def SetUEEngine(self,engine_ver,Args):
        Args.enginever = engine_ver
        Args.enginepath = Path(ConfigParser.Get().GetDefaultEnginePath(Args.enginever))
        return Args

if __name__ == '__main__':
    PyUnrealBuildSystem.Get().Start()