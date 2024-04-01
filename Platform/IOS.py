from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
from ConfigParser import *

from UBSHelper import *

class IOSPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)
        
        # key = "target_platform"
        # val[key] = "IOS"

        key = "ioscert"
        val[key] = args.ioscert

        key = "iosbundleidentifier"
        val[key] = args.iosbundlename

        return ret,val
    

class IOSTargetPlatform(BaseTargetPlatform):
    def GetTargetPlatform(self):
        return SystemHelper.IOS_TargetName()
    
    def SetupEnvironment(self):
        PrintLog("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

        path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        
        if ConfigParser.Get().IsIOSCertValid(self.Params['ioscert']):
            OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(self.Params['ioscert'])
            UnrealConfigIniManager.SetConfig_IOSCert(path_uproject_file,OneIOSCert["signing_identity"],OneIOSCert["name_mobileprovision"])
            PrintLog("IOSTargetPlatform - SetupEnvironment Certificate %s Set Done!" %self.Params['ioscert'] )
        else:
            PrintErr("IOSTargetPlatform - SetupEnvironment Certificate Set Failed")

        
        UnrealConfigIniManager.SetConfig_BundleIdentifier(path_uproject_file,self.Params['iosbundleidentifier'])

    def Package(self):
        self.SetupEnvironment()
        PrintStageLog("Package - %s Platform" % self.GetTargetPlatform())

        params = ParamsUAT()
        params.target_platform = self.GetTargetPlatform()
        params.path_uproject_file = UBSHelper.Get().GetPath_UProjectFile()
        params.path_engine = UBSHelper.Get().GetPath_UEEngine()
        params.path_archive = UBSHelper.Get().GetPath_ArchiveDirBase()

        self.RunUAT().BuildCookRun(params)