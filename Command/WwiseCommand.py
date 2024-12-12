from Command.CommandBase import *
from pathlib import Path
import os

class ParamsWwisePluginPremake():
    def __init__(self) -> None:
        self.__platform = ""

    @property
    def get_platform(self):
        return self.__platform
    
    @get_platform.setter
    def platform(self,val):
        self.__platform = val

    @property
    def get_subcommand(self):
        return " " + self.__platform 

class ParamsWwisePluginBuild():
    def __init__(self) -> None:
        self.__configuration = ""
        self.__platform = ""
        self.__architecture = ""
        self.__toolset = ""

    @property
    def get_configuration(self):
        return self.__configuration
    
    @get_configuration.setter
    def config(self,val):
        self.__configuration = val
    
    @property
    def get_platform(self):
        return self.__platform
    
    @get_platform.setter
    def platform(self,val):
        self.__platform = val
    
    @property
    def get_architecture(self):
        return self.__architecture
    
    @get_architecture.setter
    def arch(self,val):
        self.__architecture = val
    
    @property
    def get_toolset(self):
        return self.__toolset
    
    @get_toolset.setter
    def toolset(self,val):
        self.__toolset = val
    
    @property
    def get_subcommand(self):
        subcommand = ""

        if self.__configuration != "":
            subcommand += " -c " + self.__configuration
        if self.__architecture != "":
            subcommand += " -x " + self.__architecture
        if self.__toolset != "":
            subcommand += " -t " + self.__toolset
        if self.__platform != "":
            subcommand += " " + self.__platform

        return subcommand


class WwiseCommand:
    def __init__(self) -> None:
        self.__path_wp = ""
        self.__path_project = ""

    @property
    def get_path_wp(self):
        return self.__path_wp
    @get_path_wp.setter
    def path_wp(self,val):
        self.__path_wp = val

    @property
    def get_path_project(self):
        return self.__path_project
    
    @get_path_project.setter
    def path_project(self,val):
        self.__path_project = Path(val)

    def RUNCMD_UnderWwiseProject(self,command):
        path_wp_project = self.get_path_project
        original_cwd = Path.cwd()
        try:
            os.chdir(path_wp_project)
            PrintLog("WwiseCommand - change dir to project: " + str(path_wp_project))
            RUNCMD(command)
        finally:
            os.chdir(original_cwd)
            PrintLog("WwiseCommand - change dir back to " + str(original_cwd))
    
    def Premake(self,params:ParamsWwisePluginPremake):
        path_wp = self.get_path_wp
        subcommand = params.get_subcommand
        command = (
            "python " + '"' + f"{path_wp}" + '"' + " premake " + subcommand
        )
        self.RUNCMD_UnderWwiseProject(command)

    def Build(self,params:ParamsWwisePluginBuild):
        path_wp = self.get_path_wp
        subcommand = params.get_subcommand
        command = (
            "python " + '"' + f"{path_wp}" + '"' + " build " + subcommand
        )
        self.RUNCMD_UnderWwiseProject(command)


    
    
# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Profile -x x64 -t vc160 Windows_vc160
# ```

# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Debug -x arm64-v8a Android
# ```