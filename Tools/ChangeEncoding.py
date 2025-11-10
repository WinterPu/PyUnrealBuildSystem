import os
import chardet

def convert_to_utf8(file_path):
    # 检测文件编码
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    # 如果编码不是 UTF-8，则进行转换
    if encoding and encoding.lower() != 'utf-8':
        try:
            # 读取文件内容并转换为 UTF-8
            text = raw_data.decode(encoding)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Converted {file_path} from {encoding} to UTF-8.")
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")

def walk_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.h', '.cpp')):
                file_path = os.path.join(root, file)
                convert_to_utf8(file_path)

if __name__ == "__main__":
    target_directory = './LeetcodeChallenge'
    walk_directory(target_directory)