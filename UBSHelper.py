from pathlib import Path

class UBSHelper():
    _instance = None
    _Args = None

    _archive_dir = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    
    def Get():
        return UBSHelper()
    
    def Init(self,Args):
        self.Args = Args

        self._archive_dir = str(Path(Args.projectpath).parent / Args.archive_dir)

    def GetArchiveDir(self):
        return self._archive_dir
    
    def GetHostPlatform(self):
        pass




    