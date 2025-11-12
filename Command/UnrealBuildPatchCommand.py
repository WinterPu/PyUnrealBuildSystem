from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
from SystemHelper import *


class ParamsBuildPatchTool:
    def __init__(self) -> None:
        self.__mode = ""  # PatchGeneration, Enumeration, PackageChunks, etc.
        self.__build_root = ""
        self.__build_version = ""
        self.__app_name = ""
        self.__app_launch = ""
        self.__cloud_dir = ""
        self.__subcommand_extras = ""

    @property
    def get_mode(self):
        return self.__mode
    
    @property
    def get_build_root(self):
        return self.__build_root
    
    @property
    def get_build_version(self):
        return self.__build_version
    
    @property
    def get_app_name(self):
        return self.__app_name
    
    @property
    def get_app_launch(self):
        return self.__app_launch
    
    @property
    def get_cloud_dir(self):
        return self.__cloud_dir
    
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras if self.__subcommand_extras else ""

    @get_mode.setter
    def mode(self, val):
        self.__mode = val
    
    @get_build_root.setter
    def build_root(self, val):
        self.__build_root = val
    
    @get_build_version.setter
    def build_version(self, val):
        self.__build_version = val
    
    @get_app_name.setter
    def app_name(self, val):
        self.__app_name = val
    
    @get_app_launch.setter
    def app_launch(self, val):
        self.__app_launch = val
    
    @get_cloud_dir.setter
    def cloud_dir(self, val):
        self.__cloud_dir = val
    
    @get_subcommand_extras.setter
    def extra_commands(self, val):
        self.__subcommand_extras = val


class UnrealBuildPatchCommand:
    """
    UnrealBuildPatchTool 用于生成补丁数据和管理内容分发
    用于创建增量更新补丁、打包区块数据等
    """
    __buildpatch_path = Path("/Users/Shared/Epic Games/UE_5.6/Engine/Binaries/Mac/BuildPatchTool")
    __host_platform = ""

    def __init__(self, buildpatch_path_val) -> None:
        self.__buildpatch_path = buildpatch_path_val
        self.__host_platform = SystemHelper.Get().GetHostPlatform()

    def PatchGeneration(self, params: ParamsBuildPatchTool):
        """
        生成补丁数据
        用于创建游戏内容的增量更新补丁
        """
        mode = params.get_mode if params.get_mode else "PatchGeneration"
        build_root = params.get_build_root
        build_version = params.get_build_version
        app_name = params.get_app_name
        app_launch = params.get_app_launch
        cloud_dir = params.get_cloud_dir
        subcommand_extras = params.get_subcommand_extras

        command = (
            '"' + str(self.__buildpatch_path) + '"' +
            r' -mode=' + mode +  # 模式：PatchGeneration 生成补丁
            (r' -BuildRoot="' + str(build_root) + '"' if build_root else '') +  # 构建根目录
            (r' -BuildVersion="' + str(build_version) + '"' if build_version else '') +  # 构建版本号
            (r' -AppName="' + str(app_name) + '"' if app_name else '') +  # 应用名称
            (r' -AppLaunch="' + str(app_launch) + '"' if app_launch else '') +  # 启动可执行文件
            (r' -CloudDir="' + str(cloud_dir) + '"' if cloud_dir else '') +  # 云存储目录
            subcommand_extras
        )
        RUNCMD(command)

    def Enumeration(self, params: ParamsBuildPatchTool):
        """
        枚举补丁数据
        用于列出和检查现有补丁的信息
        """
        params.mode = "Enumeration"
        self.PatchGeneration(params)

    def PackageChunks(self, params: ParamsBuildPatchTool):
        """
        打包区块数据
        将补丁数据打包成可分发的区块文件
        """
        params.mode = "PackageChunks"
        self.PatchGeneration(params)