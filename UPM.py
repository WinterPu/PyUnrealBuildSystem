


from Utility.HeaderBase import *
from ConfigParser import *
from Utility.UnrealProjectManager import *
from Utility.VersionControlTool import *
from Utility.Downloader import *

from Command.GitCommand import *
from Command.ZipCommand import *
from Utility.VersionControlTool import *

from SystemBase import *

import argparse

import platform

class AgoraPluginManager(BaseSystem):

    _instance = None
    _initialized = False
    git_url_src_files = ""

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

    def Init(self):
        PrintErr("AgoraPluginManager Init")
        PrintLog(" ====== Init =======")
        ConfigParser.Get().Init()
        self.git_url_src_files = "git@github.com:AgoraIO-Extensions/Agora-Unreal-RTC-SDK.git"

    def Start(self):
        pass
        
        AgoraPluginManager.Get().Init()

        AgoraPluginManager.Get().CleanPlugin()


        PLUGIN_NAME = "AgoraPlugin"

        git_url = self.git_url_src_files
    
        sdk_ver = "4.2.1"

        sdk_mode_type = "Release"

      
        # url_windows = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/windows/full/Agora_Native_SDK_for_Windows_rel.v4.2.1_21296_FULL_20230727_1707_272784.zip"
        # url_mac = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/mac/full/Agora_Native_SDK_for_Mac_rel.v4.2.1_46142_FULL_20230727_1549_272786.zip"
        # url_android = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/android/full/Agora_Native_SDK_for_Android_rel.v4.2.1_51720_FULL_20230727_1552_272785.zip"
        # url_ios = "http://10.80.1.174:8090/agora_sdk/4.2.1/official_build/2023-07-27/ios/full/Agora_Native_SDK_for_iOS_rel.v4.2.1_65993_FULL_20230727_1551_272787.zip"

        # url_ios="https://download.agora.io/sdk/release/Agora_Native_SDK_for_iOS_rel.v4.0.0.2_56070_FULL_20220803_2250_225057.zip"
        # url_android="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Android_rel.v4.0.0.2_38413_FULL_20220803_2250_225055.zip"
        # url_mac="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Mac_rel.v4.0.0.2_41396_FULL_20220803_2256_225058.zip"
        # url_windows="https://download.agora.io/sdk/release/Agora_Native_SDK_for_Windows_rel.v4.0.0.2_15884_FULL_20220803_2250_225056.zip"
        

        bReDownloadFile = False
        

        
        url_ios = ConfigParser.Get().GetRTCSDKNativeURL_IOS(sdk_ver)
        url_android = ConfigParser.Get().GetRTCSDKNativeURL_Android(sdk_ver)
        url_windows = ConfigParser.Get().GetRTCSDKNativeURL_Win(sdk_ver)
        url_mac = ConfigParser.Get().GetRTCSDKNativeURL_Mac(sdk_ver)
        
        
        cur_path = Path(__file__).parent.absolute()
        PrintLog(cur_path)

        root_plugin_gen_path = cur_path.parent / "PluginTemp"
        repo_path = root_plugin_gen_path

  
        

        OneGitCommand = GitCommand()
        VersionControlTool.Init(OneGitCommand)
        VersionControlTool.CheckOutOneRepo(git_url,repo_path)

        repo_name = git_url.split('/')[-1].split('.')[0]
        repo_path = repo_path / repo_name
        
        ### [TBD] these are 2 Async Jobs (git & download ), they need to be synced.
        repo_path = Path(repo_path)
        plugin_tmp_path = repo_path / "PluginTmp"
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
            
            if bReDownloadFile:
                if plugin_path.exists() == True:
                    plugin_path.unlink()
                FileDownloader.DownloadWithRequests(plugin_cfg['url'],plugin_path)

            OneZipCommand =ZipCommand(self.GetHostPlatform())
            tmp_copy_dst_path = plugin_tmp_path / plugin_cfg["platform"]
            tmp_copy_dst_path.mkdir(parents=True,exist_ok= True)
            OneZipCommand.UnZipFile(plugin_path,tmp_copy_dst_path)
            for path in tmp_copy_dst_path.iterdir():
                os.rename(str(path.absolute()), str(tmp_copy_dst_path / plugin_cfg["platform"]))

        
        ##
        target_plugin_dst_path = plugin_tmp_path / "tmp_plugin_files" / PLUGIN_NAME
        target_plugin_dst_path.mkdir(parents= True, exist_ok= True)
        target_plugin_src_code_path = repo_path / "Agora-Unreal-SDK-CPP" / PLUGIN_NAME
        target_plugin_src_lib_path = plugin_tmp_path
        ## change dst here
        target_plugin_dst_lib_path = target_plugin_dst_path / "Source"/ "ThirdParty" / "AgoraPluginLibrary"
        print(target_plugin_src_code_path)
        print(target_plugin_dst_path)
        shutil.copytree(target_plugin_src_code_path,target_plugin_dst_path,dirs_exist_ok= True)

        original_src = target_plugin_src_lib_path
        original_dst = target_plugin_dst_lib_path

        for plugin_cfg in platform_list:
            target_plugin_dst_lib_path = target_plugin_dst_lib_path / plugin_cfg["platform"] / sdk_mode_type
            Path(target_plugin_dst_lib_path).mkdir(parents= True, exist_ok= True)
            target_plugin_src_lib_path = target_plugin_src_lib_path / plugin_cfg["platform"] / plugin_cfg["platform"] ##

    
            if plugin_cfg["platform"] == "Mac":
                architecture = "macos-arm64_x86_64"
                target_plugin_src_lib_path = target_plugin_src_lib_path / Path("libs") / Path("*.xcframework") / Path(architecture)
            elif plugin_cfg["platform"] == "Win":
                target_plugin_src_lib_path = target_plugin_src_lib_path / Path("sdk/x86_64")
            elif plugin_cfg["platform"] == "Android":
                target_plugin_src_lib_path = target_plugin_src_lib_path / Path("rtc/sdk/")
            elif plugin_cfg["platform"] == "IOS":
                architecture = "ios-arm64_armv7"
                target_plugin_src_lib_path = target_plugin_src_lib_path / Path("libs/*.xcframework")/ Path(architecture)
            
            PrintLog(" from %s ---> %s " %(target_plugin_src_lib_path , target_plugin_dst_lib_path))
            
            FileUtility.CopyFilesWithSymbolicLink(target_plugin_src_lib_path,target_plugin_dst_lib_path,"PRfa")
            ## shutil.copytree(str(target_plugin_src_lib_path),str(target_plugin_dst_lib_path),dirs_exist_ok= True)
            target_plugin_src_lib_path = original_src ##
            target_plugin_dst_lib_path = original_dst
         

        

        ## Modify Files Here

        ## Modify Files Here

        src_zip_files_root_path = target_plugin_dst_path.parent
        dst_zip_file_path = root_plugin_gen_path / "PluginArchive"
        dst_zip_file_path.mkdir(parents= True, exist_ok= True)
        dst_zip_file_path = dst_zip_file_path / (PLUGIN_NAME + ".zip")
        OneZipCommand.ZipFile(PLUGIN_NAME,dst_zip_file_path,src_zip_files_root_path)
    

    def ModifyFiles():
        is_audioonly_sdk = False
        file_path = Path("/Users/admin/Documents/Unreal Projects/Agora-Unreal-RTC-SDK-dev-4.2.1/Agora-Unreal-SDK-CPP-Example/Plugins/AgoraPlugin/Source/AgoraPlugin/AgoraPlugin.Build.cs")
        file_path = str(file_path)

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


    def UpdateUpluginFile(self):
        file_path = Path("/Users/admin/Documents/PluginTemp/Agora-Unreal-RTC-SDK/PluginTmp/tmp_plugin_files/AgoraPlugin/AgoraPlugin.uplugin")
        UPLUGIN_FILE = "AgoraPlugin.uplugin"

        

        sdk_version = "4.2.1"
        min_engine_version = "5.2.0"
        support_platforms = "Win64+Mac+IOS+Android"
        marketplace_url = "com.epicgames.launcher://ue/marketplace/product/4976717f4e9847d8b161f7c5adb4c1a9"
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


    def CleanPlugin(self):
        cur_path = Path(__file__).parent.absolute()
        PrintLog(cur_path)

        root_plugin_gen_path = cur_path.parent / "PluginTemp"
        repo_path = root_plugin_gen_path

        git_url = self.git_url_src_files
        repo_name = git_url.split('/')[-1].split('.')[0]
        repo_path = repo_path / repo_name
        repo_path = Path(repo_path)

        bFullDelete = False
        FileUtility.DeleteDir(root_plugin_gen_path / Path("PluginArchive"))
        plugin_tmp_path = repo_path / "PluginTmp"

        if bFullDelete  == True:
            FileUtility.DeleteDir(plugin_tmp_path)
        else:
            delete_dir_list =["Android","IOS","Mac","Win","tmp_plugin_files"]
            for dir in delete_dir_list:
                FileUtility.DeleteDir(plugin_tmp_path / Path(dir))

if __name__ == '__main__':
    ## AgoraPluginManager.Get().Init()
    AgoraPluginManager.Get().Start()
    AgoraPluginManager.Get().UpdateUpluginFile()