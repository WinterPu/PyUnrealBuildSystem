from Utility.HeaderBase import *
from SystemBase import *

from UBS import *
from WPM import *

from UBSHelper import *
# from WPMHelper import * 

from Command.WwiseCommand import *

class WwiseBuildSystem(BaseSystem):

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
        return WwiseBuildSystem()
    
    def Init(self):
        PrintStageLog("WwiseBuildSystem Init")
        PyUnrealBuildSystem.Get().Init()
        WwisePluginManager.Get().Init()

    def Start(self):
        WwiseBuildSystem.Get().Init()
        args = self.ParseCMDArgs()
        self.CreateTask(args)
    
    def ParseCMDArgs(self):
        ArgParser = argparse.ArgumentParser(description="Parse Wwise Demo Build Args")

        bIncludeConflictArgs = False
        PyUnrealBuildSystem.Get().AddArgsToParser(ArgParser,bIncludeConflictArgs)
        WwisePluginManager.Get().AddArgsToParser(ArgParser,bIncludeConflictArgs)

        self.AddArgsToParser(ArgParser)
        Args = ArgParser.parse_args()
        PrintLog(Args)
        return Args

    def AddArgsToParser(self,ArgParser,bIncludeConflictArgs = True):
        
        ArgParser.add_argument("-GenSoundBank", action="store_true")
        ArgParser.add_argument("-WwiseConsolePath", default="C:\\Program Files (x86)\\Audiokinetic\\Wwise2021.1.14.8108\\Authoring\\x64\\Release\\bin\\WwiseConsole.exe")
        ArgParser.add_argument("-WwiseProjectPath", default="")
        ArgParser.add_argument("-SoundBankDefinitionFile", default="")
        ArgParser.add_argument("-SoundBankList", default="")
        
        ArgParser.add_argument("-SoundBankPathAndroid", default="")
        ArgParser.add_argument("-SoundBankPathMac", default="")
        ArgParser.add_argument("-SoundBankPathWin", default="")
        ArgParser.add_argument("-SoundBankPathIOS", default="")
        
        ArgParser.add_argument("-UseStableGuid", action="store_true")

    def CreateTask(self,Args):
        UBSHelper.Get().Init(Args)
        
        if Args.GenSoundBank:
             self.GenerateSoundBank(Args)

        if Args.BuildCookRun:
             PyUnrealBuildSystem.Get().CreateTask(Args)

    def GenerateSoundBank(self, Args):
        PrintStageLog("Start Generate SoundBank")
        
        wwise_console = Args.WwiseConsolePath
        if not os.path.exists(wwise_console):
            PrintErr(f"Wwise Console not found at {wwise_console}")
            return
            
        params = ParamsWwiseConsoleGenerateSoundBank()
        params.project_path = Args.WwiseProjectPath
        params.use_stable_guid = Args.UseStableGuid
        
        if Args.SoundBankDefinitionFile:
             params.import_definition_file = Args.SoundBankDefinitionFile
             
        if Args.SoundBankList:
            params.add_bank(Args.SoundBankList)
            
        if Args.SoundBankPathAndroid:
            params.add_platform("Android", Args.SoundBankPathAndroid)
        if Args.SoundBankPathMac:
             params.add_platform("Mac", Args.SoundBankPathMac)
        if Args.SoundBankPathWin:
             params.add_platform("Windows", Args.SoundBankPathWin)
        if Args.SoundBankPathIOS:
             params.add_platform("iOS", Args.SoundBankPathIOS)

        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.GenerateSoundBank(wwise_console, params)

if __name__ == '__main__':
    WwiseBuildSystem.Get().Start()
