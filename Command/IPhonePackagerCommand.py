
from Command.CommandBase import *
from pathlib import Path

class ParamsIPhonePacakger:
    def __init__(self) -> None:
        self.__path_uproject_file = ""
        self.__name_bundle = ""
        self.__certficate = ""
        self.__provision = ""
        self.__subcommand_extras = ""

    @property
    def get_path_uproject_file(self):
        return self.__path_uproject_file
    @property
    def get_name_bundle(self):
        return self.__name_bundle
    @property
    def get_certificate(self):
        return self.__certficate
    @property
    def get_provision(self):
        return self.__provision
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras

    @get_path_uproject_file.setter
    def path_uproject_file(self,val):
        self.__path_uproject_file = val
    @get_name_bundle.setter
    def bunndle_name(self,val):
        self.__name_bundle = val
    @get_certificate.setter
    def certificate(self,val):
        self.__certficate = val
    @get_provision.setter
    def provision(self,val):
        self.__provision = val
    @get_subcommand_extras.setter
    def extra_commands(self,val):
        self.__subcommand_extras = val


class IPhonePackagerCommand:
    __monopath = None
    __iphonepackagerpath = None
    def __init__(self, monopath_val,iphonepackagerpath_val) -> None:
        self.__monopath = monopath_val
        self.__iphonepackagerpath = iphonepackagerpath_val

    ## List Certificate
        
    ## install Certificate

    def SignMatch(self,params:ParamsIPhonePacakger):

        path_uproject_file = params.get_path_uproject_file
        name_bundle = params.get_name_bundle
        subcommand_extras = params.get_subcommand_extras

        command = (
                '"' + str(self.__monopath) + '"' + ' "' + str(self.__iphonepackagerpath) + '" '
                r" signing_match " + '"' + str(path_uproject_file) + '"' + 
                r" -bundlename " + name_bundle  + " " + 
                subcommand_extras
             )
        RUNCMD(command)

    def Sign(self,params:ParamsIPhonePacakger):
        path_uproject_file = params.get_path_uproject_file
        name_bundle = params.get_name_bundle
        certificate = params.get_certificate
        provision  = params.get_provision
        subcommand_extras = params.get_subcommand_extras

        command = (
                '"' + str(self.__monopath) + '"' + ' "' + str(self.__iphonepackagerpath) + '" '
                r" certificates " + '"' + str(path_uproject_file) + '"' + 
                r" -bundlename " + name_bundle  + " " + 
                r" -provision " + '"' + str(provision) + '"' + 
                r" -certificate " + '"' + str(certificate) + '"' + 
                subcommand_extras
             )
        RUNCMD(command)
