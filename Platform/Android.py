from Platform.PlatformBase import *

class AndroidPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret = True
        val = {}

        key = "platform"
        val[key] = "Android"

        key = "project_path"
        val[key] = args.projectpath if 'projectpath' in args else None
        ### [TBD]
        ## validate project

        return ret,val


class AndroidTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())

        params = {}
        params["platform"] = self.GetParamVal("platform")
        params["project_path"] = self.GetParamVal("project_path")
        self.RunUAT().BuildCookRun(params)