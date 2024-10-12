


from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *
from Utility.Downloader import *

from Command.GitCommand import *
from Command.ZipCommand import *
from Command.MacRATrustCommand import *

from SystemBase import *


from UBSHelper import *

import argparse

import platform

from Base.AgoraSDKInfo import *

from UBS import *

import copy

from APMHelper import *

from Utility.ArchiveManager import *

class AgoraPluginManager(BaseSystem):

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
        return AgoraPluginManager()


    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse Plugin Manager Args")
        
        self.AddArgsToParser(ArgParser)

        Args = ArgParser.parse_args()

        PrintLog(Args)
        return Args
    
    def AddArgsToParser(self,ArgParser, bIncludeConflictArgs = True):

        ArgParser.add_argument("-nurlwin", default="")
        ArgParser.add_argument("-nurlmac", default="")
        ArgParser.add_argument("-nurlandroid", default="")
        ArgParser.add_argument("-nurlios", default="")

        ArgParser.add_argument("-agorasdktype", default="RTC")
        ArgParser.add_argument("-agorasdk", default="4.2.1")
        ArgParser.add_argument("-sdkisaudioonly",action = "store_true")
        ArgParser.add_argument("-skipnativedownload",action='store_true')
        ArgParser.add_argument("-skipgit",action='store_true')
        ArgParser.add_argument("-rmmacslink",action='store_true') # remove mac symbolic link
        ArgParser.add_argument("-agorasdkbuildconfig", default="Release")
        ArgParser.add_argument("-pluginname", default="AgoraPlugin")
        ArgParser.add_argument("-giturl", default= "git@github.com:AgoraIO-Extensions/Agora-Unreal-RTC-SDK.git")
        ArgParser.add_argument("-gitbranch", default="") 

        ArgParser.add_argument("-setenginever",action = "store_true")

        ## empty: full copy, copy all the files under the target folder.
        ArgParser.add_argument("-winarch", default="") 
        ArgParser.add_argument("-macarch", default="macos-arm64_x86_64") 
        ArgParser.add_argument("-androidarch", default="")
        ArgParser.add_argument("-iosarch", default="ios-arm64_armv7")
        ## currently, win has arch dir, Mac & IOS have no dir
        ArgParser.add_argument("-newarchstruct", action="store_true")

        #uplugin modification
        ArgParser.add_argument("-mmodifycompileoptions",action='store_true')
        ArgParser.add_argument("-mminenginever", default="5.3.0")  
        ArgParser.add_argument("-mmarketplaceurl", default="com.epicgames.launcher://ue/marketplace/product/4976717f4e9847d8b161f7c5adb4c1a9")
        ArgParser.add_argument("-msupporturl", default="https://www.agora.io/en/")  
        ArgParser.add_argument("-msupportplatforms", default="Win64+Mac+IOS+Android")

        ArgParser.add_argument("-skipgenoriginal",action='store_true')
        ArgParser.add_argument("-pluginarchivedir", default="")
        ArgParser.add_argument("-pluginfiledisplayname", default="")
        ArgParser.add_argument("-pluginsourcecodepath", default="")

        ArgParser.add_argument("-SkipGenPlugin",action='store_true')
        ArgParser.add_argument("-GenUEMarketplacePlugin",action='store_true')
        ArgParser.add_argument("-MarketplacePluginEngineList",default="")

        ArgParser.add_argument("-archiveplugin",action='store_true')
        ArgParser.add_argument("-archivepluginrootpath",default="")

        if bIncludeConflictArgs:
            pass

    ## PluginWorkingDir
    ## -- GitSourceCodeRepo
    ## -- PluginTemp
    ## ----- tmp_plugin_files
    ## -- PluginArchive
    def GetName_PluginWorkingDir(self):
        return "PluginWorkDir"
    def GetName_PluginTmpDir(self):
        return "PluginTemp"
    def GetName_FinalPluginFileTmpDir(self):
        return "tmp_plugin_files"
    def GetName_PluginArchive(self):
        return "PluginArchive"
    def GetName_PluginUEMarketplaceArchive(self):
        return "UEMarketplaceArchive"
    def GetName_PluginTmpSortSuffixName(self):
        return "_To_BE_DELETED"
    def GetName_PluginTmpDownloadDir(self):
        return "PluginTempDownload"

    def GetPath_PluginWorkingDir(self):
        cur_path = Path(__file__).parent.absolute()
        cur_path = cur_path.parent
        PrintLog("[GetPluginWorkDir] Cur PWD %s " %(str(cur_path)))
        return cur_path / self.GetName_PluginWorkingDir()
    
    def GetPath_PluginTmpDir(self):
        return Path(self.GetPath_PluginWorkingDir()) / self.GetName_PluginTmpDir()

    def GetPath_FinalPluginFileTmpDir(self):
        return Path(self.GetPath_PluginTmpDir()) / self.GetName_FinalPluginFileTmpDir()
    
    def GetPath_PluginArchiveDir(self):
        return Path(self.GetPath_PluginWorkingDir()) / self.GetName_PluginArchive()
    
    def GetPath_PluginUEMarketplaceArchiveDir(self):
        return Path(self.GetPath_PluginWorkingDir()) / self.GetName_PluginUEMarketplaceArchive()
    
    
    def GetPath_FinalPluginArchivePlacedDir(self,root_plugin_archive_path,sdkinfo:AgoraSDKInfo):
        path_category01 = Path(root_plugin_archive_path) / Path(sdkinfo.Get_SDKVer())
        if not path_category01.exists():
            path_category01.mkdir(parents=True)
        
        category02 = AgoraSDKInfo.GetName_SDKFull() if not sdkinfo.Get_SDKIsAudioOnly() else  AgoraSDKInfo.GetName_SDKAudioOnly()
        path_category02 = path_category01 / category02
        if not path_category02.exists():
            path_category02.mkdir(parents=True)
        
        return path_category02

    def Init(self):
        PrintStageLog("AgoraPluginManager Init")
        ConfigParser.Get().Init()

    def Start(self):
        AgoraPluginManager.Get().Init()
        args = self.ParseCMDArgs()
        self.CreateTask(args)

    def CreateTask(self,Args):
        if not Args.SkipGenPlugin:
            self.StartGenPlugin(Args)
        
        if Args.GenUEMarketplacePlugin:
            self.GenUEMarketplacePlugins(Args)

    def StartGenPlugin(self,Args):
        
        ## >>> Clean Plugin <<<
        AgoraPluginManager.Get().CleanPlugin(Args)
        
        ## >>> Data Preparation <<<
        PLUGIN_NAME = Args.pluginname

        git_url = Args.giturl
        git_branch = Args.gitbranch

        final_dst_plugin_path = Args.pluginarchivedir
        plugin_source_code_path = Args.pluginsourcecodepath

        sdkinfo = AgoraSDKInfo(Args.agorasdk,Args.sdkisaudioonly)
        
        sdk_build_config = Args.agorasdkbuildconfig
        ## keep mac symbolic link
        bkeep_symlink =True if not Args.rmmacslink else False

        plugin_tmp_file_dir = self.GetName_PluginTmpDir()
        plugin_tmp_sort_dir_suffix_name = self.GetName_PluginTmpSortSuffixName()
        final_plugin_file_dir = self.GetName_FinalPluginFileTmpDir() 
        plugin_archive_dir = self.GetName_PluginArchive()

        bshould_archive = Args.archiveplugin
        path_archive_plugin_root = Args.archivepluginrootpath

        bkeep_original_archive = not Args.skipgenoriginal

        # url_windows = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/windows/full/Agora_Native_SDK_for_Windows_rel.v4.2.1_21296_FULL_20230727_1707_272784.zip"
        # url_mac = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/mac/full/Agora_Native_SDK_for_Mac_rel.v4.2.1_46142_FULL_20230727_1549_272786.zip"
        # url_android = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/android/full/Agora_Native_SDK_for_Android_rel.v4.2.1_51720_FULL_20230727_1552_272785.zip"
        # url_ios = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/ios/full/Agora_Native_SDK_for_iOS_rel.v4.2.1_65993_FULL_20230727_1551_272787.zip"

        # url_ios="https://download.agora.io/sdk/release/Agora_Native_SDK_for_iOS_rel.v4.0.0.2_56070_FULL_20220803_2250_225057.zip"
        # url_android="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Android_rel.v4.0.0.2_38413_FULL_20220803_2250_225055.zip"
        # url_mac="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Mac_rel.v4.0.0.2_41396_FULL_20220803_2256_225058.zip"
        # url_windows="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Windows_rel.v4.0.0.2_15884_FULL_20220803_2250_225056.zip"
        

        bskip_download_native_sdk = Args.skipnativedownload
        

        
        url_ios = ConfigParser.Get().GetRTCSDKNativeURL_IOS(sdkinfo) if Args.nurlios == "" else Args.nurlios  
        url_android = ConfigParser.Get().GetRTCSDKNativeURL_Android(sdkinfo) if Args.nurlandroid == "" else Args.nurlandroid
        url_windows = ConfigParser.Get().GetRTCSDKNativeURL_Win(sdkinfo) if Args.nurlwin == "" else Args.nurlwin
        url_mac = ConfigParser.Get().GetRTCSDKNativeURL_Mac(sdkinfo) if Args.nurlmac == "" else Args.nurlmac
        
        
        root_path_plugin_working_dir = self.GetPath_PluginWorkingDir()
      

        ## >>> Update Git Repo <<< 
        ### [TBD] these are 2 Async Jobs (git & download ), they need to be synced.
        repo_path = root_path_plugin_working_dir

        if Args.skipgit == False:
            VersionControlTool.Get().CGit_CheckOutOneRepo(git_url,repo_path,git_branch)


        repo_name = git_url.split('/')[-1].split('.')[0]
        repo_path = repo_path / repo_name

        ## >>> Download Native SDK <<<
        plugin_tmp_path = root_path_plugin_working_dir / plugin_tmp_file_dir
        platform_list = [
            {"platform": "Win","url":url_windows}, 
            {"platform": "Mac","url":url_mac},
            {"platform": "Android","url":url_android},
            {"platform": "IOS","url":url_ios}
        ]

        ### Delete Plugin Folder if exists
        ### Ex. /Users/admin/Documents/PluginWorkDir/PluginTemp/AgoraNativeAndroidXXXXXX.zip
        plugin_tmp_path.mkdir(parents= True, exist_ok= True)
        for plugin_cfg in platform_list:
            print(plugin_cfg)
            if plugin_cfg['url'] == "":
                PrintErr("[Download Native SDK Error] target platform [%s] URL is NULL "%(plugin_cfg["platform"]))
                continue

            plugin_name = plugin_cfg['url'].split('/')[-1]
            path_plugin_zipfile = plugin_tmp_path / plugin_name
            
            if bskip_download_native_sdk != True:
                if path_plugin_zipfile.exists() == True:
                    path_plugin_zipfile.unlink()
                FileDownloader.DownloadWithRequests(plugin_cfg['url'],path_plugin_zipfile)

            OneZipCommand =ZipCommand()
            tmp_copy_dst_path = plugin_tmp_path / plugin_cfg["platform"]
            tmp_copy_dst_path.mkdir(parents=True,exist_ok= True)
            OneZipCommand.UnZipFile(path_plugin_zipfile,tmp_copy_dst_path)
            tmp_copy_file_list = list(tmp_copy_dst_path.glob('*'))
            ### Ex. make [/Users/admin/Documents/PluginWorkDir/PluginTemp/Android/AgoraNativeAndroidXXX/[native files]
            ###  ---> to [/Users/admin/Documents/PluginWorkDir/PluginTemp/Android/[native files]
            if len(tmp_copy_file_list) == 1 :
                if Path(tmp_copy_file_list[0]).is_dir() == True:
                    tmp_name = plugin_cfg["platform"] + plugin_tmp_sort_dir_suffix_name
                    tmp_dir_for_sort = tmp_copy_dst_path.parent / tmp_name
                    for path in tmp_copy_dst_path.iterdir():
                        path.rename(str(tmp_dir_for_sort))
                    for path in tmp_dir_for_sort.iterdir():
                        path.rename(tmp_copy_dst_path/path.name)
                    if tmp_dir_for_sort.exists():
                        FileUtility.DeleteDir(tmp_dir_for_sort)
                    
        ## >>> Copy Repo Plugin Files <<<
        ### Ex. Copy Repo[Agora-Unreal-SDK-CPP]/PLUGIN_NAME to Dst
        target_plugin_src_code_path = plugin_source_code_path
        if str(plugin_source_code_path) == "":
            target_plugin_src_code_path = repo_path / "Agora-Unreal-SDK-CPP" / PLUGIN_NAME
  
        ### Ex. [/Users/admin/Documents/PluginWorkDir/PluginTemp] / [tmp_plugin_files] / [AgoraPlugin]
        target_plugin_dst_path = plugin_tmp_path / final_plugin_file_dir / PLUGIN_NAME
        target_plugin_dst_path.mkdir(parents= True, exist_ok= True)
    
        PrintLog("[CopyGitRepoPluginFiles] Copy from [%s] to [%s] " %(str(target_plugin_src_code_path),str(target_plugin_dst_path)))
        FileUtility.CopyDir(target_plugin_src_code_path,target_plugin_dst_path)


        ## >>> Modify Android Template Here <<<
        ### [TBD] Add Arch Here
        target_plugin_dst_lib_path = target_plugin_dst_path / "Source"/ "ThirdParty" / (PLUGIN_NAME + "Library")
        path_android_tmpl_src = target_plugin_dst_lib_path / "Android" / sdk_build_config
        

        if VersionControlTool.Get().VerParse(sdkinfo.Get_SDKVer()) != VersionControlTool.Get().VerParse("4.2.1"):
            filename_full_tmpl = "APL_TemplateSourceFull.xml"
            filename_voice_tmpl = "APL_TemplateSourceVoice.xml"
            filename_src_tmpl = filename_full_tmpl if sdkinfo.Get_SDKIsAudioOnly() == False else filename_voice_tmpl
            filename_target_tmpl = "APL_Template.xml"

        else:
            filename_full_tmpl = "APL_armv7TemplateFULL.xml"
            filename_voice_tmpl = "APL_armv7TemplateVoice.xml"
            filename_src_tmpl = filename_full_tmpl if sdkinfo.Get_SDKIsAudioOnly() == False else filename_voice_tmpl
            filename_target_tmpl = "APL_armv7Template.xml"



        path_src_android_tmpl = path_android_tmpl_src / filename_src_tmpl
        path_dst_android_tmpl = path_android_tmpl_src / filename_target_tmpl
        FileUtility.CopyFile(path_src_android_tmpl,path_dst_android_tmpl)


        ## >>> Copy Every Platform's lib to FinalPluginTmpDir<<<
        ### [TBD] Add SDK Build Config
        ## Ex. Copy [.../PluginWorkDir/PluginTemp] / (platform)[Android] / [native files]
        ## --> To [.../PluginWorkDir/PluginTemp/tmp_plugin_files/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary]/ (platform)[Android] / sdk_build_config (debug/release)
        target_plugin_src_lib_path = plugin_tmp_path
        original_src = target_plugin_src_lib_path
        original_dst = target_plugin_dst_lib_path

        for plugin_cfg in platform_list:
            target_plugin_dst_lib_path = target_plugin_dst_lib_path / plugin_cfg["platform"] / sdk_build_config
            Path(target_plugin_dst_lib_path).mkdir(parents= True, exist_ok= True)
            target_plugin_src_lib_path = target_plugin_src_lib_path / plugin_cfg["platform"] ##

    
            architecture_str = ""
            if plugin_cfg["platform"] == "Mac":
                architecture_str = Args.macarch
            elif plugin_cfg["platform"] == "Win":
                architecture_str = Args.winarch
            elif plugin_cfg["platform"] == "Android":
                architecture_str = Args.androidarch
            elif plugin_cfg["platform"] == "IOS":
                architecture_str = Args.iosarch
            

            architecture_list = architecture_str.split('+')
            for architecture in architecture_list:
                if plugin_cfg["platform"] == "Mac":
                    target_plugin_src_lib_path = target_plugin_src_lib_path / Path("libs") / Path("*.xcframework")
                elif plugin_cfg["platform"] == "Win":
                    target_plugin_src_lib_path = target_plugin_src_lib_path / Path("sdk")
                elif plugin_cfg["platform"] == "Android":
                    target_plugin_src_lib_path = target_plugin_src_lib_path / Path("rtc/sdk/")
                elif plugin_cfg["platform"] == "IOS":
                    target_plugin_src_lib_path = target_plugin_src_lib_path / Path("libs") / Path("*.xcframework")

                if architecture != "" :
                    target_plugin_src_lib_path = target_plugin_src_lib_path / Path(architecture)

                    buse_new_arch_file_structure = Args.newarchstruct
                    bneed_to_create_arch_folder = False
                    if buse_new_arch_file_structure != True:
                            
                        if plugin_cfg["platform"] == "Win":
                            bneed_to_create_arch_folder = True

                        ## Mac and IOS don't create
                            
                    else:
                      bneed_to_create_arch_folder = True

                    if bneed_to_create_arch_folder:
                        target_plugin_dst_lib_path = target_plugin_dst_lib_path / Path(architecture)
                        target_plugin_dst_lib_path.mkdir(parents= True, exist_ok= True)

            
                ### Copy Native Libs To Tmp Plugin Dst Path 
                PrintLog(" from %s ---> %s " %(target_plugin_src_lib_path , target_plugin_dst_lib_path))
                if self.GetHostPlatform() == SystemHelper.Mac_HostName():
                    ## On Mac
                    if plugin_cfg["platform"] == "Mac":
                        FileUtility.CopyDir(target_plugin_src_lib_path,target_plugin_dst_lib_path,bkeep_symlink)
                    else:
                        ## Copy Other Platform Libs to Dst Path
                        FileUtility.CopyDir(target_plugin_src_lib_path,target_plugin_dst_lib_path)
                else:
                    ## On Windows
                    if plugin_cfg["platform"] == "IOS" or plugin_cfg["platform"] == "Mac":
                        ## Ex. D:\\Github\\PluginWorkDir\\PluginTemp\\tmp_plugin_files\\AgoraPlugin\\Source\\ThirdParty\\AgoraPluginLibrary\\IOS\\Release\
                        # Copy target_plugin_src_lib_root_path/*.xcframework/[architecture]/* to target_plugin_dst_lib_path 
                        target_plugin_src_lib_root_path = target_plugin_src_lib_path.parent.parent
                        FileUtility.CopyDirWithWildcardCharInPath_Win(target_plugin_src_lib_root_path,architecture,target_plugin_dst_lib_path)
                    else:
                        ## Copy Other Platform Libs to Dst Path
                        FileUtility.CopyDir(target_plugin_src_lib_path,target_plugin_dst_lib_path)


                ### [After Lib Copy] IOS: modify directory hierarchy
                ### A.framework -> A.embeddedframework/A.framework
                ### A.embeddedframework/A.framework ->  A.embeddedframework.zip
                if plugin_cfg["platform"] == "IOS":
                    all_framework_path_list = [ dir for dir in target_plugin_dst_lib_path.glob('*') if dir.is_dir()] 
                    for framework_dir in all_framework_path_list:
                        
                        ## A.framework -> A.embeddedframework/A.framework
                        framework_name = framework_dir.stem
                        embeddedframework_path = framework_dir.parent / Path(str(framework_name) + ".embeddedframework")
                        embeddedframework_path.mkdir(parents= True, exist_ok= True)
                        framework_dir.rename( embeddedframework_path / framework_dir.name)

                        ## A.embeddedframework/A.framework ->  A.embeddedframework.zip
                        zip_framework_name = Path(embeddedframework_path).name
                        dst_framework_path = target_plugin_dst_lib_path / (zip_framework_name + ".zip")
                        src_framework_path = target_plugin_dst_lib_path / zip_framework_name
                        OneZipCommand.ZipFile(src_framework_path,dst_framework_path)
                        FileUtility.DeleteDir(embeddedframework_path)

            target_plugin_src_lib_path = original_src
            target_plugin_dst_lib_path = original_dst
         

        ## >>> Modify Plugin Files Here <<< 
        bmodify_compile_options = Args.mmodifycompileoptions
        self.UpdateUpluginFile(target_plugin_dst_path / Path(PLUGIN_NAME+ ".uplugin"),Args)
        if bmodify_compile_options:
            self.ModifyCompileOptions(target_plugin_dst_path / Path("Source") / Path(PLUGIN_NAME) /Path( PLUGIN_NAME+ ".Build.cs"))
        self.ModifyFiles(sdkinfo.Get_SDKIsAudioOnly(),target_plugin_dst_path / Path("Source") / Path(PLUGIN_NAME) /Path( PLUGIN_NAME+ ".Build.cs"))

        
        ### >>> Zip FinalPluginTmp to Archive Dir <<<
        src_zip_files_root_path = target_plugin_dst_path.parent


        if not bkeep_original_archive and str(final_dst_plugin_path) != "":
            ## directly change dst_zip_file_path to [the path you assigned]
            dst_zip_file_path = Path(final_dst_plugin_path)
        else:
            ## use default one
            dst_zip_file_path = root_path_plugin_working_dir / plugin_archive_dir
            dst_zip_file_path.mkdir(parents= True, exist_ok= True)
            dst_zip_file_path = self.GetPath_FinalPluginArchivePlacedDir(dst_zip_file_path,sdkinfo)


        filename_final_dst_plugin = Args.pluginfiledisplayname
        if filename_final_dst_plugin == "" :
            filename_final_dst_plugin = PLUGIN_NAME
        
        dst_zip_file_path = dst_zip_file_path / (filename_final_dst_plugin + ".zip")
        src_zip_file_dir_path = src_zip_files_root_path / PLUGIN_NAME
        
        OneZipCommand.ZipFile(src_zip_file_dir_path,dst_zip_file_path)

        if bkeep_original_archive and final_dst_plugin_path != "":
            ## after generation, if bkeep_original_archive is true, and final_dst_plugin_path has value,
            ## it means: the final destination is the value you assigned
            ## Copy to the destination
            FileUtility.CopyFile(dst_zip_file_path,final_dst_plugin_path)
            dst_zip_file_path = final_dst_plugin_path
        
        PrintLog(">>>> Final Product Path: " + str(dst_zip_file_path))

        

        if bshould_archive:
            if path_archive_plugin_root != "":
                ArchiveManager.Get().SetPath_ArchiveRootDir(path_archive_plugin_root)

            OneArchiveInfo = ArchiveInfo_AgoraPlugin(sdkinfo.Get_SDKIsAudioOnly(),sdkinfo.Get_SDKVer())
            ArchiveManager.Get().ArchiveBuild(dst_zip_file_path, OneArchiveInfo)
        

 
    def CleanPlugin(self,Args,bFullClean = False):
        path_plugin_archive_dir = Path(self.GetPath_PluginArchiveDir())
        path_plugin_tmp_dir = Path(self.GetPath_PluginTmpDir())

        sdkinfo = AgoraSDKInfo(Args.agorasdk,Args.sdkisaudioonly)

        ## git repo
        git_url = Args.giturl
        repo_name = git_url.split('/')[-1].split('.')[0]

        ## clean target archive plugin
        path_final_plugin_archive_placed_dir = self.GetPath_FinalPluginArchivePlacedDir(path_plugin_archive_dir,sdkinfo)
        FileUtility.DeleteDir(path_final_plugin_archive_placed_dir)
        
        ## clean plugin tmp files
        if bFullClean == True:
            FileUtility.DeleteDir(path_plugin_tmp_dir)
        else:
            ## path_plugin_tmp_dir / [Name_FinalPluginFileTmpDir]
            ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginTemp] / [tmp_plugin_files]
            ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginTemp] / [Android]
            ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginTemp] / [Android_TO_BE_DELETED]

            FileUtility.DeleteDir(self.GetPath_FinalPluginFileTmpDir())
            delete_dir_list =["Android","IOS","Mac","Win"]
            for dir in delete_dir_list:
                FileUtility.DeleteDir(path_plugin_tmp_dir / Path(dir))
                FileUtility.DeleteDir(path_plugin_tmp_dir / Path(dir +  self.GetName_PluginTmpSortSuffixName()))

    def ModifyCompileOptions(self,src_file):

        additional_compile_options = " -Wno-unused-but-set-variable -Wno-gcc-compat -Wno-reorder-ctor  -Wno-deprecated-builtins -Wno-single-bit-bitfield-constant-conversion -Wno-nonportable-include-path "
        file_path = str(src_file)

        with open(file_path,'r') as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            if 'AdditionalCompilerArguments' in line:
                line = "            Inner.AdditionalCompilerArguments += "+ '"' + additional_compile_options + '";\n'
            new_lines.append(line)
        
        with open(file_path,'w') as file:
            file.writelines(new_lines)


    def ModifyFiles(self,IsAudioOnly,val_file_path):
        is_audioonly_sdk = IsAudioOnly
        # file_path = Path("/Users/admin/Documents/Unreal Projects/Agora-Unreal-RTC-SDK-dev-4.2.1/Agora-Unreal-SDK-CPP-Example/Plugins/AgoraPlugin/Source/AgoraPlugin/AgoraPlugin.Build.cs")
        file_path = str(val_file_path)

        with open(file_path,'r') as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            if 'bIsAudioOnlySDK' in line:
                if is_audioonly_sdk:
                    line = line.replace('false','true')
                else:
                    line = line.replace('true','false')
            new_lines.append(line)
        
        with open(file_path,'w') as file:
            file.writelines(new_lines)

    def UpdateUpluginFile(self,uplugin_file_path,Args):
        # file_path = Path("/Users/admin/Documents/PluginTemp/Agora-Unreal-RTC-SDK/PluginTmp/tmp_plugin_files/AgoraPlugin/AgoraPlugin.uplugin")
        # UPLUGIN_FILE = "AgoraPlugin.uplugin"

        sdk_version = Args.agorasdk
        min_engine_version = Args.mminenginever
        support_platforms = Args.msupportplatforms
        marketplace_url = Args.mmarketplaceurl
        msupporturl = Args.msupporturl
        sdkinfo  = AgoraSDKInfo(Args.agorasdk,Args.sdkisaudioonly,Args.agorasdktype)
        val_description = "Agora UE Plugin: %s " %(sdkinfo.ToString())

        support_platforms = support_platforms.split("+")


        ## unused: just an example for reference view
        ## [###] means it would be modified
        ## modules are controlled by the source file
        unused_template_arr = {
            "FileVersion": 3,
            "Version": 1,
            "VersionName": "4.2.1", ####
            "FriendlyName": "AgoraPlugin",
            "EngineVersion": "", ###
            "Description": "develop", ###
            "Category": "Other",
            "CreatedBy": "Agora",
            "CreatedByURL": "",
            "DocsURL": "",
            "MarketplaceURL": "", ###
            "SupportURL": "https://www.agora.io/en/", ###
            "CanContainContent": True,
            "IsBetaVersion": False,
            "IsExperimentalVersion": False,
            "Installed": False,
            "WhitelistPlatforms":["Win64","Mac","IOS","Android"], ###
            "Modules": [
                {
                    "Name": "AgoraUtilityHelper",
                    "Type": "Runtime",
                    "LoadingPhase": "Default",
                    "PlatformAllowList":["Win64","Mac","IOS","Android"] ###
                },
                {
                    "Name": "AgoraPlugin",
                    "Type": "Runtime",
                    "LoadingPhase": "Default",
                    "PlatformAllowList":["Win64","Mac","IOS","Android"] ###
                }
            ]
        }

        ## read data from the original uplugin file
        template_arr = unused_template_arr
        with open(uplugin_file_path, 'r', encoding='utf-8') as file:
            PrintLog(f"Loading uplugin from file {uplugin_file_path} ...... ")
            template_arr = json.load(file)

        ### Modification

        template_arr['VersionName'] = sdk_version

        bNeedSetEngineVersion = Args.setenginever
        if bNeedSetEngineVersion:
            ## it would influence the BP example
            template_arr['EngineVersion'] = min_engine_version

        template_arr['Description'] = val_description

        if marketplace_url != "":
            template_arr['MarketplaceURL'] = marketplace_url

        if msupporturl != "":
            template_arr['SupportURL'] = msupporturl

        template_arr['WhitelistPlatforms'] = support_platforms
        # template_arr['Modules'][0]['PlatformAllowList'] = support_platforms

        for module in template_arr["Modules"]:
            module["PlatformAllowList"] = support_platforms

        ###

        uplugin_json_str = json.dumps(template_arr, sort_keys=False, indent=4, separators=(',', ': '))
        print(uplugin_json_str)

        ### Save The File
        with open(str(uplugin_file_path),'w') as file:
            file.write(uplugin_json_str)


    def DoMacRATrustTask(self,path_project,password = ""):
        if self.GetHostPlatform() == "Mac":
            OneMacRATrustCommand= MacRATrustCommand()
            OneMacRATrustCommand.DoMacTrust(path_project,"",password)

    def RemoveSymbolicLink(self,mac_framework_path):
        framework_list = Path(mac_framework_path).glob('*')
        for framework_dir in framework_list:
            framework_path = Path(framework_dir)
            tmp_name =  framework_path.name + self.GetName_PluginTmpSortSuffixName()
            tmp_dir_for_sort = framework_path.parent / tmp_name
            if tmp_dir_for_sort.exists():
                FileUtility.DeleteDir(tmp_dir_for_sort)
            tmp_dir_for_sort.mkdir(parents=True,exist_ok=True)
            FileUtility.CopyDir(framework_path,tmp_dir_for_sort,False)
            FileUtility.DeleteDir(framework_path)
            framework_path.mkdir(parents=True,exist_ok=True)
            FileUtility.CopyDir(tmp_dir_for_sort,framework_path,False)
            FileUtility.DeleteDir(tmp_dir_for_sort)


    def DownloadAgoraSDKPlugin(self,target_sdkinfo:AgoraSDKInfo,dst_path,bkeep_symlink = True):
        plugin_url =ConfigParser.Get().GetRTCSDKURL(target_sdkinfo)
        self.DownloadPlugin(plugin_url,dst_path,bkeep_symlink)

    def DownloadPlugin(self,url_zipfile,dst_path,bkeep_symlink = True):
        name_zipfile = url_zipfile.split('/')[-1]
        tmp_download_dir = Path(dst_path) / self.GetName_PluginTmpDownloadDir()
        
        if tmp_download_dir.exists() == True:
            FileUtility.DeleteDir(tmp_download_dir)
        tmp_download_dir.mkdir(parents= True, exist_ok= True)
        
        plugin_zip_path = tmp_download_dir / name_zipfile
        FileDownloader.DownloadWithRequests(url_zipfile,plugin_zip_path)
        
        self.UnZipAndCopySDKToDstPath(plugin_zip_path,dst_path,bkeep_symlink)
        FileUtility.DeleteDir(tmp_download_dir)


    def QueryAndCopySDKToDstPath(self,target_sdkinfo:AgoraSDKInfo,dst_path,bkeep_symlink = True):
        ## Copy Agora SDK Plugin to Dst Path (UE Project)

        ## Search SDK
        path_plugin_zip = self.GetPath_QueryPluginZipFile(target_sdkinfo)

        self.UnZipAndCopySDKToDstPath(path_plugin_zip,dst_path,bkeep_symlink)

   
    def GetPath_QueryPluginZipFile(self,target_sdkinfo:AgoraSDKInfo,bforce_redownload = False, bforce_search_in_working_dir = False):
        
        result_plugin_path = None
        bfounded = False
        ## 1. >>> Check in Plugin Repo <<< 
        ### Use Archived Plugin in Plugin Repo 
        ### Ex. /Users/admin/Documents/PluginRepo
        default_plugin_repo_path = Path(ConfigParser.Get().GetDefaultPluginRepo())
        default_plugin_repo_path.mkdir(parents= True, exist_ok= True)

        url = ConfigParser.Get().GetRTCSDKURL(target_sdkinfo)
        PrintLog("[GetPlugin] Find The Plugin URL [%s] with SDKInfo[%s]" % (url,target_sdkinfo.ToString()))

        ## because the repo only has downloaded plugins with the url provided.
        if url != "" and bforce_search_in_working_dir == False:
            ## Ex. "https://download.agora.io/sdk/release/Agora_RTC_Full_SDK_4.2.1_Unreal.zip"
            plugin_name = url.split('/')[-1]
            ## Ex. /Users/admin/Documents/PluginRepo/4.2.1/   (Create 4.2.1 First)
            path_final_plugin_placed_dir = self.GetPath_FinalPluginArchivePlacedDir(default_plugin_repo_path,target_sdkinfo)
            plugin_path = path_final_plugin_placed_dir / plugin_name


            if plugin_path.exists() == True and bforce_redownload == False:
                result_plugin_path = plugin_path
                bfounded = True
                PrintLog("[GetPlugin] Use Existing Plugin[%s]" % str(result_plugin_path))

            ## 2. >>>> Download with URL
            else:
                ## Need to use sync_download
                if plugin_path.exists() == True:
                    plugin_path.unlink()
                FileDownloader.DownloadWithRequests(url,plugin_path)
                result_plugin_path = plugin_path
                bfounded = True
                PrintLog("[GetPlugin] Download The Plugin[%s] With URL[%s]" % (str(result_plugin_path),url))

        else:
            ## could not be founded in our sdk config
            ## 3. >>> Check the plugin in our work dir <<<
            plugin_working_dir = self.GetName_PluginWorkingDir()
            plugin_archive_dir = self.GetName_PluginArchive()

            cur_path = Path(__file__).parent.absolute()
            root_plugin_gen_path = cur_path.parent / plugin_working_dir

            dst_zip_file_path = self.GetPath_FinalPluginArchivePlacedDir((root_plugin_gen_path / plugin_archive_dir),target_sdkinfo)

            for item in dst_zip_file_path.glob("*.zip"):
                result_plugin_path = dst_zip_file_path / item
                bfounded = True
                PrintLog("[GetPlugin] Search Plugin in WorkingDir [%s] " % (result_plugin_path))
                break

        if bfounded == False:
            PrintErr("[GetPlugin] Plugin Not Founded ")

        return result_plugin_path
    

    def UnZipAndCopySDKToDstPath(self,src_path_zipfile,dst_path,bkeep_symlink = True):
        ## src path: an agora plugin zip file full path
        ## dst path: ue project's plugins folder
        
        ## Prepare Src Path:
        ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1] / [UnzipPluginAgoraPlugin]
        src_path_zipfile = Path(src_path_zipfile)
        dst_path = Path(dst_path)

        OneZipCommand =ZipCommand()
        unzip_path = src_path_zipfile.parent / Path("UnzipPlugin" + src_path_zipfile.stem)
        if unzip_path.exists() == True:
            FileUtility.DeleteDir(str(unzip_path))
        OneZipCommand.UnZipFile(src_path_zipfile ,unzip_path)

        ## [path_plugin] / [name_plugin].uplugin
        ## Ex. AgoraPlugin , [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1]/[UnzipPluginAgoraPlugin] / Agora_RTC_Full_SDK_4.2.1_Unreal /  AgoraPlugin / AgoraPlugin.uplugin
        name_plugin,path_plugin = UBSHelper.Get().GetInfo_PluginNameAndUPluginFilePath(unzip_path)

        ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1]/[UnzipPluginAgoraPlugin] / (plugin_name)[Agora_RTC_Full_SDK_4.2.1_Unreal] /  AgoraPlugin
        src_plugin_path = Path(path_plugin.parent)

        ## Prepare Dst Path:
        ## Ex. (UEProject)[/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example] / [AgoraPlugin]
        dst_plugin_path = dst_path / name_plugin
        if dst_plugin_path.exists() == True:
            FileUtility.DeleteDir(str(dst_plugin_path))
        dst_plugin_path.mkdir(parents= True, exist_ok= True)

        PrintLog("[CopyPlugin] Src Path: [%s] to Dst Path [%s] " % (str(src_plugin_path) , str(dst_plugin_path)))
        FileUtility.CopyDir(src_plugin_path,dst_plugin_path,bkeep_symlink)

        FileUtility.DeleteDir(str(unzip_path))



