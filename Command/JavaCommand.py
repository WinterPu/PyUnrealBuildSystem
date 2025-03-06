from Command.CommandBase import *
from pathlib import Path
from SystemHelper import *



class JavaCommand:
    def SetJavaHomePath(self,path):
        path_script = Path("./Resources/ScriptTools/SwitchJavaVersion.bat")
        command = (
            f'{path_script} "{str(Path(path))}"'
        )

        RUNCMD(command)     
