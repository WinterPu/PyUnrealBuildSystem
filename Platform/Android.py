from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
import os

from UBSHelper import *
from Command.AndroidCommand import *

## Wwise
from Command.WwiseCommand import * 
from WPMHelper import * 

class AnndroidPlatformPathUtility:
    def GetPath_AndroidSDKConfigIniOnWindows():
        ## if you start with '/', it would be treated as starting from the root path
        path_local_user_appdata= Path(os.environ["LOCALAPPDATA"])
        return path_local_user_appdata / Path("Unreal Engine/Engine/Config/UserEngine.ini")
    
class AndroidPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        key = "androidpackagename"
        val[key] = args.androidpackagename if "androidpackagename" in args else ""
        # key = "target_platform"
        # val[key] = "Android"

        return ret, val


class AndroidTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.Android_TargetName()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())
        
        ### Modify Android SDK Config
        host_platform = self.GetHostPlatform()

        if host_platform == SystemHelper.Win_HostName():
        
            engine_ver = UBSHelper.Get().GetVer_UEEngine()
            PrintLog("Before Modification: NDKROOT:  %s" % os.environ["NDKROOT"])
            PrintLog("Before Modification: NDK_ROOT:  %s" % os.environ["NDK_ROOT"])
            path_ndk = Path(os.environ["NDKROOT"])
            path_java = Path(os.environ["JAVA_HOME"])
            final_ndk_path = ""
            final_java_val = ""
            final_ndk_apilevel = ""
            if engine_ver == "4.27" or engine_ver == "4.25":
                final_ndk_path = path_ndk.parent.joinpath("21.4.7075529")
                os.environ["NDKROOT"] = str(final_ndk_path)
                os.environ["NDK_ROOT"] = str(final_ndk_path)
                final_java_val = path_java.parent.joinpath("jdk-11")
                final_ndk_apilevel = "android-21"
            else:
                final_ndk_path = path_ndk.parent.joinpath("25.1.8937393")
                os.environ["NDKROOT"] = str(final_ndk_path)
                os.environ["NDK_ROOT"] = str(final_ndk_path)
                final_java_val = path_java.parent.joinpath("jdk-11")
                final_ndk_apilevel = "android-25"

            PrintLog("Cur NDKROOT:  %s" % os.environ["NDKROOT"])
            PrintLog("Cur NDK_ROOT:  %s" % os.environ["NDK_ROOT"])

            ## Modify Android SDK Config
            val_java = UnrealConfigIniManager.GenIniVal_Path(final_java_val)
            val_ndk = UnrealConfigIniManager.GenIniVal_Path(final_ndk_path)
            val_ndk_apilevel = final_ndk_apilevel

            path_android_sdk_config_ini =  AnndroidPlatformPathUtility.GetPath_AndroidSDKConfigIniOnWindows()
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "NDKPath",val_ndk,True)
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "JavaPath", val_java,True)
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "NDKAPILevel",val_ndk_apilevel,True)

        else:
            PrintErr("TBD - Not Ready, SetupEnvironment Android on Mac Platform")
            return

        
        UnrealConfigIniManager.SetConfig_AndroidPackageName(UBSHelper.Get().GetPath_UProjectFile(),self.Params['androidpackagename'])



        ## SDKManager
        engine_ver = UBSHelper.Get().GetVer_UEEngine()
        if engine_ver == "4.27" or engine_ver == "4.25":
            PrintLog("SDKManager - UnInstall Android API")
            OneAndroidCommand = AndroidCommand()
            OneAndroidCommand.SDKManager_UnInstall("platforms;android-33")
            

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())

        params = ParamsUAT()
        params.target_platform = self.GetTargetPlatform()
        params.path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        params.path_engine = UBSHelper.Get().GetPath_UEEngine()
        params.path_archive = UBSHelper.Get().GetPath_ArchiveDirBase()
        params.skip_build_editor = UBSHelper.Get().ShouldSkipBuildEditor()

        self.RunUAT().BuildCookRun(params)

        self.PostPackaged()

        self.ArchiveProduct()

    
    def PostPackaged(self):
        PrintStageLog("PostPackaged - Android")

        path_archive_dir = UBSHelper.Get().GetPath_ArchiveDir(self.GetTargetPlatform())
        self.SetArchivePath_FinalProductDir(path_archive_dir)







