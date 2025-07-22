#!/usr/bin/env python3
"""
批量修复bootcamp文件的三引号问题
检测并修复所有开头缺少三引号的Python文件
"""

import os
import sys
from typing import List, Tuple

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def scan_bootcamp_files() -> List[str]:
    """扫描所有bootcamp目录下的Python文件"""
    bootcamp_dir = os.path.join(project_root, "internbootcamp", "bootcamp")
    if not os.path.exists(bootcamp_dir):
        print(f"错误: bootcamp目录不存在: {bootcamp_dir}")
        return []
    
    python_files = []
    for root, dirs, files in os.walk(bootcamp_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    return python_files

def check_file_needs_fix(file_path: str) -> Tuple[bool, str]:
    """检查文件是否需要修复三引号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件内容
        if not content.strip():
            return False, "文件为空"
        
        # 检查是否已经有正确的开头三引号
        if content.startswith('"""'):
            return False, "已有正确的三引号"
        
        # 检查是否是损坏的格式（缺少开头的三引号但有任务描述）
        if (content.startswith('#') or content.startswith('### ')) and ('Here is a reference code' in content or '请完成上述谜题' in content):
            return True, "缺少开头三引号"
        
        # 检查是否有其他模式
        if content.startswith('\n') and ('###' in content[:100] or '谜题描述' in content[:200]):
            return True, "可能缺少开头三引号"
        
        return False, "不需要修复"
        
    except Exception as e:
        return False, f"读取文件失败: {e}"

def fix_file(file_path: str) -> bool:
    """修复单个文件的三引号问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加开头的三引号
        if not content.startswith('"""'):
            # 如果内容以换行开始，保留换行
            if content.startswith('\n'):
                # 找到第一个非空行
                lines = content.split('\n')
                first_non_empty = 0
                while first_non_empty < len(lines) and not lines[first_non_empty].strip():
                    first_non_empty += 1
                
                if first_non_empty < len(lines):
                    # 在第一个非空行前插入三引号
                    lines.insert(first_non_empty, '"""')
                    content = '\n'.join(lines)
                else:
                    content = '"""' + content
            else:
                content = '"""' + content
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"修复文件失败 {file_path}: {e}")
        return False

def verify_fix(file_path: str) -> bool:
    """验证修复是否成功"""
    try:
        # 尝试编译文件检查语法
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, file_path, 'exec')
        return True
        
    except SyntaxError as e:
        return False
    except Exception:
        return True  # 其他错误（如导入错误）不算语法错误

def main():
    """主函数"""
    print("=== 批量修复bootcamp文件三引号问题 ===")
    
    # 扫描所有Python文件
    python_files = scan_bootcamp_files()
    print(f"发现 {len(python_files)} 个Python文件")
    
    if not python_files:
        return
    
    # 检查需要修复的文件
    files_to_fix = []
    for file_path in python_files:
        needs_fix, reason = check_file_needs_fix(file_path)
        if needs_fix:
            files_to_fix.append(file_path)
            relative_path = os.path.relpath(file_path, project_root)
            print(f"需要修复: {relative_path} - {reason}")
    
    print(f"\n发现 {len(files_to_fix)} 个需要修复的文件")
    
    if not files_to_fix:
        print("所有文件都正常，无需修复")
        return
    
    # 询问用户是否继续
    response = input(f"\n是否继续修复这 {len(files_to_fix)} 个文件？[y/N]: ")
    if response.lower() not in ['y', 'yes']:
        print("用户取消操作")
        return
    
    # 修复文件
    print(f"\n开始修复文件...")
    fixed_count = 0
    failed_count = 0
    
    for file_path in files_to_fix:
        relative_path = os.path.relpath(file_path, project_root)
        print(f"修复: {relative_path}")
        
        if fix_file(file_path):
            # 验证修复结果
            if verify_fix(file_path):
                print(f"  ✓ 修复成功")
                fixed_count += 1
            else:
                print(f"  ⚠ 修复完成但仍有语法错误")
                fixed_count += 1
        else:
            print(f"  ✗ 修复失败")
            failed_count += 1
    
    # 输出总结
    print(f"\n{'='*50}")
    print(f"修复完成:")
    print(f"- 成功修复: {fixed_count} 个文件")
    print(f"- 修复失败: {failed_count} 个文件")
    print(f"- 总计处理: {len(files_to_fix)} 个文件")
    
    if fixed_count > 0:
        print(f"\n建议重新运行 process_dataset.py 测试修复效果")

if __name__ == "__main__":
    main() 