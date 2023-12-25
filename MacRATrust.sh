#!/bin/bash

## Resolving Trusted Execution Problems
### 1. 'XXXX.framework' can't be opened because Apple cannot check it for malicious software.
### 2. 'AppXXX is damaged and can’t be opened. You should move it to the Trash'

echo $1

PathToYourProject=$1

if [ -z "" ]
then
    PathToYourProject="/Users/admin/Documents/LLS/AgoraExample/"
fi

echo $PathToYourProject
for file in $(ls "${PathToYourProject}/Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/Mac/Release");
do
    sudo xattr -r -d com.apple.quarantine "${PathToYourProject}/Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/Mac/Release/${file}"
done