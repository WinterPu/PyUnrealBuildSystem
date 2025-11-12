from Command.CommandBase import *
from Logger.Logger import *
from pathlib import Path
from SystemHelper import *

from Command.GenerateProjectFilesWithShellCommand import *

class ParamsUAT:
    def __init__(self) -> None:
        self.__path_uproject_file = ""
        self.__target_platform = ""
        self.__path_archive = ""
        self.__path_log = ""
        self.__subcommand_extras = ""

        self.__bskip_build_editor = False

        ## Plugin 
        self.__path_uplugin_file = ""
        self.__path_plugin_output_dir = ""

        ## BuildGraph
        self.__path_buildgraph_file = ""

    @property
    def get_path_uproject_file(self):
        return self.__path_uproject_file
    @property
    def get_target_platform(self):
        return self.__target_platform
    
    @property
    def get_subcommand_archive_dir(self):
        subcommand = ""
        str_path_archive = str(self.__path_archive)
        if str_path_archive and len(str_path_archive) > 0:
            subcommand = ' -archivedirectory="' +str_path_archive+'" '
        return subcommand
    
    @property
    def get_subcommand_log(self):
        return (r" -log=" + '"' + str(self.__path_log) + '"') if self.__path_log != "" else ""
    @property
    def get_subcommand_extras(self):
        return " " + self.__subcommand_extras
    
    @property
    def get_flag_skip_build_editor(self) -> bool:
        return self.__bskip_build_editor

    ## BuildPlugin 
    @property
    def get_path_plugin_output_dir(self):
        return self.__path_plugin_output_dir
    
    @property
    def get_path_uplugin_file(self):
        return self.__path_uplugin_file
    

    @get_path_uproject_file.setter
    def path_uproject_file(self,val):
        self.__path_uproject_file = val

    @get_target_platform.setter
    def target_platform(self,val):
        self.__target_platform = val
    
    @get_subcommand_archive_dir.setter
    def path_archive(self,val):
        self.__path_archive = val

    @get_subcommand_log.setter
    def path_log(self,val):
        self.__path_log = val
    @get_subcommand_extras.setter
    def extra_commands(self,val):
        self.__subcommand_extras = val

    @get_flag_skip_build_editor.setter
    def skip_build_editor(self,val:bool):
        self.__bskip_build_editor = val

    ## BuildPlugin
    @get_path_uplugin_file.setter
    def path_uplugin_file(self,val):
        self.__path_uplugin_file = val

    @get_path_plugin_output_dir.setter
    def path_plugin_output_dir(self,val):
        self.__path_plugin_output_dir = val


    ## BuildGraph
    @property
    def get_path_buildgraph_file(self):
        return self.__path_buildgraph_file

    @get_path_buildgraph_file.setter
    def path_buildgraph_file(self,val):
        self.__path_buildgraph_file = val


