


from VersionControlModule.VCMBase import *
class VCMSVN(VCMBase):
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return VCMSVN()

    def __init__(self) -> None:
        super().__init__()

    def GetModuleName():
        return str(VCMType.SVN)