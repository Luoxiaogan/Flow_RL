#!/usr/bin/env python3
"""
Check the actual uniqueness of data in generated datasets.
"""

import json
import os
from collections import Counter


def load_jsonl(filepath: str):
    """Load JSONL file."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def main():
    base_dir = "D:\\temp\\Flow_RL\\Processed_dataset\\group_theory"
    
    for dataset in ["is_simple", "is_abelian", "is_isomorphic", "center"]:
        print(f"\n{dataset}:")
        print("-" * 40)
        
        for split in ["train", "test"]:
            filepath = os.path.join(base_dir, dataset, f"{split}.jsonl")
            if os.path.exists(filepath):
                data = load_jsonl(filepath)
                questions = [item['question'] for item in data]
                unique_questions = list(set(questions))
                
                print(f"{split}: {len(data)} total, {len(unique_questions)} unique")
                
                # Show first few unique examples
                print(f"  First 2 unique examples:")
                for i, q in enumerate(unique_questions[:2]):
                    # Find answer for this question
                    answer = next(item['answer'] for item in data if item['question'] == q)
                    print(f"    Q: {q[:80]}...")
                    print(f"    A: {answer}")
                    print()


if __name__ == "__main__":
    main()