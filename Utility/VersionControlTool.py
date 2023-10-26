

class VersionControlTool:
    VersionControlCommand = None
    def Init(VersionControlCommand):
        VersionControlTool.VersionControlCommand = VersionControlCommand

    def Get():
        return VersionControlTool.VersionControlCommand
    
    def CheckOutOneRepo(url):
        VersionControlTool.Get().GitVersion()

    def GitReset(url):
        print("Discard All Changes")
    