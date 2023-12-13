from Platform.PlatformBase import *
import os

class AndroidPlatformBase(PlatformBase):
    def GenTargetPlatformParams(args):
        ret = True
        val = {}

        key = "platform"
        val[key] = "Android"

        key = "project_path"
        val[key] = args.projectpath if 'projectpath' in args else None


        key = "enginever"
        val[key] = args.enginever if 'enginever' in args else "4.27"
        ### [TBD]
        ## validate project

        return ret,val


class AndroidTargetPlatform(BaseTargetPlatform):
    def SetupEnvironment(self):
        print("SetupEnvironment - %s Platform" % self.GetTargetPlatform())
        engine_ver = self.GetParamVal("enginever")
        PrintLog("Before Modification: NDKROOT:  %s" % os.environ['NDKROOT'])
        PrintLog("Before Modification: NDK_ROOT:  %s" % os.environ['NDK_ROOT'])
        path_ndk = Path(os.environ['NDKROOT'])
        if engine_ver == "4.27" or engine_ver == "4.25":
            final_ndk_path = path_ndk.parent.joinpath("21.4.7075529")
            os.environ['NDKROOT'] = str(final_ndk_path)
        else:
            final_ndk_path = path_ndk.joinpath("25.1.8937393")
            os.environ['NDKROOT'] = str(final_ndk_path)

        PrintLog("Cur NDKROOT:  %s" % os.environ['NDKROOT'])
        PrintLog("Cur NDK_ROOT:  %s" % os.environ['NDK_ROOT'])

    def Package(self):
        self.SetupEnvironment()
        print("Package - %s Platform" % self.GetTargetPlatform())

        params = {}
        params["platform"] = self.GetParamVal("platform")
        params["project_path"] = self.GetParamVal("project_path")
        self.RunUAT().BuildCookRun(params)