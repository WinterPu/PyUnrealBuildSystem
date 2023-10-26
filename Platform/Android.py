from Platform.PlatformBase import *

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