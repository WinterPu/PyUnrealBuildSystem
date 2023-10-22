from PlatformBase import *


def WinPlatform(PlatformBase):
    def SetupEnvironment():
        print("SetupEnvironment - Win Platform")

    def Package():
        SetupEnvironment()
        print("Package - Win Platform")
