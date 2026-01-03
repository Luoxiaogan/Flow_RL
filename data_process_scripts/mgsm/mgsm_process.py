import json
import os
import csv
from pathlib import Path
import re
import sys

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def examine_original_data():
    """Examine the format of the original MGSM data"""
    
    # Paths to the downloaded TSV files
    base_path = "D:/temp/Flow_RL/Datasets/mgsm/datasets--juletxara--mgsm/snapshots/f52417ca77bd71e9888ddc29f92587660725d2b4"
    
    languages = {
        'bn': 'mgsm_bn.tsv',
        'de': 'mgsm_de.tsv'
    }
    
    data_stats = {}
    
    for lang, filename in languages.items():
        file_path = os.path.join(base_path, filename)
        
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 - {file_path}")
            continue
            
        print(f"\n检查 {lang} 语言数据集...")
        print(f"文件路径: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # TSV format: question\tanswer
            reader = csv.reader(f, delimiter='\t')
            rows = list(reader)
            
            print(f"数据集大小: {len(rows)} 个样本")
            
            # Show first 3 samples
            print(f"\n前3个样本:")
            for i, row in enumerate(rows[:3]):
                if len(row) >= 2:
                    question = row[0]
                    answer = row[1]
                    print(f"  样本 {i+1}:")
                    print(f"    问题: {question[:100]}...")
                    print(f"    答案: {answer}")
                    print()
            
            data_stats[lang] = {
                'count': len(rows),
                'file': file_path
            }
    
    return data_stats

def extract_answer_from_text(answer_text):
    """Extract numeric answer from answer text"""
    # For MGSM, the answer is usually just a number
    answer_text = str(answer_text).strip()
    
    # If it's already just a number, return it
    if answer_text.replace(',', '').replace('.', '').replace('-', '').isdigit():
        return answer_text.replace(',', '')
    
    # Try to find a number in the text
    # Look for patterns like "= number" or just numbers
    patterns = [
        r'=\s*([\d,.-]+)',
        r':\s*([\d,.-]+)',
        r'([\d,.-]+)\s*$',
        r'([\d,.-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, answer_text)
        if match:
            return match.group(1).replace(',', '')
    
    # If no number found, return the original text
    return answer_text

def process_data_to_jsonl():
    """Process TSV data to JSONL format matching the project structure"""
    
    # Input and output paths
    base_path = "D:/temp/Flow_RL/Datasets/mgsm/datasets--juletxara--mgsm/snapshots/f52417ca77bd71e9888ddc29f92587660725d2b4"
    output_dir = "D:/temp/Flow_RL/Processed_dataset"
    
    os.makedirs(output_dir, exist_ok=True)
    
    languages = {
        'bn': 'mgsm_bn.tsv',
        'de': 'mgsm_de.tsv'
    }
    
    for lang, filename in languages.items():
        input_file = os.path.join(base_path, filename)
        output_file = os.path.join(output_dir, f"mgsm_{lang}.jsonl")
        
        if not os.path.exists(input_file):
            print(f"跳过不存在的文件: {input_file}")
            continue
        
        print(f"\n处理 {lang} 语言数据集...")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        
        processed_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                reader = csv.reader(infile, delimiter='\t')
                
                for idx, row in enumerate(reader):
                    if len(row) >= 2:
                        question = row[0].strip()
                        answer_text = row[1].strip()
                        
                        # Extract numeric answer
                        final_answer = extract_answer_from_text(answer_text)
                        
                        # Create JSONL entry matching GSM8K format
                        entry = {
                            "idx": idx,
                            "question": question,
                            "answer": answer_text,  # Original answer
                            "final_answer": final_answer,  # Extracted numeric answer
                            "language": lang,
                            "source": "mgsm"
                        }
                        
                        # Write as JSONL (one JSON object per line)
                        json.dump(entry, outfile, ensure_ascii=False)
                        outfile.write('\n')
                        
                        processed_count += 1
                        
                        # Show progress every 50 samples
                        if (processed_count + 1) % 50 == 0:
                            print(f"  已处理 {processed_count} 个样本...")
        
        print(f"✓ 完成! 共处理 {processed_count} 个样本")
        print(f"  输出保存到: {output_file}")

def verify_processed_data():
    """Verify the processed JSONL files"""
    
    output_dir = "D:/temp/Flow_RL/Processed_dataset"
    languages = ['bn', 'de']
    
    print("\n验证处理后的数据...")
    print("=" * 50)
    
    for lang in languages:
        output_file = os.path.join(output_dir, f"mgsm_{lang}.jsonl")
        
        if not os.path.exists(output_file):
            print(f"文件不存在: {output_file}")
            continue
        
        print(f"\n检查 mgsm_{lang}.jsonl:")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"  总行数: {len(lines)}")
            
            # Check first entry
            if lines:
                first_entry = json.loads(lines[0])
                print(f"  第一个条目:")
                print(f"    idx: {first_entry['idx']}")
                print(f"    question: {first_entry['question'][:100]}...")
                print(f"    final_answer: {first_entry['final_answer']}")
                print(f"    language: {first_entry['language']}")
                print(f"    source: {first_entry['source']}")

def main():
    """Main processing pipeline"""
    print("MGSM 数据集处理脚本")
    print("=" * 50)
    
    # Step 1: Examine original data
    print("\n步骤 1: 检查原始数据")
    data_stats = examine_original_data()
    
    # Step 2: Process to JSONL
    print("\n步骤 2: 转换为 JSONL 格式")
    process_data_to_jsonl()
    
    # Step 3: Verify processed data
    print("\n步骤 3: 验证处理结果")
    verify_processed_data()
    
    print("\n" + "=" * 50)
    print("处理完成!")
    
    # Summary
    print("\n数据集统计:")
    for lang, stats in data_stats.items():
        print(f"  {lang}: {stats['count']} 个样本")

if __name__ == "__main__":
    main()