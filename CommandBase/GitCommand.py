from CommandBase.Command import *

class GitCommand:
    def GetToolName(self):
        return "Git"
    def GitVersion(self):
        command = (
            r"git"
            r" -v"
        )

        RUNCMD(command)       

    def GitClone(self,url):
        command = (
            r"git"
            r" -clone " + url
        )

        RUNCMD(command)

    def GitRevert(self,path):
        command = (
            r"git"
            r" -revert " + path
        )

        RUNCMD(command)