#####################################################################################
#################################### Wwise ##########################################
    def Package_Wwise(self):
        WPMHelper.Get().CleanWwiseProject()

        self.SetupEnvironment_Wwise()

        list_config = ["Debug","Profile","Release"]
        list_arch = ["armeabi-v7a", "x86", "arm64-v8a", "x86_64"]
        platform = "Android"

        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()

        one_param_premake = ParamsWwisePluginPremake()
        one_param_premake.platform = "Android"
        OneWwiseCommand.Premake(one_param_premake)

        for one_config in list_config:
            for one_arch in list_arch:
                one_param = ParamsWwisePluginBuild()
                one_param.config = one_config
                one_param.arch = one_arch
                one_param.platform = platform

                OneWwiseCommand.Build(one_param)

        PrintStageLog("Android - Package_Wwise Build Complete")

        ## Archive
        ## Final Product

        
        path_Android_output_root_path = ""

        bneed_to_change_root_path = SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName()
        if bneed_to_change_root_path:
            ## this should be defined in wp.py scripts in Wwise base folder 
            path_Android_output_root_path = Path("D:/WwiseAndroidOutput")


        for one_config in list_config:
            for one_arch in list_arch:
                OneArchiveInfo = ArchiveInfo_WwisePlugin(
                    WPMHelper.Get().GetName_WwisePluginName(),
                    WPMHelper.Get().GetVer_Wwise(),
                    SystemHelper.Android_TargetName(),
                    one_config,
                    one_arch

                )
                extension = "so"
                name_final_product = OneArchiveInfo.GetArchiveName()   + "." +  extension
                path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() / ("Android_" + one_arch) / one_config / "lib" / name_final_product
                if bneed_to_change_root_path:
                    path_target_archive_file = path_Android_output_root_path / one_config / one_arch / name_final_product

                PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
                bshould_clean_others_when_archving = False
                ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

        PrintStageLog("Android - Package_Wwise Archive Complete")


    def SetupEnvironment_Wwise(self):
        PrintStageLog("SetupEnvironment_Wwise - Android")
        
        PrintLog("Before Modification: NDKROOT:  %s" % os.environ["NDKROOT"])
        PrintLog("Before Modification: NDK_ROOT:  %s" % os.environ["NDK_ROOT"])
        
        path_ndk = Path(os.environ["NDKROOT"])
        
        final_ndk_path = path_ndk.parent.joinpath("25.1.8937393")
        # final_ndk_path = path_ndk.parent.joinpath("21.4.7075529")
        
        os.environ["NDKROOT"] = str(final_ndk_path)
        os.environ["NDK_ROOT"] = str(final_ndk_path)

        PrintLog("Cur NDKROOT:  %s" % os.environ["NDKROOT"])
        PrintLog("Cur NDK_ROOT:  %s" % os.environ["NDK_ROOT"])


        ## Modifiy In 
        if SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName():
            path_android_script_in_wwise_script = Path("C:\Program Files (x86)\Audiokinetic\Wwise 2021.1.14.8108\Scripts\Build\Plugins\common\command\android.py")
            PrintWarn(f"Please check modification of android script in wwise build script {path_android_script_in_wwise_script}")

            #### Change The Code Here ### 
            # libs_out = " NDK_LIBS_OUT=" + '"' + os.path.join(out_dir_root, config, "libs").replace("\\", "/") + '"'
            # ndk_out = " NDK_OUT=" + '"' +os.path.join(out_dir_root, config, "lib").replace("\\", "/") + '"' # the missing "s" at lib is on purpose
            # ndk_app_out = " NDK_APP_OUT="+ '"' + out_dir_root.replace("\\", "/") + '"'
            # target_out = " TARGET_OUT="+ '"' + os.path.join(out_dir_root, config, "lib").replace("\\", "/") + '"'

            #### Change The Code To ###
            # from pathlib import Path
            # def wrap_str(val_str):
            #     return '"' + val_str + '"'
            #     # return str('"' + val_str + '"').replace('\\', '//')
            
            # # ......
            # path_lib = Path("D://WwiseAndroidOutput") / config
            # libs_out = " NDK_LIBS_OUT=" + wrap_str(str(path_lib))
            # ndk_out = " NDK_OUT=" + wrap_str(str(path_lib)) 
            # ndk_app_out = " NDK_APP_OUT=" + wrap_str(str(path_lib))
            # target_out = " TARGET_OUT=" + wrap_str(str(path_lib))
        