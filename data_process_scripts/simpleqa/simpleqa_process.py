import json
import os
import sys
from pathlib import Path
import ast

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def parse_metadata(metadata_str):
    """Parse metadata string to dictionary"""
    try:
        # Use ast.literal_eval for safe evaluation
        metadata_dict = ast.literal_eval(metadata_str)
        return metadata_dict
    except:
        # If parsing fails, return as string
        return metadata_str

def examine_original_data():
    """Examine the format of the original SimpleQA data"""
    
    # Path to the downloaded JSONL file
    input_file = "D:/temp/Flow_RL/Datasets/simpleqa/simpleqa_test.jsonl"
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        return None
    
    print(f"检查 SimpleQA 数据集...")
    print(f"文件路径: {input_file}")
    
    # Read and analyze data
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"数据集大小: {len(lines)} 个样本")
    
    # Parse and analyze structure
    samples = []
    topics = {}
    answer_types = {}
    
    for line in lines:
        if line.strip():
            sample = json.loads(line)
            samples.append(sample)
            
            # Parse metadata
            metadata = parse_metadata(sample.get('metadata', ''))
            if isinstance(metadata, dict):
                topic = metadata.get('topic', 'Unknown')
                answer_type = metadata.get('answer_type', 'Unknown')
                topics[topic] = topics.get(topic, 0) + 1
                answer_types[answer_type] = answer_types.get(answer_type, 0) + 1
    
    # Show statistics
    print(f"\n主题分布:")
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {topic}: {count} 个样本")
    
    print(f"\n答案类型分布:")
    for atype, count in sorted(answer_types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {atype}: {count} 个样本")
    
    # Show sample structure
    if samples:
        print(f"\n数据字段:")
        for key in samples[0].keys():
            print(f"  - {key}")
        
        print(f"\n前3个样本:")
        for i, sample in enumerate(samples[:3]):
            metadata = parse_metadata(sample.get('metadata', ''))
            print(f"\n样本 {i+1}:")
            print(f"  问题: {sample['problem'][:100]}...")
            print(f"  答案: {sample['answer']}")
            if isinstance(metadata, dict):
                print(f"  主题: {metadata.get('topic', 'N/A')}")
                print(f"  答案类型: {metadata.get('answer_type', 'N/A')}")
    
    return {
        'file_path': input_file,
        'sample_count': len(samples),
        'samples': samples,
        'topics': topics,
        'answer_types': answer_types
    }

def process_data_to_jsonl():
    """Process SimpleQA data to standardized JSONL format"""
    
    # Input and output paths
    input_file = "D:/temp/Flow_RL/Datasets/simpleqa/simpleqa_test.jsonl"
    output_dir = "D:/temp/Flow_RL/Processed_dataset"
    output_file = os.path.join(output_dir, "simpleqa.jsonl")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n处理 SimpleQA 数据集...")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    
    # Read original data
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed_count = 0
    
    # Process and write to new format
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx, line in enumerate(lines):
            if line.strip():
                sample = json.loads(line)
                
                # Parse metadata
                metadata = parse_metadata(sample.get('metadata', ''))
                
                # Create standardized entry
                entry = {
                    "idx": idx,
                    "question": sample["problem"],
                    "answer": sample["answer"],
                    "topic": metadata.get('topic', 'Unknown') if isinstance(metadata, dict) else 'Unknown',
                    "answer_type": metadata.get('answer_type', 'Unknown') if isinstance(metadata, dict) else 'Unknown',
                    "urls": metadata.get('urls', []) if isinstance(metadata, dict) else [],
                    "source": "simpleqa",
                    "original_metadata": sample.get('metadata', '')
                }
                
                # Write as JSONL
                json.dump(entry, outfile, ensure_ascii=False)
                outfile.write('\n')
                
                processed_count += 1
                
                # Show progress every 500 samples
                if (processed_count + 1) % 500 == 0:
                    print(f"  已处理 {processed_count} 个样本...")
    
    print(f"✓ 完成! 共处理 {processed_count} 个样本")
    print(f"  输出保存到: {output_file}")
    
    return output_file, processed_count

def verify_processed_data():
    """Verify the processed JSONL file"""
    
    output_file = "D:/temp/Flow_RL/Processed_dataset/simpleqa.jsonl"
    
    print("\n验证处理后的数据...")
    print("=" * 50)
    
    if not os.path.exists(output_file):
        print(f"文件不存在: {output_file}")
        return
    
    print(f"检查 simpleqa.jsonl:")
    
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"  总行数: {len(lines)}")
        
        # Collect statistics
        topics = {}
        answer_types = {}
        
        for line in lines:
            if line.strip():
                entry = json.loads(line)
                topics[entry['topic']] = topics.get(entry['topic'], 0) + 1
                answer_types[entry['answer_type']] = answer_types.get(entry['answer_type'], 0) + 1
        
        # Check first and last entries
        if lines:
            first_entry = json.loads(lines[0])
            last_entry = json.loads(lines[-1])
            
            print(f"\n  第一个条目:")
            print(f"    idx: {first_entry['idx']}")
            print(f"    question: {first_entry['question'][:60]}...")
            print(f"    answer: {first_entry['answer']}")
            print(f"    topic: {first_entry['topic']}")
            print(f"    answer_type: {first_entry['answer_type']}")
            print(f"    source: {first_entry['source']}")
            
            print(f"\n  最后一个条目:")
            print(f"    idx: {last_entry['idx']}")
            print(f"    question: {last_entry['question'][:60]}...")
            print(f"    answer: {last_entry['answer']}")
            print(f"    topic: {last_entry['topic']}")
            
        print(f"\n  主题统计 (前5个):")
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {topic}: {count}")
            
        print(f"\n  答案类型统计:")
        for atype, count in sorted(answer_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    {atype}: {count}")

def main():
    """Main processing pipeline"""
    print("SimpleQA 数据集处理脚本")
    print("=" * 50)
    
    # Step 1: Examine original data
    print("\n步骤 1: 检查原始数据")
    data_info = examine_original_data()
    
    if not data_info:
        print("无法读取原始数据，退出处理")
        return
    
    # Step 2: Process to standardized JSONL
    print("\n步骤 2: 转换为标准化 JSONL 格式")
    output_file, count = process_data_to_jsonl()
    
    # Step 3: Verify processed data
    print("\n步骤 3: 验证处理结果")
    verify_processed_data()
    
    print("\n" + "=" * 50)
    print("处理完成!")
    print(f"\n数据集统计:")
    print(f"  总样本数: {count}")
    print(f"  输出文件: {output_file}")
    print(f"  主题数: {len(data_info['topics'])}")
    print(f"  答案类型数: {len(data_info['answer_types'])}")

if __name__ == "__main__":
    main()