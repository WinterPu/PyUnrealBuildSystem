from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
from SystemHelper import *


class ParamsUnrealPak:
    def __init__(self) -> None:
        self.__pak_file_path = ""  # 输出的.pak文件路径
        self.__source_path = ""  # 源文件路径或响应文件路径
        self.__mount_point = ""  # 挂载点
        self.__compress = False  # 是否压缩
        self.__encrypt = False  # 是否加密
        self.__encrypt_index = False  # 是否加密索引
        self.__encryption_key = ""  # 加密密钥
        self.__subcommand_extras = ""

    @property
    def get_pak_file_path(self):
        return self.__pak_file_path
    
    @property
    def get_source_path(self):
        return self.__source_path
    
    @property
    def get_mount_point(self):
        return self.__mount_point
    
    @property
    def get_compress(self):
        return self.__compress
    
    @property
    def get_encrypt(self):
        return self.__encrypt
    
    @property
    def get_encrypt_index(self):
        return self.__encrypt_index
    
    @property
    def get_encryption_key(self):
        return self.__encryption_key
    
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras if self.__subcommand_extras else ""

    @get_pak_file_path.setter
    def pak_file_path(self, val):
        self.__pak_file_path = val
    
    @get_source_path.setter
    def source_path(self, val):
        self.__source_path = val
    
    @get_mount_point.setter
    def mount_point(self, val):
        self.__mount_point = val
    
    @get_compress.setter
    def compress(self, val: bool):
        self.__compress = val
    
    @get_encrypt.setter
    def encrypt(self, val: bool):
        self.__encrypt = val
    
    @get_encrypt_index.setter
    def encrypt_index(self, val: bool):
        self.__encrypt_index = val
    
    @get_encryption_key.setter
    def encryption_key(self, val):
        self.__encryption_key = val
    
    @get_subcommand_extras.setter
    def extra_commands(self, val):
        self.__subcommand_extras = val


class UnrealPakCommand:
    """
    UnrealPak 用于创建、提取和管理 PAK 文件
    PAK 文件是 Unreal Engine 的资源打包格式，用于将多个资源文件打包成单个文件
    """
    __unrealpak_path = Path("/Users/Shared/Epic Games/UE_5.6/Engine/Binaries/Mac/UnrealPak")
    __host_platform = ""

    def __init__(self, unrealpak_path_val) -> None:
        self.__unrealpak_path = unrealpak_path_val
        self.__host_platform = SystemHelper.Get().GetHostPlatform()

    def CreatePak(self, params: ParamsUnrealPak):
        """
        创建 PAK 文件
        将指定目录或文件列表打包成 .pak 文件
        """
        pak_file_path = params.get_pak_file_path
        source_path = params.get_source_path
        mount_point = params.get_mount_point
        compress = params.get_compress
        encrypt = params.get_encrypt
        encrypt_index = params.get_encrypt_index
        encryption_key = params.get_encryption_key
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__unrealpak_path) + '"' +
            r' "' + str(pak_file_path) + '"' +  # 输出的PAK文件路径
            r' -create="' + str(source_path) + '"' +  # 源路径（目录或响应文件）
            (r' -mountpoint="' + str(mount_point) + '"' if mount_point else '') +  # 挂载点，指定PAK内文件的虚拟路径根目录
            (r' -compress' if compress else '') +  # 压缩PAK文件以减小体积
            (r' -encrypt' if encrypt else '') +  # 加密PAK文件内容
            (r' -encryptindex' if encrypt_index else '') +  # 加密PAK文件索引
            (r' -encryptionkey="' + str(encryption_key) + '"' if encryption_key else '') +  # AES加密密钥（64位十六进制）
            subcommand_extras
        )
        RUNCMD(command)

    def ExtractPak(self, params: ParamsUnrealPak):
        """
        解压 PAK 文件
        将 PAK 文件内容解压到指定目录
        """
        pak_file_path = params.get_pak_file_path
        source_path = params.get_source_path  # 这里作为输出目录
        encryption_key = params.get_encryption_key
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__unrealpak_path) + '"' +
            r' "' + str(pak_file_path) + '"' +  # 要解压的PAK文件路径
            r' -extract' +  # 解压命令
            r' "' + str(source_path) + '"' +  # 解压目标目录
            (r' -encryptionkey="' + str(encryption_key) + '"' if encryption_key else '') +  # 如果PAK加密，需提供解密密钥
            subcommand_extras
        )
        RUNCMD(command)

    def ListPak(self, params: ParamsUnrealPak):
        """
        列出 PAK 文件内容
        显示 PAK 文件中包含的所有文件及其信息
        """
        pak_file_path = params.get_pak_file_path
        encryption_key = params.get_encryption_key
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__unrealpak_path) + '"' +
            r' "' + str(pak_file_path) + '"' +  # PAK文件路径
            r' -list' +  # 列出内容命令
            (r' -encryptionkey="' + str(encryption_key) + '"' if encryption_key else '') +  # 如果PAK加密，需提供解密密钥
            subcommand_extras
        )
        RUNCMD(command)

    def TestPak(self, params: ParamsUnrealPak):
        """
        测试 PAK 文件完整性
        验证 PAK 文件是否损坏或有错误
        """
        pak_file_path = params.get_pak_file_path
        encryption_key = params.get_encryption_key
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__unrealpak_path) + '"' +
            r' "' + str(pak_file_path) + '"' +  # PAK文件路径
            r' -test' +  # 测试命令
            (r' -encryptionkey="' + str(encryption_key) + '"' if encryption_key else '') +  # 如果PAK加密，需提供解密密钥
            subcommand_extras
        )
        RUNCMD(command)