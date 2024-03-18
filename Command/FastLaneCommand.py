from Command.CommandBase import *

## brew install ruby
## sudo gem install sigh

class FastLaneCommand:
    None

    def IPAResign(self,path_ipa,signing_identity,provisioning_profile):
        command = (
            r'fastlane sigh resign  "' + str(path_ipa) +'" --signing_identity '+ '"' + signing_identity + '" '+ '-p ' + '"' +provisioning_profile + '"'
        )

        RUNCMD(command)
