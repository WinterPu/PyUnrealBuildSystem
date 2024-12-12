from SystemHelper import *
from pathlib import Path
from FileIO.FileUtility import *
from ConfigParser import *
class WPMHelper:
    __instance = None
    __initialized = False
    __Args = None
    __apple_team_id = ""

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__initialized = False
        return cls.__instance
    
    def __init__(self) -> None:
        if not self.__initialized: 
            super().__init__()

            ## Init

            self.__initialized = True

    
    def Get():
        return WPMHelper()
    
    def Init(self,Args):
        self.__Args = Args
        self.__apple_team_id = ""

        if self.__Args.ioscert != "":
            ConfigParser.Get().Init()
            OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(self.__Args.ioscert)
            self.__apple_team_id = OneIOSCert.get_team_id



    
    def GetArgs(self):
        return self.__Args

    def GetPath_WPProject(self):
        return Path(self.__Args.wpprojectpath)

    def GetPath_WwiseBase(self):
        path_wwise_base = self.__Args.pathwwisebase
        if path_wwise_base == "":
            if SystemHelper.Get().GetHostPlatform() == SystemHelper.Mac_HostName():
                path_wwise_base = Path("/Applications/Audiokinetic")

            elif SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName():
                path_wwise_base = Path("C:\Program Files (x86)\Audiokinetic")
        
        ver_wwise = self.__Args.wwisever

        path_wwise_ver = str("Wwise") +  str(ver_wwise)

        path_final = path_wwise_base / path_wwise_ver

        if not path_final.exists():
            path_wwise_ver =  str("Wwise ") + str(ver_wwise)
            path_final = path_wwise_base / path_wwise_ver

        return path_final
    

    def GetPath_WwiseWPScript(self):
        return self.GetPath_WwiseBase() / Path("Scripts/Build/Plugins/wp.py")
    

    def GetPath_WwiseSDKBase(self):
        return self.GetPath_WwiseBase() / Path("SDK")
    
    def GetName_WwisePluginName(self):
        return self.__Args.wwisepluginname

    def GetWwiseDefaultTeamID(self):
        return self.__Args.wwise_xcode_generated_teamid

    def GetAppleTeamID(self):
        return self.__apple_team_id
    
                
    def CleanWwiseProject(self):
        path_wp_project = self.GetPath_WPProject()
        name_mac_xcodeworkspace = self.GetName_WwisePluginName() + "_Mac.xcworkspace"
        FileUtility.DeleteDir(path_wp_project / name_mac_xcodeworkspace)
        name_ios_xcodeworkspace = self.GetName_WwisePluginName() + "_iOS.xcworkspace"
        FileUtility.DeleteDir(path_wp_project / name_ios_xcodeworkspace)

        name_mac_shared_xcodeproj = self.GetName_WwisePluginName() + "_Mac_shared.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / "SoundEngine" / name_mac_shared_xcodeproj)
        name_mac_static_xcodeproj = self.GetName_WwisePluginName() + "_Mac_static.xcodeproj"
        FileUtility.DeleteDir(path_wp_project  / "SoundEngine" / name_mac_static_xcodeproj)
        name_ios_shared_xcodeproj = self.GetName_WwisePluginName() + "_iOS_shared.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / "SoundEngine" / name_ios_shared_xcodeproj)
        name_ios_static_xcodeproj = self.GetName_WwisePluginName() + "_iOS_static.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / "SoundEngine" / name_ios_static_xcodeproj)