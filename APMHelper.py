from pathlib import Path
import shutil
from FileIO.FileUtility import *

class APMHelper:
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

            ## Init

            self.__initialized = True

    
    def Get():
        return APMHelper()
    
    def replace_in_file(self,file_path, content_replacements):
        content = file_path.read_text(encoding='utf-8')
        
        for old, new in content_replacements.items():
            content = content.replace(old, new)
        
        file_path.write_text(content, encoding='utf-8')

    def rename_file(self,file_path, name_replacements):
        new_filename = file_path.name
        
        ## replace [filename] if matches
        for old, new in name_replacements.items():
            new_filename = new_filename.replace(old, new)

        ## if [filename] replaced, return new [filepath]
        if new_filename != file_path.name:
            new_file_path = file_path.with_name(new_filename)
            file_path.rename(new_file_path)
            return new_file_path
        return file_path

    def rename_directory(self,directory, name_replacements):
        new_directory_name = directory.name
        
        for old, new in name_replacements.items():
            new_directory_name = new_directory_name.replace(old, new)

        if new_directory_name != directory.name:
            new_directory_path = directory.parent / new_directory_name
            directory.rename(new_directory_path)
            return new_directory_path
        return directory

    def should_exclude(self,item, exclude_paths):
        ## 1. covert [item] to the absolute path
        ## 2. covert [excluded] to the absolute path
        ## 3. check if [item] is a subpath of [excluded]
        ## 4. at any time the result is true, it would return true
        return any(Path(item).resolve().is_relative_to(Path(excluded).resolve()) for excluded in exclude_paths)

    def process_files_and_directories(self,directory, extensions, content_replacements, name_replacements, exclude_paths):
        
        # loop over files: 
        ## rglob [DFS]: so the parent would be replaced first
        ## Ex. 
        ## Src: AgoraPlugin/Source/AgoraPlugin/Public
        ## should be:AgoraVoicePlugin/Source/[AgoraVoicePlugin]/Plugin
        for item in directory.rglob('*'):
            if item.is_dir():

                if self.should_exclude(item, exclude_paths):
                    PrintLog(f"Exclude path {item}")
                    continue

                ## task01: rename the dir
                renamed_directory =  self.rename_directory(item, name_replacements)

                ## process all files in the currrent path:
                for file_path in renamed_directory.glob('*'):
                    if file_path.is_file() and any(file_path.suffix == ext for ext in extensions):
    
                        ## task01: rename the file
                        new_file_path = self.rename_file(file_path, name_replacements)
                        ## task02: replace the content
                        self.replace_in_file(new_file_path, content_replacements)
                        
            elif item.is_file() and any(item.suffix == ext for ext in extensions):

                if  self.should_exclude(item, exclude_paths):
                    PrintLog(f"Exclude file path {item}")
                    continue
                
                ## task01: rename the file
                new_file_path =  self.rename_file(item, name_replacements)
                ## task02: replace the content
                self.replace_in_file(new_file_path, content_replacements)

    def CopyDirWithContentReplaced(
                self,

                ## Ex.
                ## path_src_dir = Path('/Users/admin/Documents/PluginWorkDir/Agora-Unreal-RTC-SDK/Agora-Unreal-SDK-CPP/AgoraPlugin') 
                ## path_dst_dir = Path('/Users/admin/Documents/PluginWorkDir/Agora-Unreal-RTC-SDK/Agora-Unreal-SDK-CPP/AgoraVoicePlugin')

                path_src_dir,
                path_dst_dir,

                # pattern01: [extensions]: what kind of files need to be checked
                extensions = ['.cpp', '.h', '.cs', '.uplugin'],

                # pattern02: [content_replacements]: [old , new] replace the old one with the new one
                content_replacements = {
                    'AgoraPlugin': 'AgoraVoicePlugin',
                    'AGORAPLUGIN_API': 'AGORAVOICEPLUGIN_API',
                    'FAgoraPluginModule': 'FAgoraVoicePluginModule'
                },
                
                # pattern03: [name_replacements] [old , new] replace the old one with the new one
                name_replacements = {
                    'AgoraPlugin': 'AgoraVoicePlugin'  # 示例
                },

                ## Pattern04 [exclude_paths] : [already_replaced_path]
                # Ex.
                ## Src: AgoraPlugin/Source/AgoraPlugin/Public
                ## should be:AgoraVoicePlugin/Source/[AgoraVoicePlugin]/Plugin

                ## Ex. 
                # exclude_path01 = path_dst_dir / "Source/AgoraVoicePlugin/Public/AgoraCppPlugin/include"
                # exclude_paths = [exclude_path01] 
                exclude_paths = []
                ):
        
        if path_dst_dir.exists():
            FileUtility.DeleteDir(path_dst_dir)
        
        FileUtility.CopyDir(path_src_dir,path_dst_dir,True,bmac_use_shutil = True)
        
        self.process_files_and_directories(path_dst_dir, extensions, content_replacements, name_replacements, exclude_paths)



    
    

