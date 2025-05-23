from pathlib import Path
from Logger.Logger import *
from ConfigParser import *
from SystemHelper import *
from Utility.VersionControlTool import *

class UBSHelper():
    __instance = None
    
    __Args = None

    __path_engine = None
    __ver_engine = None
    __path_uproject_file = None
    __path_archive_dir_base = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def Get():
        return UBSHelper()
    
    def Init(self,Args):
        ## Init with Args from UBS
        self.__Args = Args
        self.__InitInner_UProjectFile(Args)
        self.__InitInner_EngineVer(Args)
        self.__InitInner_EnginePath(Args)
        self.__InitInner_ArchiveDir(Args)

    def __InitInner_UProjectFile(self,Args):
        self.__path_uproject_file = Path(Args.uprojectpath)
    
    def __InitInner_EngineVer(self,Args):
        self.__ver_engine = Args.enginever

    def __InitInner_EnginePath(self,Args):
        val_path_engine = Args.enginepath
        if val_path_engine == "" :
            val_path_engine = Path(ConfigParser.Get().GetDefaultEnginePath(Args.enginever))
        PrintLog("[UBS] Check UE Engine Path: IsCustom[%s] UseEnginePath[%s] " %(str(Args.enginepath != ""),str(val_path_engine)) )
        self.__path_engine  = val_path_engine
        Args.enginepath = val_path_engine

    def __InitInner_ArchiveDir(self,Args):
        val_archive_dir = Args.archive_dir
        if val_archive_dir == "":
            val_archive_dir = Path(Args.uprojectpath).parent / "ArchivedBuilds"
        else:
            val_archive_dir = Path(Args.uprojectpath).parent / Args.archive_dir

        self.__path_archive_dir_base = val_archive_dir
        Args.archive_dir = val_archive_dir

    def GetName_AllIOSCertsArchiveDir(self):
        return "AllIOSCerts"


    def SetUEEngineWithVer(self,ver_engine):
        self.__Args.enginever = ver_engine
        self.__Args.enginepath = Path(ConfigParser.Get().GetDefaultEnginePath(ver_engine))
        self.__InitInner_EngineVer(self.__Args)
        self.__InitInner_EnginePath(self.__Args)

        
    def GetUBSArgs(self):
        return self.__Args
    
    def GetPath_UProjectFile(self):
        return self.__path_uproject_file
    
    def GetPath_ProjectRoot(self):
        return Path(self.__path_uproject_file).parent

    def GetPath_UEEngine(self):
        path_engine = self.__path_engine if self.__path_engine != None else ""
        return Path(path_engine)
    
    def GetVer_UEEngine(self):
        return self.__ver_engine
    
    def GetName_ArchiveDir(self,target_platform,ver_engine):
        folder_platform = target_platform
        if target_platform == SystemHelper.Mac_TargetName():
            if float(ver_engine) < 5:
                folder_platform = "MacNoEditor"
            else:
                folder_platform = "Mac"
        elif  target_platform == SystemHelper.Win64_TargetName():
            if float(ver_engine) < 5:
                folder_platform = "WindowsNoEditor"
            else:
                folder_platform = "Windows"
        return folder_platform

    def GetPath_ArchiveDirBase(self):
        return self.__path_archive_dir_base
    
    def GetPath_ArchiveDir(self,target_platform):
        ## Combine with the custom defined archive dir
        folder_platform = self.GetName_ArchiveDir(target_platform,self.GetVer_UEEngine())
        return Path(self.__path_archive_dir_base) / folder_platform
    
    def GetPath_DefaultArchiveDir(self,target_platform):
        folder_platform = self.GetName_ArchiveDir(target_platform,self.GetVer_UEEngine())
        return Path(self.__Args.uprojectpath).parent / "ArchivedBuilds" / folder_platform

    def GetPath_BinariesTargetDir(self,target_platform):
        if self.__Args == None:
            PrintErr(f"__Args None")
            return
        return Path(self.__Args.uprojectpath).parent / "Binaries" / target_platform
    
    def GetPath_Binaries(self):
        if self.__Args == None:
            PrintErr(f"__Args None")
            return

        return Path(self.__Args.uprojectpath).parent / "Binaries"
    
    def GetName_GenericPackagedAppName(self,target_platform,extra_tag = ""):
        if self.__Args == None:
            PrintErr(f"__Args None")
            return
        name_genericbase = Path(self.__Args.uprojectpath).stem
        name_app = "UnknownPlatform"
        if target_platform == SystemHelper.Win_InArgsTargetName() or target_platform == SystemHelper.Win64_TargetName():
            name_app = f"{name_genericbase}{extra_tag}.exe"
        elif  target_platform == SystemHelper.Mac_TargetName():
            name_app = f"{name_genericbase}{extra_tag}.app"
        elif target_platform == SystemHelper.IOS_TargetName():
            name_app = f"{name_genericbase}{extra_tag}.ipa"
        elif target_platform == SystemHelper.Android_TargetName():
            name_app = f"{name_genericbase}{extra_tag}.apk"

        return name_app
    

    def ShouldSkipBuildEditor(self) -> bool:
        if self.__Args == None:
            PrintErr(f"__Args None")
            return False

        return True if self.__Args.SkipBuildEditor else False
    

    def ShouldPackageWithAllIOSCerts(self) -> bool:
        if self.__Args == None:
            PrintErr(f"__Args None")
            return False
        
        return True if self.__Args.WithAllIOSCerts else False
    
  
