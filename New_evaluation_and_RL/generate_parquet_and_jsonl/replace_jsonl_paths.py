#!/usr/bin/env python3
"""
Script to replace paths in JSONL files from Windows format to Linux server format.
Replaces "D:/temp/Flow_RL" with "/nas/ganluo/Flow_RL" in the data_path field.

Usage:
    python replace_jsonl_paths.py file1.jsonl file2.jsonl ...
    python replace_jsonl_paths.py *.jsonl
    python replace_jsonl_paths.py train_data/*.jsonl test_data/*.jsonl
"""

import json
import argparse
import sys
import os
import glob
from pathlib import Path
from typing import List, Tuple
import shutil
from datetime import datetime


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Replace paths in JSONL files from Windows to Linux format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python replace_jsonl_paths.py test.jsonl
  python replace_jsonl_paths.py test.jsonl train.jsonl
  python replace_jsonl_paths.py *.jsonl
  python replace_jsonl_paths.py train_data/*.jsonl test_data/*.jsonl
  python replace_jsonl_paths.py --no-backup test.jsonl
  python replace_jsonl_paths.py --dry-run *.jsonl
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='JSONL files to process (supports wildcards)'
    )
    
    parser.add_argument(
        '--old-path',
        default='/nas/ganluo/Flow_RL',
        help='Old path to replace (default: D:/temp/Flow_RL)'
    )
    
    parser.add_argument(
        '--new-path',
        default='D:/temp/Flow_RL',
        help='New path to replace with (default: /nas/ganluo/Flow_RL)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without actually modifying files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed processing information'
    )
    
    return parser.parse_args()


def expand_file_paths(file_patterns: List[str]) -> List[str]:
    """Expand file patterns (wildcards) to actual file paths."""
    expanded_files = []
    
    for pattern in file_patterns:
        # Use glob to expand wildcards
        matches = glob.glob(pattern)
        if matches:
            expanded_files.extend(matches)
        else:
            # If no matches, check if file exists directly
            if os.path.exists(pattern):
                expanded_files.append(pattern)
            else:
                print(f"警告: 未找到匹配的文件: {pattern}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in expanded_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    return unique_files


def backup_file(file_path: str) -> str:
    """Create a backup of the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak_{timestamp}"
    
    # If a simple .bak already exists, use timestamp
    simple_backup = f"{file_path}.bak"
    if not os.path.exists(simple_backup):
        backup_path = simple_backup
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def process_jsonl_line(line: str, old_path: str, new_path: str) -> Tuple[str, bool]:
    """
    Process a single line from JSONL file.
    Returns: (processed_line, was_modified)
    """
    try:
        # Parse JSON
        data = json.loads(line.strip())
        
        # Check if data_path exists and contains old path
        modified = False
        if 'data_path' in data and isinstance(data['data_path'], str):
            if old_path in data['data_path']:
                # Replace the path
                data['data_path'] = data['data_path'].replace(old_path, new_path)
                modified = True
        
        # Check nested extra_info.data_path as well
        if 'extra_info' in data and isinstance(data.get('extra_info'), dict):
            if 'data_path' in data['extra_info'] and isinstance(data['extra_info']['data_path'], str):
                if old_path in data['extra_info']['data_path']:
                    data['extra_info']['data_path'] = data['extra_info']['data_path'].replace(old_path, new_path)
                    modified = True
        
        # Return JSON string
        return json.dumps(data, ensure_ascii=False) + '\n', modified
        
    except json.JSONDecodeError as e:
        print(f"  警告: 无法解析JSON行: {e}")
        return line, False
    except Exception as e:
        print(f"  错误处理行: {e}")
        return line, False


def process_file(file_path: str, old_path: str, new_path: str, 
                 create_backup: bool = True, dry_run: bool = False, 
                 verbose: bool = False) -> Tuple[int, int]:
    """
    Process a single JSONL file.
    Returns: (total_lines, modified_lines)
    """
    print(f"\n处理文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"  错误: 文件不存在")
        return 0, 0
    
    if not file_path.endswith('.jsonl'):
        print(f"  警告: 文件不是.jsonl格式，跳过")
        return 0, 0
    
    # Read all lines
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  错误读取文件: {e}")
        return 0, 0
    
    # Process each line
    processed_lines = []
    total_lines = len(lines)
    modified_lines = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip():  # Skip empty lines
            new_line, was_modified = process_jsonl_line(line, old_path, new_path)
            processed_lines.append(new_line)
            
            if was_modified:
                modified_lines += 1
                if verbose:
                    print(f"  行 {i}: 已替换路径")
        else:
            processed_lines.append(line)
    
    # Write back if not dry run and there were modifications
    if modified_lines > 0:
        if dry_run:
            print(f"  [预览模式] 将修改 {modified_lines}/{total_lines} 行")
            if verbose and modified_lines > 0:
                print(f"  示例替换: {old_path} -> {new_path}")
        else:
            # Create backup if requested
            if create_backup:
                backup_path = backup_file(file_path)
                print(f"  已创建备份: {backup_path}")
            
            # Write modified content
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(processed_lines)
                print(f"  已更新: {modified_lines}/{total_lines} 行被修改")
            except Exception as e:
                print(f"  错误写入文件: {e}")
                return total_lines, 0
    else:
        print(f"  无需修改 (共 {total_lines} 行)")
    
    return total_lines, modified_lines


def main():
    """Main function."""
    args = parse_arguments()
    
    # Expand file paths
    files_to_process = expand_file_paths(args.files)
    
    if not files_to_process:
        print("错误: 没有找到要处理的文件")
        sys.exit(1)
    
    print(f"准备处理 {len(files_to_process)} 个文件")
    print(f"替换规则: {args.old_path} -> {args.new_path}")
    
    if args.dry_run:
        print("*** 预览模式 - 不会实际修改文件 ***")
    
    # Process each file
    total_files = len(files_to_process)
    total_lines_all = 0
    modified_lines_all = 0
    successful_files = 0
    
    for file_path in files_to_process:
        total_lines, modified_lines = process_file(
            file_path,
            args.old_path,
            args.new_path,
            create_backup=not args.no_backup,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if total_lines > 0:
            successful_files += 1
            total_lines_all += total_lines
            modified_lines_all += modified_lines
    
    # Summary
    print("\n" + "="*50)
    print("处理完成:")
    print(f"  成功处理文件: {successful_files}/{total_files}")
    print(f"  总行数: {total_lines_all}")
    print(f"  修改行数: {modified_lines_all}")
    
    if args.dry_run:
        print("\n提示: 这是预览模式，没有实际修改文件。")
        print("      移除 --dry-run 参数来执行实际替换。")


if __name__ == '__main__':
    main()