from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download
import os
import sys
import json

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Dataset name 
dataset_name = "evalplus/mbppplus"

# Local path for saving
local_path = "D:/temp/Flow_RL/Datasets/mbppplus"
os.makedirs(local_path, exist_ok=True)

print("开始下载 MBPP++ 数据集...")
print(f"数据集: {dataset_name}")
print(f"保存路径: {local_path}")
print("-" * 50)

# Method 1: Try standard dataset loading
print("\n方法1: 尝试标准数据集加载...")
try:
    # Try loading without configuration first
    dataset = load_dataset(dataset_name, cache_dir=local_path)
    
    print("[OK] 数据集加载成功!")
    print(f"数据集信息: {dataset}")
    
    # Check available splits
    for split in dataset.keys():
        print(f"\n{split} 分割:")
        print(f"  样本数: {len(dataset[split])}")
        print(f"  特征: {dataset[split].features}")
        
        # Show first sample
        if len(dataset[split]) > 0:
            sample = dataset[split][0]
            print(f"  第一个样本:")
            for key, value in sample.items():
                if isinstance(value, str):
                    print(f"    {key}: {value[:100]}..." if len(value) > 100 else f"    {key}: {value}")
                else:
                    print(f"    {key}: {value}")
    
    # Save to local files
    print("\n保存数据到本地文件...")
    for split in dataset.keys():
        output_file = os.path.join(local_path, f"mbppplus_{split}.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset[split]:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        print(f"  {split} 保存到: {output_file}")
        
except Exception as e:
    print(f"[ERROR] 标准加载失败: {e}")
    
    # Method 2: Try direct file download
    print("\n方法2: 尝试直接下载文件...")
    try:
        api = HfApi()
        
        # List all files in the repository
        files = api.list_repo_files(repo_id=dataset_name, repo_type="dataset")
        print(f"仓库文件数量: {len(files)}")
        
        # Show all files
        print("仓库文件列表:")
        for file in files[:20]:  # Show first 20 files
            print(f"  - {file}")
        
        # Look for data files
        data_files = [f for f in files if f.endswith(('.json', '.jsonl', '.parquet', '.csv'))]
        print(f"\n数据文件: {data_files}")
        
        # Download data files
        for file_path in data_files:
            print(f"\n下载: {file_path}")
            try:
                local_file = hf_hub_download(
                    repo_id=dataset_name,
                    filename=file_path,
                    repo_type="dataset",
                    cache_dir=local_path
                )
                print(f"  [OK] 保存到: {local_file}")
                
                # Try to read and show sample
                if file_path.endswith('.json'):
                    with open(local_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            print(f"  样本数: {len(data)}")
                            print(f"  第一个样本预览:")
                            first = data[0]
                            for key, value in (first.items() if isinstance(first, dict) else enumerate(first)):
                                if isinstance(value, str):
                                    print(f"    {key}: {value[:100]}...")
                                else:
                                    print(f"    {key}: {value}")
                                    
                elif file_path.endswith('.jsonl'):
                    with open(local_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"  行数: {len(lines)}")
                        if lines:
                            first = json.loads(lines[0])
                            print(f"  第一行预览:")
                            for key, value in first.items():
                                if isinstance(value, str):
                                    print(f"    {key}: {value[:100]}...")
                                else:
                                    print(f"    {key}: {value}")
                        
            except Exception as e:
                print(f"  [ERROR] 下载失败: {e}")
                
    except Exception as e:
        print(f"[ERROR] 直接下载失败: {e}")

print("\n" + "=" * 50)
print("下载过程完成!")