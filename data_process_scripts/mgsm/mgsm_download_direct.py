import os
import json
import requests
from huggingface_hub import HfApi, hf_hub_download
from pathlib import Path

# Languages to download
languages = ["bn", "de"]  # Bengali and German

# Local path for saving
local_path = "D:/temp/Flow_RL/Datasets/mgsm"
os.makedirs(local_path, exist_ok=True)

print("开始下载 MGSM 数据集 (直接下载方法)...")
print(f"目标语言: {', '.join(languages)}")
print(f"保存路径: {local_path}")
print("-" * 50)

# Initialize HF API
api = HfApi()

# Get repository information
repo_id = "juletxara/mgsm"
print(f"\n获取仓库信息: {repo_id}")

try:
    # List all files in the repository
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    print(f"仓库中的文件数量: {len(files)}")
    
    # Filter files for our target languages
    target_files = []
    for lang in languages:
        lang_files = [f for f in files if lang in f and (f.endswith('.json') or f.endswith('.jsonl') or f.endswith('.tsv'))]
        target_files.extend(lang_files)
        print(f"  {lang} 相关文件: {lang_files}")
    
    if not target_files:
        print("\n查找其他格式文件...")
        # Look for any files containing language codes
        for lang in languages:
            pattern_files = [f for f in files if f"mgsm_{lang}" in f or f"{lang}.json" in f or f"{lang}_" in f]
            if pattern_files:
                target_files.extend(pattern_files)
                print(f"  找到 {lang} 文件: {pattern_files}")
    
    # Download each file
    print(f"\n需要下载的文件: {target_files}")
    
    for file_path in target_files:
        print(f"\n下载文件: {file_path}")
        try:
            # Download file
            local_file = hf_hub_download(
                repo_id=repo_id,
                filename=file_path,
                repo_type="dataset",
                cache_dir=local_path
            )
            print(f"  [OK] 下载成功: {local_file}")
            
            # Try to read and display sample
            if file_path.endswith('.json') or file_path.endswith('.jsonl'):
                with open(local_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    print(f"  文件预览 (前3行):")
                    for line in lines:
                        print(f"    {line[:100]}...")
                        
        except Exception as e:
            print(f"  [ERROR] 下载失败: {e}")
    
    # Also try to download the main test files directly
    print("\n尝试下载测试集文件...")
    test_files = ["test.json", "test.jsonl", "mgsm_bn.tsv", "mgsm_de.tsv"]
    for test_file in test_files:
        if test_file in files:
            print(f"  下载 {test_file}...")
            try:
                local_file = hf_hub_download(
                    repo_id=repo_id,
                    filename=test_file,
                    repo_type="dataset",
                    cache_dir=local_path
                )
                print(f"    [OK] 成功: {local_file}")
            except Exception as e:
                print(f"    [ERROR] 失败: {e}")
                
except Exception as e:
    print(f"[ERROR] 获取仓库信息失败: {e}")

print("\n" + "=" * 50)
print("下载完成!")
print(f"数据保存在: {local_path}")