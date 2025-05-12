command = (
    '"' + str(self.uatpath) + '"' +
    r" BuildCookRun -nocompileeditor -installed -nop4 -project=/Users/admin/Documents/AgoraExample/AgoraExample.uproject -cook -stage -archive -archivedirectory=/Users/admin/Documents/Build"
    r" -package -ue4exe='/Users/Shared/Epic Games/UE_4.27/Engine/Binaries/Mac/UE4Editor.app/Contents/MacOS/UE4Editor' -compressed -ddc=InstalledDerivedDataBackendGraph -pak -prereqs -nodebuginfo -targetplatform=Mac -build -target=AgoraExample -clientconfig=Development -utf8output" + 
    extra_commands
)