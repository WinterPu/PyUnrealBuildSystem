import subprocess
import threading
import sys
from Logger.Logger import *
from pathlib import Path
import os
import locale

# 全局编码配置（由 BaseSystem 初始化时设置）
_SUBPROCESS_ENCODING = None

def SetSubprocessEncoding(encoding):
    """设置子进程命令的默认编码（由 BaseSystem 调用）"""
    global _SUBPROCESS_ENCODING
    _SUBPROCESS_ENCODING = encoding

def GetSubprocessEncoding():
    """获取子进程命令应该使用的编码"""
    global _SUBPROCESS_ENCODING
    if _SUBPROCESS_ENCODING is None:
        # 如果没有初始化，使用智能检测
        if sys.platform == 'win32':
            # Windows: 工具通常输出 GBK
            return 'gbk'
        else:
            # Linux/Mac: 使用 UTF-8
            return 'utf-8'
    return _SUBPROCESS_ENCODING

def ExportCMDLog(readline):
    for line in iter(readline, ""):
        if line:
            # 移除行尾的空白字符（包括换行符）
            PrintLog(line.rstrip())
        if len(line) == 0:
            break


## [val_encoding] On Windows, 'utf-8' UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position in Python.
def RUNCMD(command, val_encoding=None, bignore_error_for_no_termination = False, bSync=True):
    # 如果没有指定编码，使用全局配置的编码
    if val_encoding is None:
        val_encoding = GetSubprocessEncoding()
    
    popen = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding=val_encoding,
        errors='replace',  # 将无法解码的字符替换为 � 而不是忽略
        bufsize=1,
    )

    PrintLog("[Command]: " + command)

    # stdout, stderr = popen.communicate()

    # print(stdout)
    # print(stderr)

    # if popen.returncode == 0:
    #     print("Success RunCommand: ", popen.args)
    # else:
    #     print("[Error] -Code: %d RunCommand: " % (popen.returncode), popen.args)

    thread1 = threading.Thread(target=ExportCMDLog, args=(popen.stdout.readline,))
    thread2 = threading.Thread(target=ExportCMDLog, args=(popen.stderr.readline,))

    # Start Threads
    thread1.start()
    thread2.start()

    ## Sync or Async
    if bSync == True:
        ## Wait For Them to complete
        thread1.join()
        thread2.join()
        ##PrintLog("[Command Complete]: " + command)
       

        ## wait for the process to complete
        popen.wait() # This will block until the command completes

    if not bignore_error_for_no_termination and popen.returncode != 0:
        PrintErr(f"ErrorCode[{popen.returncode}] RunCommand Failed [{command}]")
        sys.exit(popen.returncode)

    PrintLog("[Command Complete]: " + command)

    #  if ret.returncode == 0:
    #     print("Success RunCommand: ", ret.args)
    # else:
    #     print("[Error] -Code: %d RunCommand: " % (ret.returncode), ret.args)
    # print(ret.stdout)
    # print(ret.stderr)

def RUNCMD_BUILDSYSTEM_CWD(command, logtitle = ""):
    original_cwd = Path.cwd()
    target_cwd = Path(__file__).parent.parent
    if logtitle == "":
        logtitle = "RUNCMD_BUILDSYSTEM_CWD"
    try:
        os.chdir(target_cwd)
        PrintLog(f"{logtitle} - change dir to project: {target_cwd}")
        RUNCMD(command)
    finally:
        os.chdir(original_cwd)
        PrintLog(f"{logtitle} - change dir back to {original_cwd}")
