from Logger.Logger import *
from pathlib import Path
from ConfigParser import *
class UnrealConfigIniManager:
    
    def GenIniVal_Path(path):
        return "(Path=\"%s\")" % path

    def SetConfig_AndroidPackageName(path_uproject,package_name):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]","PackageName",package_name,True)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)


    def SetConfig_BundleIdentifier(path_uproject,bundle_identifier):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
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
            if bUseMordenXcode:
                UnrealConfigIniManager.SetConfig_IOSCert_XCodeProject(path_uproject_file,OneIOSCert["signing_identity"],OneIOSCert["path_mobileprovision"])
            else:
                UnrealConfigIniManager.SetConfig_IOSCert_UEConfig(path_uproject_file,OneIOSCert["signing_identity"],OneIOSCert["name_mobileprovision"])

            bRet = True        
        else:
            bRet = False
        return bRet
    
    ## section etc = "[/Script/IOSRuntimeSettings.IOSRuntimeSettings]"
    def SetConfig(path_ini,section,key,val,bAppendIfNotFounded = False):

        path_ini = Path(path_ini)

        with open(path_ini,'r') as file:
            lines = file.readlines()

        bFoundedSection = False
        bSectionExists = False
        bHasAddedKeyVal = False
        new_lines = []
        for line in lines:
            if line.strip().startswith('[') and line.strip().endswith(']'):

                ## Precheck
                if bFoundedSection and not bHasAddedKeyVal:
                    ## Only Found Section
                    ## Section was found but key=val was not fouond within it
                    ## add key=val
                    
                    if bAppendIfNotFounded:
                        PrintLog("[ModifyConfig Ini] File[%s] Section[%s] AddKeyVal: Key[%s] -> NewVal[%s]"%(path_ini.name,section,key,val))
                        new_lines.append(f'{key}={val}\n\n\n')
                        bHasAddedKeyVal = True


                if line.strip() == section:
                    bFoundedSection = True
                    bSectionExists = True
                else:
                    bFoundedSection = False

            elif bFoundedSection and line.strip().startswith(key + '='):
                ### Found Section & Key=Val
                bHasAddedKeyVal = True
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

        with open(path_ini, 'w') as file:
            file.writelines(new_lines)

