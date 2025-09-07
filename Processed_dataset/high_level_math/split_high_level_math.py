import json
import os
from pathlib import Path
import random

# Set random seed for reproducibility
random.seed(42)

# Define base paths
base_path = Path("D:/temp/Flow_RL/Processed_dataset/high_level_math")
output_path = base_path

# Define datasets to process
datasets = [
    ("aime_2024.jsonl", "aime2024"),
    ("aime_2025.jsonl", "aime2025"),
    ("limr.jsonl", "limr"),
    ("math_500.jsonl", "math500")
]

def split_dataset(input_file, output_prefix, train_ratio=0.2):
    """Split a JSONL dataset into train and test sets."""
    
    # Read all data
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    
    # Shuffle data with fixed seed
    random.shuffle(data)
    
    # Calculate split point
    n_total = len(data)
    n_train = int(n_total * train_ratio)
    
    # Split data
    train_data = data[:n_train]
    test_data = data[n_train:]
    
    # Create output directory if it doesn't exist
    output_dir = output_path / output_prefix
    output_dir.mkdir(exist_ok=True)
    
    # Write train data
    train_file = output_dir / "train.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # Write test data
    test_file = output_dir / "test.jsonl"
    with open(test_file, 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Dataset: {output_prefix}")
    print(f"  Total: {n_total} samples")
    print(f"  Train: {len(train_data)} samples ({len(train_data)/n_total*100:.1f}%)")
    print(f"  Test: {len(test_data)} samples ({len(test_data)/n_total*100:.1f}%)")
    print(f"  Saved to: {output_dir}")
    print()
    
    return len(train_data), len(test_data)

def main():
    print("=" * 60)
    print("Splitting high_level_math datasets")
    print("Train ratio: 20%, Test ratio: 80%")
    print("Random seed: 42")
    print("=" * 60)
    print()
    
    total_train = 0
    total_test = 0
    
    for input_filename, output_prefix in datasets:
        input_file = base_path / input_filename
        if input_file.exists():
            n_train, n_test = split_dataset(input_file, output_prefix)
            total_train += n_train
            total_test += n_test
        else:
            print(f"Warning: {input_file} not found, skipping...")
            print()
    
    print("=" * 60)
    print("Summary:")
    print(f"Total train samples: {total_train}")
    print(f"Total test samples: {total_test}")
    print(f"Total samples: {total_train + total_test}")
    print("=" * 60)

if __name__ == "__main__":
    main()