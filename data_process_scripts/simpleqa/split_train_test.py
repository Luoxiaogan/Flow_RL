import json
import os
import random
from pathlib import Path
import sys

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def split_jsonl_file(input_file, output_dir, train_ratio=0.8, random_seed=42):
    """
    Split a JSONL file into train and test sets
    
    Args:
        input_file: Path to input JSONL file
        output_dir: Directory to save split files
        train_ratio: Ratio of data for training (default 0.8)
        random_seed: Random seed for reproducibility
    """
    
    # Set random seed for reproducibility
    random.seed(random_seed)
    
    # Get base filename without extension
    base_name = Path(input_file).stem
    
    # Read all data
    print(f"\n处理文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse JSON lines
    data = []
    for line in lines:
        if line.strip():  # Skip empty lines
            data.append(json.loads(line))
    
    total_samples = len(data)
    print(f"  总样本数: {total_samples}")
    
    # Shuffle data
    indices = list(range(total_samples))
    random.shuffle(indices)
    
    # Calculate split point
    train_size = int(total_samples * train_ratio)
    test_size = total_samples - train_size
    
    # Split indices
    train_indices = sorted(indices[:train_size])
    test_indices = sorted(indices[train_size:])
    
    print(f"  训练集大小: {train_size} ({train_ratio*100:.0f}%)")
    print(f"  测试集大小: {test_size} ({(1-train_ratio)*100:.0f}%)")
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect statistics
    train_topics = {}
    test_topics = {}
    train_answer_types = {}
    test_answer_types = {}
    
    # Write train file
    train_file = os.path.join(output_dir, f"{base_name}_train.jsonl")
    with open(train_file, 'w', encoding='utf-8') as f:
        for i, idx in enumerate(train_indices):
            sample = data[idx].copy()
            # Update idx to be sequential in the new file
            sample['idx'] = i
            
            # Collect stats
            train_topics[sample.get('topic', 'Unknown')] = train_topics.get(sample.get('topic', 'Unknown'), 0) + 1
            train_answer_types[sample.get('answer_type', 'Unknown')] = train_answer_types.get(sample.get('answer_type', 'Unknown'), 0) + 1
            
            json.dump(sample, f, ensure_ascii=False)
            f.write('\n')
    print(f"  训练集保存到: {train_file}")
    
    # Write test file
    test_file = os.path.join(output_dir, f"{base_name}_test.jsonl")
    with open(test_file, 'w', encoding='utf-8') as f:
        for i, idx in enumerate(test_indices):
            sample = data[idx].copy()
            # Update idx to be sequential in the new file
            sample['idx'] = i
            
            # Collect stats
            test_topics[sample.get('topic', 'Unknown')] = test_topics.get(sample.get('topic', 'Unknown'), 0) + 1
            test_answer_types[sample.get('answer_type', 'Unknown')] = test_answer_types.get(sample.get('answer_type', 'Unknown'), 0) + 1
            
            json.dump(sample, f, ensure_ascii=False)
            f.write('\n')
    print(f"  测试集保存到: {test_file}")
    
    # Show distribution
    print(f"\n  训练集主题分布 (前3个):")
    for topic, count in sorted(train_topics.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {topic}: {count}")
    
    print(f"\n  测试集主题分布 (前3个):")
    for topic, count in sorted(test_topics.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {topic}: {count}")
    
    print(f"\n  训练集答案类型分布:")
    for atype, count in sorted(train_answer_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {atype}: {count}")
    
    print(f"\n  测试集答案类型分布:")
    for atype, count in sorted(test_answer_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {atype}: {count}")
    
    return {
        'train_file': train_file,
        'test_file': test_file,
        'train_size': train_size,
        'test_size': test_size,
        'train_topics': train_topics,
        'test_topics': test_topics
    }

def verify_split(train_file, test_file):
    """Verify the split files"""
    
    print(f"\n验证分割文件:")
    
    # Check train file
    with open(train_file, 'r', encoding='utf-8') as f:
        train_lines = f.readlines()
        if train_lines:
            first_train = json.loads(train_lines[0])
            print(f"  训练集第一个样本:")
            print(f"    idx: {first_train['idx']}")
            print(f"    question: {first_train['question'][:60]}...")
            print(f"    answer: {first_train['answer']}")
            print(f"    topic: {first_train.get('topic', 'N/A')}")
            print(f"    answer_type: {first_train.get('answer_type', 'N/A')}")
    
    # Check test file
    with open(test_file, 'r', encoding='utf-8') as f:
        test_lines = f.readlines()
        if test_lines:
            first_test = json.loads(test_lines[0])
            print(f"  测试集第一个样本:")
            print(f"    idx: {first_test['idx']}")
            print(f"    question: {first_test['question'][:60]}...")
            print(f"    answer: {first_test['answer']}")
            print(f"    topic: {first_test.get('topic', 'N/A')}")
            print(f"    answer_type: {first_test.get('answer_type', 'N/A')}")
    
    print(f"\n  训练集总行数: {len(train_lines)}")
    print(f"  测试集总行数: {len(test_lines)}")

def main():
    """Main function to split SimpleQA dataset"""
    
    print("SimpleQA 数据集训练/测试分割")
    print("=" * 60)
    
    # Input and output directories
    input_dir = "D:/temp/Flow_RL/Processed_dataset"
    output_dir = "D:/temp/Flow_RL/Processed_dataset/simpleqa_split"
    
    # Configuration
    train_ratio = 0.8  # 80% for training, 20% for testing
    random_seed = 42   # For reproducibility
    
    print(f"\n配置:")
    print(f"  输入目录: {input_dir}")
    print(f"  输出目录: {output_dir}")
    print(f"  训练集比例: {train_ratio*100:.0f}%")
    print(f"  测试集比例: {(1-train_ratio)*100:.0f}%")
    print(f"  随机种子: {random_seed}")
    
    # Process SimpleQA file
    input_file = os.path.join(input_dir, "simpleqa.jsonl")
    
    if not os.path.exists(input_file):
        print(f"\n[错误] 文件不存在: {input_file}")
        print("请先运行 simpleqa_process.py 生成处理后的数据")
        return
    
    # Split the file
    result = split_jsonl_file(
        input_file=input_file,
        output_dir=output_dir,
        train_ratio=train_ratio,
        random_seed=random_seed
    )
    
    # Verify the split
    verify_split(result['train_file'], result['test_file'])
    
    # Summary
    print("\n" + "=" * 60)
    print("分割完成！")
    print(f"\n汇总:")
    print(f"  训练集: {result['train_size']} 样本")
    print(f"  测试集: {result['test_size']} 样本")
    print(f"  总样本数: {result['train_size'] + result['test_size']}")
    print(f"  训练集主题数: {len(result['train_topics'])}")
    print(f"  测试集主题数: {len(result['test_topics'])}")
    
    # List all generated files
    print(f"\n生成的文件:")
    if os.path.exists(output_dir):
        split_files = os.listdir(output_dir)
        for file in sorted(split_files):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  {file} ({file_size:,} bytes)")

if __name__ == "__main__":
    main()