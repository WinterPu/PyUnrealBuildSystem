from Utility.HeaderBase import *

class VersionControlTool:
    VersionControlCommand = None
    def Init(VersionControlCommand):
        VersionControlTool.VersionControlCommand = VersionControlCommand

    def Get():
        return VersionControlTool.VersionControlCommand
    
    def CheckOutOneRepo(url,dstpath):
        VersionControlTool.Get().GitVersion()

        repo_name = url.split('/')[-1].split('.git')[0]
        PrintLog(repo_name)
        dst_repo_path = Path(dstpath).joinpath(repo_name)
        PrintLog(dst_repo_path)
        PrintLog(dst_repo_path.exists())
        if(dst_repo_path.exists()):
            VersionControlTool.Get().GitReset(dst_repo_path)
            VersionControlTool.Get().GitPull(dst_repo_path)
        else:
            VersionControlTool.Get().GitClone(url,dst_repo_path)




    def GitReset(url):
        print("Discard All Changes")
    