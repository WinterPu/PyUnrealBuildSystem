from Utility.HeaderBase import *
from Utility.VersionControlTool import *
import argparse

## Command Tool for Version Control Tool
version_info = {}
class VersionControlCmdTool:
    def Init():
        pass
 
    def Start():
        PrintStageLog("Start Version Control Tool")
        VersionControlCmdTool.Init()


        ## 
        args = VersionControlCmdTool.ParseCMDArgs()
        VersionControlCmdTool.CreateTask(args)



    def ParseCMDArgs():
        ArgParser = argparse.ArgumentParser(description="Parse Package Args")


        ## Utility Command
        ArgParser.add_argument("-GitClone", action='store_true')
        ArgParser.add_argument("-GitRevert", action='store_true')
        ArgParser.add_argument("-GitClean", action='store_true')
        ArgParser.add_argument("-GenProject", action='store_true')
        ArgParser.add_argument("-url", default="git@github.com:AgoraIO-Extensions/Agora-Unreal-RTC-SDK.git")
        ArgParser.add_argument("-dstpath", default=Path("C:/Users/admin/Documents/Unreal Projects/"))
        ArgParser.add_argument("-branch", default=Path("main"))

        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args
        

    def CreateTask(Args):
        if Args.GitClone == True:
            url = Args.url
            dstpath = Args.dstpath
            branch = Args.branch
            VersionControlTool.Get().CGit_CheckOutOneRepo(url,dstpath,branch)

if __name__ == '__main__':
    VersionControlCmdTool.Start()