class UATCommand:
    __uatpath = Path("/Users/Shared/Epic Games/UE_5.2/Engine/Build/BatchFiles/RunUAT.sh")
    __host_platform = ""
    __path_genproj_script = ""
    def __init__(self, uatpath_val,path_script_genproj = "") -> None:
        self.__uatpath = uatpath_val
        self.__host_platform = SystemHelper.Get().GetHostPlatform()
        if self.__host_platform == SystemHelper.Mac_HostName():
            self.__path_genproj_script = path_script_genproj

    def BuildCookRun(self,params:ParamsUAT):
        ### Command

        target_platform = params.get_target_platform
        path_uproject_file = params.get_path_uproject_file
        subcommand_archive_dir = params.get_subcommand_archive_dir
        subcommand_extras = params.get_subcommand_extras

        bshould_build_editor = not params.get_flag_skip_build_editor

        # ## need 
        # command = (
        #     '"' + str(self.uatpath) + '"' +
        #     r" BuildCookRun  -project="+ '"' +str(project_path)+ '"' + 
        #     r" -targetplatform="+platform+
        #     r" -SkipBuildEditor"
        #     r" -clientconfig=Development"
        #     r" -Build"
        #     r" -GenerateDSYM"
        #     r" -Cook"
        #     r" -Stage"
        #     r" -Archive"
        #     r" -package"
        #     r" -verbose"+
        #     extra_commands
        #  )
        # RUNCMD(command)


        

        ## Step 01: BuildEditor

        if bshould_build_editor:

            platform_editor = SystemHelper.Mac_TargetName()

            if self.__host_platform == SystemHelper.Win_HostName():
                
                if target_platform == SystemHelper.IOS_TargetName():
                    PrintErr("TBD - Not Ready, Packaging IOS on Windows Platform")
                    return
                
                if target_platform == SystemHelper.Mac_TargetName():
                    PrintErr("Not Support, Packaging Mac on Windows Platform")
                    return
                
                platform_editor = SystemHelper.Win64_TargetName()

            elif self.__host_platform == SystemHelper.Mac_HostName():

                if target_platform == SystemHelper.Android_TargetName():
                    PrintErr("TBD - Not Ready, Packaging Android on Mac Platform")
                    return
                
                if target_platform == SystemHelper.Win64_TargetName():
                    PrintErr("Not Support, Packaging Win on Mac Platform")
                    return


                platform_editor = SystemHelper.Mac_TargetName()


            command = (
                    '"' + str(self.__uatpath) + '"' +
                    r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                    r" -targetplatform="+platform_editor+
                    r" -clientconfig=Development"
                    r" -Build"
                    r" -GenerateDSYM"
                    r" -Cook"
                    #r" -allmaps -pak"
                    r" -Stage"
                    r" -Archive"
                    r" -package"
                    r" -verbose"+
                    subcommand_extras
            
            )
            
            RUNCMD(command, bignore_error_for_no_termination=True)
        
        else:
            PrintWarn("Skip Building Editor ....")




        ## Step 02: BuildCookRun

        if target_platform == SystemHelper.IOS_TargetName():
            
            ## Gen UE Project On Mac
            OneGenerateProjectFilesWithShellCommand = GenerateProjectFilesWithShellCommand(self.__path_genproj_script)
            params_genwithshell = ParamsGenProjectWithShell()
            params_genwithshell.path_uproject_file = path_uproject_file
            OneGenerateProjectFilesWithShellCommand.GenerateProjectFiles(params_genwithshell)

            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + subcommand_archive_dir +
                r" -package"
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

        elif target_platform == SystemHelper.Mac_TargetName() :

            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -CookAll"
                r" -Stage"
                r" -Archive" + subcommand_archive_dir + 
                r" -package"
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

        else:

            ## [TBD] blueprint project also needs 2 times build
            
            command = (
                '"' + str(self.__uatpath) + '"' +
                r" BuildCookRun  -project="+ '"' +str(path_uproject_file)+ '"' + 
                r" -targetplatform="+target_platform+
                r" -SkipBuildEditor"
                r" -clientconfig=Development"
                r" -Build"
                r" -GenerateDSYM"
                r" -Cook"
                r" -Stage"
                r" -Archive"  + subcommand_archive_dir +
                r" -package"
                # r" -prereqs"
                # r" -compressed"
                # r" -pak"   Create PAK files (compressed asset packages)
                r" -verbose"+
                subcommand_extras
            )
            RUNCMD(command)

    

    def BuildPlugin(self,params:ParamsUAT):
        ## Command
        target_platform = params.get_target_platform
        path_uplugin_file = params.get_path_uplugin_file
        path_plugin_output = params.get_path_plugin_output_dir
        subcommand_extras = params.get_subcommand_extras

        command = (
            "\"" + str(self.__uatpath) + "\"" +
            r" BuildPlugin  -plugin="+ '"' + str(path_uplugin_file) + '"'+
            r" -TargetPlatforms="+target_platform+
            r" -package="+ '"' + str(path_plugin_output) + '"'+
            r" -rocket"+ # means precompiled & installed engine version
            subcommand_extras
        )
        RUNCMD(command)



    def BuildGraph(self, params: ParamsUAT):
        ## Command
        path_buildgraph_file = params.get_path_buildgraph_file
        subcommand_extras = params.get_subcommand_extras
        
        command = (
            "\"" + str(self.__uatpath) + "\"" +
            r" BuildGraph  -Script="+ '"' + str(path_buildgraph_file) + '"'+
            subcommand_extras
        )

        RUNCMD(command)

    def Cook(self, params: ParamsUAT):
        ## Command
        target_platform = params.get_target_platform
        path_uproject_file = params.get_path_uproject_file
        subcommand_archive_dir = params.get_subcommand_archive_dir
        subcommand_extras = params.get_subcommand_extras

        # Get project name from uproject file path
        project_name = Path(path_uproject_file).stem
        
        # Get Unreal Editor path based on UAT path
        uat_path_obj = Path(self.__uatpath)
        engine_root = uat_path_obj.parent.parent.parent  # Go up from BatchFiles/RunUAT.sh to Engine root
        
        if self.__host_platform == SystemHelper.Mac_HostName():
            unreal_editor_path = engine_root / "Binaries" / "Mac" / "UnrealEditor.app" / "Contents" / "MacOS" / "UnrealEditor"
        elif self.__host_platform == SystemHelper.Win_HostName():
            unreal_editor_path = engine_root / "Binaries" / "Win64" / "UnrealEditor.exe"
        else:
            unreal_editor_path = ""

        command = (
            '"' + str(self.__uatpath) + '"' +
            # 为项目指定脚本路径，告诉UAT从哪个项目获取自动化脚本
            r' -ScriptsForProject="' + str(path_uproject_file) + '"' +
            
            # ===== Turnkey 命令部分：用于验证和管理SDK =====
            r' Turnkey' +
            r' -command=VerifySdk' +  # 验证SDK是否正确安装和配置
            r' -platform=' + target_platform +  # 指定目标平台（Mac/Win64/IOS/Android等）
            r' -UpdateIfNeeded' +  # 如果SDK不是最新版本或缺失，自动更新
            r' -project="' + str(path_uproject_file) + '"' +  # 指定项目文件路径
            
            # ===== BuildCookRun 命令部分：执行构建、烘焙和打包 =====
            r' BuildCookRun' +
            r' -nop4' +  # 不使用 Perforce 版本控制系统
            r' -utf8output' +  # 使用 UTF-8 编码输出日志，支持多语言字符
            r' -nocompileeditor' +  # 不编译编辑器代码
            r' -skipbuildeditor' +  # 跳过构建编辑器步骤
            r' -cook' +  # 执行内容烘焙（Cook），将资源转换为平台特定格式
            r' -project="' + str(path_uproject_file) + '"' +  # 指定要烘焙的项目文件
            r' -target=' + project_name +  # 指定构建目标名称（通常是项目名）
            # 指定 UnrealEditor 可执行文件的完整路径，用于烘焙过程
            (r' -unrealexe="' + str(unreal_editor_path) + '"' if unreal_editor_path else '') +
            r' -platform=' + target_platform +  # 指定目标平台
            r' -installed' +  # 使用已安装的引擎版本（预编译版本），而不是源码版本
            r' -skipstage' +  # 跳过打包阶段（Stage），只执行烘焙不生成最终包
            r' -nocompile' +  # 不编译项目代码
            r' -nocompileuat' +  # 不编译 UAT（Unreal Automation Tool）本身
            subcommand_extras  # 额外的自定义命令参数
        )
        RUNCMD(command)