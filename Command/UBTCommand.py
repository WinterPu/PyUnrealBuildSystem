from Command.CommandBase import *
from pathlib import Path


class ParamsUBT:
    def __init__(self) -> None:
        self.__path_uproject_file = ""
        self.__path_log = ""
        self.__subcommand_extras = ""

    @property
    def get_path_uproject_file(self):
        return self.__path_uproject_file
    @property
    def get_subcommand_log(self):
        return (r" -log=" + '"' + str(self.__path_log) + '"') if self.__path_log != "" else ""
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras

    @get_path_uproject_file.setter
    def path_uproject_file(self,val):
        self.__path_uproject_file = val
    @get_subcommand_log.setter
    def path_log(self,val):
        self.__path_log = val
    @get_subcommand_extras.setter
    def extra_commands(self,val):
        self.__subcommand_extras = val
    


class UBTCommand:
    __path_ubt = Path(
        "/Users/Shared/Epic Games/UE_5.2/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool"
    )
    __path_mono = ""
    def __init__(self, ubtpath_val,path_mono = "") -> None:
        self.__path_ubt = ubtpath_val
        self.__path_mono = path_mono

    def GenerateProjectFiles(self, params:ParamsUBT):

        path_uproject_file = params.get_path_uproject_file
        subcommand_log = params.get_subcommand_log
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__path_ubt) + '"' +
            r" -projectfiles  -project=" + '"' + str(path_uproject_file) + '"' +
            r" -game"
            r" -rocket"
            r" -progress" + subcommand_log + " " + 
            subcommand_extras
        )
        RUNCMD(command)


    def GenerateIOSProject(self,params:ParamsUBT):

        path_uproject_file = params.get_path_uproject_file
        subcommand_extras = params.get_subcommand_extras

        command = (
                r' bash "' + str(self.__path_mono) + '"' + ' "' + str(self.__path_ubt) + '" '
                r" -XcodeProjectFiles"
                r" -project=" + '"' + str(path_uproject_file) + '"' + 
                r" -platforms=IOS"
                r" -game"
                r" -nointellisense"
                r" -IOSdeployonly"
                r" -ignorejunk"
                r" -projectfileformat=XCode"
                r" -includetemptargets" 
                r" -automated" + 
                # r" -log="/Users/admin/Library/Logs/Unreal Engine/LocalBuildLogs/UBT-.txt""
                subcommand_extras
             )
        
        RUNCMD(command)