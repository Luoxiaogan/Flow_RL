#!/usr/bin/env python3
"""
批量修复bootcamp文件中的导入问题
将所有 'from bootcamp import Basebootcamp' 改为 'from ..base import Basebootcamp'
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """修复单个文件中的导入问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if 'from bootcamp import Basebootcamp' in content:
            # 使用正则表达式替换
            new_content = re.sub(
                r'from bootcamp import Basebootcamp',
                'from ..base import Basebootcamp',
                content
            )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Fixed: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 设置bootcamp目录路径
    bootcamp_dir = Path("InternBootcamp/internbootcamp/bootcamp")
    
    if not bootcamp_dir.exists():
        print(f"Bootcamp directory not found: {bootcamp_dir}")
        return
    
    fixed_count = 0
    total_count = 0
    
    # 遍历所有子目录
    for task_dir in bootcamp_dir.iterdir():
        if task_dir.is_dir() and not task_dir.name.startswith('.'):
            # 查找每个任务目录中的Python文件
            for py_file in task_dir.glob("*.py"):
                if py_file.name != "__init__.py" and py_file.name != "base.py":
                    total_count += 1
                    if fix_imports_in_file(py_file):
                        fixed_count += 1
    
    print(f"\nSummary:")
    print(f"Total files processed: {total_count}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files unchanged: {total_count - fixed_count}")

if __name__ == "__main__":
    main() 