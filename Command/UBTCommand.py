from Command.CommandBase import *
from pathlib import Path


class UBTCommand:
    ubtpath = Path(
        "/Users/Shared/Epic Games/UE_5.2/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool"
    )

    def __init__(self, ubtpath_val) -> None:
        self.ubtpath = ubtpath_val

    def GenerateProjectFiles(self, params):
        key = "project_file_path"
        project_path = params[key] if key in params else ""

        bneed_log_path = False
        path_log = ""
        sub_command_log = (
            (r" -log=" + '"' + str(path_log) + '"') if bneed_log_path else ""
        )

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""

        command = (
            '"' + str(self.ubtpath) + '"' +
            r" -projectfiles  -project=" + '"' + str(project_path) + '"' +
            r" -game"
            r" -rocket"
            r" -progress" + sub_command_log + " " + extra_commands
        )
        RUNCMD(command)
