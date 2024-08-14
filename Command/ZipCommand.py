from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
import os
from SystemHelper import *

class ZipCommand:
    __host_platform = "Win"
    def __init__(self) -> None:
        self.__host_platform = SystemHelper.Get().GetHostPlatform()
        

    def UnZipFile(self,src_zip_path,dst_dir_path):
        ## Unzip [src_zip_path's content] under dst_dir_path
        ## Ex. Mac2.zip (content: /Mac/....)   dst_dir_path: Mac3
        ## Final: Mac3/Mac/...

        if self.__host_platform == SystemHelper.Win_HostName():        
            command = (
                r"7z x  " + '"'+str(src_zip_path) + '"  -o"' + str(dst_dir_path) + '"' 
            )
            RUNCMD(command)
        elif self.__host_platform == SystemHelper.Mac_HostName():
            command = (
                r"unzip  " + '"'+str(src_zip_path) + '"  -d "' + str(dst_dir_path) + '"' 
            )
            RUNCMD(command)
        
        else:
            PrintErr("Command - Invalid Platform " +  self.__host_platform )

    def ZipFile(self,src_dir_path,dst_zip_file_path, command_param = "ry"):        
        # dst_zip_file_path: with "zip" file extension
        if self.__host_platform == SystemHelper.Win_HostName():

            ## Ex.
            ## src_dir_path: 
            #  D:\\Github\\PluginWorkDir\\PluginTemp\\tmp_plugin_files\\AgoraPlugin\\Source\\ThirdParty\\AgoraPluginLibrary\\IOS\\Release\\AgoraVideoSegmentationExtension.embeddedframework 
            src_path = Path(src_dir_path) / "*"
            command = (
                r"7z a -tzip " + '"'+str(dst_zip_file_path) + '" "' + str(src_path) + '"' 
            )

            RUNCMD(command)

        elif self.__host_platform == SystemHelper.Mac_HostName():
            ## [TBD] Check if it is needed 
            
            ## if not use [src_root_path], the zip file would start from /user (example: /user/admin/xxxx/the_zip_folder_you_want)
            src_root_path = Path(src_dir_path).parent
            cur_path = Path.cwd()
            os.chdir(str(src_root_path))
            command = (
                r"zip -" + command_param + ' "'+str(dst_zip_file_path) + '" "' + str(src_dir_path.name) + '"' 
            )
            RUNCMD(command)

            os.chdir(str(cur_path))
        else:
            PrintErr("Command - Invalid Platform " +  self.__host_platform )