import argparse
from pathlib import Path

def change_file_extension(directory, old_extension, new_extension):
    # 将目录转换为 Path 对象
    dir_path = Path(directory)
    
    # 遍历指定目录下所有文件
    for file_path in dir_path.glob(f'*{old_extension}'):
        # 构造新的文件名
        new_file_path = file_path.with_suffix(f".{new_extension}")
        # 重命名文件
        file_path.rename(new_file_path)
        print(f'Renamed: {file_path} to {new_file_path}')

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Change file extensions in a directory.')
    parser.add_argument('-path',default="", help='The directory to search files in.')
    parser.add_argument('-oldex',default="", help='The old file extension to change from.')
    parser.add_argument('-newex',default="", help='The new file extension to change to.')

    # 解析命令行参数
    args = parser.parse_args()

    # 调用函数
    change_file_extension(args.path, args.oldex, args.newex)

if __name__ == '__main__':
    main()