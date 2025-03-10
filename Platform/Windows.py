from Platform.PlatformBase import *
from Command.UBTCommand import *
from Command.WwiseCommand import *
from WPMHelper import * 
from pathlib import Path

from UBSHelper import *

import os
from packaging import version
import xml.etree.ElementTree as ET
import xml.dom.minidom
class WinPlatformPathUtility:
    def GetRunUATPath():
        ## if you start with '/', it would be treated as starting from the root path
        return Path("Engine/Build/BatchFiles/RunUAT.bat")

    def GetRunIOSPackager():
        return Path("Engine/Binaries/DotNET/IOS/IPhonePackager.exe")

    def GetUBTPath():
        path  = Path("Engine/Binaries/DotNET/UnrealBuildTool.exe")

        if UBSHelper.Get().Is_UE53_Or_Later():
            path = Path("Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.exe")

        return path
    
    def GetUBTConfigPath():
        path = Path(os.environ['APPDATA']) / "Unreal Engine" / "UnrealBuildTool" / "BuildConfiguration.xml"
        return path
    
    def GetDefaultMSVCInstalledDir(vs_version):
        path = Path(os.environ['PROGRAMFILES']) / "Microsoft Visual Studio" / vs_version / Path("Community/VC/Tools/MSVC")
        return path


class WinPlatformBase(PlatformBase):
    def GenHostPlatformParams(args):
        ret, val = PlatformBase.GenHostPlatformParams(args)

        key = "uat_path"
        val["uat_path"] = UBSHelper.Get().GetPath_UEEngine() / WinPlatformPathUtility.GetRunUATPath()

        return ret, val

    def GenTargetPlatformParams(args):
        ret, val = PlatformBase.GenTargetPlatformParams(args)

        # key = "target_platform"
        # val[key] = "Win64"
        
        PrintLog("PlatformBase - GenParams")
        return ret, val


class WinHostPlatform(BaseHostPlatform):
    def GenerateProject(self, path_uproject_file):
        ## uproject file could be any uproject file, not only the target project
        ubt_path = Path(UBSHelper.Get().GetPath_UEEngine()) / Path(WinPlatformPathUtility.GetUBTPath())

        one_command = UBTCommand(ubt_path)

        params = ParamsUBT()
        params.path_uproject_file = path_uproject_file

        one_command.GenerateProjectFiles(params)
        PrintLog("BaseHostPlatform - GenerateProject")


class WinTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.Win64_TargetName()
    
    def SetupEnvironment(self):
        print("SetupEnvironment - Win Platform")
        PrintLog("[Win] UnrealBuildTool - SetupEnvironment: Engine Path [%s]" % UBSHelper.Get().GetVer_UEEngine())
        if UBSHelper.Get().Is_UE55_Or_Later():
            self.SetupEnvironment_UnrealBuildTools(False)
        elif  UBSHelper.Get().Is_UE4_Or_Earlier():
            pass
        else:
            ##  UE4 < Version < UE5.5
            msvc_ver = self.FindHighestCompatibleMSVCVersion(max_version="14.38.33130")
            self.SetupEnvironment_UnrealBuildTools(True,msvc_ver)

        self.CleanPreviousArchivedBuild()
    
    ## TBD(WinterPu) Optimize the method 
    def SetupEnvironment_UnrealBuildTools(self,enable : bool, msvc_ver: str = "14.43.34808", vs_version = "VisualStudio2022"):
        ## Set MSVC Version UnrealBuildTool used
        PrintLog(f"[Win] UnrealBuildTool - SetupEnvironment: Enable {enable} MSVC Version {msvc_ver}")

        config_path = WinPlatformPathUtility.GetUBTConfigPath()

        # read XML File
        namespace = "https://www.unrealengine.com/BuildConfiguration"
        ET.register_namespace('', namespace)
        
        if config_path.exists():
            tree = ET.parse(config_path)
            root = tree.getroot()
        else:
            PrintErr("Cannot find BuildConfiguration.xml")
            return
        

        if enable:

            windows_platform = root.find(f".//{{{namespace}}}WindowsPlatform")
            
            if windows_platform is None:
                ## if not exists: create one
                windows_platform = ET.SubElement(root, "WindowsPlatform")
                compiler = ET.SubElement(windows_platform, "Compiler")
                compiler.text = vs_version
                version_elem = ET.SubElement(windows_platform, "CompilerVersion")
                version_elem.text = msvc_ver
            else:
                ## if exists: update the version
                ## TBD(WinterPu) Check XML Find Logic
                version_elem = windows_platform.find(f"{{{namespace}}}CompilerVersion")
                if version_elem is not None and version_elem.text != msvc_ver:
                    version_elem.text = msvc_ver
        else:
            ## delete the WindowsPlatform node
            windows_platform = root.find(f".//{{{namespace}}}WindowsPlatform")
            PrintLog(f"Remove WindowsPlatform Node: {windows_platform}")
            if windows_platform is not None:
                root.remove(windows_platform)

        # format xml and save the file
        xmlstr = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf-8')).toprettyxml(indent="  ")
        # remove whitespace
        xmlstr = '\n'.join(line for line in xmlstr.split('\n') if line.strip())

        config_path.write_text(xmlstr, encoding='utf-8')

    def FindHighestCompatibleMSVCVersion(self,max_version="14.38.33130"):
        ## find the [highest msvc version] which is < max_version limit:
        try:
            vs_ver = "2022"
            msvc_base_path = WinPlatformPathUtility.GetDefaultMSVCInstalledDir(vs_ver)
            
            if not msvc_base_path.exists():
                PrintWarn(f"Cannot Find msvc base path {msvc_base_path}")
                return None
                
            # Get All MSVC Versions
            versions = []
            for dir_path in msvc_base_path.iterdir():
                if dir_path.is_dir():
                    try:
                        ver = version.parse(dir_path.name)
                        versions.append((ver, dir_path.name))
                    except version.InvalidVersion:
                        ## Skip the invalid folder name
                        continue
            
            if not versions:
                PrintWarn("Cannot find any installed MSVC Versions")
                return None
                
            # ranking
            versions.sort(reverse=True)
            
            # find the highest version which is < max_version
            max_ver = version.parse(max_version)
            compatible_version = None
            
            for ver, ver_str in versions:
                if ver < max_ver:
                    compatible_version = ver_str
                    break
            
            if compatible_version:
                return compatible_version
            else:
                PrintWarn(f"cannot find version < {max_version} version")
                return None
        except Exception as e:
            PrintWarn(f"failed to find highest msvc version, error {e}")
            return None
        
    def Package(self):
        self.SetupEnvironment()
        PrintStageLog("Package - %s Platform" % self.GetTargetPlatform())

        params = ParamsUAT()
        params.target_platform = self.GetTargetPlatform()
        params.path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        params.path_engine = UBSHelper.Get().GetPath_UEEngine()
        params.path_archive = UBSHelper.Get().GetPath_ArchiveDirBase()
        params.skip_build_editor = UBSHelper.Get().ShouldSkipBuildEditor()
        
        self.RunUAT().BuildCookRun(params)

        self.PostPackaged()

        self.ArchiveProduct()

    
    def PostPackaged(self):
        PrintStageLog("PostPackaged - Win")

        path_archive_dir = UBSHelper.Get().GetPath_ArchiveDir(self.GetTargetPlatform())
        self.SetArchivePath_FinalProductDir(path_archive_dir)
    

    def CleanPreviousArchivedBuild(self):
        ## UE would not clean the previous archived build by default
        ## if you don't clean them
        ## Ex. it would archive the app built by 5.5 to the folder which contains the app built by 5.4

        ## Ex. error example: 
        ## Plugin 'OpenImageDenoise' failed to load because module 'OpenImageDenoise' could not be found.  Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project.

        ## Delete Default ArchiveBuild
        PrintLog(f"CleanPreviousArchivedBuild - {self.GetTargetPlatform()}")
        path_default_archive_build = UBSHelper.Get().GetPath_DefaultArchiveDir(self.GetTargetPlatform())
        if path_default_archive_build.exists():
            FileUtility.DeleteDir(path_default_archive_build)



