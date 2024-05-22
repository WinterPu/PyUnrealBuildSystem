from Command.CommandBase import *

## brew install ruby
## sudo gem install sigh
from pathlib import Path

class FastLaneCommand:
    None

    def IPAResign(self,path_ipa,signing_identity,provisioning_profile):
        cwd = Path.cwd()
        path_abs_mobileprovision = cwd.joinpath(provisioning_profile).resolve()

        command = (
            r'fastlane sigh resign  "' + str(path_ipa) +'" --signing_identity '+ '"' + signing_identity + '" '+ '-p ' + '"' + str(path_abs_mobileprovision) + '"'
        )

        RUNCMD(command)
