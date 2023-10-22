import shutil
import os
from Utility.HeaderBase import *


class FileUtility:
    def DeleteFile(path):
        PrintLog("DeleteFile", path)

    def DeleteDir(path):
        if os.path.exists(path):
            PrintLog("DeleteDir")
            shutil.rmtree(path)
        else:
            PrintLog("%s not exists" % path)
