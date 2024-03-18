
from pathlib import Path
class PathConfiger:
    
    def GetMobileProvisionCachePath():
        return Path.home() / "Library" / "MobileDevice" / "Provisioning Profiles" 