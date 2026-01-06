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

class ParamsWwiseConsoleGenerateSoundBank():
    def __init__(self) -> None:
        self.__project_path = ""
        self.__use_stable_guid = False
        self.__import_definition_file = ""
        self.__platforms = [] # list of {'platform': str, 'path': str}
        self.__banks = [] # list of str
        self.__languages = [] # list of str
        self.__custom_args = ""
    
    @property
    def project_path(self):
        return self.__project_path
    @project_path.setter
    def project_path(self, val):
        self.__project_path = val

    @property
    def use_stable_guid(self):
        return self.__use_stable_guid
    @use_stable_guid.setter
    def use_stable_guid(self, val:bool):
        self.__use_stable_guid = val

    @property
    def import_definition_file(self):
        return self.__import_definition_file
    @import_definition_file.setter
    def import_definition_file(self, val):
        self.__import_definition_file = val
    
    @property
    def platforms(self):
        return self.__platforms
    
    ## Android, Mac, Windows, iOS
    def add_platform(self, platform_name, soundbank_path):
        self.__platforms.append({'platform': platform_name, 'path': soundbank_path})

    def add_bank(self, bank_path):
        self.__banks.append(bank_path)

    @property
    def languages(self):
        return self.__languages
    
    def add_language(self, language):
        self.__languages.append(language)
        
    @property 
    def custom_args(self):
        return self.__custom_args
    @custom_args.setter
    def custom_args(self, val):
        self.__custom_args = val

    @property
    def get_arguments(self):
        args = ""
        if self.__project_path:
            args += f' "{self.__project_path}"'
        
        if self.__use_stable_guid:
            args += " --use-stable-guid"
        
        if self.__import_definition_file:
            args += f' --import-definition-file "{self.__import_definition_file}"'
            
        for p in self.__platforms:
            args += f' --platform "{p["platform"]}" --soundbank-path {p["platform"]} "{p["path"]}"'

        for b in self.__banks:
             args += f' --bank "{b}"'
        
        for l in self.__languages:
            args += f' --language "{l}"'
            
        if self.__custom_args:
            args += " " + self.__custom_args

        return args


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

    def GenerateSoundBank(self, wwise_console_path, params:ParamsWwiseConsoleGenerateSoundBank):
        command = f'"{wwise_console_path}" generate-soundbank{params.get_arguments}'
        RUNCMD(command)


    
    
# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Profile -x x64 -t vc160 Windows_vc160
# ```

# ```
# python "C:\Program Files (x86)\Audiokinetic\Wwise 2023.1.6.8555\Scripts\Build\Plugins\wp.py" build -c Debug -x arm64-v8a Android
# ```