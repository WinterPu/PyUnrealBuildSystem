from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
import os

class ZipCommand:
    platform = "Win"
    def __init__(self,param_platform = "Win") -> None:
        if param_platform == "Win":
            self.platform = "Win"
        else:
            self.platform = "Mac"
        

    def UnZipFile(self,src_path,dst_path):

        if self.platform == "Win":        
            pass
        elif self.platform == "Mac":
            command = (
                r"unzip  " + '"'+str(src_path) + '"  -d "' + str(dst_path) + '"' 
            )
            RUNCMD(command)
        
        else:
            PrintErr("Command - Invalid Platform " +  self.platform )

    def ZipFile(self,src_dir_name,dst_zip_file_path, src_root_path = Path("."), command_param = "ry"):        
        ## [TBD] Check if it is needed 
        
        ## if not use [src_root_path], the zip file would start from /user (example: /user/admin/xxxx/the_zip_folder_you_want)
        cur_path = Path.cwd()
        os.chdir(str(src_root_path))
        command = (
            r"zip -" + command_param + ' "'+str(dst_zip_file_path) + '" "' + str(src_dir_name) + '"' 
        )
        RUNCMD(command)

        os.chdir(str(cur_path))