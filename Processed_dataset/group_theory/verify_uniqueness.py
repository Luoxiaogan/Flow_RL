#!/usr/bin/env python3
"""
Verify uniqueness of questions in group theory datasets.
"""

import json
import os
from collections import Counter
from typing import Dict, List, Set


def load_jsonl(filepath: str) -> List[Dict]:
    """Load a JSONL file."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def check_uniqueness(data: List[Dict], dataset_name: str) -> bool:
    """Check if all questions in the dataset are unique."""
    questions = [item['question'] for item in data]
    unique_questions = set(questions)
    
    if len(questions) != len(unique_questions):
        print(f"[ERROR] {dataset_name}: 发现重复问题！")
        print(f"   总问题数: {len(questions)}")
        print(f"   唯一问题数: {len(unique_questions)}")
        print(f"   重复数: {len(questions) - len(unique_questions)}")
        
        # Find and print duplicates
        counter = Counter(questions)
        duplicates = {q: count for q, count in counter.items() if count > 1}
        if duplicates:
            print(f"   重复的问题:")
            for q, count in list(duplicates.items())[:3]:  # Show first 3 duplicates
                print(f"     - 出现 {count} 次: {q[:100]}...")
        return False
    else:
        print(f"[OK] {dataset_name}: 所有问题都是唯一的 ({len(questions)} 个问题)")
        return True


def check_answer_distribution(data: List[Dict], dataset_name: str):
    """Check the distribution of answers in the dataset."""
    answers = [item['answer'] for item in data]
    counter = Counter(answers)
    
    print(f"   答案分布:")
    for answer, count in sorted(counter.items(), key=lambda x: -x[1]):
        percentage = (count / len(answers)) * 100
        print(f"     {answer}: {count} ({percentage:.1f}%)")


def main():
    """Main verification function."""
    base_dir = "D:\\temp\\Flow_RL\\Processed_dataset\\group_theory"
    
    datasets = [
        "is_simple",
        "is_abelian", 
        "is_isomorphic",
        "center"
    ]
    
    print("=" * 60)
    print("群论数据集唯一性验证")
    print("=" * 60)
    
    all_unique = True
    
    for dataset in datasets:
        print(f"\n检查 {dataset} 数据集:")
        print("-" * 40)
        
        # Check training data
        train_path = os.path.join(base_dir, dataset, "train.jsonl")
        if os.path.exists(train_path):
            train_data = load_jsonl(train_path)
            is_unique = check_uniqueness(train_data, f"{dataset}/train")
            check_answer_distribution(train_data, f"{dataset}/train")
            all_unique = all_unique and is_unique
        else:
            print(f"[WARNING] 找不到训练集: {train_path}")
            
        # Check test data
        test_path = os.path.join(base_dir, dataset, "test.jsonl")
        if os.path.exists(test_path):
            test_data = load_jsonl(test_path)
            is_unique = check_uniqueness(test_data, f"{dataset}/test")
            check_answer_distribution(test_data, f"{dataset}/test")
            all_unique = all_unique and is_unique
        else:
            print(f"[WARNING] 找不到测试集: {test_path}")
            
        # Check overlap between train and test
        if os.path.exists(train_path) and os.path.exists(test_path):
            train_questions = set(item['question'] for item in train_data)
            test_questions = set(item['question'] for item in test_data)
            overlap = train_questions & test_questions
            
            if overlap:
                print(f"[WARNING] 训练集和测试集有重叠: {len(overlap)} 个问题")
                all_unique = False
            else:
                print(f"[OK] 训练集和测试集无重叠")
    
    print("\n" + "=" * 60)
    if all_unique:
        print("[SUCCESS] 所有数据集都通过了唯一性验证！")
    else:
        print("[FAIL] 有些数据集存在重复问题，需要修复。")
    print("=" * 60)


if __name__ == "__main__":
    main()