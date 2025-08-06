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


    ### About Authoring
    def GetPath_WwiseAuthoringPathBase(self):
        ### For Mac
        path = "Unknown"
        if SystemHelper.Get().GetHostPlatform() == SystemHelper.Mac_HostName():

            ## Ex. /Library/Application Support/Audiokinetic/Wwise 2021.1.14.8108/Authoring
            
            path_base = Path("/Library/Application Support/Audiokinetic")
            path_wwise_authoring_lib_base = self.GetCombinedPath_WwiseBase(path_base,self.GetVer_Wwise())
            path =path_wwise_authoring_lib_base / Path("Authoring")
        elif SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName(): 
            ## C:\Program Files (x86)\Audiokinetic\Wwise 2021.1.14.8108\Authoring
            path_wwise_base = self.GetPath_WwiseBase()
            path =path_wwise_base / Path("Authoring")

        return path
    
    def GetPath_DefaultWwiseAuthoringRelease(self):
        return self.GetPath_WwiseAuthoringPathBase() / Path("x64") / Path("Release") / Path("bin") / Path("Plugins")

    
    def GetArgs(self):
        return self.__Args

    def GetPath_WPProject(self):
        return Path(self.__Args.wpprojectpath)
    
    def GetCombinedPath_WwiseBase(self,path_base,wwise_ver):
        ## Wwise Folder:
        ### 1. Sometimes: Wwise2021.1.14.8108
        ### 2. Sometimes: Wwise 2021.1.14.8108

        path_wwise_ver = str("Wwise") +  str(wwise_ver)
        path_final = path_base / path_wwise_ver

        if not path_final.exists():
            path_wwise_ver =  str("Wwise ") + str(wwise_ver)
            path_final = path_base / path_wwise_ver

        return path_final

    def GetPath_WwiseBase(self):
        path_wwise_base = self.__Args.pathwwisebase
        if path_wwise_base == "":
            if SystemHelper.Get().GetHostPlatform() == SystemHelper.Mac_HostName():
                path_wwise_base = Path("/Applications/Audiokinetic")

            elif SystemHelper.Get().GetHostPlatform() == SystemHelper.Win_HostName():
                path_wwise_base = Path("C:\Program Files (x86)\Audiokinetic")
        
        ver_wwise = self.__Args.wwisever

        path_final = self.GetCombinedPath_WwiseBase(path_wwise_base,ver_wwise)

        return path_final
    

    def GetPath_WwiseWPScript(self):
        return self.GetPath_WwiseBase() / Path("Scripts/Build/Plugins/wp.py")
    

    def GetPath_WwiseSDKBase(self):
        return self.GetPath_WwiseBase() / Path("SDK")
    
    def GetVer_Wwise(self):
        return self.__Args.wwisever
    
    def GetName_WwisePluginName(self):
        return self.__Args.wwisepluginname

    ## Windows
    def GetWindowsToolsetList(self):
        ## Full List
        str_toolset = self.__Args.wwise_windows_toolset
        return str_toolset.split('+')
    
    def GetWindowsToolsetBuildBlackList(self):
        ## Not Build List
        str_toolset = self.__Args.wwise_windows_toolset_not_build
        return str_toolset.split('+')

    ## Mac / IOS
    def GetWwiseDefaultTeamID(self):
        return self.__Args.wwise_xcode_generated_teamid

    def GetAppleTeamID(self):
        return self.__apple_team_id
    
    def IsBuildWwiseAuthoring(self):
        return self.__Args.authoring
                
    def CleanWwiseProject(self):
        path_wp_project = self.GetPath_WPProject()
        NAME_PLUGIN = self.GetName_WwisePluginName()

        NAME_SOUND_ENGINE = "SoundEnginePlugin"
        ## Windows
        win_toolset_list = self.GetWindowsToolsetList()
        for one_toolset in win_toolset_list:
            name_sln_authoring = NAME_PLUGIN + "_Authoring_Windows_" + one_toolset + ".sln"
            path_sln_authoring = path_wp_project / name_sln_authoring
            FileUtility.DeleteFile(path_sln_authoring)
        
            name_sln_windows_shared = NAME_PLUGIN + "_Windows_" + one_toolset + "_shared.sln"
            path_sln_windows_shared = path_wp_project / name_sln_windows_shared
            FileUtility.DeleteFile(path_sln_windows_shared)
            
            name_vcxproj_windows_shared = NAME_PLUGIN + "_Windows_" + one_toolset + "_shared.vcxproj"
            path_vcxproj_windows_shared = path_wp_project / NAME_SOUND_ENGINE / name_vcxproj_windows_shared
            FileUtility.DeleteFile(path_vcxproj_windows_shared)
            

            name_vcxproj_filters_windows_shared = NAME_PLUGIN + "_Windows_" + one_toolset + "_shared.vcxproj.filters"
            path_vcxproj_filters_windows_shared = path_wp_project / NAME_SOUND_ENGINE / name_vcxproj_filters_windows_shared
            FileUtility.DeleteFile(path_vcxproj_filters_windows_shared)

            name_sln_windows_static = NAME_PLUGIN + "_Windows_" + one_toolset + "_static.sln"
            path_sln_windows_static = path_wp_project / name_sln_windows_static
            FileUtility.DeleteFile(path_sln_windows_static)

            name_vcxproj_windows_static = NAME_PLUGIN + "_Windows_" + one_toolset + "_static.vcxproj"
            path_vcxproj_windows_static = path_wp_project / NAME_SOUND_ENGINE / name_vcxproj_windows_static
            FileUtility.DeleteFile(path_vcxproj_windows_static)  

            name_vcxproj_filters_windows_static = NAME_PLUGIN + "_Windows_" + one_toolset + "_static.vcxproj.filters"
            path_vcxproj_filters_windows_static = path_wp_project / NAME_SOUND_ENGINE / name_vcxproj_filters_windows_static
            FileUtility.DeleteFile(path_vcxproj_filters_windows_static)


        #Android
        name_android_mk = NAME_PLUGIN + "_Android.mk"
        path_android_mk = path_wp_project/ name_android_mk
        FileUtility.DeleteFile(path_android_mk)
            

        name_android_application_mk = NAME_PLUGIN + "_Android_application.mk"
        path_android_application_mk = path_wp_project / name_android_application_mk
        FileUtility.DeleteFile(path_android_application_mk)


        name_android_shared_mk = NAME_PLUGIN + "_Android_shared.mk"
        path_android_shared_mk = path_wp_project / NAME_SOUND_ENGINE  / name_android_shared_mk
        FileUtility.DeleteFile(path_android_shared_mk)

        name_android_static_mk = NAME_PLUGIN + "_Android_static.mk"
        path_android_static_mk = path_wp_project  / NAME_SOUND_ENGINE / name_android_static_mk
        FileUtility.DeleteFile(path_android_static_mk)


        ## Mac / iOS
        name_mac_xcodeworkspace = NAME_PLUGIN + "_Mac.xcworkspace"
        FileUtility.DeleteDir(path_wp_project / name_mac_xcodeworkspace)
        name_ios_xcodeworkspace = NAME_PLUGIN + "_iOS.xcworkspace"
        FileUtility.DeleteDir(path_wp_project / name_ios_xcodeworkspace)

        name_mac_shared_xcodeproj = NAME_PLUGIN + "_Mac_shared.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / NAME_SOUND_ENGINE / name_mac_shared_xcodeproj)
        name_mac_static_xcodeproj = NAME_PLUGIN + "_Mac_static.xcodeproj"
        FileUtility.DeleteDir(path_wp_project  / NAME_SOUND_ENGINE / name_mac_static_xcodeproj)
        name_ios_shared_xcodeproj = NAME_PLUGIN + "_iOS_shared.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / NAME_SOUND_ENGINE / name_ios_shared_xcodeproj)
        name_ios_static_xcodeproj = NAME_PLUGIN + "_iOS_static.xcodeproj"
        FileUtility.DeleteDir(path_wp_project / NAME_SOUND_ENGINE / name_ios_static_xcodeproj)