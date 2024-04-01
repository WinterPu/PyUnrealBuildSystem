from Command.CommandBase import *

class ParamsGenProjectWithShell:
    def __init__(self) -> None:
        self.__path_uproject_file = ""
        self.__subcommand_extras = ""

    @property
    def get_path_uproject_file(self):
        return self.__path_uproject_file
    
    @property
    def get_subcommand_extras(self):
        return self.__subcommand_extras
    

    @get_path_uproject_file.setter
    def path_uproject_file(self,val):
        self.__path_uproject_file = val

    @get_subcommand_extras.setter
    def extra_commands(self,val):
        self.__subcommand_extras = val
    


class GenerateProjectFilesWithShellCommand:
    __script_path = ""
    def __init__(self, script_path_val) -> None:
        self.__script_path = script_path_val

    def GenerateProjectFiles(self,params:ParamsGenProjectWithShell):
        ### Command
        path_uproject_file = params.get_path_uproject_file
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__script_path) + '"' + 
            r" -project="+ '"'  + str(path_uproject_file) + '"'
            r" -game"+
            subcommand_extras
        )
        
        RUNCMD(command)