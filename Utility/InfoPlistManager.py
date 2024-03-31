import plistlib
from pathlib import Path

class InfoPlistManager:

    def GetInfoPListPath(path_app):
        return  Path(path_app) / "Contents"/ "Info.plist"
    
    def AddAgoraPermissionToInfoPlist(path_app):
        path_plist = InfoPlistManager.GetInfoPListPath(path_app)

        with open(path_plist,"rb") as file:
            data_plist = plistlib.load(file)

        data_plist['NSCameraUsageDescription'] = 'Agora Camera Permission'
        data_plist['NSMicrophoneUsageDescription'] = 'Agora Microphone Permission'

        with open(path_plist,"wb") as file:
            plistlib.dump(data_plist,file)

    
    def ModifyAppInfoPList(path_app,key,val):
        path_plist = InfoPlistManager.GetInfoPListPath(path_app)
        InfoPlistManager.ModifyInfoPlist(path_plist,key,val)

    def ModifyInfoPlist(path_plist,key,val):
        with open(path_plist,"rb") as file:
            data_plist = plistlib.load(file)

        data_plist[key] = val

        with open(path_plist,"wb") as file:
            plistlib.dump(data_plist,file)