#!/bin/bash

ProjectPath="/Users/admin/Documents/Agora-Unreal-SDK-CPP-Example"
MacFrameworkPath="Plugins/AgoraPlugin/Source/ThirdParty/AgoraPluginLibrary/Mac/Release"
DstPath="${ProjectPath}/${MacFrameworkPath}"

helpFunction()
{
   echo ""
   echo "Usage: $0 -P parameterA -D parameterB"
   echo -P "\t-P Project Path"
   echo -D "\t-D DstPath: [ProjectPath/MacFrameworkPath], we will finally use this path"
   echo ""
   echo "=== Resolving Trusted Execution Problems === "
   echo "1. 'XXXX.framework' can't be opened because Apple cannot check it for malicious software."
   echo "2. 'AppXXX is damaged and can’t be opened. You should move it to the Trash'"
   exit 1 # Exit script after printing help
}

while getopts ":P:D:" opt
do
   case "$opt" in
      P ) ArgProjectPath="$OPTARG" ;;
      D ) ArgDstPath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done


if [ -n "$ArgProjectPath" ] && [ -z "$ArgDstPath" ]
then
   DstPath="${ArgProjectPath}/${MacFrameworkPath}"
elif [ -n "$ArgDstPath" ]
then
   echo "===== Directly Set DstPath ====="
   DstPath="${ArgDstPath}"
fi

echo "[ProjectPath] = $ProjectPath"
echo "[DstPath] = $DstPath "

for file in $(ls "${DstPath}");
do
    sudo xattr -r -d com.apple.quarantine "${DstPath}/${file}"
done