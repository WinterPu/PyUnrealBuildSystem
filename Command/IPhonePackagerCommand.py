
from Command.CommandBase import *
from pathlib import Path


class IPhonePackagerCommand:
    monopath = None
    iphonepackagerpath = None
    def __init__(self, monopath_val,iphonepackagerpath_val) -> None:
        self.monopath = monopath_val
        self.iphonepackagerpath = iphonepackagerpath_val

    ## List Certificate
        
    ## install Certificate

    def SignMatch(self,params):
        key = "project_path"
        project_path = params[key] if key in params else ""

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""

        key = "bundlename"
        bundlename =  params[key] if key in params else ""

        command = (
                '"' + str(self.monopath) + '"' + ' "' + str(self.iphonepackagerpath) + '" '
                r" signing_match " + '"' + str(project_path) + '"' + 
                r" -bundlename " + bundlename  + " " + 
                extra_commands
             )
        RUNCMD(command)

    def Sign(self,params):
        key = "project_path"
        project_path = params[key] if key in params else ""

        key = "extra_commands"
        extra_commands = params[key] if key in params else ""

        key = "bundlename"
        bundlename =  params[key] if key in params else ""


        key = "certficate"
        certificate =  params[key] if key in params else ""

        key = "provision"
        provision =  params[key] if key in params else ""


        certificate = ""

        provision  = ""

        command = (
                '"' + str(self.monopath) + '"' + ' "' + str(self.iphonepackagerpath) + '" '
                r" certificates " + '"' + str(project_path) + '"' + 
                r" -bundlename " + bundlename  + " " + 
                # r" -provision " + '"' + str(provision) + '"' + 
                # r" -certificate " + '"' + str(certificate) + '"' + 
                extra_commands
             )
        RUNCMD(command)