### Archive Product Path

    def GetPath_FinalProduct(self,target_platform,bInBinaries = False):
        name_product = self.GetName_GenericPackagedAppName(target_platform)
        path = self.GetPath_ArchiveDir(target_platform) / name_product
        if bInBinaries:
            path = self.GetPath_BinariesTargetDir(target_platform) / name_product
        path = Path(path)
        PrintLog(f"**** Final Product Path: {path}")
        return path
    
###   

    def GetName_ProjectName(self,path_uproject_file = ""):
        if path_uproject_file == "":
            return Path(self.__path_uproject_file).stem
        else:
            return Path(path_uproject_file).stem
    

    def GetName_PackagedApp(self,target_platform):
        if  target_platform == SystemHelper.Mac_TargetName():
            return self.GetName_ProjectName() + ".app"
        else:
            PrintErr("Current Not Supported")
            return "TBD"

    def GetInfo_PluginNameAndUPluginFilePath(self,path_plugin_folder):
        ## search in path_plugin_folder to find upluign file. 
        ## get the plugin name the same as the uplugin file

        uplugin_files = list(Path(path_plugin_folder).rglob("*.uplugin"))
        path_uplugin_file = ""
        name_plugin = ""
        for uplugin_file in uplugin_files:
            if "__MACOSX" in str(uplugin_file):
                    ## not the target one
                    pass
            else:
                path_uplugin_file = Path(uplugin_file)
                name_plugin = Path(path_uplugin_file).stem
                PrintLog("[GetPluginInfo] plugin name [%s] uplugin file path: [%s] " % (name_plugin , str(path_uplugin_file)))
                if name_plugin != path_uplugin_file.parent.name:
                    PrintWarn("[GetPluginInfo] the plugin folder name [%s] is not equal to uplugin file name [%s]" %( path_uplugin_file.parent.name,name_plugin))
        
        return name_plugin, path_uplugin_file
    


    def Is_UE53_Or_Later(self):
        return VersionControlTool.Get().VerParse(self.__ver_engine) >= VersionControlTool.Get().VerParse("5.3.0")
    
    def Is_UE5_Or_Later(self):
        return VersionControlTool.Get().VerParse(self.__ver_engine) >= VersionControlTool.Get().VerParse("5.0.0")

    def Is_UE4_Or_Earlier(self):
        return VersionControlTool.Get().VerParse(self.__ver_engine) < VersionControlTool.Get().VerParse("5.0.0")
    
    def Is_UE55_Or_Later(self):
        ## UE5.5 requires a newer msvc version
        return VersionControlTool.Get().VerParse(self.__ver_engine) >= VersionControlTool.Get().VerParse("5.5.0")

    def DoesUseModernXcodeProject(self):
        return self.Is_UE53_Or_Later()

    def should_archive_product(self):
        return True if self.__Args.ArchiveProduct else False
    

    def should_clean_dir_before_archiving(self):
        return True if self.__Args.CleanOldArchives else False
    

    def GetTargetPlatform(self):
        if self.__Args == None:
            PrintErr(f"__Args None")
            return ""
        
        return self.__Args.targetplatform




    