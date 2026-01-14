from Logger.Logger import *
from pathlib import Path
from ConfigParser import *
class UnrealConfigIniManager:
    
    def GenIniVal_Path(path):
        return "(Path=\"%s\")" % str(path).replace('\\', '/')

    def SetConfig_AndroidPackageName(path_uproject,package_name):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]","PackageName",package_name,True)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)


    def SetConfig_BundleIdentifier(path_uproject,bundle_val,buse_morden_xcode_project = False):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():

            if buse_morden_xcode_project == True:
                ## For Morden Xcode Project
                bundle_identifier_prefix = bundle_val
                UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","CodeSigningPrefix",bundle_identifier_prefix,True)
                UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","BundleIdentifier","$(UE_SIGNING_PREFIX).$(UE_PRODUCT_NAME_STRIPPED)",True)
            else:
                ## MobileProvision needs to be specified with a file name
                bundle_identifier = bundle_val
                UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","BundleIdentifier",bundle_identifier,True)

        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)

    def SetConfig_IOSCert_XCodeProject(path_uproject,signing_certificate,path_mobileprovision):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        str_path_mobileprovision = '(FilePath="' + str(path_mobileprovision) + '")'
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","bUseAutomaticCodeSigning","False")
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","IOSSigningIdentity",signing_certificate)
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","IOSProvisioningProfile",str_path_mobileprovision)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)

    def SetConfig_Mac_XCodeProject(path_uproject,signing_certificate):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","bUseAutomaticCodeSigning","False")
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/MacTargetPlatform.XcodeProjectSettings]","MacSigningIdentity",signing_certificate)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)

    def SetConfig_IOSCert_UEConfig(path_uproject,signing_certificate,mobile_provision):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","MobileProvision",mobile_provision)
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","SigningCertificate",signing_certificate)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)

    def SetConfig_IOSCert(path_uproject_file,params_ioscert,bUseMordenXcode = False):
        bRet = True
        if ConfigParser.Get().IsIOSCertValid(params_ioscert):
            OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(params_ioscert)
            
            if OneIOSCert == None:
                return False
            
            if bUseMordenXcode:
                UnrealConfigIniManager.SetConfig_IOSCert_XCodeProject(
                    path_uproject_file,
                    OneIOSCert.get_signing_identity,
                    OneIOSCert.get_filepath_mobileprovision
                )
            else:
                UnrealConfigIniManager.SetConfig_IOSCert_UEConfig(
                    path_uproject_file,
                    OneIOSCert.get_signing_identity,
                    OneIOSCert.get_filename_mobileprovision
                )

            bRet = True        
        else:
            bRet = False
        return bRet
    
    ## section etc = "[/Script/IOSRuntimeSettings.IOSRuntimeSettings]"
    def SetConfig(path_ini,section,key,val,bAppendIfNotFounded = True):

        path_ini = Path(path_ini)

        with open(path_ini,'r') as file:
            lines = file.readlines()

        bFoundedSection = False
        bSectionExists = False
        bFoundedKeyVal = False
        new_lines = []
        for line in lines:

            ## Check if it is a section
            if line.strip().startswith('[') and line.strip().endswith(']'):

                ## Precheck
                if bFoundedSection and not bFoundedKeyVal:
                    ## Only Found Section
                    ## Section was found but key=val was not fouond within it
                    ## add key=val
                    

                    ## Ex. section=[A] key=[K] val=[V]
                    # --> check section[B]
                    # --> it would add key-val line first
                    # --> then,  new_lines.append(line) ==> add section [B]
                    if bAppendIfNotFounded:
                        PrintLog("[ModifyConfig Ini] File[%s] Section[%s] AddKeyVal: Key[%s] -> NewVal[%s]"%(path_ini.name,section,key,val))
                        new_lines.append(f'{key}={val}\n\n\n')
                        bFoundedKeyVal = True


                if line.strip() == section:
                    bFoundedSection = True
                    bSectionExists = True
                else:
                    bFoundedSection = False

            elif bFoundedSection and line.strip().startswith(key + '='):
                ### Found Section & Key=Val
                bFoundedKeyVal = True
                new_lines.append(f'{key}={val}\n')
                PrintLog("[ModifyConfig Ini] File[%s] Section[%s] ModifyKeyVal: Key[%s] -> NewVal[%s]"%(path_ini.name,section,key,val))
                continue
        
            new_lines.append(line)

        if bAppendIfNotFounded:
            if bSectionExists == False:
                ## if section not founded, append it at the end of the file
                new_lines.append("\n\n")
                new_lines.append(section +"\n")
                new_lines.append(f'{key}={val}\n')
                PrintLog("[ModifyConfig Ini] File[%s] Add All At The Bottom:  Section[%s]: Key[%s] -> NewVal[%s]"%(path_ini.name,section,key,val))
            elif not bFoundedKeyVal:
                ## to the end, not found the key-val
                new_lines.append("\n")
                new_lines.append(f'{key}={val}\n')
                PrintLog("[ModifyConfig Ini] File[%s] Add All At The Bottom:  Section[%s]: Key[%s] -> NewVal[%s]"%(path_ini.name,section,key,val))


        with open(path_ini, 'w') as file:
            file.writelines(new_lines)

    @staticmethod
    def GetConfig(path_ini, section, key):
        if not path_ini.exists():
            return None
        
        with open(path_ini, 'r') as file:
            lines = file.readlines()
        
        in_section = False
        target_section = section.strip()
        target_key = key.strip()

        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                # Case insensitive check for section
                if line.lower() == target_section.lower():
                    in_section = True
                else:
                    in_section = False
            elif in_section and '=' in line:
                # Handle possible spaces around =
                parts = line.split('=', 1)
                current_key = parts[0].strip()
                if current_key.lower() == target_key.lower():
                    return parts[1].strip()
                
        return None

    @staticmethod
    def GetBundleIdentifier(path_ini, project_name):
        # 1. Try IOS Runtime Settings
        bundle_id = UnrealConfigIniManager.GetConfig(path_ini, "[/Script/IOSRuntimeSettings.IOSRuntimeSettings]", "BundleIdentifier")
        
        # 2. Try Mac Target Settings
        if not bundle_id:
            bundle_id = UnrealConfigIniManager.GetConfig(path_ini, "[/Script/MacTargetPlatform.XcodeProjectSettings]", "BundleIdentifier")
            
        # 3. Check for Macros or Failure
        if not bundle_id or "$(" in bundle_id:
            # Resolve Prefix
            prefix = UnrealConfigIniManager.GetConfig(path_ini, "[/Script/IOSRuntimeSettings.IOSRuntimeSettings]", "CodeSigningPrefix")
            if not prefix:
                prefix = UnrealConfigIniManager.GetConfig(path_ini, "[/Script/MacTargetPlatform.XcodeProjectSettings]", "CodeSigningPrefix")
            
            if not prefix:
                prefix = "io.agora"
            
            # Construct ID
            bundle_id = f"{prefix}.{project_name}"
            PrintLog(f"UnrealConfigIniManager - Resolved Bundle ID from prefix: {bundle_id}")
        else:
            PrintLog(f"UnrealConfigIniManager - Read Bundle ID: {bundle_id}")
            
        return bundle_id

