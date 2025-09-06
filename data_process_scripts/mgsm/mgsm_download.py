from datasets import load_dataset
import os
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Dataset name and languages to download
dataset_name = "juletxara/mgsm"
languages = ["bn", "de"]  # Bengali and German

# Local path for saving
local_path = "D:/temp/Flow_RL/Datasets/mgsm"
os.makedirs(local_path, exist_ok=True)

print("开始下载 MGSM 数据集...")
print(f"目标语言: {', '.join(languages)}")
print(f"保存路径: {local_path}")
print("-" * 50)

# Store all downloaded datasets
all_datasets = {}

for lang in languages:
    print(f"\n正在下载 {lang} 语言子集...")
    
    try:
        # Try new loading format first (trust_remote_code for newer datasets)
        dataset = load_dataset(dataset_name, lang, cache_dir=local_path, trust_remote_code=True)
        all_datasets[lang] = dataset
        
        print(f"[OK] {lang} 下载成功!")
        print(f"  数据集信息: {dataset}")
        
        # Show sample from test set (MGSM only has test set)
        if 'test' in dataset:
            print(f"  测试集大小: {len(dataset['test'])}")
            print(f"  示例问题:")
            sample = dataset['test'][0]
            print(f"    Question: {sample['question'][:100]}...")
            print(f"    Answer: {sample.get('answer', 'N/A')}")
            if 'answer_number' in sample:
                print(f"    Answer Number: {sample['answer_number']}")
                
    except Exception as e:
        print(f"[ERROR] {lang} 下载失败: {e}")
        # Try alternative approach using direct download
        print(f"  尝试备用方法...")
        try:
            # Try without specifying configuration
            dataset = load_dataset(f"juletxara/mgsm", split=f"test", cache_dir=local_path, trust_remote_code=True)
            all_datasets[lang] = dataset
            print(f"  [OK] 使用备用方法成功!")
        except Exception as e2:
            print(f"  [ERROR] 备用方法也失败: {e2}")

print("\n" + "=" * 50)
print("下载完成!")
print(f"成功下载的语言: {list(all_datasets.keys())}")
print(f"数据保存在: {local_path}")