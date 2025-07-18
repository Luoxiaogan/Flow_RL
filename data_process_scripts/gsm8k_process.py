import json
import os
from pathlib import Path

def examine_original_data():
    """检查原始数据的格式"""
    try:
        from datasets import load_dataset
        
        # 使用和下载时相同的方式加载数据
        dataset_name = "openai/gsm8k"
        local_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Datasets/gsm8k"
        
        print("使用datasets库加载GSM8K数据...")
        dataset = load_dataset(dataset_name, 'main', cache_dir=local_path)
        
        print(f"数据集信息: {dataset}")
        
        # 检查训练集
        if 'train' in dataset:
            train_data = dataset['train']
            print(f"\n训练集大小: {len(train_data)}")
            print(f"训练集特征: {train_data.features}")
            print("训练集前3个样本:")
            for i in range(min(3, len(train_data))):
                sample = train_data[i]
                print(f"  样本 {i+1}:")
                print(f"    问题: {sample['question'][:100]}...")
                print(f"    答案: {sample['answer'][:100]}...")
                print()
        
        # 检查测试集
        if 'test' in dataset:
            test_data = dataset['test']
            print(f"测试集大小: {len(test_data)}")
            print(f"测试集特征: {test_data.features}")
            print("测试集前3个样本:")
            for i in range(min(3, len(test_data))):
                sample = test_data[i]
                print(f"  样本 {i+1}:")
                print(f"    问题: {sample['question'][:100]}...")
                print(f"    答案: {sample['answer'][:100]}...")
                print()
        
        return dataset
        
    except ImportError:
        print("错误: 需要安装 datasets 库")
        print("请运行: pip install datasets")
        return None
    except Exception as e:
        print(f"加载数据集时出错: {e}")
        return None

def process_gsm8k_to_jsonl():
    """将GSM8K数据转换为ScoreFlow需要的JSONL格式"""
    try:
        from datasets import load_dataset
        
        # 使用和下载时相同的方式加载数据
        dataset_name = "openai/gsm8k"
        local_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Datasets/gsm8k"
        
        print("加载GSM8K数据集...")
        dataset = load_dataset(dataset_name, 'main', cache_dir=local_path)
        
        output_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k"
        os.makedirs(output_path, exist_ok=True)
        
        # 处理训练集和测试集
        for split_name in ['train', 'test']:
            if split_name not in dataset:
                print(f"警告: 数据集中没有 {split_name} 分割")
                continue
                
            split_data = dataset[split_name]
            output_file = os.path.join(output_path, f"{split_name}.jsonl")
            
            print(f"处理 {split_name} 数据集 ({len(split_data)} 条记录)...")
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                processed_count = 0
                
                for index, item in enumerate(split_data):
                    try:
                        # 转换为ScoreFlow期望的格式
                        processed_data = {
                            "question": item["question"],
                            "answer": item["answer"],
                            "index": index  # 添加索引方便追踪
                        }
                        
                        # 写入处理后的数据
                        outfile.write(json.dumps(processed_data, ensure_ascii=False) + '\n')
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"第 {index} 行处理错误: {e}")
                        continue
                
                print(f"成功处理 {processed_count} 条 {split_name} 数据，保存到: {output_file}")
        
        # 创建ScoreFlow期望的数据集路径
        scoreflow_dataset_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/ScoreFlow/benchmark/datasets"
        os.makedirs(scoreflow_dataset_path, exist_ok=True)
        
        # 复制测试集到ScoreFlow期望的位置
        test_source = os.path.join(output_path, "test.jsonl")
        test_target = os.path.join(scoreflow_dataset_path, "gsm8k.jsonl")
        
        if os.path.exists(test_source):
            import shutil
            shutil.copy2(test_source, test_target)
            print(f"已复制测试集到ScoreFlow路径: {test_target}")
        
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
    processed_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k"
    scoreflow_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/ScoreFlow/benchmark/datasets/gsm8k.jsonl"
    
    files_to_check = [
        os.path.join(processed_path, "test.jsonl"),
        os.path.join(processed_path, "train.jsonl"),
        scoreflow_path
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
    print("=== 步骤1: 检查原始数据 ===")
    dataset = examine_original_data()
    
    if dataset is not None:
        print("\n=== 步骤2: 处理数据到JSONL格式 ===")
        success = process_gsm8k_to_jsonl()
        
        if success:
            print("\n=== 步骤3: 验证处理结果 ===")
            verify_processed_data()
            
            print("\n=== 处理完成 ===")
            print("处理后的数据位置:")
            print("- 训练集: /Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k/train.jsonl")
            print("- 测试集: /Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k/test.jsonl")
            print("- ScoreFlow使用: /Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/ScoreFlow/benchmark/datasets/gsm8k.jsonl")
        else:
            print("\n数据处理失败")
    else:
        print("\n无法加载原始数据")