from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
from SystemHelper import *

from Command.GenerateProjectFilesWithShellCommand import *

class ParamsUAT:
    def __init__(self) -> None:
        self.__path_uproject_file = ""
        self.__target_platform = ""
        self.__path_archive = ""
        self.__path_log = ""
        self.__subcommand_extras = ""

        ## Plugin 
        self.__path_uplugin_file = ""
        self.__path_plugin_output_dir = ""

    @property
    def get_path_uproject_file(self):
        return self.__path_uproject_file
    @property
    def get_target_platform(self):
        return self.__target_platform
    
    @property
    def get_subcommand_archive_dir(self):
        subcommand = ""
        str_path_archive = str(self.__path_archive)
        if str_path_archive and len(str_path_archive) > 0:
            subcommand = ' -archivedirectory="' +str_path_archive+'" '
        return subcommand
    
    @property
    def get_subcommand_log(self):
        return (r" -log=" + '"' + str(self.__path_log) + '"') if self.__path_log != "" else ""
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras
    
    ## BuildPlugin 
    @property
    def get_path_plugin_output_dir(self):
        return self.__path_plugin_output_dir
    
    @property
    def get_path_uplugin_file(self):
        return self.__path_uplugin_file
    

    @get_path_uproject_file.setter
    def path_uproject_file(self,val):
        self.__path_uproject_file = val

    @get_target_platform.setter
    def target_platform(self,val):
        self.__target_platform = val
    
    @get_subcommand_archive_dir.setter
    def path_archive(self,val):
        self.__path_archive = val

    @get_subcommand_log.setter
    def path_log(self,val):
        self.__path_log = val
    @get_subcommand_extras.setter
    def extra_commands(self,val):
        self.__subcommand_extras = val

    ## BuildPlugin
    @get_path_uplugin_file.setter
    def path_uplugin_file(self,val):
        self.__path_uplugin_file = val

    @get_path_plugin_output_dir.setter
    def path_plugin_output_dir(self,val):
        self.__path_plugin_output_dir = val


class UATCommand:
    __uatpath = Path("/Users/Shared/Epic Games/UE_5.2/Engine/Build/BatchFiles/RunUAT.sh")
    __host_platform = ""
    __path_genproj_script = ""
    def __init__(self, uatpath_val,path_script_genproj = "") -> None:
        self.__uatpath = uatpath_val
        self.__host_platform = SystemHelper.Get().GetHostPlatform()
        if self.__host_platform == SystemHelper.Mac_HostName():
            self.__path_genproj_script = path_script_genproj

    def BuildCookRun(self,params:ParamsUAT):
        ### Command

        target_platform = params.get_target_platform
        path_uproject_file = params.get_path_uproject_file
        subcommand_archive_dir = params.get_subcommand_archive_dir
        subcommand_extras = params.get_subcommand_extras

        # ## need 
        # command = (
        #     '"' + str(self.uatpath) + '"' +
        #     r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
        #     r" -targetplatform="+platform+
        #     r" -SkipBuildEditor"
        #     r" -clientconfig=Development"
        #     r" -Build"
        #     r" -GenerateDSYM"
        #     r" -Cook"
        #     r" -Stage"
        #     r" -Archive"
        #     r" -package"
        #     r" -verbose"+
        #     extra_commands
        #  )
        # RUNCMD(command)


        

        ## Step 01: BuildEditor

    
        platform_editor = "Mac"

        if self.__host_platform == SystemHelper.Win_HostName():
            
            if target_platform == SystemHelper.IOS_TargetName():
                PrintErr("TBD - Not Ready, Packaging IOS on Windows Platform")
                return
            
            if target_platform == SystemHelper.Mac_TargetName():
                PrintErr("Not Support, Packaging Mac on Windows Platform")
                return
            
            platform_editor = "Win"

        elif self.__host_platform == SystemHelper.Mac_HostName():

            if target_platform == SystemHelper.Android_TargetName():
                PrintErr("TBD - Not Ready, Packaging Android on Mac Platform")
                return
            
            if target_platform == SystemHelper.Win64_TargetName():
                PrintErr("Not Support, Packaging Win on Mac Platform")
                return


            platform_editor = "Mac"


        command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                #r" -allmaps -pak"
                r" -Stage"
                r" -Archive"
                r" -package"
                r" -verbose"+
                subcommand_extras
        
        )
        
        RUNCMD(command)




        ## Step 02: BuildCookRun

        if target_platform == SystemHelper.IOS_TargetName():
            
            ## Gen UE Project On Mac
            OneGenerateProjectFilesWithShellCommand = GenerateProjectFilesWithShellCommand(self.__path_genproj_script)
            params_genwithshell = ParamsGenProjectWithShell()
            params_genwithshell.path_uproject_file = path_uproject_file
            OneGenerateProjectFilesWithShellCommand.GenerateProjectFiles(params_genwithshell)

            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + subcommand_archive_dir +
                r" -package"
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

        elif target_platform == SystemHelper.Mac_TargetName() :

            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -CookAll"
                r" -Stage"
                r" -Archive" + subcommand_archive_dir + 
                r" -package"
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

        else:

            ## [TBD] blueprint project also needs 2 times build
            
            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + subcommand_archive_dir +
                r" -package"
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

    

    def BuildPlugin(self,params:ParamsUAT):
        ## Command
        target_platform = params.get_target_platform
        path_uplugin_file = params.get_path_uplugin_file
        path_plugin_output = params.get_path_plugin_output_dir
        subcommand_extras = params.get_subcommand_extras

        command = (
            "\"" + str(self.__uatpath) + "\"" +
            r" BuildPlugin  -plugin="+ '"' + str(path_uplugin_file) + '"'+
            r" -TargetPlatforms="+target_platform+
            r" -package="+ '"' + str(path_plugin_output) + '"'+
            r" -rocket"+ # means precompiled & installed engine version
            subcommand_extras
        )
        RUNCMD(command)