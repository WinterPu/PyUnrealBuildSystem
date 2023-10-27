from CommandBase.Command import *
from pathlib import Path

class UATCommand:
    uatpath= Path("/Users/Shared/Epic Games/UE_5.2/Engine/Build/BatchFiles/RunUAT.sh")
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

        command = (
            '"' + str(self.uatpath) + '"' +
            r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
            r" -targetplatform="+platform+
            r" -clientconfig=Development"
            r" -Build"
            r" -Cook"
            r" -Stage"
            r" -Archive"
            r" -package"+
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
            r" BuildPlugin  -plugin="+ str(plugin_path)+
            r" -targetplatform="+platform+
            r" -package="+ output_path +
            r" -rocket"+ # means precompiled & installed engine version
            extra_commands
         )
        RUNCMD(command)