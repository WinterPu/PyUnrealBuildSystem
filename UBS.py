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

from UBSHelper import *
from SystemHelper import *

version_info = {}
class PyUnrealBuildSystem(BaseSystem):
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
        return PyUnrealBuildSystem()
    
    
    def Start(self):
        PrintStageLog("Start Build System")
        PyUnrealBuildSystem.Get().Init()
        args = PyUnrealBuildSystem.Get().ParseCMDArgs()
        PyUnrealBuildSystem.Get().CreateTask(args)

    def Init(self):
        ## Init System Info
        PrintStageLog("PyUnrealBuildSystem Init")
        PyUnrealBuildSystem.Get().InitBuildSystemInfo()

        ConfigParser.Get().Init()

    def InitBuildSystemInfo(self):
        val_version = "1.""0.""0"
        version_info['SystemVersion'] = val_version
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
        default_targetsystem = self.GetHostPlatform()
        if default_targetsystem == SystemHelper.Win_HostName():
            default_targetsystem = SystemHelper.Win64_TargetName()

        ArgParser.add_argument("-enginepath", default="")
        ArgParser.add_argument("-enginever", default="4.27")
        ArgParser.add_argument("-uprojectpath", default=Path("/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject"))   
        ArgParser.add_argument("-upluginpath", default="") ## if "": use the plugin under the plugins file
        ArgParser.add_argument("-targetplatform", default=default_targetsystem)
        ArgParser.add_argument("-androidpackagename", default="com.YourCompany.[PROJECT]")
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
        ArgParser.add_argument("-GenIOSProject", action='store_true')

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
    

    def InitConfig(self):
        PrintLog("Init Log")
        ## Host Machine
        

    def CreateTask(self,Args):
        ## Init Host Platform
        type_hostplatform = SystemHelper.Get().GetHostPlatform()

        UBSHelper.Get().Init(Args)

        ret_host,host_platform = CreateHostPlatform(type_hostplatform,Args)
        if ret_host == False:
            PrintErrWithFrame(sys._getframe())
            return
        

        if Args.BuildPlugin == True:
            pass
            ## [TBD] Modify
            # arg_targetplatform = Args.targetplatform
            # arg_path_uproject_file = Args.uprojectpath
            # arg_path_project = arg_path_uproject_file.parent
            # plugin_path = arg_path_project  / Path("Plugins/AgoraVoicePlugin/AgoraVoicePlugin.uplugin")
            # output_path = arg_path_project  / Path("Saved/PluginOutput/")
            # if Args.upluginpath != "":
            #     plugin_path = Path(Args.upluginpath)
            #     output_path = plugin_path.parent.parent / Path("output/")
            # host_platform.BuildPlugin(plugin_path,arg_targetplatform,output_path)
        
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
            path_project = Path(Args.uprojectpath).parent
            ## Path \ or not

            ## [TBD] clean xcproject
            UnrealProjectManager.CleanProject(path_project)

        if Args.GenProject == True:
            path_uproject_file = Path(Args.uprojectpath)
            ## [TBD] some needs \ and some doesn't need \
            UnrealProjectManager.GenerateProject(host_platform,path_uproject_file)

        if Args.GenIOSProject == True:
            path_uproject_file = Path(Args.uprojectpath)
            ## [TBD] some needs \ and some doesn't need \
            UnrealProjectManager.GenerateIOSProject(host_platform,path_uproject_file)

        if Args.GitClone == True:
            url = ""
            OneGitCommand = GitCommand()
            VersionControlTool.Init(OneGitCommand)
            VersionControlTool.CheckOutOneRepo(url)

        bTestCommand = False
        if bTestCommand:
            if self.GetHostPlatform() == SystemHelper.Mac_HostName():
                path_uproject_file = Args.uprojectpath
                bundlename = Args.iosbundlename
                host_platform.IOSSign(path_uproject_file,bundlename)           

        if Args.IPAResign == True:
            OneFastLaneCommand = FastLaneCommand()
            path_uproject = Path(Args.uprojectpath)
            name_app = path_uproject.stem + ".ipa"

            path_ipa = Path(Args.uprojectpath).parent / "ArchivedBuilds"/ "IOS" / name_app
            
            tag_name_ios_cert = Args.ioscert
            if ConfigParser.Get().IsIOSCertValid(tag_name_ios_cert) :
                PrintLog("[IPAResign] Use IOS Certificate %s " %tag_name_ios_cert)
                OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(tag_name_ios_cert)
                OneFastLaneCommand.IPAResign(path_ipa,OneIOSCert["signing_identity"],OneIOSCert["path_mobileprovision"])
            
        
        if Args.SetUEConfigIni == True:
            UnrealConfigIniManager.SetConfig(Args.IniFile,Args.IniSection,Args.IniKey,Args.IniVal,True)
            
            #OneIOSCert = ConfigParser.Get().GetOneIOSCertificate("D")
            #UnrealConfigIniManager.SetConfig_IOSCert(Args.uprojectpath,OneIOSCert["signing_identity"],OneIOSCert["provisioning_profile"])
        

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
        name_plugin,path_uplugin_file = UBSHelper.Get().GetInfo_PluginNameAndUPluginFilePath(path_unzip)
        
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
            UBSHelper.Get().SetUEEngineWithVer(engine_ver) 
            
            ret_host,tmp_host_platform = CreateHostPlatform(self.GetHostPlatform(),Args)
            tmp_host_platform.BuildPlugin(path_uplugin_file,arg_targetplatform,path_output_dir)
            PrintStageLog(test_complete_log_keyword + " Engine Ver[%s]" %engine_ver)

        PrintStageLog("Test Plugin Complete --- Use keyword [%s] to search in your log" %test_complete_log_keyword )

        ## [Ater Test] Recover UE Engine
        UBSHelper.Get().SetUEEngineWithVer(cur_enginever)

        if path_output_dir.exists():
            FileUtility.DeleteDir(path_output_dir)

if __name__ == '__main__':
    PyUnrealBuildSystem.Get().Start()