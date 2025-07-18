from datasets import load_dataset
import os

# HumanEval数据集只有test split
try:
    ds = load_dataset("openai_humaneval", split="test", cache_dir="/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/human_eval")
    print(f"HumanEval test 已缓存，共 {len(ds)} 条")
    
    # 查看数据格式
    if len(ds) > 0:
        sample = ds[0]
        print(f"样本字段: {list(sample.keys())}")
        print(f"任务ID: {sample['task_id']}")
        print(f"提示: {sample['prompt'][:100]}...")
        print(f"测试: {sample['test'][:100]}...")
        print()
        
except Exception as e:
    print(f"加载HumanEval数据集时出错: {e}")
    print("可能需要先安装: pip install datasets")