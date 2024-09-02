from Command.CommandBase import *
from pathlib import Path
import os 



class AndroidCommand:

    ## Win

    __path_sdkmanager = Path(os.getenv('LOCALAPPDATA')) / Path("Android/Sdk/cmdline-tools/10.0/bin/sdkmanager.bat")
    __path_adb = Path(os.getenv('LOCALAPPDATA')) / Path("Android/Sdk/platform-tools/adb.exe")


    def SDKManager_Install(self,install_subcommand,bshow_list = False):
        # sub_command = "platforms;android-"+api_version
        # sub_command = "build-tools;33.0.1"

        subcommands = str(install_subcommand).split('+')
        subcommand = ""
        for one_subcommand in subcommands:
            subcommand = subcommand +'"'+ str(one_subcommand) + '" '

        command = (
            '"' + str(self.__path_sdkmanager) + '"' +
            r" --install " + str(subcommand) 
        )
        RUNCMD(command)

        if bshow_list:
            self.SDKManager_List()

    def SDKManager_UnInstall(self,uninstall_subcommand,bshow_list = False):
        # sub_command = "platforms;android-"+api_version
        # sub_command = "build-tools;33.0.1"
        subcommands = str(uninstall_subcommand).split('+')
        subcommand = ""
        for one_subcommand in subcommands:
            subcommand = subcommand + '"'+ str(one_subcommand) + '" '

        command = (
            '"' + str(self.__path_sdkmanager) + '"' +
            r" --uninstall "  + str(subcommand)
        )
        RUNCMD(command)

        if bshow_list:
            self.SDKManager_List()

    def SDKManager_List(self):
        command = (
            '"' + str(self.__path_sdkmanager) + '"' +
            r" --list "
        )
        RUNCMD(command)

    def ADB_Input(self,input_text):
        command = (
            '"' + str(self.__path_adb) + '"' +
            r" shell input text " + '"' + str(input_text) + '"'
        )
        RUNCMD(command)