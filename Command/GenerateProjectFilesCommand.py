from Command.CommandBase import *

class GenerateProjectFilesCommand:
    script_path = ""
    def __init__(self, script_path_val) -> None:
        self.script_path = script_path_val

    def GenerateProjectFiles(self,params):
        ### Command
        key = "project_file_path"
        project_path = params[key] if key in params else ""

        key = "extra_command"
        extra_commands = params[key] if key in params else ""

        command = (
            '"' + str(self.script_path) + '"' + 
            r" -project="+ '"'  + str(project_path) + '"'
            r" -game"+
            extra_commands
         )
        RUNCMD(command)