import shutil
import os
from Utility.HeaderBase import *
import platform

class FileUtility:
    def CopyFilesWithSymbolicLink(src_path,dst_path, param = "Pr"):
        command = (
            r" cp -"+param + " " + str(src_path) + "/* " + str(dst_path)
        )
        #PrintLog(command)
        RUNCMD(command)

    def DeleteFile(path):
        PrintLog("DeleteFile", path)

    def DeleteDir(path):
        osplatform = platform.platform().lower()
        if "windows" in osplatform:
            ## In [Intermediate] Folder, there are some Android files with names containing dollar signs, such as:
            # [GameActivity$VirtualKeyboardInput$VirtualKeyboardInputConnection.class]
            command = (
                r"rmdir /s /q " + '"' + path + '"'
            )

            RUNCMD(command, "gbk")

        else:
            if os.path.exists(str(path)):
                PrintLog("DeleteDir " + str(path))
                shutil.rmtree(str(path))
            else:
                PrintLog("%s not exists" % path)
