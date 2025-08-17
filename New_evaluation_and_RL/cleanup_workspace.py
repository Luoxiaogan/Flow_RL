#!/usr/bin/env python3
"""
清理workspace目录中的旧文件
将reward_gsm8k_*文件移动到archive目录
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_workspace():
    """清理workspace目录中的旧文件"""
    
    workspace_dir = Path("/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/workspace")
    
    if not workspace_dir.exists():
        print(f"❌ Workspace目录不存在: {workspace_dir}")
        return
    
    print("="*60)
    print("清理Workspace目录")
    print("="*60)
    
    # 遍历所有benchmark目录
    for benchmark_dir in workspace_dir.iterdir():
        if not benchmark_dir.is_dir():
            continue
            
        print(f"\n📁 处理目录: {benchmark_dir.name}")
        
        # 查找旧的reward_*文件
        old_files = list(benchmark_dir.glob("reward_*.py")) + \
                   list(benchmark_dir.glob("reward_*.meta.json"))
        
        if not old_files:
            print(f"   ✓ 没有需要清理的文件")
            continue
        
        # 创建archive目录
        archive_dir = benchmark_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        print(f"   找到 {len(old_files)} 个旧文件")
        
        # 移动文件到archive
        moved_count = 0
        for old_file in old_files:
            try:
                # 目标路径
                dest_file = archive_dir / old_file.name
                
                # 如果目标文件已存在，添加时间戳
                if dest_file.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_file = archive_dir / f"{old_file.stem}_{timestamp}{old_file.suffix}"
                
                # 移动文件
                shutil.move(str(old_file), str(dest_file))
                print(f"   📦 归档: {old_file.name} -> archive/{dest_file.name}")
                moved_count += 1
                
            except Exception as e:
                print(f"   ❌ 移动失败 {old_file.name}: {e}")
        
        print(f"   ✅ 成功归档 {moved_count} 个文件到 {archive_dir}")
    
    print("\n" + "="*60)
    print("清理完成")
    print("="*60)
    
    # 显示当前目录结构
    print("\n当前目录结构:")
    for benchmark_dir in workspace_dir.iterdir():
        if not benchmark_dir.is_dir():
            continue
        
        print(f"\n{benchmark_dir.name}/")
        
        # 统计workflow目录
        workflow_dirs = [d for d in benchmark_dir.iterdir() 
                        if d.is_dir() and d.name.startswith("workflow_")]
        if workflow_dirs:
            print(f"  📁 {len(workflow_dirs)} 个workflow目录")
            # 显示最新的3个
            for wd in sorted(workflow_dirs, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                print(f"     - {wd.name}")
            if len(workflow_dirs) > 3:
                print(f"     ... 还有 {len(workflow_dirs)-3} 个")
        
        # 检查archive目录
        archive_dir = benchmark_dir / "archive"
        if archive_dir.exists():
            archived_files = list(archive_dir.glob("*"))
            if archived_files:
                print(f"  📦 archive/ ({len(archived_files)} 个归档文件)")


if __name__ == "__main__":
    cleanup_workspace()