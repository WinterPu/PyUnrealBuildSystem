from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
import os


class AnndroidPlatformPathUtility:
    def GetAndroidSDKConfigIniPathOnWindows():
        ## if you start with '/', it would be treated as starting from the root path
        return Path("Unreal Engine/Engine/Config/UserEngine.ini")
    
class AndroidPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        key = "platform"
        val[key] = "Android"

        key = "enginever"
        val[key] = args.enginever if "enginever" in args else "4.27"

        # key = "project_path"
        # val[key] = args.projectpath if 'projectpath' in args else None

        ### [TBD]
        ## validate project

        return ret, val


class AndroidTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())
        
        ### Modify Android SDK Config
        host_platform = self.GetParamVal("host_platform")

        if host_platform == "Win":
        
            engine_ver = self.GetParamVal("enginever")
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
                final_java_val = path_java.parent.parent.joinpath("jdk-11")
                final_ndk_apilevel = "android-21"
            else:
                final_ndk_path = path_ndk.joinpath("25.1.8937393")
                os.environ["NDKROOT"] = str(final_ndk_path)
                os.environ["NDK_ROOT"] = str(final_ndk_path)
                final_java_val = path_java.parent.parent.joinpath("jdk-11")
                final_ndk_apilevel = "android-25"

            PrintLog("Cur NDKROOT:  %s" % os.environ["NDKROOT"])
            PrintLog("Cur NDK_ROOT:  %s" % os.environ["NDK_ROOT"])

            ## Modify Android SDK Config
            path_local_user_appdata= Path(os.environ["LOCALAPPDATA"])


            val_java = UnrealConfigIniManager.GenIniVal_Path(final_java_val)
            val_ndk = UnrealConfigIniManager.GenIniVal_Path(final_ndk_path)
            val_ndk_apilevel = final_ndk_apilevel


            path_android_sdk_config_ini = path_local_user_appdata / AnndroidPlatformPathUtility.GetAndroidSDKConfigIniPathOnWindows()
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "NDKPath",val_ndk,True)
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "JavaPath", val_java,True)
            UnrealConfigIniManager.SetConfig(path_android_sdk_config_ini, "[/Script/AndroidPlatformEditor.AndroidSDKSettings]", "NDKAPILevel",val_ndk_apilevel,True)

        else:
            PrintErr("TBD - Not Ready, SetupEnvironment Android on Mac Platform")
            return

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())
        self.RunUAT().BuildCookRun(self.Params)
