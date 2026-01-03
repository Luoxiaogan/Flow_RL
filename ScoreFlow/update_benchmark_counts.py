#!/usr/bin/env python3
"""
Update data_train_max_num and data_test_max_num in benchmark_mapping file
by counting actual lines in the data files.

Usage:
    python update_benchmark_counts.py <benchmark_mapping_file>

Example:
    python update_benchmark_counts.py /Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/ScoreFlow/benchmark_mapping_0921.jsonl
"""

import json
import sys
import os
from pathlib import Path


def count_lines_in_file(filepath: str) -> int:
    """Count number of lines in a file"""
    if not os.path.exists(filepath):
        print(f"  ⚠️  文件不存在: {filepath}")
        return 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            count = sum(1 for line in f if line.strip())
        return count
    except Exception as e:
        print(f"  ❌ 读取文件失败 {filepath}: {e}")
        return 0


def update_benchmark_mapping(mapping_file: str):
    """Update benchmark mapping file with actual line counts"""

    if not os.path.exists(mapping_file):
        print(f"❌ 映射文件不存在: {mapping_file}")
        sys.exit(1)

    print(f"📊 正在更新benchmark映射文件: {mapping_file}")
    print("=" * 80)

    # Read all entries
    entries = []
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"❌ 第{line_num}行JSON解析失败: {e}")
                    continue

    # Update each entry
    updated_entries = []
    for entry in entries:
        benchmark = entry.get('benchmark', 'unknown')
        print(f"\n📌 处理 benchmark: {benchmark}")

        # Count train data lines
        train_file = entry.get('data_train_dir', '')
        if train_file:
            train_count = count_lines_in_file(train_file)
            old_train_count = entry.get('data_train_max_num', 0)
            entry['data_train_max_num'] = train_count
            print(f"  训练集: {train_file}")
            print(f"    原值: {old_train_count}, 实际行数: {train_count}")

        # Count test data lines
        test_file = entry.get('data_test_dir', '')
        if test_file:
            test_count = count_lines_in_file(test_file)
            old_test_count = entry.get('data_test_max_num', 0)
            entry['data_test_max_num'] = test_count
            print(f"  测试集: {test_file}")
            print(f"    原值: {old_test_count}, 实际行数: {test_count}")

        updated_entries.append(entry)

    # Create backup
    backup_file = mapping_file + '.backup'
    print(f"\n💾 创建备份: {backup_file}")
    with open(mapping_file, 'r') as src, open(backup_file, 'w') as dst:
        dst.write(src.read())

    # Write updated file
    print(f"✍️  写入更新后的映射文件: {mapping_file}")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        for entry in updated_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print("\n" + "=" * 80)
    print("✅ 更新完成!")
    print(f"   - 共处理 {len(updated_entries)} 个benchmark")
    print(f"   - 备份已保存至: {backup_file}")


def main():
    if len(sys.argv) != 2:
        print("用法: python update_benchmark_counts.py <benchmark_mapping_file>")
        print("\n示例:")
        print("  python update_benchmark_counts.py /Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/ScoreFlow/benchmark_mapping_0921.jsonl")
        sys.exit(1)

    mapping_file = sys.argv[1]
    update_benchmark_mapping(mapping_file)


if __name__ == "__main__":
    main()