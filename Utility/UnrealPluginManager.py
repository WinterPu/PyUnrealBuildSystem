from FileIO.FileUtility import *
from Utility.HeaderBase import *
import json



class UnrealPluginManager:
    def BuildPlugin(path,UE_Ver):
        print("BuildPlugin")

    
    def UpdateUpluginFile():
        UPLUGIN_DEST_PATH = "./"
        UPLUGIN_FILE = "AgoraPlugin.uplugin"

        

        sdk_version = "4.2.1"
        min_engine_version = "5.3.0"
        support_platforms = "Win64+Mac+IOS+Android"
        marketplace_url = ""
        support_platforms = support_platforms.split("+")



        template_arr = {
            "FileVersion": 3,
            "Version": 1,
            "VersionName": "4.2.1", ####
            "FriendlyName": "AgoraPlugin",
            "EngineVersion": "5.3.0", ###
            "Description": "develop",
            "Category": "Other",
            "CreatedBy": "Agora",
            "CreatedByURL": "",
            "DocsURL": "",
            "MarketplaceURL": "", ###
            "SupportURL": "https://www.agora.io/en/",
            "CanContainContent": True,
            "IsBetaVersion": False,
            "IsExperimentalVersion": False,
            "Installed": False,
            "WhitelistPlatforms":["Win64","Mac","IOS","Android"],
            "Modules": [
                {
                    "Name": "AgoraPlugin",
                    "Type": "Runtime",
                    "LoadingPhase": "Default",
                    "PlatformAllowList":["Win64","Mac","IOS","Android"]
                }
            ]
        }


        ### Modification

        template_arr['VersionName'] = sdk_version
        template_arr['EngineVersion'] = min_engine_version
        if marketplace_url != "":
            template_arr['MarketplaceURL'] = marketplace_url
        template_arr['WhitelistPlatforms'] = support_platforms
        template_arr['Modules'][0]['PlatformAllowList'] = support_platforms

        ### 

        uplugin_json_str = json.dumps(template_arr, sort_keys=False, indent=4, separators=(',', ': '))
        print(uplugin_json_str)



        ### Save The File 
        file = open(os.path.join(UPLUGIN_DEST_PATH,UPLUGIN_FILE),'w')
        file.write(uplugin_json_str)
        file.close()