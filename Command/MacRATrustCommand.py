from Command.CommandBase import *
from pathlib import Path
import os

class MacRATrustCommand:
    
    def DoMacTrust(self,path_project,dst_path = "",password = ""):
        password_command = ""
        if password_command != "":
            password_command = password
            
        extra_cmd_dst_path = ""
        if dst_path != "":
            extra_cmd_dst_path = " -D " + '"'+str(dst_path) + ' "'
        command = (
            r" sudo bash ./MacRATrust.sh -P " + '"'+str(path_project) + '"' + extra_cmd_dst_path + " " + password_command
        )
        RUNCMD(command)