###### For UE Marketplace #####
    def GenRenamedPluginSrcFiles(self,path_root_repo,old_plugin_name,new_plugin_name):

        path_src_dir = path_root_repo / str(old_plugin_name)
        path_dst_dir = path_root_repo / str(new_plugin_name)

        extensions = ['.cpp', '.h', '.cs', '.uplugin']

        # pattern02: [content_replacements]: [old , new] replace the old one with the new one
        content_replacements = {
            'AgoraPlugin': 'AgoraVoicePlugin',
            'AGORAPLUGIN_API': 'AGORAVOICEPLUGIN_API',
            'FAgoraPluginModule': 'FAgoraVoicePluginModule'
        }

        # pattern03: [name_replacements] [old , new] replace the old one with the new one
        name_replacements = {
            'AgoraPlugin': 'AgoraVoicePlugin'
        }


        exclude_path01 = path_dst_dir / "Source/AgoraVoicePlugin/Public/AgoraCppPlugin/include"
        

        exclude_paths = [exclude_path01]

        APMHelper.Get().CopyDirWithContentReplaced(path_src_dir,path_dst_dir,extensions,content_replacements,name_replacements,exclude_paths)




    def GenUEMarketplacePlugins(self,Args):
        
        path_root_ue_marketplace_archive_dir = self.GetPath_PluginUEMarketplaceArchiveDir()

        if Args.archiveplugin:
            sdk_version = Args.agorasdk
            path_root_ue_marketplace_archive_dir = ArchiveManager.Get().GetPath_TargetArchiveDir(ArchiveInfo_AgoraPluginMarketplace(sdk_version))
            PrintLog(f"Notice! ArchivePlugin Eanbled, Root Path Changed {path_root_ue_marketplace_archive_dir}")

        target_enginelist = ['5.4.0','5.3.0','5.2.0']
        if Args.MarketplacePluginEngineList != "":
            target_enginelist = str(Args.MarketplacePluginEngineList).split('+')

        gen_configs = {
            "FullSDK": {
                "enginelist":target_enginelist,
                "issdkaudioonly":False,
                "filename":"Agora_RTC_FULL_SDK_#_Unreal",
                "pluginname":"AgoraPlugin"
            },
            "VoiceSDK":{
                "enginelist":target_enginelist,
                "issdkaudioonly":False,
                "filename":"Agora_RTC_VOICE_SDK_#_Unreal",
                "pluginname":"AgoraVoicePlugin"
            }
        }

        for key_one_config ,val_one_config in gen_configs.items():
            path_one_config = Path(path_root_ue_marketplace_archive_dir)/ str(key_one_config)
            if path_one_config.exists():
                FileUtility.DeleteDir(path_one_config)
            path_one_config.mkdir(exist_ok=True,parents=True)

            bfirst_time = True
            for one_engine_ver in val_one_config['enginelist']:
                path_one_gen_plugin = path_one_config / Path(str(one_engine_ver))
                if path_one_gen_plugin.exists():
                    FileUtility.DeleteDir(path_one_gen_plugin)
                path_one_gen_plugin.mkdir(exist_ok=True,parents=True)
                

                sdkinfo = AgoraSDKInfo(Args.agorasdk,val_one_config['issdkaudioonly'])

                one_time_args = copy.deepcopy(Args)

                one_time_args.setenginever = True
                one_time_args.mminenginever = one_engine_ver
                one_time_args.pluginarchivedir = str(path_one_gen_plugin)
                zip_filename = val_one_config['filename']
                zip_filename = str(zip_filename).replace('#',sdkinfo.Get_SDKVer())
                one_time_args.pluginfiledisplayname = zip_filename
            

                git_url = Args.giturl
                repo_name = git_url.split('/')[-1].split('.')[0]
                path_root_repo = self.GetPath_PluginWorkingDir() / repo_name / "Agora-Unreal-SDK-CPP"
                plugin_name = str(val_one_config['pluginname'])
                target_plugin_src_code_path = path_root_repo / plugin_name
                one_time_args.pluginsourcecodepath = target_plugin_src_code_path
                PrintLog(f"Plugin Src Code Path: {target_plugin_src_code_path}")
                one_time_args.pluginname = plugin_name

                one_time_args.archiveplugin = False

                if bfirst_time == True:
                    one_time_args.skipgit = True
                    one_time_args.skipnativedownload = True                    
                    
                    original_plugin_name = "AgoraPlugin"
                    cur_plugin_name = val_one_config['pluginname'] 
                    if cur_plugin_name != original_plugin_name:
                        self.GenRenamedPluginSrcFiles(path_root_repo,original_plugin_name,cur_plugin_name)

                    bfirst_time = False

                else:
                    one_time_args.skipgit = True
                    one_time_args.skipnativedownload = True 
                
                
                PrintStageLog(f"Gen One Plugin Config[{key_one_config}] Engine[{one_engine_ver}]")
                dst_zip_file_path = self.GetPath_PluginArchiveDir()
                path_final_plugin_file = self.GetPath_FinalPluginArchivePlacedDir(dst_zip_file_path,sdkinfo)

                self.StartGenPlugin(one_time_args)
                FileUtility.CopyDir(path_final_plugin_file,path_one_gen_plugin)
                PrintLog(f"Check Args {one_time_args}")
                
                PrintStageLog(f"Complete Gen One Plugin Config[{key_one_config}] Engine[{one_engine_ver}]")

###### For UE Marketplace #####

if __name__ == '__main__':
    AgoraPluginManager.Get().Start()
    # AgoraPluginManager.Get().Init()
    # AgoraPluginManager.Get().DownloadAgoraSDKPlugin("/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/Plugins","4.2.1",False)