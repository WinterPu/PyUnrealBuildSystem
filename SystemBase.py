from Utility.HeaderBase import *
import platform
import traceback
class BaseSystem:
    version = "1.""0.""0"
    version_info = {}
    def __init__(self) -> None:
        self.version_info['SystemVersion'] = self.version
        self.version_info['PythonVersion'] = platform.python_version()
        ossystem = platform.platform().lower()
        if 'windows' in ossystem:
            self.version_info['HostMachineOS'] = "Win"
        elif 'macos' in ossystem:
            self.version_info['HostMachineOS'] = "Mac"
        else:
            self.version_info['HostMachineOS'] = ossystem
        PrintLog(self.version_info)
    
    def GetHostPlatform(self):
        return self.version_info['HostMachineOS']