# PyUnrealBuildSystem
Unreal Build System with Python

## Usage

### Platform
1. Use Windows to build [Win,Android]
2. Use Mac to build [Mac,IOS]


### Main
1. UBS.py: Unreal Build System
   1. UBSHelper.py: handle Unreal related Args from UBS
2. APM.py: Agora Plugin Manager
3. ABS.py = UBS.py + APM.py: Agora Build System



### Example
```
python ABS.py -uprojectpath='/Users/admin/Documents/Agora-Unreal-RTC-SDK/Agora-Unreal-SDK-Blueprint-Example/AgoraBPExample.uproject' -enginever=5.4 -ioscert="D" -BuildUEProject -agorasdk="4.4.0" -targetplatform=IOS -AddPostXcodeBuild

python ABS.py -uprojectpath='/Users/admin/Documents/Agora-Unreal-RTC-SDK/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject'  -enginever=5.4 -ioscert="D" -BuildUEProject -agorasdk="4.4.0" -targetplatform=IOS -AddPostXcodeBuild

python ABS.py -uprojectpath='/Users/admin/Documents/Agora-Unreal-RTC-SDK/Agora-Unreal-SDK-CPP-Example/AgoraExample.uproject'  -ioscert="D" -BuildUEProject -agorasdk="4.4.0" -targetplatform=IOS -AddPostXcodeBuild -SkipClean -SkipCopySDKToProject

### Test Plugin
python ABS.py -TestAgoraPlugin -QuerySDK -agorasdk="4.5.0" -BuildPluginEngineList="5.5+5.4+5.3" 

```
