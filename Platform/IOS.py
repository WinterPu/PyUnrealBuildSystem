from Platform.PlatformBase import *

class IOSPlatformBase(PlatformBase):
    def GenTargetPlatformParams(params):
        ret = True
        val = {}

        key = "platform"
        val[key] = "IOS"

        key = "project_path"
        val[key] = params[key] if key in params else None
        ### [TBD]
        ## validate project

        return ret,val
    

class IOSTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())

        params = {}
        params["platform"] = self.GetParamVal("platform")
        params["project_path"] = self.GetParamVal("project_path")
        self.RunUAT().BuildCookRun(params)