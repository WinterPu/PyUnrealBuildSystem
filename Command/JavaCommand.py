from Command.CommandBase import *
from pathlib import Path
from SystemHelper import *



class JavaCommand:
    ## For Jenkins Environment: you could use  withEnv(["JAVA_HOME=${PAHT_JAVA_HOME}"]) in your groovy script
    def SetJavaHomePath(self,path):
        path_script = Path("./Tools/bat/SwitchJavaVersion.bat")
        command = (
            f'{path_script} "{str(Path(path))}"'
        )

        RUNCMD(command)     
