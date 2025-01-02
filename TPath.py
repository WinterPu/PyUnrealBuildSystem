## Tool For Path
import argparse
from pathlib import Path
ArgParser = argparse.ArgumentParser(description="Windows Path")
ArgParser.add_argument("-v", default="")
ArgParser.add_argument("-p", action="store_true")
ArgParser.add_argument("-r", action="store_true")
ArgParser.add_argument("-d", action="store_true")
Args = ArgParser.parse_args()
val = Args.v
if val != "":
    path = Path(val)
    if Args.p:
        path = path.parent
    path_str = str(path)
    if Args.r: ## forward slash
        path_str = path_str.replace('\\', '/')
    if Args.d: ## double backslash
        path_str = path_str.replace('\\', '\\\\')
    print(path_str)

