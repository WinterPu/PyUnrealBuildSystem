from Logger.Logger import *
from pathlib import Path
class UnrealConfigIniManager:
    
    def GenIniVal_Path(path):
        return "(Path=\"%s\")" % path

    def SetConfig_BundleIdentifier(path_uproject,bundle_identifier):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","BundleIdentifier",bundle_identifier,True)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)


    def SetConfig_IOSCert(path_uproject,signing_certificate,mobile_provision):
        path = Path(path_uproject)
        path_ini = path.parent / "Config" / "DefaultEngine.ini"
        if path_ini.exists():
           ## MobileProvision needs to be specified with a file name
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","MobileProvision",mobile_provision)
           UnrealConfigIniManager.SetConfig(path_ini,"[/Script/IOSRuntimeSettings.IOSRuntimeSettings]","SigningCertificate",signing_certificate)
        else:
            PrintErr("Config Ini File [%s] Not Found" %path_ini)

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

