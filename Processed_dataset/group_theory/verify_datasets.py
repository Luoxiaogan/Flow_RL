#!/usr/bin/env python3
"""
Verify the quality of generated group theory datasets.
"""

import json
import os
from collections import Counter

def verify_dataset(filepath, dataset_name):
    """Verify a single dataset file."""
    print(f"\n验证 {dataset_name}:")
    print("-" * 50)
    
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"数据条数: {len(lines)}")
    
    # Parse all entries
    entries = []
    for i, line in enumerate(lines):
        try:
            entry = json.loads(line.strip())
            entries.append(entry)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误在第{i+1}行: {e}")
    
    # Check structure
    if entries:
        print(f"数据结构: {list(entries[0].keys())}")
        
        # For classification tasks, check answer distribution
        if dataset_name in ["is_simple", "is_abelian", "is_cyclic"]:
            answers = [entry['answer'] for entry in entries]
            answer_dist = Counter(answers)
            print(f"答案分布: {dict(answer_dist)}")
            
            # Check balance
            total = len(answers)
            for answer, count in answer_dist.items():
                percentage = (count / total) * 100
                print(f"  {answer}: {count} ({percentage:.1f}%)")
        
        # For center task, check answer format
        elif dataset_name == "center":
            answers = [entry['answer'] for entry in entries]
            
            # Check if all answers are numeric strings
            numeric_answers = [a for a in answers if a.isdigit()]
            print(f"数值答案数量: {len(numeric_answers)}/{len(answers)}")
            
            # Show distribution of center orders
            center_orders = Counter(answers)
            print(f"中心阶数分布 (前10个):")
            for order, count in sorted(center_orders.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)[:10]:
                print(f"  阶数 {order}: {count}次")
        
        # Show sample entries
        print("\n示例数据 (前2条):")
        for i, entry in enumerate(entries[:2]):
            print(f"\n示例 {i+1}:")
            print(f"  问题: {entry['question'][:100]}...")
            print(f"  答案: {entry['answer']}")

def main():
    """Verify all generated datasets."""
    base_dir = "D:\\temp\\Flow_RL\\Processed_dataset\\group_theory"
    
    datasets = [
        ("is_simple", "判断单群"),
        ("is_abelian", "判断交换群"),
        ("is_cyclic", "判断循环群"),
        ("center", "计算群的中心")
    ]
    
    print("=" * 60)
    print("群论数据集质量验证报告")
    print("=" * 60)
    
    for dataset_name, chinese_name in datasets:
        print(f"\n\n### {chinese_name} ({dataset_name}) ###")
        
        # Verify training set
        train_path = os.path.join(base_dir, dataset_name, "train.jsonl")
        verify_dataset(train_path, f"{dataset_name}/train")
        
        # Verify test set
        test_path = os.path.join(base_dir, dataset_name, "test.jsonl")
        verify_dataset(test_path, f"{dataset_name}/test")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()