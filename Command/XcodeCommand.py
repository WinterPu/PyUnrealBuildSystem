from Command.CommandBase import *
from pathlib import Path

class ParamsXcodebuild:

    def __init__(self) -> None:
        self.__path_workspace = ""
        self.__scheme = "AgoraExample"
        self.__configuration = "Development"
        self.__destination="generic/platform=iOS"
        self.__sdk = "iphoneos"
        self.__code_sign_identity = ""
        self.__provisioning_profile_specifier = ""

    @property
    def get_workspace(self):
        return self.__path_workspace
    
    @property
    def get_scheme(self):
        return self.__scheme
    
    @property
    def get_configuration(self):
        return self.__configuration
    
    @property
    def get_destination(self):
        return self.__destination
    
    @property
    def get_sdk(self):
        return self.__sdk
    
    @property
    def get_codesign_identity(self):
        return self.__code_sign_identity
    
    @property
    def get_provisioning_profile_specifier(self):
        return self.__provisioning_profile_specifier
    

    @get_workspace.setter
    def workspace(self,val):
        self.__path_workspace = Path(val)

    @get_scheme.setter
    def scheme(self,val):
        self.__scheme = val

    @get_configuration.setter
    def configuration(self,val):
        self.__configuration = val
    
    @get_destination.setter
    def destination(self,val):
        self.__destination = val

    @get_sdk.setter
    def sdk(self,val):
        self.__sdk = val

    @get_codesign_identity.setter
    def codesign_identity(self,val):
        self.__code_sign_identity = val

    @get_provisioning_profile_specifier.setter
    def provisioning_profile_specifier(self,val):
        self.__provisioning_profile_specifier = val


class XcodeCommand:
    def __init__(self) -> None:
        pass

    def XcodeBuild(self,params:ParamsXcodebuild):
        
        path_workspace = params.get_workspace
        scheme = params.get_scheme
        configuration = params.get_configuration
        destination = params.get_destination
        sdk = params.get_sdk

        codesign_identity = params.get_codesign_identity
        subcommand_codesign_identity = (r" CODE_SIGN_IDENTITY=" + '"' + str(codesign_identity) + '" ') if codesign_identity != "" else ""

        provisioning_profile_specifier = params.get_provisioning_profile_specifier
        subcommand_provisioning_profile_specifier = (r" PROVISIONING_PROFILE_SPECIFIER=" + '"' + str(provisioning_profile_specifier) + '" ') if provisioning_profile_specifier != "" else ""

        # /usr/bin/env UBT_NO_POST_DEPLOY=true /usr/bin/xcrun xcodebuild build 
        # -workspace "/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example/AgoraExample_IOS.xcworkspace" 
        # -scheme 'AgoraExample' -configuration "Development" -destination generic/platform=iOS -sdk iphoneos
        
        command = (
            r"/usr/bin/xcrun xcodebuild build "
            r" -workspace " + '"' + str(path_workspace)  + '"' + 
            r" -scheme " + '"' + str(scheme)  + '"' + 
            r" -configuration " + '"' + str(configuration)  + '"' + 
            r" -destination " + '"' + str(destination)  + '"' + 
            r" -sdk " + '"' + str(sdk)  + '"' + 
            subcommand_codesign_identity + 
            subcommand_provisioning_profile_specifier
        )

        RUNCMD(command)



    def PlistBuddy(self,command,path_infoplist):
        ## Ex.
        ## Add :UIBackgroundModes array
        ## Add :UIBackgroundModes:0 string audio
        ## Add :UIBackgroundModes:1 string fetch
        ## Add :UIBackgroundModes:2 string location
        ## Add :UIBackgroundModes:3 string voip
        ## Add :UIBackgroundModes:4 string processing

        path_infoplist =  Path(path_infoplist)
        command = (
            r"/usr/libexec/PlistBuddy "
            r" -c " + '"' + str(command)  + '"' +
            path_infoplist
        )

        RUNCMD(command)
        