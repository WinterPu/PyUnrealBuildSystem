from Command.CommandBase import *
from pathlib import Path


class ParamsWwise:
    def __init__(self) -> None:
        self.__path_wp = ""

    @property
    def get_path_wp(self):
        return self.__path_wp
    @get_path_wp.setter
    def path_wp(self,val):
        self.__path_wp = val


class ParamsWwisePluginBuild:
    def __init__(self) -> None:
        self.__path_wp = ""

    @property
    def get_path_wp(self):
        return self.__path_wp
    @get_path_wp.setter
    def path_wp(self,val):
        self.__path_wp = val

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
    
    def Premake(self,params:ParamsWwise):
        path_wp = params.get_path_wp
        default = "Authoring"
        command = (
            '" python ' + str(path_wp) + '"' + " premake"
        )
        RUNCMD(command)

    def Build(self,params:ParamsWwisePluginBuild):
        path_wp = params.get_path_wp
        subcommand = params.get_subcommand
        command = (
            '" python ' + str(path_wp) + '"' + " build " + subcommand
        )
        RUNCMD(command)

        pass
    
# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Profile -x x64 -t vc160 Windows_vc160
# ```

# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Debug -x arm64-v8a Android
# ```