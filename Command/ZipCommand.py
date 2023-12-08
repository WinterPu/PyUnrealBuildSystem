from Command.CommandBase import *
from pathlib import Path
import os

class ZipCommand:

    def UnZipFile(self,src_path,dst_path):
        command = (
            r"unzip -d " + '"'+str(src_path) + '" "' + str(dst_path) + '"' 
        )
        RUNCMD(command)

    def ZipFile(self,src_path,dst_zip_file_path, src_root_path = Path("."), command_param = ""):
        if command_param == "":
            command_param = " -ry "
        
        ## [TBD] Check if it is needed 
        cur_path = Path.cwd()
        os.chdir(str(src_root_path))
        command = (
            r"zip " + command_param + '"'+str(dst_zip_file_path) + '" "' + str(src_path) + '"' 
        )
        RUNCMD(command)

        os.chdir(str(cur_path))