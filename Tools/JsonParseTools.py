#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JsonParseTools.py - 通用JSON/字典解析工具

功能：
1. 智能解析JSON或Python字典格式的文本
2. 自动normalize（规范化）数据
3. 灵活提取任意字段
4. 针对Artifactory URL的优化提取
5. 支持嵌套字段访问（如 a.b.c）
6. 支持命令行和Python模块两种使用方式

作者: puwentao@agora.io
日期: 2024-11-20
"""

import json
import re
import sys
import argparse
from typing import Dict, List, Any, Optional, Union


class JsonParser:
    """通用JSON/字典解析器"""
    
    def __init__(self, data_str: str, normalize: bool = True, verbose: bool = False):
        """
        初始化解析器
        
        Args:
            data_str: JSON字符串或Python字典字符串
            normalize: 是否进行规范化处理（默认True）
            verbose: 是否显示详细信息（默认False）
        """
        self.raw_data = data_str
        self.verbose = verbose
        self.normalize_enabled = normalize
        
        # 规范化
        if normalize:
            data_str = self._normalize(data_str)
        
        # 解析
        self.parsed_data = self._parse(data_str)
    
    def _log(self, message: str):
        """输出日志（如果verbose=True）"""
        if self.verbose:
            print(f"[JsonParser] {message}", file=sys.stderr)
    
    def _normalize(self, data_str: str) -> str:
        """
        规范化数据字符串
        
        处理：
        1. 去除首尾空白
        2. 处理转义字符
        3. 统一换行符
        
        Args:
            data_str: 原始字符串
            
        Returns:
            规范化后的字符串
        """
        self._log("开始规范化数据...")
        
        # 去除首尾空白
        data_str = data_str.strip()
        
        # 记录原始长度
        original_len = len(data_str)
        self._log(f"原始数据长度: {original_len} 字符")
        
        return data_str
    
    def _parse(self, data_str: str) -> Dict[str, Any]:
        """
        智能解析数据字符串
        
        尝试多种解析方法：
        1. eval() - 适用于Python字典
        2. json.loads() - 适用于标准JSON
        3. ast.literal_eval() - 安全的Python解析
        4. 单引号替换 - 降级方案
        
        Args:
            data_str: 数据字符串
            
        Returns:
            解析后的字典
        """
        # 方法1: eval() - 最适合Python字典
        try:
            data = eval(data_str)
            if isinstance(data, dict):
                self._log("✅ 使用 eval() 解析成功")
                return data
        except SyntaxError:
            self._log("⚠️ eval() 解析失败（语法错误）")
        except Exception as e:
            self._log(f"⚠️ eval() 解析失败: {e}")
        
        # 方法2: json.loads() - 标准JSON
        try:
            data = json.loads(data_str)
            self._log("✅ 使用 json.loads() 解析成功")
            return data
        except json.JSONDecodeError as e:
            self._log(f"⚠️ json.loads() 解析失败: {e}")
        
        # 方法3: ast.literal_eval() - 安全解析
        try:
            import ast
            data = ast.literal_eval(data_str)
            if isinstance(data, dict):
                self._log("✅ 使用 ast.literal_eval() 解析成功")
                return data
        except (SyntaxError, ValueError) as e:
            self._log(f"⚠️ ast.literal_eval() 解析失败: {e}")
        
        # 方法4: 单引号替换
        try:
            json_str = data_str.replace("'", '"')
            data = json.loads(json_str)
            self._log("✅ 使用单引号替换后解析成功")
            return data
        except Exception as e:
            self._log(f"⚠️ 单引号替换解析失败: {e}")
        
        # 所有方法失败
        self._log("❌ 所有解析方法都失败")
        return {}
    
    def get(self, field_path: str, default: Any = None) -> Any:
        """
        获取字段值（支持嵌套访问）
        
        Args:
            field_path: 字段路径，支持点号分隔（如 'a.b.c'）
            default: 字段不存在时的默认值
            
        Returns:
            字段值
            
        Examples:
            parser.get('version')           # 简单字段
            parser.get('user.name')         # 嵌套字段
            parser.get('items.0.title')     # 数组元素
        """
        if not field_path:
            return default
        
        # 分割路径
        parts = field_path.split('.')
        current = self.parsed_data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, default)
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index] if 0 <= index < len(current) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default
            
            if current is None:
                return default
        
        return current
    
    def extract_urls(self, 
                    source_field: str = None,
                    pattern: str = None,
                    artifactory_only: bool = False) -> List[str]:
        """
        提取URL
        
        Args:
            source_field: 源字段路径，None表示从整个数据中提取
            pattern: 自定义正则表达式，None使用默认URL模式
            artifactory_only: 仅提取Artifactory URL（默认False）
            
        Returns:
            URL列表
        """
        # 获取源文本
        if source_field:
            text = self.get(source_field, '')
            if not isinstance(text, str):
                text = str(text)
        else:
            text = json.dumps(self.parsed_data)
        
        # 确定匹配模式
        if artifactory_only:
            # Artifactory专用模式
            pattern = r'https?://[^\s]*artifactory[^\s]*'
            self._log("使用 Artifactory 专用模式")
        elif pattern is None:
            # 默认URL模式
            pattern = r'https?://[^\s]+'
            self._log("使用默认 URL 模式")
        else:
            self._log(f"使用自定义模式: {pattern}")
        
        # 提取URL
        urls = re.findall(pattern, text)
        
        # 清理和去重
        cleaned_urls = []
        seen = set()
        for url in urls:
            # 清理末尾的标点符号
            url = re.sub(r'[,;)}\]"\'>]+$', '', url)
            if url and url not in seen:
                cleaned_urls.append(url)
                seen.add(url)
        
        self._log(f"提取到 {len(cleaned_urls)} 个URL")
        return cleaned_urls
    
    def search(self, keyword: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        搜索包含关键字的所有字段
        
        Args:
            keyword: 搜索关键字
            case_sensitive: 是否区分大小写（默认False）
            
        Returns:
            包含关键字的字段字典 {field_path: value}
        """
        results = {}
        
        def search_recursive(data, path=''):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查key
                    key_match = keyword in key if case_sensitive else keyword.lower() in key.lower()
                    
                    # 检查value（如果是字符串）
                    value_match = False
                    if isinstance(value, str):
                        value_match = keyword in value if case_sensitive else keyword.lower() in value.lower()
                    
                    if key_match or value_match:
                        results[current_path] = value
                    
                    # 递归搜索
                    search_recursive(value, current_path)
                    
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    current_path = f"{path}.{i}" if path else str(i)
                    search_recursive(item, current_path)
        
        search_recursive(self.parsed_data)
        self._log(f"搜索 '{keyword}' 找到 {len(results)} 个匹配")
        return results
    
    def keys(self) -> List[str]:
        """获取所有顶级字段名"""
        return list(self.parsed_data.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """返回解析后的完整字典"""
        return self.parsed_data.copy()
    
    def to_json(self, indent: int = None, ensure_ascii: bool = False) -> str:
        """
        转换为JSON字符串
        
        Args:
            indent: 缩进空格数，None表示紧凑格式
            ensure_ascii: 是否转义非ASCII字符
            
        Returns:
            JSON字符串
        """
        return json.dumps(self.parsed_data, indent=indent, ensure_ascii=ensure_ascii)
    
    def print_structure(self, max_depth: int = 3):
        """
        打印数据结构
        
        Args:
            max_depth: 最大深度
        """
        def print_recursive(data, depth=0, prefix=''):
            if depth > max_depth:
                print(f"{prefix}...")
                return
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        print(f"{prefix}{key}: {type(value).__name__}")
                        print_recursive(value, depth + 1, prefix + '  ')
                    else:
                        value_preview = str(value)[:50]
                        if len(str(value)) > 50:
                            value_preview += '...'
                        print(f"{prefix}{key}: {value_preview}")
            
            elif isinstance(data, list):
                print(f"{prefix}[列表，{len(data)} 个元素]")
                if data and depth < max_depth:
                    print(f"{prefix}  [0]: {type(data[0]).__name__}")
                    if isinstance(data[0], (dict, list)):
                        print_recursive(data[0], depth + 1, prefix + '    ')
        
        print("=" * 60)
        print("数据结构:")
        print("=" * 60)
        print_recursive(self.parsed_data)
        print("=" * 60)


def parse(data_str: str, normalize: bool = True, verbose: bool = False) -> JsonParser:
    """
    快速解析接口
    
    Args:
        data_str: JSON或字典字符串
        normalize: 是否规范化
        verbose: 是否显示详细信息
        
    Returns:
        JsonParser对象
    """
    return JsonParser(data_str, normalize=normalize, verbose=verbose)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='通用JSON/字典解析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:

  # 提取字段
  python JsonParseTools.py -f data.txt --get version
  python JsonParseTools.py -f data.txt --get user.name
  
  # 提取所有URL
  python JsonParseTools.py -f data.txt --extract-urls
  
  # 仅提取Artifactory URL
  python JsonParseTools.py -f data.txt --extract-urls --artifactory
  
  # 从指定字段提取URL
  python JsonParseTools.py -f data.txt --extract-urls --source compile_result
  
  # 搜索关键字
  python JsonParseTools.py -f data.txt --search version
  
  # 查看所有字段
  python JsonParseTools.py -f data.txt --keys
  
  # 查看数据结构
  python JsonParseTools.py -f data.txt --structure
  
  # 输出JSON
  python JsonParseTools.py -f data.txt --output json --pretty
        """
    )
    
    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', help='输入文件路径')
    input_group.add_argument('-d', '--data', help='直接输入数据字符串')
    input_group.add_argument('-b', '--base64', help='Base64编码的数据（推荐用于PowerShell）')
    
    # 操作选项
    parser.add_argument('--get', help='提取指定字段（支持嵌套，如 a.b.c）')
    parser.add_argument('--extract-urls', action='store_true', help='提取URL')
    parser.add_argument('--source', help='URL提取源字段（配合 --extract-urls）')
    parser.add_argument('--artifactory', action='store_true', help='仅提取Artifactory URL')
    parser.add_argument('--pattern', help='自定义URL匹配模式（正则表达式）')
    parser.add_argument('--search', help='搜索包含关键字的字段')
    parser.add_argument('--keys', action='store_true', help='显示所有顶级字段名')
    parser.add_argument('--structure', action='store_true', help='显示数据结构')
    
    # 输出选项
    parser.add_argument('--output', choices=['json', 'raw'], help='输出格式')
    parser.add_argument('--pretty', action='store_true', help='美化输出')
    parser.add_argument('--no-normalize', action='store_true', help='不进行规范化')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 读取数据
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data_str = f.read().strip()
        except Exception as e:
            print(f"❌ 读取文件失败: {e}", file=sys.stderr)
            return 1
    elif args.base64:
        # Base64解码
        try:
            import base64
            data_str = base64.b64decode(args.base64).decode('utf-8')
            if args.verbose:
                print("✓ Base64解码成功", file=sys.stderr)
        except Exception as e:
            print(f"❌ Base64解码失败: {e}", file=sys.stderr)
            return 1
    else:
        data_str = args.data
    
    # 解析数据
    normalize = not args.no_normalize
    json_parser = parse(data_str, normalize=normalize, verbose=args.verbose)
    
    # 根据参数执行操作
    if args.get:
        # 提取字段
        value = json_parser.get(args.get)
        if value is None:
            print(f"⚠️ 字段 '{args.get}' 不存在或为None", file=sys.stderr)
            return 1
        if isinstance(value, (dict, list)):
            print(json.dumps(value, indent=2 if args.pretty else None, ensure_ascii=False))
        else:
            print(value)
    
    elif args.extract_urls:
        # 提取URL
        urls = json_parser.extract_urls(
            source_field=args.source,
            pattern=args.pattern,
            artifactory_only=args.artifactory
        )
        
        url_type = "Artifactory" if args.artifactory else "所有"
        source_info = f"从 {args.source}" if args.source else "从整个数据"
        print(f"📦 {source_info} 提取到 {len(urls)} 个 {url_type} URL:")
        for url in urls:
            print(url)
    
    elif args.search:
        # 搜索关键字
        results = json_parser.search(args.search)
        print(f"🔍 搜索 '{args.search}' 找到 {len(results)} 个匹配:")
        for field_path, value in results.items():
            value_preview = str(value)[:100]
            if len(str(value)) > 100:
                value_preview += '...'
            print(f"  {field_path}: {value_preview}")
    
    elif args.keys:
        # 显示所有字段
        keys = json_parser.keys()
        print(f"📋 顶级字段 ({len(keys)} 个):")
        for key in keys:
            print(f"  - {key}")
    
    elif args.structure:
        # 显示结构
        json_parser.print_structure()
    
    elif args.output:
        # 输出数据
        if args.output == 'json':
            print(json_parser.to_json(indent=2 if args.pretty else None))
        else:
            print(json_parser.to_dict())
    
    else:
        # 默认：显示基本信息
        print("=" * 60)
        print("📊 JSON解析结果")
        print("=" * 60)
        keys = json_parser.keys()
        print(f"✅ 解析成功")
        print(f"📋 顶级字段数: {len(keys)}")
        print(f"📝 字段列表: {', '.join(keys[:5])}")
        if len(keys) > 5:
            print(f"           ...还有 {len(keys) - 5} 个字段")
        print()
        print("💡 提示: 使用 --help 查看更多操作")
        print("   - 提取字段: --get field_name")
        print("   - 提取URL: --extract-urls --artifactory")
        print("   - 查看结构: --structure")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

