from Utility.HeaderBase import *
import argparse

class _template_mananger_():
    __instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__initialized = False
        return cls.__instance
    
    def __init__(self) -> None:
        if not self.__initialized: 
            super().__init__()
            self.__initialized = True
    
    def Get():
        return _template_mananger_()


    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse _template_mananger_ Args")
        
        self.AddArgsToParser(ArgParser)

        Args = ArgParser.parse_args()

        PrintLog(Args)
        return Args
    
    def AddArgsToParser(self,ArgParser, bIncludeConflictArgs = True):
        ArgParser.add_argument('-wwisever',default="2024.1.0.8669")
        if bIncludeConflictArgs:
            pass
    
    def Init(self):
        PrintStageLog("_template_mananger_ Init")

    def Start(self):
        _template_mananger_.Get().Init()
        args = self.ParseCMDArgs()
        self.CreateTask(args)

    def CreateTask(self,Args):
        pass



if __name__ == '__main__':
    _template_mananger_.Get().Start()