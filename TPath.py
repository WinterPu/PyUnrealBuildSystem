## Tool For Path
import argparse
from pathlib import Path
ArgParser = argparse.ArgumentParser(description="Windows Path")
ArgParser.add_argument("-v", default="")
ArgParser.add_argument("-p", action="store_true")
ArgParser.add_argument("-r", action="store_true")
Args = ArgParser.parse_args()
val = Args.v
if val != "":
    path = Path(val)
    if Args.p:
        path = path.parent
    path_str = str(path)
    if Args.r:
        path_str = path_str.replace('\\', '\\\\')
    print(path_str)
