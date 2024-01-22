from Platform.PlatformBase import *

class IOSPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret,val = PlatformBase.GenTargetPlatformParams(args)
        
        key = "platform"
        val[key] = "IOS"

        # key = "project_path"
        # val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        return ret,val
    

class IOSTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())
        self.RunUAT().BuildCookRun(self.Params)