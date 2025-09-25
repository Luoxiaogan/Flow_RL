#!/usr/bin/env python3
"""
03_generate_test_data.py
Generate test data without context for RAG evaluation
"""

import json
import os
from typing import Dict, List
from tqdm import tqdm

def load_validation_data(filepath: str) -> List[Dict]:
    """Load validation.jsonl file"""
    data = []
    print(f"加载验证集数据: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    print(f"成功加载 {len(data)} 条数据")
    return data

def create_test_data(data: List[Dict]) -> List[Dict]:
    """
    Create test data by removing context field but keeping supporting facts

    Args:
        data: Original validation data with context

    Returns:
        Test data without context field
    """
    test_data = []

    print("生成测试数据...")
    for sample in tqdm(data, desc="处理样本"):
        # Create new sample without context
        test_sample = {
            'question': sample['question'],
            'answer': sample['answer'],
            'index': sample['index'],
            'original_index': sample['original_index'],
            'split': sample['split'],
            'type': sample['type'],
            'level': sample['level'],
            # Keep supporting facts for evaluation
            'original_supporting_facts': sample['supporting_facts']
        }

        test_data.append(test_sample)

    return test_data

def calculate_size_reduction(original_data: List[Dict], test_data: List[Dict]) -> Dict:
    """Calculate the size reduction from removing context"""
    # Calculate sizes
    original_size = len(json.dumps(original_data, ensure_ascii=False))
    test_size = len(json.dumps(test_data, ensure_ascii=False))
    reduction_bytes = original_size - test_size
    reduction_percent = (1 - test_size / original_size) * 100

    stats = {
        'original_size_bytes': original_size,
        'original_size_mb': original_size / (1024 * 1024),
        'test_size_bytes': test_size,
        'test_size_mb': test_size / (1024 * 1024),
        'reduction_bytes': reduction_bytes,
        'reduction_mb': reduction_bytes / (1024 * 1024),
        'reduction_percent': reduction_percent
    }

    return stats

def analyze_supporting_facts(data: List[Dict]) -> Dict:
    """Analyze the supporting facts distribution"""
    stats = {
        'total_samples': len(data),
        'title_counts': {},
        'sentence_counts': [],
        'unique_titles': set()
    }

    for sample in data:
        sf = sample['original_supporting_facts']
        titles = sf.get('title', [])
        sent_ids = sf.get('sent_id', [])

        # Count sentences per sample
        stats['sentence_counts'].append(len(sent_ids))

        # Track unique titles
        for title in titles:
            stats['unique_titles'].add(title)
            stats['title_counts'][title] = stats['title_counts'].get(title, 0) + 1

    # Calculate statistics
    stats['avg_supporting_sentences'] = sum(stats['sentence_counts']) / len(stats['sentence_counts'])
    stats['max_supporting_sentences'] = max(stats['sentence_counts'])
    stats['min_supporting_sentences'] = min(stats['sentence_counts'])
    stats['unique_titles_count'] = len(stats['unique_titles'])

    # Get top referenced titles
    top_titles = sorted(stats['title_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    stats['top_referenced_titles'] = [
        {'title': title, 'count': count}
        for title, count in top_titles
    ]

    # Remove the raw set for JSON serialization
    del stats['unique_titles']
    del stats['sentence_counts']  # Too large for summary

    return stats

def save_test_data(test_data: List[Dict], output_file: str):
    """Save test data to JSONL file"""
    print(f"\n保存测试数据到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in test_data:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    print(f"成功保存 {len(test_data)} 条测试数据")

def main():
    # Paths
    base_dir = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/Processed_dataset/hotpotqa'
    validation_file = os.path.join(base_dir, 'validation.jsonl')
    output_file = os.path.join(base_dir, 'validation_vector.jsonl')
    stats_file = os.path.join(base_dir, 'vector/data/test_data_statistics.json')

    # Load original validation data
    original_data = load_validation_data(validation_file)

    # Create test data
    test_data = create_test_data(original_data)

    # Calculate size reduction
    size_stats = calculate_size_reduction(original_data, test_data)

    # Analyze supporting facts
    sf_stats = analyze_supporting_facts(test_data)

    # Print statistics
    print("\n" + "="*50)
    print("测试数据生成统计:")
    print("="*50)
    print(f"总样本数: {len(test_data)}")
    print(f"\n文件大小变化:")
    print(f"  原始大小: {size_stats['original_size_mb']:.2f} MB")
    print(f"  测试数据大小: {size_stats['test_size_mb']:.2f} MB")
    print(f"  减少大小: {size_stats['reduction_mb']:.2f} MB")
    print(f"  压缩比例: {size_stats['reduction_percent']:.1f}%")
    print(f"\n支撑事实统计:")
    print(f"  平均支撑句子数: {sf_stats['avg_supporting_sentences']:.2f}")
    print(f"  最大支撑句子数: {sf_stats['max_supporting_sentences']}")
    print(f"  最小支撑句子数: {sf_stats['min_supporting_sentences']}")
    print(f"  涉及的唯一文档数: {sf_stats['unique_titles_count']}")
    print(f"\n最常被引用的文档 (Top 10):")
    for doc_info in sf_stats['top_referenced_titles']:
        print(f"  - {doc_info['title'][:50]}... : {doc_info['count']} 次")

    # Save test data
    save_test_data(test_data, output_file)

    # Save statistics
    all_stats = {
        'file_stats': size_stats,
        'supporting_facts_stats': sf_stats,
        'total_samples': len(test_data)
    }

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)
    print(f"\n保存统计信息到: {stats_file}")

    print("\n测试数据生成完成! ✓")
    print(f"输出文件: {output_file}")

if __name__ == "__main__":
    main()