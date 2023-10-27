import shutil
import os
from Utility.HeaderBase import *
import platform

class FileUtility:
    def DeleteFile(path):
        PrintLog("DeleteFile", path)

    def DeleteDir(path):
        osplatform = platform.platform().lower()
        if "windows" in osplatform:
            ## In [Intermediate] Folder, there are some Android files with names containing dollar signs, such as:
            # [GameActivity$VirtualKeyboardInput$VirtualKeyboardInputConnection.class]
            command = (
                r"rmdir /s /q" + '"' + path + '"'
            )
            
            RUNCMD(command, "gbk")

        else:
            if os.path.exists(path):
                PrintLog("DeleteDir")
                shutil.rmtree(path)
            else:
                PrintLog("%s not exists" % path)
