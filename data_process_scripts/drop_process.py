import json
import os
from pathlib import Path
from datasets import load_dataset

def examine_drop_data():
    """检查DROP数据的格式"""
    try:
        print("加载DROP数据集...")
        cache_dir = "/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/drop"
        
        # 加载两个分割
        train_ds = load_dataset("drop", split="train", cache_dir=cache_dir)
        validation_ds = load_dataset("drop", split="validation", cache_dir=cache_dir)
        
        print(f"训练集大小: {len(train_ds)}")
        print(f"验证集大小: {len(validation_ds)}")
        print(f"训练集特征: {train_ds.features}")
        
        # 检查样本格式
        print("\n训练集前3个样本:")
        for i in range(min(3, len(train_ds))):
            sample = train_ds[i]
            print(f"  样本 {i+1}:")
            print(f"    问题: {sample['question'][:100]}...")
            print(f"    段落: {sample['passage'][:100]}...")
            if 'answers_spans' in sample:
                spans = sample['answers_spans']['spans']
                print(f"    答案: {spans[:3] if spans else 'N/A'}")
            if 'query_id' in sample:
                print(f"    查询ID: {sample['query_id']}")
            print()
        
        return train_ds, validation_ds
        
    except Exception as e:
        print(f"加载数据集时出错: {e}")
        return None, None

def process_drop_to_jsonl():
    """将DROP数据转换为JSONL格式"""
    try:
        print("=== 步骤1: 加载原始数据 ===")
        train_ds, validation_ds = examine_drop_data()
        
        if train_ds is None or validation_ds is None:
            print("无法加载数据集")
            return False
        
        # 创建输出目录
        output_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/drop"
        os.makedirs(output_path, exist_ok=True)
        
        print("\n=== 步骤2: 处理和保存数据 ===")
        
        # 处理两个分割
        datasets = [
            ("train", train_ds),
            ("validation", validation_ds)
        ]
        
        for split_name, dataset in datasets:
            output_file = os.path.join(output_path, f"{split_name}.jsonl")
            
            print(f"处理 {split_name} 数据集 ({len(dataset)} 条记录)...")
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                processed_count = 0
                
                for index, item in enumerate(dataset):
                    try:
                        # 转换为标准格式
                        processed_data = {
                            "question": item["question"],
                            "passage": item["passage"],
                            "index": index,
                            "split": split_name
                        }
                        
                        # 处理答案格式
                        if "answers_spans" in item and item["answers_spans"]["spans"]:
                            processed_data["answer"] = item["answers_spans"]["spans"][0]  # 取第一个答案
                            processed_data["all_answers"] = item["answers_spans"]["spans"]
                        else:
                            processed_data["answer"] = ""
                            processed_data["all_answers"] = []
                        
                        # 保存其他字段
                        if "query_id" in item:
                            processed_data["query_id"] = item["query_id"]
                        if "passage_id" in item:
                            processed_data["passage_id"] = item["passage_id"]
                        if "wiki_page_id" in item:
                            processed_data["wiki_page_id"] = item["wiki_page_id"]
                        if "date" in item:
                            processed_data["date"] = item["date"]
                        if "number" in item:
                            processed_data["number"] = item["number"]
                        if "number_with_subtype" in item:
                            processed_data["number_with_subtype"] = item["number_with_subtype"]
                        
                        # 写入处理后的数据
                        outfile.write(json.dumps(processed_data, ensure_ascii=False) + '\n')
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"{split_name} 第 {index} 行处理错误: {e}")
                        continue
                
                print(f"成功处理 {processed_count} 条 {split_name} 数据，保存到: {output_file}")
        
        return True
        
    except ImportError:
        print("错误: 需要安装 datasets 库")
        print("请运行: pip install datasets")
        return False
    except Exception as e:
        print(f"处理数据集时出错: {e}")
        return False

def verify_processed_data():
    """验证处理后的数据格式"""
    processed_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/drop"
    
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
                        print(f"  问题: {data['question'][:50]}...")
                        print(f"  段落: {data['passage'][:50]}...")
                        print(f"  答案: {data['answer'][:30]}...")
                        print(f"  索引: {data['index']}")
                        print(f"  数据集: {data['split']}")
                        if 'query_id' in data:
                            print(f"  查询ID: {data['query_id']}")
                        if 'all_answers' in data and data['all_answers']:
                            print(f"  所有答案数: {len(data['all_answers'])}")
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
    print("=== DROP数据处理脚本 ===")
    
    success = process_drop_to_jsonl()
    
    if success:
        print("\n=== 步骤3: 验证处理结果 ===")
        verify_processed_data()
        
        print("\n=== 处理完成 ===")
        print("处理后的数据位置:")
        print("- 训练集: /home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/drop/train.jsonl")
        print("- 验证集: /home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/drop/validation.jsonl")
    else:
        print("\n数据处理失败")
