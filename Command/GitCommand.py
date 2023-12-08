from Command.CommandBase import *

class GitCommand:
    def GetToolName(self):
        return "Git"
    def GitVersion(self):
        command = (
            r"git"
            r" -v"
        )

        RUNCMD(command)       

    def GitClone(self,url,dst_path = "."):
        command = (
             r"git"
            r" clone " + url + " " + dst_path
        )

        RUNCMD(command)

    def GitResetHard(self,dst_path = ".",command =" --hard"):
        command = (
            r"git" + " -C " + '"' + dst_path + '"' + 
            r" reset " + command
        )

        RUNCMD(command)

    def GitPull(self,dst_path = ".",command = ""):
        command = (
            r"git" + " -C " + '"' + dst_path + '"' + 
            r" pull " + command
        )

        RUNCMD(command)