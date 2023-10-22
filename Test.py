from CommandBase.Command import *
from Utility.UnrealProjectManager import *

# RUNCMD(["dir", "/b"])  # 序列参数
# RUNCMD("exit 1")  # 字符串参数


import argparse

# ArgParser = argparse.ArgumentParser(description="Test argparse")
# ArgParser.add_argument("-targetplatform", default="Win64")
# ArgParser.add_argument("-agorasdk", default="4.2.1")
# Args = ArgParser.parse_args()
# print(Args.targetplatform)
# print(Args.agorasdk)

# command = (
#     r"D:\GameEngine\UE_5.2\Engine\Build\BatchFiles\RunUAT.bat"
#     r" BuildCookRun  -project=C:\Users\admin\Documents\SVNRepo\ClientRepo\Trunk\UATTestProject\AgoraExample.uproject"
#     r" -targetplatform=Win64"
#     r" -Build"
#     r" -Cook"
#     r" -Stage"
#     r" -archive"
#     r" -package"
# )

# RUNCMD(command)


ProjectRootPath = r"C:\Users\admin\Documents\SVNRepo\ClientRepo\Trunk\UATTestProject"

UnrealProjectManager.CleanProject(ProjectRootPath)
