import shutil
import os
from Command.CommandBase import *
from Logger.Logger import *
import platform
from pathlib import Path

class FileUtility:
    def GetPlatform():
        return platform.platform().lower()
    
    def IsPlatform_Windows():
        return "windows" in FileUtility.GetPlatform()
    
    def IsPlatform_Mac():
        return "mac" in FileUtility.GetPlatform()


    def CopyFile(src_path,dst_path):
        PrintLog("CopyFile: " + str(src_path) + " to " + str(dst_path))
        shutil.copy2(str(src_path),str(dst_path))



    def CopyDir(src_path,dst_path,bkeep_symlink = True,bmac_use_shutil = False,mac_cp_custom_params = ""):
        ## Case: Copy .app:
        ### there are 2 ways:
        ### 1. bmac_use_shutil = True
        ### 2. mac_cp_custom_params = "PR"
        if FileUtility.IsPlatform_Mac() and (not bmac_use_shutil):
            if mac_cp_custom_params != "":
                mac_cp_custom_params =  "-" + mac_cp_custom_params if mac_cp_custom_params != " " else ""
                command = (
                    r" cp "+ str(mac_cp_custom_params) + " " + str(src_path) + " " + str(dst_path)
                )
                #PrintLog(command)
                RUNCMD(command)
            else:
                if bkeep_symlink:
                    param = "PRfa"
                else:
                    param = "RLf"
            
                command = (
                    r" cp -"+param + " " + str(src_path) + " " + str(dst_path)
                )
                #PrintLog(command)
                RUNCMD(command)
        
        else:
            ## src_path cannot have wildcard char [*] in the path on windows
            shutil.copytree(str(src_path),str(dst_path),dirs_exist_ok= True, symlinks = bkeep_symlink)

    
    ### Because windows doesn't support wildcard char in the path, 
    ### so we need to use this function to copy the files with wildcard char in the path
    ## 
    ## Windows - Wildcard Char: *
    ## Ex. pattern = "*.xcframework"
    ## Example Copy D:\\Github\\PluginWorkDir\\PluginTemp\\Mac\\libs\\*.xcframework\\macos-arm64_x86_64 ---> 
    ## D:\\Github\\PluginWorkDir\\PluginTemp\\tmp_plugin_files\\AgoraPlugin\\Source\\ThirdParty\\AgoraPluginLibrary\\Mac\\Release 
    def CopyDirWithWildcardCharInPath_Win(src_root_path,src_sub_path,dst_path,pattern = "*.xcframework"):
        # Copy src_root_path/[pattern]/[src_sub_path]/* to dst_path
        src_sub_path = Path(src_sub_path) / "*"
        PrintLog("CopyDirWithWildcardCharInPath_Win with pattern[%s] src_root[%s]/pattern[%s]/src_sub_path[%s] to dst_path[%s] " %(str(pattern),str(src_root_path),str(pattern),str(src_sub_path),str(dst_path)))
        for pattern_dir in Path(src_root_path).glob(pattern):
            for file in pattern_dir.glob(str(src_sub_path)):
                dest_file = Path(dst_path) / file.name
                shutil.copytree(str(file),str(dest_file),dirs_exist_ok= True)
    

    def DeleteFile(path,bForce = False):
        PrintLog("DeleteFile " + str(path))
        path = str(path)
        if bForce:
            command = (
                r"rm -f " + '"' + path + '"'
            )
            RUNCMD(command, "gbk")

        else:
            Path(path).unlink()


    def DeleteDir(path):
        if FileUtility.IsPlatform_Windows():
            ## In [Intermediate] Folder, there are some Android files with names containing dollar signs, such as:
            # [GameActivity$VirtualKeyboardInput$VirtualKeyboardInputConnection.class]
            command = (
                r"rmdir /s /q " + '"' + str(path) + '"'
            )

            RUNCMD(command, "gbk")

        else:
            if os.path.exists(str(path)):
                PrintLog("DeleteDir " + str(path))
                shutil.rmtree(str(path))
            else:
                PrintLog("%s not exists" % path)
