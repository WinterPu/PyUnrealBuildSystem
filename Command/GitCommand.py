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
            r" clone  --progress " + url + ' "' + str(dst_path) + '"'
        )

        RUNCMD(command)

    def GitReset(self,dst_path = ".",command =" --hard"):
        command = (
            r"git" + " -C " + '"' + str(dst_path) + '"' + 
            r" reset " + command
        )

        RUNCMD(command)

    def GitPull(self,dst_path = ".",command = ""):
        command = (
            r"git" + " -C " + '"' + str(dst_path) + '"' + 
            r" pull --progress " + command
        )

        RUNCMD(command)