#####################################################################################
#################################### Wwise ##########################################
    def Package_Wwise(self):
        WPMHelper.Get().CleanWwiseProject()

        list_config = ["Debug","Profile","Release"]
        arch = "x64"
        toolset = WPMHelper.Get().GetWindowsToolsetList()
        not_build_black_list = WPMHelper.Get().GetWindowsToolsetBuildBlackList()
       
        OneWwiseCommand = WwiseCommand()
        OneWwiseCommand.path_project = WPMHelper.Get().GetPath_WPProject()
        OneWwiseCommand.path_wp = WPMHelper.Get().GetPath_WwiseWPScript()
        
        one_param_premake = ParamsWwisePluginPremake()
        ## Authoring would generate all platforms
        one_param_premake.platform = "Authoring"
        OneWwiseCommand.Premake(one_param_premake)

        for one_config in list_config:
            one_param = ParamsWwisePluginBuild()
            one_param.config = one_config
            one_param.arch = arch

            for one_toolset in toolset:
                if one_toolset in not_build_black_list:
                    PrintLog("Skip Build - %s" % one_toolset)
                    continue
                one_param.toolset = one_toolset
                one_param.platform = "Windows_" + one_toolset
                OneWwiseCommand.Build(one_param)
        
        PrintStageLog("Win64 - Package_Wwise Build Complete")
        
        ## Archive
        ## Final Product 
        for one_config in list_config:
            for one_toolset in toolset:
                if one_toolset in not_build_black_list:
                    PrintLog("Skip Archive - %s" % one_toolset)
                    continue

                OneArchiveInfo = ArchiveInfo_WwisePlugin(
                    WPMHelper.Get().GetName_WwisePluginName(),
                    WPMHelper.Get().GetVer_Wwise(),
                    SystemHelper.Win64_TargetName(),
                    one_config,
                    arch,
                    one_toolset
                )
                extension = "dll"
                name_final_product = OneArchiveInfo.GetArchiveName()   + "."  + extension
                path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() / ( arch + "_" + one_toolset) / one_config / "bin" / name_final_product
                PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
                bshould_clean_others_when_archving = False
                ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

                extension = "lib"
                name_final_product = OneArchiveInfo.GetArchiveName()  + "."   + extension
                path_target_archive_file = WPMHelper.Get().GetPath_WwiseSDKBase() / ( arch + "_" + one_toolset) / one_config  / "bin" / name_final_product
                PrintWarn("Src Wwise Final Product [%s]" % path_target_archive_file)
                bshould_clean_others_when_archving = False
                ArchiveManager.Get().ArchiveBuild(path_target_archive_file,OneArchiveInfo,bshould_clean_others_when_archving,extension)

        PrintStageLog("Win64 - Package_Wwise Archive Complete")