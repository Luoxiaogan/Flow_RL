#!/usr/bin/env python3
"""
01_extract_documents.py
Extract and deduplicate documents from HotpotQA validation set
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Set
import hashlib
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

def extract_documents(data: List[Dict]) -> Dict[str, Dict]:
    """
    Extract all documents from the dataset and deduplicate by title
    Returns: {title: document_info}
    """
    documents = {}
    doc_id_counter = 0
    source_indices = defaultdict(list)

    print("提取文档中...")
    for idx, sample in enumerate(tqdm(data, desc="处理样本")):
        context = sample.get('context', {})
        titles = context.get('title', [])
        sentences_list = context.get('sentences', [])

        for title, sentences in zip(titles, sentences_list):
            if title not in documents:
                # Create new document entry
                doc_id = f"doc_{doc_id_counter:05d}"
                doc_id_counter += 1

                # Join sentences to create full text
                full_text = " ".join(sentences)

                documents[title] = {
                    'doc_id': doc_id,
                    'title': title,
                    'sentences': sentences,
                    'full_text': full_text,
                    'num_sentences': len(sentences),
                    'text_length': len(full_text),
                    'source_indices': []
                }

            # Track which samples this document appears in
            documents[title]['source_indices'].append(idx)

    # Remove duplicate indices
    for doc in documents.values():
        doc['source_indices'] = list(set(doc['source_indices']))
        doc['appearance_count'] = len(doc['source_indices'])

    return documents

def calculate_statistics(documents: Dict[str, Dict], data: List[Dict]) -> Dict:
    """Calculate statistics about the extracted documents"""
    stats = {
        'total_samples': len(data),
        'unique_documents': len(documents),
        'total_document_occurrences': sum(len(sample.get('context', {}).get('title', []))
                                         for sample in data),
        'avg_doc_length': sum(doc['text_length'] for doc in documents.values()) / len(documents),
        'avg_sentences_per_doc': sum(doc['num_sentences'] for doc in documents.values()) / len(documents),
        'max_doc_length': max(doc['text_length'] for doc in documents.values()),
        'min_doc_length': min(doc['text_length'] for doc in documents.values()),
    }

    # Document appearance frequency
    appearance_counts = [doc['appearance_count'] for doc in documents.values()]
    stats['max_appearances'] = max(appearance_counts)
    stats['min_appearances'] = min(appearance_counts)
    stats['avg_appearances'] = sum(appearance_counts) / len(appearance_counts)

    # Documents that appear most frequently
    most_frequent = sorted(documents.items(),
                          key=lambda x: x[1]['appearance_count'],
                          reverse=True)[:10]
    stats['most_frequent_documents'] = [
        {'title': title, 'count': doc['appearance_count']}
        for title, doc in most_frequent
    ]

    return stats

def save_documents(documents: Dict[str, Dict], output_dir: str):
    """Save documents to JSONL file"""
    output_file = os.path.join(output_dir, 'documents.jsonl')

    print(f"\n保存文档到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for title, doc in documents.items():
            # Don't save source_indices in the main file (too large)
            doc_to_save = {k: v for k, v in doc.items() if k != 'source_indices'}
            f.write(json.dumps(doc_to_save, ensure_ascii=False) + '\n')

    print(f"成功保存 {len(documents)} 个唯一文档")

    # Save document index mapping
    index_file = os.path.join(output_dir, 'document_index.json')
    index_data = {
        'title_to_doc_id': {title: doc['doc_id'] for title, doc in documents.items()},
        'doc_id_to_title': {doc['doc_id']: title for title, doc in documents.items()}
    }

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"保存文档索引到: {index_file}")

    # Save document appearance mapping (for analysis)
    appearance_file = os.path.join(output_dir, 'document_appearances.json')
    appearances = {
        title: {
            'doc_id': doc['doc_id'],
            'source_indices': doc['source_indices'],
            'count': doc['appearance_count']
        }
        for title, doc in documents.items()
    }

    with open(appearance_file, 'w', encoding='utf-8') as f:
        json.dump(appearances, f, ensure_ascii=False, indent=2)
    print(f"保存文档出现记录到: {appearance_file}")

def main():
    # Paths
    base_dir = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/Processed_dataset/hotpotqa'
    validation_file = os.path.join(base_dir, 'validation.jsonl')
    output_dir = os.path.join(base_dir, 'vector/data')

    # Load data
    data = load_validation_data(validation_file)

    # Extract and deduplicate documents
    documents = extract_documents(data)

    # Calculate statistics
    stats = calculate_statistics(documents, data)

    # Print statistics
    print("\n" + "="*50)
    print("文档提取统计:")
    print("="*50)
    print(f"总样本数: {stats['total_samples']}")
    print(f"总文档出现次数: {stats['total_document_occurrences']}")
    print(f"唯一文档数: {stats['unique_documents']}")
    print(f"去重比例: {(1 - stats['unique_documents']/stats['total_document_occurrences'])*100:.2f}%")
    print(f"\n文档长度统计:")
    print(f"  平均长度: {stats['avg_doc_length']:.0f} 字符")
    print(f"  最大长度: {stats['max_doc_length']} 字符")
    print(f"  最小长度: {stats['min_doc_length']} 字符")
    print(f"  平均句子数: {stats['avg_sentences_per_doc']:.1f}")
    print(f"\n文档出现频率:")
    print(f"  最多出现: {stats['max_appearances']} 次")
    print(f"  最少出现: {stats['min_appearances']} 次")
    print(f"  平均出现: {stats['avg_appearances']:.2f} 次")
    print(f"\n最频繁出现的文档 (Top 10):")
    for doc_info in stats['most_frequent_documents']:
        print(f"  - {doc_info['title'][:50]}... : {doc_info['count']} 次")

    # Save documents and statistics
    save_documents(documents, output_dir)

    # Save statistics
    stats_file = os.path.join(output_dir, 'extraction_statistics.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n保存统计信息到: {stats_file}")

    print("\n文档提取完成! ✓")

if __name__ == "__main__":
    main()