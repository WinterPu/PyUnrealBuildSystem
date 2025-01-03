from Command.CommandBase import *
from pathlib import Path
from SystemHelper import *
import os 


class LipoCommand:
    def __init__(self) -> None:
        pass

    def CreateUniversalArch(self,path_output,path_x8664,path_arm64):
        command = (
            "lipo -create " + " -output " + str(path_output) + " "  + str(path_x8664) + " " + str(path_arm64) 
        )
        RUNCMD(command)