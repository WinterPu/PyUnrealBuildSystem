from Utility.HeaderBase import *
from ConfigParser import *
from Utility.VersionControlTool import *

from Command.GitCommand import *

import argparse

import platform

version_info = {}
class VersionContrlTool:

    def Start():
        PrintStageLog("Start Version Control Tool")
        VersionContrlTool.Init()


        ## 
        args = VersionContrlTool.ParseCMDArgs()
        VersionContrlTool.CreateTask(args)

    def Init():
        return

    def ParseCMDArgs():
        ArgParser = argparse.ArgumentParser(description="Parse Package Args")


        ## Utility Command
        ArgParser.add_argument("-GitClone", action='store_true')
        ArgParser.add_argument("-GitRevert", action='store_true')
        ArgParser.add_argument("-GitClean", action='store_true')
        ArgParser.add_argument("-GenProject", action='store_true')
        ArgParser.add_argument("-url", default="git@github.com:AgoraIO-Extensions/Agora-Unreal-RTC-SDK.git")
        ArgParser.add_argument("-dstpath", default=Path("C:/Users/admin/Documents/Unreal Projects/"))

        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args
        

    def CreateTask(Args):
        if Args.GitClone == True:
            url = Args.url
            dstpath = Args.dstpath
            OneGitCommand = GitCommand()
            VersionControlTool.Init(OneGitCommand)
            VersionControlTool.CheckOutOneRepo(url,dstpath)

if __name__ == '__main__':
    VersionContrlTool.Start()