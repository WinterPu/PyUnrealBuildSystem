import platform
import traceback
import sys
from SystemHelper import SystemHelper
import locale

class BaseSystem:
    __version = "1.""0.""0"
    __version_info = {}
    __encoding_info = None  # 延迟初始化
    
    def __init__(self) -> None:
        self.__version_info['SystemVersion'] = self.__version
        self.__version_info['PythonVersion'] = platform.python_version()
        self.__version_info['HostMachineOS'] = SystemHelper.Get().GetHostPlatform()
        
        # 自动初始化编码环境并注入到 CommandBase
        self._InitEncodingEnvironment()
        from Command.CommandBase import SetSubprocessEncoding
        SetSubprocessEncoding(self.GetSubprocessEncoding())
    
    def _InitEncodingEnvironment(self):
        """初始化和检测编码环境（延迟初始化）"""
        if self.__encoding_info is not None:
            return  # 已经初始化过
            
        self.__encoding_info = {}
        self.__encoding_info['ConsoleEncoding'] = sys.stdout.encoding
        self.__encoding_info['SystemEncoding'] = locale.getpreferredencoding()
        self.__encoding_info['DefaultEncoding'] = sys.getdefaultencoding()
        self.__encoding_info['Platform'] = sys.platform
        
        # 确定子进程命令的默认编码
        if sys.platform == 'win32':
            # Windows 上：7z 等工具始终输出 GBK，不管控制台编码
            self.__encoding_info['SubprocessEncoding'] = 'gbk'
        else:
            # Linux/Mac：使用 UTF-8
            self.__encoding_info['SubprocessEncoding'] = 'utf-8'
    
    def GetEncodingInfo(self):
        """获取编码信息字典"""
        if self.__encoding_info is None:
            self._InitEncodingEnvironment()
        return self.__encoding_info.copy()
    
    def GetSubprocessEncoding(self):
        """获取子进程命令应该使用的编码"""
        if self.__encoding_info is None:
            self._InitEncodingEnvironment()
        return self.__encoding_info.get('SubprocessEncoding', 'utf-8')
    
    def PrintEncodingInfo(self):
        """打印编码环境信息（用于调试）"""
        if self.__encoding_info is None:
            self._InitEncodingEnvironment()
        from Logger.Logger import PrintLog
        PrintLog("=" * 60)
        PrintLog("System Encoding Environment:")
        for key, value in self.__encoding_info.items():
            PrintLog(f"  {key}: {value}")
        PrintLog("=" * 60)
    
    def GetHostPlatform(self):
        return self.__version_info['HostMachineOS']