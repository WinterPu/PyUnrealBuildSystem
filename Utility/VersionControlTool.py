from Utility.HeaderBase import *

## using command
from Command.GitCommand import *

## using modules
from VersionControlModule.VCMGit import * 

## Version
from packaging.version import parse 


class VersionControlTool:
    __instance = None
    __GitCommand = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__initialized = False
        return cls.__instance
    
    def __init__(self) -> None:
        if not self.__initialized: 
            super().__init__()

            ## Init
            self.__GitCommand = GitCommand()

            self.__initialized = True

    def Get():
        return VersionControlTool()

    ## Utility API 
    def VerParse(self,version):
        return parse(version)


    ### APIs

    ## Command Git Method [CheckOutOneRepo]
    def CGit_CheckOutOneRepo(self,url,dstpath,branch_name =""):
        self.__GitCommand.GitVersion()

        repo_name = url.split('/')[-1].split('.git')[0]
        dst_repo_path = Path(dstpath).joinpath(repo_name)

        PrintLog(f"{repo_name}: Status[{dst_repo_path.exists()}] - dst_repo_path[{str(dst_repo_path)}]")
        if(dst_repo_path.exists()):
            self.__GitCommand.GitReset(dst_repo_path)
            self.__GitCommand.GitFetch(dst_repo_path)
            if branch_name != "":
                self.__GitCommand.GitCheckout(dst_repo_path,branch_name)
            else:
                self.__GitCommand.GitPull(dst_repo_path)
        else:
            self.__GitCommand.GitClone(url,dst_repo_path)
            self.__GitCommand.GitCheckout(dst_repo_path,branch_name)

    ## Module Git Method [CheckOutOneRepo]
    def MGit_CheckOutOneRepo(self,url,dstpath,branch_name =""):
        VCMGit.Get().CheckOutOneRepo(url,dstpath,branch_name)


    def GitReset(url):
        print("Discard All Changes")
    