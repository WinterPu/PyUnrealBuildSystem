from Command.CommandBase import *
from pathlib import Path
import os

class MacRATrustCommand:
    
    def DoMacTrust(self,project_path):
        command = (
            r" sudo bash ./MacRATrust.sh " + '"'+str(project_path) + '"'
        )
        RUNCMD(command)
