import json
import os
import random
from datasets import load_dataset
from pathlib import Path

def examine_hotpotqa_data():
    """检查HotpotQA数据的格式"""
    try:
        print("加载HotpotQA数据集...")
        cache_dir = "/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/hotpotqa"
        
        # 加载训练集和验证集
        train_ds = load_dataset("hotpot_qa", "distractor", split="train", cache_dir=cache_dir)
        validation_ds = load_dataset("hotpot_qa", "distractor", split="validation", cache_dir=cache_dir)
        
        print(f"训练集大小: {len(train_ds)}")
        print(f"验证集大小: {len(validation_ds)}")
        print(f"训练集特征: {train_ds.features}")
        
        # 检查样本格式
        print("\n训练集前3个样本:")
        for i in range(min(3, len(train_ds))):
            sample = train_ds[i]
            print(f"  样本 {i+1}:")
            print(f"    问题: {sample['question'][:100]}...")
            print(f"    答案: {sample['answer'][:50]}...")
            if 'supporting_facts' in sample:
                print(f"    支撑事实数量: {len(sample['supporting_facts'])}")
            print()
        
        return train_ds, validation_ds
        
    except Exception as e:
        print(f"加载数据集时出错: {e}")
        return None, None

def sample_and_process_hotpotqa():
    """采样并处理HotpotQA数据为JSONL格式"""
    try:
        print("=== 步骤1: 加载原始数据 ===")
        train_ds, validation_ds = examine_hotpotqa_data()
        
        if train_ds is None or validation_ds is None:
            print("无法加载数据集")
            return False
        
        # 设置随机种子保证可复现性
        random.seed(42)
        
        print("\n=== 步骤2: 随机采样 ===")
        # 从训练集随机采样8000条
        train_indices = list(range(len(train_ds)))
        random.shuffle(train_indices)
        sampled_train_indices = train_indices[:8000]
        
        # 从验证集随机采样1500条
        val_indices = list(range(len(validation_ds)))
        random.shuffle(val_indices)
        sampled_val_indices = val_indices[:1500]
        
        print(f"从训练集({len(train_ds)}条)中采样: {len(sampled_train_indices)}条")
        print(f"从验证集({len(validation_ds)}条)中采样: {len(sampled_val_indices)}条")
        
        # 创建输出目录
        output_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/hotpotqa"
        os.makedirs(output_path, exist_ok=True)
        
        print("\n=== 步骤3: 处理和保存数据 ===")
        
        # 处理训练集
        train_output_file = os.path.join(output_path, "train.jsonl")
        with open(train_output_file, 'w', encoding='utf-8') as outfile:
            processed_count = 0
            for idx_in_sample, original_idx in enumerate(sampled_train_indices):
                try:
                    item = train_ds[original_idx]
                    
                    # 转换为标准格式
                    processed_data = {
                        "question": item["question"],
                        "answer": item["answer"],
                        "index": idx_in_sample,
                        "original_index": original_idx,
                        "split": "train"
                    }
                    
                    # 如果有额外信息，也可以保存
                    if "supporting_facts" in item:
                        processed_data["supporting_facts"] = item["supporting_facts"]
                    if "context" in item:
                        processed_data["context"] = item["context"]
                    if "level" in item:
                        processed_data["level"] = item["level"]
                    if "type" in item:
                        processed_data["type"] = item["type"]
                    
                    outfile.write(json.dumps(processed_data, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                except Exception as e:
                    print(f"训练集第 {idx_in_sample} 条处理错误: {e}")
                    continue
            
            print(f"成功处理 {processed_count} 条训练数据，保存到: {train_output_file}")
        
        # 处理验证集
        val_output_file = os.path.join(output_path, "validation.jsonl")
        with open(val_output_file, 'w', encoding='utf-8') as outfile:
            processed_count = 0
            for idx_in_sample, original_idx in enumerate(sampled_val_indices):
                try:
                    item = validation_ds[original_idx]
                    
                    # 转换为标准格式
                    processed_data = {
                        "question": item["question"],
                        "answer": item["answer"],
                        "index": idx_in_sample,
                        "original_index": original_idx,
                        "split": "validation"
                    }
                    
                    # 如果有额外信息，也可以保存
                    if "supporting_facts" in item:
                        processed_data["supporting_facts"] = item["supporting_facts"]
                    if "context" in item:
                        processed_data["context"] = item["context"]
                    if "level" in item:
                        processed_data["level"] = item["level"]
                    if "type" in item:
                        processed_data["type"] = item["type"]
                    
                    outfile.write(json.dumps(processed_data, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                except Exception as e:
                    print(f"验证集第 {idx_in_sample} 条处理错误: {e}")
                    continue
            
            print(f"成功处理 {processed_count} 条验证数据，保存到: {val_output_file}")
        
        return True
        
    except Exception as e:
        print(f"处理数据集时出错: {e}")
        return False

def verify_processed_hotpotqa():
    """验证处理后的HotpotQA数据格式"""
    processed_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/hotpotqa"
    
    files_to_check = [
        os.path.join(processed_path, "train.jsonl"),
        os.path.join(processed_path, "validation.jsonl")
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n=== 验证文件: {file_path} ===")
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 3:  # 只显示前3条
                        break
                    try:
                        data = json.loads(line.strip())
                        print(f"记录 {i+1}:")
                        print(f"  问题: {data['question'][:100]}...")
                        print(f"  答案: {data['answer'][:50]}...")
                        print(f"  索引: {data['index']}")
                        print(f"  原始索引: {data['original_index']}")
                        print(f"  数据集: {data['split']}")
                        if 'type' in data:
                            print(f"  类型: {data['type']}")
                        print()
                    except Exception as e:
                        print(f"记录 {i+1}: 解析失败 - {e}")
            
            # 统计总行数
            with open(file_path, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for _ in f)
            print(f"总计: {total_lines} 条记录")
        else:
            print(f"文件不存在: {file_path}")

if __name__ == "__main__":
    print("=== HotpotQA数据处理脚本 ===")
    
    success = sample_and_process_hotpotqa()
    
    if success:
        print("\n=== 验证处理结果 ===")
        verify_processed_hotpotqa()
        
        print("\n=== 处理完成 ===")
        print("处理后的数据位置:")
        print("- 训练集样本(8000条): /home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/hotpotqa/train.jsonl")
        print("- 验证集样本(1500条): /home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/hotpotqa/validation.jsonl")
    else:
        print("\n数据处理失败")