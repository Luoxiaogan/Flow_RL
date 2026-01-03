import json
import os
from pathlib import Path

def examine_original_data():
    """检查原始数据的格式"""
    try:
        from datasets import load_dataset
        
        # 使用和下载时相同的方式加载数据
        dataset_name = "openai_humaneval"
        local_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/human_eval"

        print("使用datasets库加载HumanEval数据...")
        dataset = load_dataset(dataset_name, split="test", cache_dir=local_path)
        
        print(f"数据集信息: {dataset}")
        print(f"测试集大小: {len(dataset)}")
        print(f"测试集特征: {dataset.features}")
        
        # 检查测试集前3个样本
        print("测试集前3个样本:")
        for i in range(min(3, len(dataset))):
            sample = dataset[i]
            print(f"  样本 {i+1}:")
            print(f"    任务ID: {sample['task_id']}")
            print(f"    提示: {sample['prompt'][:100]}...")
            print(f"    入口点: {sample['entry_point']}")
            print(f"    标准解: {sample['canonical_solution'][:100]}...")
            print()
        
        return dataset
        
    except ImportError:
        print("错误: 需要安装 datasets 库")
        print("请运行: pip install datasets")
        return None
    except Exception as e:
        print(f"加载数据集时出错: {e}")
        return None

def process_human_eval_to_jsonl():
    """将HumanEval数据转换为JSONL格式"""
    try:
        from datasets import load_dataset
        
        # 使用和下载时相同的方式加载数据
        dataset_name = "openai_humaneval"
        local_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/human_eval"
        
        print("加载HumanEval数据集...")
        dataset = load_dataset(dataset_name, split="test", cache_dir=local_path)
        
        output_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/human_eval"
        os.makedirs(output_path, exist_ok=True)
        
        # 处理测试集
        output_file = os.path.join(output_path, "test.jsonl")
        
        print(f"处理测试数据集 ({len(dataset)} 条记录)...")
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            processed_count = 0
            
            for index, item in enumerate(dataset):
                try:
                    # 转换为标准格式
                    processed_data = {
                        "task_id": item["task_id"],
                        "prompt": item["prompt"],
                        "entry_point": item["entry_point"],
                        "canonical_solution": item["canonical_solution"],
                        "test": item["test"],
                        "index": index,  # 添加索引方便追踪
                        "split": "test"
                    }
                    
                    # 为了保持与其他数据集的一致性
                    processed_data["question"] = item["prompt"]
                    processed_data["answer"] = item["canonical_solution"]
                    
                    # 写入处理后的数据
                    outfile.write(json.dumps(processed_data, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                except Exception as e:
                    print(f"第 {index} 行处理错误: {e}")
                    continue
            
            print(f"成功处理 {processed_count} 条测试数据，保存到: {output_file}")
        
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
    processed_path = "/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/human_eval"
    
    files_to_check = [
        os.path.join(processed_path, "test.jsonl")
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
                        print(f"  任务ID: {data['task_id']}")
                        print(f"  提示: {data['prompt'][:50]}...")
                        print(f"  入口点: {data['entry_point']}")
                        print(f"  索引: {data['index']}")
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
    print("=== HumanEval数据处理脚本 ===")
    print("=== 步骤1: 检查原始数据 ===")
    dataset = examine_original_data()
    
    if dataset is not None:
        print("\n=== 步骤2: 处理数据到JSONL格式 ===")
        success = process_human_eval_to_jsonl()
        
        if success:
            print("\n=== 步骤3: 验证处理结果 ===")
            verify_processed_data()
            
            print("\n=== 处理完成 ===")
            print("处理后的数据位置:")
            print("- 测试集: /home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/human_eval/test.jsonl")
        else:
            print("\n数据处理失败")
    else:
        print("\n无法加载原始数据")