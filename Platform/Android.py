from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
import os

from UBSHelper import *
from Command.AndroidCommand import *

class AnndroidPlatformPathUtility:
    def GetPath_AndroidSDKConfigIniOnWindows():
        ## if you start with '/', it would be treated as starting from the root path
        path_local_user_appdata= Path(os.environ["LOCALAPPDATA"])
        return path_local_user_appdata / Path("Unreal Engine/Engine/Config/UserEngine.ini")
    
class AndroidPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        key = "androidpackagename"
        val[key] = args.androidpackagename
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

        self.RunUAT().BuildCookRun(params)
