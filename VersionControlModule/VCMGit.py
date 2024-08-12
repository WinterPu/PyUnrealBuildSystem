from git import Repo
from pathlib import Path
import logging

from git.remote import RemoteProgress

from VersionControlModule.VCMBase import *

import os

class GitProgress(RemoteProgress):
    # def update(self,op_code,cur_count,max_count=None,message=''):
    #     print(f"{op_code}:{cur_count} / {max_count or 'Unknown'} {message}")
    def update(self,*args):
        print(self._cur_line)
    def line_dropped(self, line: str):
        print(line)


class VCMGit(VCMBase):
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return VCMGit()


    __GitProgressIns = None
    def __init__(self) -> None:
        super().__init__()
        self.__GitProgressIns = GitProgress()
        
        # Log
        os.environ['GIT_PYTHON_TRACE'] = 'full'
        logging.basicConfig(level=logging.DEBUG)

    def GetModuleName():
        return str(VCMType.Git)
    

    ## API Wrapper
    def CheckOutOneRepo(self,url,to_path, branch=""):
        repo_name = url.split('/')[-1].split('.git')[0]
        dst_repo_path = Path(to_path).joinpath(repo_name)
        PrintLog(f"{repo_name} ->Status[{dst_repo_path.exists()}] : str({dst_repo_path})")
        if dst_repo_path.exists():
            repo =  Repo(dst_repo_path)
            repo.head.reset(index=True,working_tree=True)
            repo_remote =repo.remote()
            repo_remote.pull()
            
        else:
            return self.clone_from(url,dst_repo_path,branch)

    ## Native
    def clone_from(self,url,to_path,branch):
        repo =  Repo.clone_from(url=url,to_path=to_path,branch= branch,progress=self.__GitProgressIns)
        assert repo.__class__ is Repo
        return repo
