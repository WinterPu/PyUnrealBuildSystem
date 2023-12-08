from Command.CommandBase import *
from pathlib import Path

class UBTCommand:
    ubtpath= Path("/Users/Shared/Epic\ Games/UE_5.2/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool")
    def __init__(self, ubtpath_val) -> None:
        self.ubtpath = ubtpath_val

    def GenerateProject(self,params):
        key = "project_path"
        project_path = params[key] if key in params else ""
        
        log_path=""

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""
        
        command = (
            '"' + str(self.ubtpath) + '"' +
            r" -projectfiles  -project="+ '"' +str(project_path)+ '"' + 
            r" -game"
            r" -rocket"
            r" -progress"
            r" -log="+ '"' +str(log_path)+ '"' + 
            extra_commands
         )
        RUNCMD(command)