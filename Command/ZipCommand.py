from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
import os
from SystemHelper import *

class ZipCommand:
    __host_platform = "Win"
    def __init__(self,param_platform = "Win") -> None:
        self.__host_platform = SystemHelper.Get().GetHostPlatform()
        

    def UnZipFile(self,src_path,dst_path):

        if self.__host_platform == SystemHelper.Win_HostName():        
            pass
        elif self.__host_platform == SystemHelper.Mac_HostName():
            command = (
                r"unzip  " + '"'+str(src_path) + '"  -d "' + str(dst_path) + '"' 
            )
            RUNCMD(command)
        
        else:
            PrintErr("Command - Invalid Platform " +  self.__host_platform )

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