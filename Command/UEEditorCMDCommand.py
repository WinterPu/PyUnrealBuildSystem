from Command.CommandBase import *
from UBSHelper import *
from pathlib import *
from SystemHelper import *

class UEEditorCMDCommandUtility():
    def GetPath_DefaultUEBinaries(path_engine_base,host_platform):
        platform = "Win64"
        if host_platform == SystemHelper.Mac_HostName():
            platform = "Mac"
        return Path(path_engine_base) / Path("Engine/Binaries") / Path(platform) 
    
    def GetName_UEEditor(host_platform,is_ue4,is_cmd):
        name = "UnrealEditor"
        if is_ue4:
            name = "UE4Editor"

        if is_cmd:
            name = name + "-Cmd"
        
        if host_platform == SystemHelper.Win_HostName():
            name = name + ".exe"
        
        return name


## Unreal CommandLet 
class UEEditorCMDCommand:
    def GetPath_UEEditorCMD(self):
        path_engine_base = UBSHelper.Get().GetPath_UEEngine()
        host_platform = SystemHelper.Get().GetHostPlatform()
        is_ue4 = UBSHelper.Get().Is_UE4_Or_Earlier()
        name_cmd =  UEEditorCMDCommandUtility.GetName_UEEditor(host_platform,is_ue4,is_cmd = True)
        return UEEditorCMDCommandUtility.GetPath_DefaultUEBinaries(path_engine_base,host_platform) / name_cmd
    

# UnrealEditor.exe [GameName or .uproject] -run=cook -targetplatform=[Platform] -cookonthefly -iterate -map=[Map Name]
    def RUNUECMD_Cook(self):
        path_uproject = UBSHelper.Get().GetPath_UProjectFile()
        path_ueeditor = self.GetPath_UEEditorCMD()
        target_platform = UBSHelper.Get().GetTargetPlatform()
        command = (
            f'{path_ueeditor} "{str(path_uproject)}"  -run=cook -targetplatform={target_platform} -cookonthefly -iterate'
        )
        RUNCMD(command)