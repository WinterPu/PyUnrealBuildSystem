from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path

class UATCommand:
    uatpath = Path("/Users/Shared/Epic Games/UE_5.2/Engine/Build/BatchFiles/RunUAT.sh")
    def __init__(self, uatpath_val) -> None:
        self.uatpath = uatpath_val

    def BuildCookRun(self,params):
        ### Command
        key = "platform"
        platform = params[key] if key in params else ""

        key = "project_path"
        project_path = params[key] if key in params else ""

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""

        key = "engine_path"
        engine_path = params[key] if key in params else ""

        key = 'host_platform'
        hostplatfom = params[key] if key in params else ""

        key = "archive_dir"
        archive_dir = params[key] if key in params else ""
        param_command_archive_dir = ""
        if archive_dir and len(archive_dir) > 0:
            param_command_archive_dir = ' -archivedirectory="' + archive_dir+'" '

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

        if platform == "IOS":
            
            if hostplatfom == "Win":
                PrintErr("TBD - Not Ready, Packaging IOS on Windows Platform")
                return
            
            from Platform.Mac import MacPlatformPathUtility
            script_path = Path(engine_path) / MacPlatformPathUtility.GetGenerateProjectScriptPath()
            
            command = (
                '"' + str(script_path) + '"' + 
                r" -project="+ '"'  + str(project_path) + '"'
                r" -game"+
                extra_commands
            )
            RUNCMD(command)

            command = (
                '"' + str(self.uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
                r" -targetplatform="+platform+
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"
                r" -package"
                r" -verbose"+
                extra_commands
             )
            RUNCMD(command)

            command = (
                '"' + str(self.uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
                r" -targetplatform="+platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + param_command_archive_dir +
                r" -package"
                r" -verbose"+
                extra_commands
            )
            RUNCMD(command)

        elif platform == "Mac" :
            
            command = (
                '"' + str(self.uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
                r" -targetplatform="+platform+
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                #r" -allmaps -pak"
                r" -Stage"
                r" -Archive"
                r" -package"
                r" -verbose"+
                extra_commands
             )
            RUNCMD(command)

            command = (
                '"' + str(self.uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
                r" -targetplatform="+platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -CookAll"
                r" -Stage"
                r" -Archive" + param_command_archive_dir + 
                r" -package"
                r" -verbose"+
                extra_commands
            )
            RUNCMD(command)

        else:
            command = (
                '"' + str(self.uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
                r" -targetplatform="+platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + param_command_archive_dir +
                r" -package"
                r" -verbose"+
                extra_commands
            )
            RUNCMD(command)

    def BuildPlugin(self,params):
        ## Command
        key = "platform"
        platform = params[key] if key in params else ""

        key = "plugin_path"
        plugin_path = params[key] if key in params else ""

        key = "output_path"
        output_path = params[key] if key in params else ""   

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""    


        command = (
            "\"" + str(self.uatpath) + "\"" +
            r" BuildPlugin  -plugin="+ '"' + str(plugin_path) + '"'+
            r" -TargetPlatforms="+platform+
            r" -package="+ '"' + str(output_path) + '"'+
            r" -rocket"+ # means precompiled & installed engine version
            extra_commands
        )
        RUNCMD(command)