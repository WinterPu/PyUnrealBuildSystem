from Utility.HeaderBase import *
import platform
import traceback
from SystemHelper import *
class BaseSystem:
    __version = "1.""0.""0"
    __version_info = {}
    def __init__(self) -> None:
        self.__version_info['SystemVersion'] = self.__version
        self.__version_info['PythonVersion'] = platform.python_version()
        self.__version_info['HostMachineOS'] = SystemHelper.Get().GetHostPlatform()
    
    def GetHostPlatform(self):
        return self.__version_info['HostMachineOS']