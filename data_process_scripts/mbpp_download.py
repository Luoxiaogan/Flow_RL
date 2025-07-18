from datasets import load_dataset
import os

# MBPP数据集有train, test, validation三个split
try:
    for split in ["train", "test", "validation"]:
        ds = load_dataset("mbpp", split=split, cache_dir="/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/mbpp")
        print(f"MBPP {split} 已缓存，共 {len(ds)} 条")
        
        # 查看数据格式
        if len(ds) > 0:
            sample = ds[0]
            print(f"{split} 样本字段: {list(sample.keys())}")
            print(f"任务ID: {sample['task_id']}")
            print(f"文本: {sample['text'][:100]}...")
            print(f"代码: {sample['code'][:100]}...")
            print()
        
except Exception as e:
    print(f"加载MBPP数据集时出错: {e}")
    print("可能需要先安装: pip install datasets")