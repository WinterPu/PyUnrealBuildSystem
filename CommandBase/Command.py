import subprocess
import threading

from Utility.HeaderBase import *


def ExportCMDLog(readline):
    for line in iter(readline, ""):
        PrintLog(line)
        if len(line) == 0:
            break


def RUNCMD(command):
    popen = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="ISO-8859-1", ## On Windows, 'utf-8' UnicodeDecodeError: ‘utf-8’ codec can’t decode byte 0x92 in position in Python. 
        bufsize=1,
    )

    PrintLog("[Command]: "+command)

    # stdout, stderr = popen.communicate()

    # print(stdout)
    # print(stderr)

    # if popen.returncode == 0:
    #     print("Success RunCommand: ", popen.args)
    # else:
    #     print("[Error] -Code: %d RunCommand: " % (popen.returncode), popen.args)

    thread1 = threading.Thread(target=ExportCMDLog, args=(popen.stdout.readline,))
    thread2 = threading.Thread(target=ExportCMDLog, args=(popen.stderr.readline,))
    thread1.start()
    thread2.start()

    #  if ret.returncode == 0:
    #     print("Success RunCommand: ", ret.args)
    # else:
    #     print("[Error] -Code: %d RunCommand: " % (ret.returncode), ret.args)
    # print(ret.stdout)
    # print(ret.stderr)
