#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONL to JSON List Converter
Convert JSONL (JSON Lines) file to a single JSON array file
"""

import json
import sys
import os
from pathlib import Path
import argparse
from typing import List, Dict, Any


def jsonl_to_json_list(input_file: str, output_file: str = None, 
                       pretty: bool = True, encoding: str = 'utf-8') -> int:
    """
    Convert JSONL file to JSON list format
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSON file (if None, auto-generate)
        pretty: Whether to pretty-print the JSON output
        encoding: File encoding (default: utf-8)
    
    Returns:
        Number of records converted
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ 错误: 输入文件不存在: {input_file}")
        return 0
    
    # Auto-generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.with_suffix('.json'))
        print(f"📝 输出文件: {output_file}")
    
    # Read JSONL and convert to list
    json_list = []
    error_lines = []
    
    try:
        with open(input_file, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                try:
                    json_obj = json.loads(line)
                    json_list.append(json_obj)
                except json.JSONDecodeError as e:
                    error_lines.append((line_num, str(e)))
                    print(f"⚠️  警告: 第 {line_num} 行解析失败: {e}")
    
    except Exception as e:
        print(f"❌ 读取文件错误: {e}")
        return 0
    
    # Write JSON list to output file
    try:
        with open(output_file, 'w', encoding=encoding) as f:
            if pretty:
                json.dump(json_list, f, indent=2, ensure_ascii=False)
            else:
                json.dump(json_list, f, ensure_ascii=False)
        
        print(f"✅ 成功转换 {len(json_list)} 条记录")
        
        if error_lines:
            print(f"⚠️  跳过了 {len(error_lines)} 行错误数据")
            if len(error_lines) <= 5:
                for line_num, error in error_lines:
                    print(f"   - 第 {line_num} 行: {error}")
        
        return len(json_list)
        
    except Exception as e:
        print(f"❌ 写入文件错误: {e}")
        return 0


def batch_convert(directory: str, pattern: str = "*.jsonl", 
                 pretty: bool = True) -> None:
    """
    Batch convert all JSONL files in a directory
    
    Args:
        directory: Directory path containing JSONL files
        pattern: File pattern to match (default: *.jsonl)
        pretty: Whether to pretty-print the JSON output
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    jsonl_files = list(dir_path.glob(pattern))
    
    if not jsonl_files:
        print(f"❌ 没有找到匹配的JSONL文件: {pattern}")
        return
    
    print(f"📁 找到 {len(jsonl_files)} 个JSONL文件")
    print("-" * 50)
    
    total_records = 0
    success_count = 0
    
    for jsonl_file in jsonl_files:
        print(f"\n处理: {jsonl_file.name}")
        records = jsonl_to_json_list(str(jsonl_file), pretty=pretty)
        if records > 0:
            total_records += records
            success_count += 1
    
    print("-" * 50)
    print(f"\n📊 总结: 成功转换 {success_count}/{len(jsonl_files)} 个文件")
    print(f"📝 总记录数: {total_records}")


def peek_jsonl(input_file: str, num_lines: int = 5) -> None:
    """
    Preview first N lines of JSONL file
    
    Args:
        input_file: Path to JSONL file
        num_lines: Number of lines to preview
    """
    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return
    
    print(f"📄 预览文件: {input_file}")
    print(f"显示前 {num_lines} 条记录:")
    print("-" * 50)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            
            try:
                json_obj = json.loads(line.strip())
                print(f"\n记录 {i + 1}:")
                print(json.dumps(json_obj, indent=2, ensure_ascii=False)[:500])
                if len(json.dumps(json_obj)) > 500:
                    print("... (内容已截断)")
            except json.JSONDecodeError:
                print(f"\n记录 {i + 1}: [解析错误]")


def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(
        description='JSONL转JSON列表转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 转换单个文件
  python jsonl_to_json.py input.jsonl
  
  # 指定输出文件名
  python jsonl_to_json.py input.jsonl -o output.json
  
  # 压缩格式输出（不美化）
  python jsonl_to_json.py input.jsonl --compact
  
  # 批量转换目录下所有JSONL文件
  python jsonl_to_json.py --batch ./data/
  
  # 预览JSONL文件内容
  python jsonl_to_json.py input.jsonl --peek
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='输入JSONL文件路径')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('--compact', action='store_true', 
                       help='压缩输出（不美化）')
    parser.add_argument('--batch', metavar='DIR', 
                       help='批量转换指定目录下的所有JSONL文件')
    parser.add_argument('--pattern', default='*.jsonl', 
                       help='批量转换时的文件匹配模式 (默认: *.jsonl)')
    parser.add_argument('--peek', action='store_true', 
                       help='预览JSONL文件前几行')
    parser.add_argument('--peek-lines', type=int, default=5, 
                       help='预览行数 (默认: 5)')
    parser.add_argument('--encoding', default='utf-8', 
                       help='文件编码 (默认: utf-8)')
    
    args = parser.parse_args()
    
    # Batch conversion mode
    if args.batch:
        batch_convert(args.batch, args.pattern, pretty=not args.compact)
        return
    
    # Check if input file is provided
    if not args.input_file:
        parser.print_help()
        sys.exit(1)
    
    # Peek mode
    if args.peek:
        peek_jsonl(args.input_file, args.peek_lines)
        return
    
    # Single file conversion
    result = jsonl_to_json_list(
        args.input_file, 
        args.output,
        pretty=not args.compact,
        encoding=args.encoding
    )
    
    sys.exit(0 if result > 0 else 1)


if __name__ == '__main__':
    main()