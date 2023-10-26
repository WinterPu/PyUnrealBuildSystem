import json
import os
from Utility.HeaderBase import *

path_val = r"/Users/admin/Documents/PyUnrealBuildSystem/Config/Config.json"

class ConfigParser:
    def ParseConfig(local_path):
        ## [TBD]
        path = path_val
        file_json = open(path)
        print("Parse Config")
        json_data = json.load(file_json)
        PrintLog(json_data)
        json_data['UEEnginePath'] = '/Users/admin/Documents/'
        PrintLog(json_data)
        

    

    