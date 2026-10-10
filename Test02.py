from Command.UnrealPakCommand import *
from pathlib import Path

params = ParamsUnrealPak()
params.pak_file_path = str(Path("C:/Users/WinterPu/Desktop/BasicCookDemo/Windows/BasicCook/Content/Paks/BasicCook-Windows.pak"))
params.source_path = str(Path("C:/Users/WinterPu/Desktop/BasicCookDemo/"))
params.encryption_key = ""
params.extra_commands = ""

OneCommand = UnrealPakCommand(Path("D:/.T-GameEngine/UE_5.6/Engine/Binaries/Win64/UnrealPak.exe"))
OneCommand.ExtractPak(params)

