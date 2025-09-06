import json
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def examine_original_data():
    """Examine the format of the original MBPP++ data"""
    
    # Path to the downloaded JSONL file
    input_file = "D:/temp/Flow_RL/Datasets/mbppplus/mbppplus_test.jsonl"
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        return None
    
    print(f"检查 MBPP++ 数据集...")
    print(f"文件路径: {input_file}")
    
    # Read and analyze data
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"数据集大小: {len(lines)} 个样本")
    
    # Parse and analyze structure
    samples = []
    for line in lines:
        if line.strip():
            samples.append(json.loads(line))
    
    # Show sample structure
    if samples:
        print(f"\n数据字段:")
        for key in samples[0].keys():
            print(f"  - {key}")
        
        print(f"\n前3个样本:")
        for i, sample in enumerate(samples[:3]):
            print(f"\n样本 {i+1}:")
            print(f"  task_id: {sample['task_id']}")
            print(f"  prompt: {sample['prompt'][:100]}...")
            print(f"  code长度: {len(sample['code'])} 字符")
            print(f"  test_list数量: {len(sample.get('test_list', []))}")
    
    return {
        'file_path': input_file,
        'sample_count': len(samples),
        'samples': samples
    }

def process_data_to_jsonl():
    """Process MBPP++ data to standardized JSONL format"""
    
    # Input and output paths
    input_file = "D:/temp/Flow_RL/Datasets/mbppplus/mbppplus_test.jsonl"
    output_dir = "D:/temp/Flow_RL/Processed_dataset"
    output_file = os.path.join(output_dir, "mbppplus.jsonl")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n处理 MBPP++ 数据集...")
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
                
                # Create standardized entry
                entry = {
                    "idx": idx,
                    "task_id": sample["task_id"],
                    "prompt": sample["prompt"],
                    "code": sample["code"],
                    "test_list": sample.get("test_list", []),
                    "test_imports": sample.get("test_imports", []),
                    "test": sample.get("test", ""),
                    "source_file": sample.get("source_file", ""),
                    "source": "mbppplus"
                }
                
                # Write as JSONL
                json.dump(entry, outfile, ensure_ascii=False)
                outfile.write('\n')
                
                processed_count += 1
                
                # Show progress every 50 samples
                if (processed_count + 1) % 50 == 0:
                    print(f"  已处理 {processed_count} 个样本...")
    
    print(f"✓ 完成! 共处理 {processed_count} 个样本")
    print(f"  输出保存到: {output_file}")
    
    return output_file, processed_count

def verify_processed_data():
    """Verify the processed JSONL file"""
    
    output_file = "D:/temp/Flow_RL/Processed_dataset/mbppplus.jsonl"
    
    print("\n验证处理后的数据...")
    print("=" * 50)
    
    if not os.path.exists(output_file):
        print(f"文件不存在: {output_file}")
        return
    
    print(f"检查 mbppplus.jsonl:")
    
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"  总行数: {len(lines)}")
        
        # Check first and last entries
        if lines:
            first_entry = json.loads(lines[0])
            last_entry = json.loads(lines[-1])
            
            print(f"\n  第一个条目:")
            print(f"    idx: {first_entry['idx']}")
            print(f"    task_id: {first_entry['task_id']}")
            print(f"    prompt: {first_entry['prompt'][:80]}...")
            print(f"    code长度: {len(first_entry['code'])} 字符")
            print(f"    test_list数量: {len(first_entry['test_list'])}")
            print(f"    source: {first_entry['source']}")
            
            print(f"\n  最后一个条目:")
            print(f"    idx: {last_entry['idx']}")
            print(f"    task_id: {last_entry['task_id']}")
            print(f"    prompt: {last_entry['prompt'][:80]}...")
            print(f"    source: {last_entry['source']}")

def main():
    """Main processing pipeline"""
    print("MBPP++ 数据集处理脚本")
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

if __name__ == "__main__":
    main()