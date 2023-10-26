from CommandBase.Command import *

class UATCommand:
    uatpath= "/Users/Shared/Epic\ Games/UE_5.2/Engine/Build/BatchFiles/RunUAT.sh"
    def __init__(self, uatpath_val) -> None:
        self.uatpath = uatpath_val

    def BuildCookRun(self,params):
        ### Command
        key = "platform"
        platform = params[key] if key in params else ""

        key = "project_path"
        project_path = params[key] if key in params else ""

        key = "extra_command"
        extra_commands = params[key] if key in params else ""


        project_path = "/Users/admin/Documents/Unreal Projects/Agora-Unreal-RTC-SDK-dev-4.2.1/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject"
        command = (
            self.uatpath+
            r" BuildCookRun  -project="+"'" +project_path+ "'"
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
            self.uatpath+
            r" BuildPlugin  -plugin="+plugin_path+
            r" -targetplatform="+platform+
            r" -package="+ output_path +
            r" -rocket"+ # means precompiled & installed engine version
            extra_commands
         )
        RUNCMD(command)