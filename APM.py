


from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *
from Utility.Downloader import *

from Command.GitCommand import *
from Command.ZipCommand import *
from Command.MacRATrustCommand import *
from Utility.VersionControlTool import *

from SystemBase import *

import argparse

import platform

class AgoraPluginManager(BaseSystem):

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
        ArgParser.add_argument("-sdkisaudioonly",default=False)
        ArgParser.add_argument("-skipnativedownload",action='store_true')
        ArgParser.add_argument("-skipgit",action='store_true')
        ArgParser.add_argument("-rmmacslink",action='store_true') # remove mac symbolic link
        ArgParser.add_argument("-agorasdkbuildconfig", default="Release")
        ArgParser.add_argument("-pluginname", default="AgoraPlugin")
        ArgParser.add_argument("-giturl", default= "git@github.com:AgoraIO-Extensions/Agora-Unreal-RTC-SDK.git")

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
        ArgParser.add_argument("-msupportplatforms", default="Win64+Mac+IOS+Android") 

        if bIncludeConflictArgs:
            pass

    ## PluginWorkingDir
    ## -- PluginTemp
    ## ----- tmp_plugin_files
    ## -- PluginArchive
    def Get_PluginWorkingDir(self):
        return "PluginWorkDir"
    def Get_PluginTmpFileDir(self):
        return "PluginTemp"
    def Get_FinalPluginFileDir(self):
        return "tmp_plugin_files"
    def Get_PluginArchive(self):
        return "PluginArchive"
    def Get_PluginTmpSortSuffixName(self):
        return "_To_BE_DELETED"

    def Get_FinalPluginPlacedDir(self,root_plugin_archive_path,sdk_ver,is_audio_only):
        path_category01 = Path(root_plugin_archive_path) / Path(sdk_ver)
        if not path_category01.exists():
            path_category01.mkdir(parents=True)
        
        category02 = "Full" if not is_audio_only else "AudioOnly"
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
   
        self.StartGenPlugin(Args)

    def StartGenPlugin(self,Args):

        AgoraPluginManager.Get().CleanPlugin(Args)
        PLUGIN_NAME = Args.pluginname

        git_url = Args.giturl
    
        sdk_ver = Args.agorasdk

        sdk_mode_type = Args.agorasdkbuildconfig

        bis_audio_only = Args.sdkisaudioonly

        bis_mac_remove_symbolic_link =Args.rmmacslink

        plugin_working_dir = self.Get_PluginWorkingDir()
        plugin_tmp_file_dir = self.Get_PluginTmpFileDir()
        plugin_tmp_sort_dir_suffix_name = self.Get_PluginTmpSortSuffixName()
        final_plugin_file_dir = self.Get_FinalPluginFileDir() 
        plugin_archive_dir = self.Get_PluginArchive()

        # url_windows = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/windows/full/Agora_Native_SDK_for_Windows_rel.v4.2.1_21296_FULL_20230727_1707_272784.zip"
        # url_mac = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/mac/full/Agora_Native_SDK_for_Mac_rel.v4.2.1_46142_FULL_20230727_1549_272786.zip"
        # url_android = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/android/full/Agora_Native_SDK_for_Android_rel.v4.2.1_51720_FULL_20230727_1552_272785.zip"
        # url_ios = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/ios/full/Agora_Native_SDK_for_iOS_rel.v4.2.1_65993_FULL_20230727_1551_272787.zip"

        # url_ios="https://download.agora.io/sdk/release/Agora_Native_SDK_for_iOS_rel.v4.0.0.2_56070_FULL_20220803_2250_225057.zip"
        # url_android="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Android_rel.v4.0.0.2_38413_FULL_20220803_2250_225055.zip"
        # url_mac="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Mac_rel.v4.0.0.2_41396_FULL_20220803_2256_225058.zip"
        # url_windows="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Windows_rel.v4.0.0.2_15884_FULL_20220803_2250_225056.zip"
        

        bskip_download_native_sdk = Args.skipnativedownload
        

        
        url_ios = ConfigParser.Get().GetRTCSDKNativeURL_IOS(sdk_ver) if Args.nurlios == "" else Args.nurlios  
        url_android = ConfigParser.Get().GetRTCSDKNativeURL_Android(sdk_ver) if Args.nurlandroid == "" else Args.nurlandroid
        url_windows = ConfigParser.Get().GetRTCSDKNativeURL_Win(sdk_ver) if Args.nurlwin == "" else Args.nurlwin
        url_mac = ConfigParser.Get().GetRTCSDKNativeURL_Mac(sdk_ver) if Args.nurlmac == "" else Args.nurlmac
        
        
        cur_path = Path(__file__).parent.absolute()
        PrintLog(cur_path)

        root_plugin_gen_path = cur_path.parent / plugin_working_dir
        repo_path = root_plugin_gen_path

  
        

        OneGitCommand = GitCommand()
        VersionControlTool.Init(OneGitCommand)

        if Args.skipgit == False:
            VersionControlTool.CheckOutOneRepo(git_url,repo_path)

        repo_name = git_url.split('/')[-1].split('.')[0]
        repo_path = repo_path / repo_name

        ### [TBD] these are 2 Async Jobs (git & download ), they need to be synced.
        plugin_tmp_path = root_plugin_gen_path / plugin_tmp_file_dir
        platform_list = [
            {"platform": "Win","url":url_windows}, 
            {"platform": "Mac","url":url_mac},
            {"platform": "Android","url":url_android},
            {"platform": "IOS","url":url_ios}
        ]

        ## Delete Plugin Folder if exists

        plugin_tmp_path.mkdir(parents= True, exist_ok= True)
        for plugin_cfg in platform_list:
            print(plugin_cfg)
            plugin_name = plugin_cfg['url'].split('/')[-1]
            plugin_path = plugin_tmp_path / plugin_name
            
            if bskip_download_native_sdk != True:
                if plugin_path.exists() == True:
                    plugin_path.unlink()
                FileDownloader.DownloadWithRequests(plugin_cfg['url'],plugin_path)

            OneZipCommand =ZipCommand(self.GetHostPlatform())
            tmp_copy_dst_path = plugin_tmp_path / plugin_cfg["platform"]
            tmp_copy_dst_path.mkdir(parents=True,exist_ok= True)
            OneZipCommand.UnZipFile(plugin_path,tmp_copy_dst_path)
            tmp_copy_file_list = list(tmp_copy_dst_path.glob('*'))
            ## just make [platform] -> [content]
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
                    
        ##
        target_plugin_dst_path = plugin_tmp_path / final_plugin_file_dir / PLUGIN_NAME
        target_plugin_dst_path.mkdir(parents= True, exist_ok= True)
        target_plugin_src_code_path = repo_path / "Agora-Unreal-SDK-CPP" / PLUGIN_NAME
        target_plugin_src_lib_path = plugin_tmp_path
        ## change dst here

        ## Copy Repo[Agora-Unreal-SDK-CPP]/PLUGIN to Dst
        target_plugin_dst_lib_path = target_plugin_dst_path / "Source"/ "ThirdParty" / "AgoraPluginLibrary"
        print(target_plugin_src_code_path)
        print(target_plugin_dst_path)
        shutil.copytree(target_plugin_src_code_path,target_plugin_dst_path,dirs_exist_ok= True)


        ###### Modify Android Template Here ###### 
        path_android_tmpl_src = target_plugin_dst_lib_path / "Android" / "Release"
        filename_full_tmpl = "APL_armv7TemplateFULL.xml"
        filename_voice_tmpl = "APL_armv7TemplateVoice.xml"
        filename_src_tmpl = filename_full_tmpl if bis_audio_only == False else filename_voice_tmpl
        filename_target_tmpl = "APL_armv7Template.xml"
        shutil.copy(path_android_tmpl_src / filename_src_tmpl,path_android_tmpl_src / filename_target_tmpl)

        original_src = target_plugin_src_lib_path
        original_dst = target_plugin_dst_lib_path

        for plugin_cfg in platform_list:
            target_plugin_dst_lib_path = target_plugin_dst_lib_path / plugin_cfg["platform"] / sdk_mode_type
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

            count_architecture = len(architecture_list)
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

                PrintLog(" from %s ---> %s " %(target_plugin_src_lib_path , target_plugin_dst_lib_path))
                
                if plugin_cfg["platform"] == "Mac" and bis_mac_remove_symbolic_link == True:
                    FileUtility.CopyFilesWithSymbolicLink(target_plugin_src_lib_path,target_plugin_dst_lib_path,"RLf")
                else:
                    FileUtility.CopyFilesWithSymbolicLink(target_plugin_src_lib_path,target_plugin_dst_lib_path,"PRfa")
                
                if plugin_cfg["platform"] == "IOS":
                    all_framework_path_list = [ dir for dir in target_plugin_dst_lib_path.glob('*') if dir.is_dir()] 
                    for framework_dir in all_framework_path_list:
                        
                        ## Example: A.framework -> A.embeddedframework/A.framework
                        ## A.embeddedframework/A.framework ->  A.embeddedframework.zip
                        framework_name = framework_dir.stem
                        embeddedframework_path = framework_dir.parent / Path(str(framework_name) + ".embeddedframework")
                        embeddedframework_path.mkdir(parents= True, exist_ok= True)
                        framework_dir.rename( embeddedframework_path / framework_dir.name)


                        zip_framework_name = Path(embeddedframework_path).name
                        dst_framework_path = target_plugin_dst_lib_path / (zip_framework_name + ".zip")
                        OneZipCommand.ZipFile(zip_framework_name,dst_framework_path,target_plugin_dst_lib_path)
                        FileUtility.DeleteDir(embeddedframework_path)
            ## shutil.copytree(str(target_plugin_src_lib_path),str(target_plugin_dst_lib_path),dirs_exist_ok= True)
            target_plugin_src_lib_path = original_src ##
            target_plugin_dst_lib_path = original_dst
         

        

        ## Modify Files Here
        bmodify_compile_options = Args.mmodifycompileoptions
        self.UpdateUpluginFile(target_plugin_dst_path / Path( PLUGIN_NAME+ ".uplugin"),Args)
        if bmodify_compile_options:
            self.ModifyCompileOptions(target_plugin_dst_path / Path("Source") / Path(PLUGIN_NAME) /Path( PLUGIN_NAME+ ".Build.cs"))
        self.ModifyFiles(bis_audio_only,target_plugin_dst_path / Path("Source") / Path(PLUGIN_NAME) /Path( PLUGIN_NAME+ ".Build.cs"))
        ## Modify Files Here

        src_zip_files_root_path = target_plugin_dst_path.parent
        dst_zip_file_path = root_plugin_gen_path / plugin_archive_dir
        dst_zip_file_path.mkdir(parents= True, exist_ok= True)
        dst_zip_file_path = self.Get_FinalPluginPlacedDir(dst_zip_file_path,sdk_ver,bis_audio_only)
        dst_zip_file_path = dst_zip_file_path / (PLUGIN_NAME + ".zip")
        OneZipCommand.ZipFile(PLUGIN_NAME,dst_zip_file_path,src_zip_files_root_path)
        

        PrintLog(">>>> Final Product Path: " + str(dst_zip_file_path))

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


    def UpdateUpluginFile(self,file_path,Args):
        # file_path = Path("/Users/admin/Documents/PluginTemp/Agora-Unreal-RTC-SDK/PluginTmp/tmp_plugin_files/AgoraPlugin/AgoraPlugin.uplugin")
        # UPLUGIN_FILE = "AgoraPlugin.uplugin"

        sdk_version = Args.agorasdk
        min_engine_version = Args.mminenginever
        support_platforms = Args.msupportplatforms
        marketplace_url = Args.mmarketplaceurl

        support_platforms = support_platforms.split("+")

        template_arr = {
            "FileVersion": 3,
            "Version": 1,
            "VersionName": "4.2.1", ####
            "FriendlyName": "AgoraPlugin",
            "EngineVersion": "5.3.0", ###
            "Description": "develop",
            "Category": "Other",
            "CreatedBy": "Agora",
            "CreatedByURL": "",
            "DocsURL": "",
            "MarketplaceURL": "", ###
            "SupportURL": "https://www.agora.io/en/",
            "CanContainContent": True,
            "IsBetaVersion": False,
            "IsExperimentalVersion": False,
            "Installed": False,
            "WhitelistPlatforms":["Win64","Mac","IOS","Android"],
            "Modules": [
                {
                    "Name": "AgoraPlugin",
                    "Type": "Runtime",
                    "LoadingPhase": "Default",
                    "PlatformAllowList":["Win64","Mac","IOS","Android"]
                }
            ]
        }


        ### Modification

        template_arr['VersionName'] = sdk_version
        template_arr['EngineVersion'] = min_engine_version
        if marketplace_url != "":
            template_arr['MarketplaceURL'] = marketplace_url
        template_arr['WhitelistPlatforms'] = support_platforms
        template_arr['Modules'][0]['PlatformAllowList'] = support_platforms

        ### 

        uplugin_json_str = json.dumps(template_arr, sort_keys=False, indent=4, separators=(',', ': '))
        print(uplugin_json_str)

        ### Save The File
        with open(str(file_path),'w') as file:
            file.write(uplugin_json_str)


    def CleanPlugin(self,Args):
        cur_path = Path(__file__).parent.absolute()
        PrintLog(cur_path)

        plugin_working_dir = self.Get_PluginWorkingDir()
        plugin_tmp_file_dir = self.Get_PluginTmpFileDir()
        final_plugin_file_dir = self.Get_FinalPluginFileDir()
        plugin_archive_dir =  self.Get_PluginArchive()
        plugin_tmp_sort_dir_suffix_name = self.Get_PluginTmpSortSuffixName()

        sdk_ver =  Args.agorasdk
        bis_audio_only = Args.sdkisaudioonly

        root_plugin_gen_path = cur_path.parent / plugin_working_dir
        repo_path = root_plugin_gen_path

        git_url = Args.giturl
        repo_name = git_url.split('/')[-1].split('.')[0]

        bFullDelete = False
        path_target_plugin_placed_dir = self.Get_FinalPluginPlacedDir(root_plugin_gen_path / Path(plugin_archive_dir),sdk_ver,bis_audio_only)
        FileUtility.DeleteDir(path_target_plugin_placed_dir)
        plugin_tmp_path = root_plugin_gen_path / plugin_tmp_file_dir

        if bFullDelete == True:
            FileUtility.DeleteDir(plugin_tmp_path)
        else:
            delete_dir_list =["Android","IOS","Mac","Win",final_plugin_file_dir]
            for dir in delete_dir_list:
                FileUtility.DeleteDir(plugin_tmp_path / Path(dir))
                if dir != final_plugin_file_dir:
                    FileUtility.DeleteDir(plugin_tmp_path / Path(dir + plugin_tmp_sort_dir_suffix_name))

    def DownloadAgoraSDKPlugin(self,dst_path,sdk_ver,is_audio_only,bkeep_symlink = True):
        plugin_url =ConfigParser.Get().GetRTCSDKURL(sdk_ver,is_audio_only)
        self.DownloadPlugin(plugin_url,dst_path,bkeep_symlink)

    def DownloadPlugin(self,plugin_url,dst_path,bkeep_symlink = True):
        plugin_name = plugin_url.split('/')[-1]
        tmp_download_dir = Path(dst_path) / Path(plugin_name).stem
        if tmp_download_dir.exists() == True:
            FileUtility.DeleteDir(tmp_download_dir)

        tmp_download_dir.mkdir(parents= True, exist_ok= True)
        
        plugin_zip_path = tmp_download_dir / plugin_name
        FileDownloader.DownloadWithRequests(plugin_url,plugin_zip_path)
        OneZipCommand = ZipCommand(self.GetHostPlatform())
        OneZipCommand.UnZipFile(plugin_zip_path,tmp_download_dir)

        self.MovePluginToDstPath(tmp_download_dir,dst_path,bkeep_symlink)
        FileUtility.DeleteDir(tmp_download_dir)
    
    def MovePluginToDstPath(self,src_working_dir,dst_path,bkeep_symlink = True):
        uplugin_files = list(Path(src_working_dir).rglob("*.uplugin"))
        plugin_path = ""
        plugin_name = ""
        for uplugin_file in uplugin_files:
            if "__MACOSX" in str(uplugin_file):
                    pass
            else:
                final_uplugin_path = Path(uplugin_file)
                plugin_name = Path(final_uplugin_path).stem
                PrintLog("Find the uplugin name [%s] file path: [%s] " % (plugin_name , str(final_uplugin_path)))
                plugin_path = Path(final_uplugin_path).parent
                if plugin_name != plugin_path.name:
                    PrintErr("The Plugin Folder Name [%s] is not equal to uplugin file name [%s]" %( plugin_path.name,plugin_name))

        plugin_dst_path = Path(dst_path) / plugin_name
        if plugin_dst_path.exists() == True:
            FileUtility.DeleteDir(plugin_dst_path)

        plugin_dst_path.mkdir(parents= True, exist_ok= True)

        if bkeep_symlink :
            FileUtility.CopyFilesWithSymbolicLink(plugin_path,plugin_dst_path,"PRfa")
        else:
            FileUtility.CopyFilesWithSymbolicLink(plugin_path,plugin_dst_path,"RLf")

    def RemoveSymbolicLink(self,mac_framework_path):
        framework_list = Path(mac_framework_path).glob('*')
        for framework_dir in framework_list:
            framework_path = Path(framework_dir)
            tmp_name =  framework_path.name + "tmp"
            tmp_dir_for_sort = framework_path.parent / tmp_name
            if tmp_dir_for_sort.exists():
                FileUtility.DeleteDir(tmp_dir_for_sort)
            tmp_dir_for_sort.mkdir(parents=True,exist_ok=True)
            FileUtility.CopyFilesWithSymbolicLink(framework_path,tmp_dir_for_sort,"RLf")
            FileUtility.DeleteDir(framework_path)
            framework_path.mkdir(parents=True,exist_ok=True)
            FileUtility.CopyFilesWithSymbolicLink(tmp_dir_for_sort,framework_path,"RLf")
            FileUtility.DeleteDir(tmp_dir_for_sort)

    
    
    def GetPluginZipFilePathFromRepo(self,sdk_ver,bis_audio_only,bforce_redownload = False, bforce_search_in_working_dir = False):
        result_plugin_path = None
        bfounded = False
        ## 1. >>> Check in Plugin Repo <<< 
        ### Use Archived Plugin in Plugin Repo 
        ### Ex. /Users/admin/Documents/PluginRepo
        default_plugin_repo_path = Path(ConfigParser.Get().GetDefaultPluginRepo())
        default_plugin_repo_path.mkdir(parents= True, exist_ok= True)

        url = ConfigParser.Get().GetRTCSDKURL(sdk_ver,bis_audio_only)
        PrintLog("[GetPlugin] Find The Plugin URL [%s]" % url)

        ## because the repo only has downloaded plugins with the url provided.
        if url != "" and bforce_search_in_working_dir == False:
            ## Ex. "https://download.agora.io/sdk/release/Agora_RTC_Full_SDK_4.2.1_Unreal.zip"
            plugin_name = url.split('/')[-1]
            ## Ex. /Users/admin/Documents/PluginRepo/4.2.1/   (Create 4.2.1 First)
            path_final_plugin_placed_dir = self.Get_FinalPluginPlacedDir(default_plugin_repo_path,sdk_ver,bis_audio_only)
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
            plugin_working_dir = self.Get_PluginWorkingDir()
            plugin_archive_dir = self.Get_PluginArchive()

            cur_path = Path(__file__).parent.absolute()
            root_plugin_gen_path = cur_path.parent / plugin_working_dir

            dst_zip_file_path = self.Get_FinalPluginPlacedDir((root_plugin_gen_path / plugin_archive_dir) , sdk_ver, bis_audio_only)

            for item in dst_zip_file_path.glob("*.zip"):
                result_plugin_path = dst_zip_file_path / item
                bfounded = True
                PrintLog("[GetPlugin] Search Plugin in WorkingDir [%s] " % (result_plugin_path))
                break

        if bfounded == False:
            PrintErr("[GetPlugin] Plugin Not Founded ")

        return result_plugin_path
    
    def DoMacRATrustTask(self,project_path,password = ""):
        if self.GetHostPlatform() == "Mac":
            OneMacRATrustCommand= MacRATrustCommand()
            OneMacRATrustCommand.DoMacTrust(project_path,"",password)

    def CopySDKToDstPath(self,val_plugin_name,sdk_type,val_sdk_ver,val_is_audio_only,dst_path):
        ## Copy Agora SDK Plugin to Dst Path (UE Project)

        plugin_name = val_plugin_name
        plugin_sdk_ver = val_sdk_ver
        plugin_is_audio_only = val_is_audio_only
        plugin_path = self.GetPluginZipFilePathFromRepo(plugin_sdk_ver,plugin_is_audio_only)

        ## Prepare Dst Path:
        ## Ex. (UEProject)[/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example] / [AgoraPlugin]
        dst_plugin_path = dst_path / plugin_name

        if dst_plugin_path.exists() == True:
            FileUtility.DeleteDir(str(dst_plugin_path))
        dst_plugin_path.mkdir(parents= True, exist_ok= True)

        ## Prepare Src Path:
        ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1] / [UnzipPluginAgoraPlugin]
        OneZipCommand =ZipCommand(self.GetHostPlatform())
        unzip_path = plugin_path.parent / Path("UnzipPlugin" + plugin_path.stem)
        OneZipCommand.UnZipFile(plugin_path ,unzip_path)

        ## Suppose: Unzipped Folder would be [PluginName] (unzipped_folder_name == plugin_name)
        ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1]/[UnzipPluginAgoraPlugin] / (plugin_name)[Agora_RTC_Full_SDK_4.2.1_Unreal] /  AgoraPlugin
        src_plugin_path = unzip_path / plugin_name
        ## Ex. [/Users/admin/Documents/PluginWorkDir/PluginArchive/4.3.1]/[UnzipPluginAgoraPlugin] /  AgoraPlugin
        if src_plugin_path.exists() != True:
            src_plugin_path = unzip_path.parent / plugin_name
        PrintLog("Copy Src Path: [%s] to Dst Path [%s] " % (str(src_plugin_path) , str(dst_plugin_path)))
        shutil.copytree(str(src_plugin_path),str(dst_plugin_path),dirs_exist_ok= True)
        FileUtility.DeleteDir(str(unzip_path))
        

if __name__ == '__main__':
    AgoraPluginManager.Get().Start()
    # AgoraPluginManager.Get().Init()
    # AgoraPluginManager.Get().DownloadAgoraSDKPlugin("ddd","4.2.1",False)