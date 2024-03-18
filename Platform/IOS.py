from Platform.PlatformBase import *
from Utility.UnrealConfigIniManager import *
from ConfigParser import *
class IOSPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)
        
        key = "platform"
        val[key] = "IOS"

        key = "ioscert"
        val[key] = args.ioscert

        key = "iosbundleidentifier"
        val[key] = args.iosbundlename

        # key = "project_path"
        # val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        return ret,val
    

class IOSTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        PrintLog("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

        if ConfigParser.Get().IsIOSCertValid(self.Params['ioscert']):
            OneIOSCert = ConfigParser.Get().GetOneIOSCertificate(self.Params['ioscert'])
            UnrealConfigIniManager.SetConfig_IOSCert(self.Params['project_path'],OneIOSCert["signing_identity"],OneIOSCert["name_mobileprovision"])
            PrintLog("IOSTargetPlatform - SetupEnvironment Certificate %s Set Done!" %self.Params['ioscert'] )
        else:
            PrintErr("IOSTargetPlatform - SetupEnvironment Certificate Set Failed")

        UnrealConfigIniManager.SetConfig_BundleIdentifier(self.Params['project_path'],self.Params['iosbundleidentifier'])

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())
        self.RunUAT().BuildCookRun(self.Params)