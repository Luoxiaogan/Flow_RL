import json
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def analyze_jsonl_file(file_path):
    """Analyze a JSONL file and return statistics"""
    
    stats = {
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'sample_count': 0,
        'languages': set(),
        'sources': set(),
        'first_sample': None,
        'last_sample': None
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.strip():
            sample = json.loads(line)
            stats['sample_count'] += 1
            
            if 'language' in sample:
                stats['languages'].add(sample['language'])
            if 'source' in sample:
                stats['sources'].add(sample['source'])
            
            if i == 0:
                stats['first_sample'] = sample
            if i == len(lines) - 1:
                stats['last_sample'] = sample
    
    return stats

def main():
    """Generate comprehensive summary of MGSM datasets"""
    
    print("MGSM 数据集处理汇总报告")
    print("=" * 70)
    
    # Directories to check
    base_dir = "D:/temp/Flow_RL"
    
    directories = {
        "原始 TSV 文件": "Datasets/mgsm/datasets--juletxara--mgsm/snapshots/f52417ca77bd71e9888ddc29f92587660725d2b4",
        "处理后 JSONL": "Processed_dataset",
        "训练/测试分割": "Processed_dataset/mgsm_split"
    }
    
    # Check each directory
    for dir_name, dir_path in directories.items():
        full_path = os.path.join(base_dir, dir_path)
        
        print(f"\n### {dir_name}")
        print(f"路径: {full_path}")
        
        if not os.path.exists(full_path):
            print("  [目录不存在]")
            continue
        
        # List relevant files
        if "TSV" in dir_name:
            # List TSV files
            tsv_files = [f for f in os.listdir(full_path) if f.endswith('.tsv')]
            print(f"  TSV 文件数量: {len(tsv_files)}")
            for tsv_file in tsv_files:
                file_path = os.path.join(full_path, tsv_file)
                file_size = os.path.getsize(file_path)
                
                # Count lines in TSV
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                
                print(f"    • {tsv_file}: {line_count} 行, {file_size:,} bytes")
        
        else:
            # List JSONL files for MGSM
            jsonl_files = [f for f in os.listdir(full_path) if 'mgsm' in f and f.endswith('.jsonl')]
            
            if jsonl_files:
                print(f"  MGSM JSONL 文件数量: {len(jsonl_files)}")
                
                total_samples = 0
                for jsonl_file in sorted(jsonl_files):
                    file_path = os.path.join(full_path, jsonl_file)
                    stats = analyze_jsonl_file(file_path)
                    
                    print(f"    • {jsonl_file}:")
                    print(f"        样本数: {stats['sample_count']}")
                    print(f"        文件大小: {stats['file_size']:,} bytes")
                    print(f"        语言: {', '.join(stats['languages'])}")
                    
                    total_samples += stats['sample_count']
                
                if "split" in dir_path:
                    print(f"  总样本数: {total_samples}")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("数据集统计汇总:")
    
    # Check split directory for final stats
    split_dir = os.path.join(base_dir, "Processed_dataset/mgsm_split")
    if os.path.exists(split_dir):
        train_files = [f for f in os.listdir(split_dir) if 'train' in f]
        test_files = [f for f in os.listdir(split_dir) if 'test' in f]
        
        train_total = 0
        test_total = 0
        
        for f in train_files:
            stats = analyze_jsonl_file(os.path.join(split_dir, f))
            train_total += stats['sample_count']
        
        for f in test_files:
            stats = analyze_jsonl_file(os.path.join(split_dir, f))
            test_total += stats['sample_count']
        
        print(f"\n语言数量: 2 (bn, de)")
        print(f"每种语言原始样本: 250")
        print(f"训练集总样本: {train_total}")
        print(f"测试集总样本: {test_total}")
        print(f"训练/测试比例: {train_total}/{test_total} = {train_total/(train_total+test_total)*100:.0f}%/{test_total/(train_total+test_total)*100:.0f}%")
    
    # Processing pipeline summary
    print("\n处理流程:")
    print("  1. 下载原始 TSV 文件 (mgsm_bn.tsv, mgsm_de.tsv)")
    print("  2. 转换为统一 JSONL 格式 (包含 question, answer, final_answer 等字段)")
    print("  3. 80/20 分割为训练集和测试集")
    print("  4. 保存到 Processed_dataset/mgsm_split/ 目录")
    
    print("\n✓ 数据集处理完成，可用于模型训练和评估")

if __name__ == "__main__":
    main()