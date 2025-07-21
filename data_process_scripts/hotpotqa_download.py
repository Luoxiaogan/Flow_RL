# HotpotQA 下载脚本
# 由于 Hugging Face datasets 不再支持旧的脚本格式，我们需要使用其他方法

import os
import json
import requests
from tqdm import tqdm

def download_hotpotqa_direct():
    """直接从原始源下载 HotpotQA 数据集"""
    
    # 创建保存目录
    save_dir = "/Users/luogan/Code/workflow_generation/Flow_RL/Datasets/hotpotqa"
    os.makedirs(save_dir, exist_ok=True)
    
    # HotpotQA 官方下载链接
    urls = {
        "train": "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_train_v1.1.json",
        "dev": "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json",
        "dev_fullwiki": "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_fullwiki_v1.json"
    }
    
    for split, url in urls.items():
        filename = os.path.join(save_dir, f"hotpot_{split}.json")
        
        # 如果文件已存在，跳过下载
        if os.path.exists(filename):
            print(f"{split} 文件已存在: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  共 {len(data)} 条数据")
            continue
        
        print(f"正在下载 {split} 数据集...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载并保存
            with open(filename, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=split) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            # 验证下载的文件
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"{split} 下载完成，共 {len(data)} 条数据")
                
        except requests.exceptions.RequestException as e:
            print(f"下载 {split} 失败: {e}")
        except json.JSONDecodeError as e:
            print(f"{split} 文件解析失败: {e}")
            # 删除损坏的文件
            if os.path.exists(filename):
                os.remove(filename)

def convert_to_jsonl(json_file, jsonl_file):
    """将 JSON 格式转换为 JSONL 格式"""
    print(f"正在转换 {json_file} 到 {jsonl_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"转换完成，共 {len(data)} 条数据")

if __name__ == "__main__":
    # 1. 下载原始数据
    download_hotpotqa_direct()
    
    # 2. 可选：转换为 JSONL 格式
    save_dir = "/Users/luogan/Code/workflow_generation/Flow_RL/Datasets/hotpotqa"
    
    # 转换训练集
    train_json = os.path.join(save_dir, "hotpot_train.json")
    train_jsonl = os.path.join(save_dir, "train.jsonl")
    if os.path.exists(train_json) and not os.path.exists(train_jsonl):
        convert_to_jsonl(train_json, train_jsonl)
    
    # 转换验证集
    dev_json = os.path.join(save_dir, "hotpot_dev.json")
    dev_jsonl = os.path.join(save_dir, "validation.jsonl")
    if os.path.exists(dev_json) and not os.path.exists(dev_jsonl):
        convert_to_jsonl(dev_json, dev_jsonl)