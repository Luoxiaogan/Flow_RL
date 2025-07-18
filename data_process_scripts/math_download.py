from datasets import load_dataset
import os

# MATH数据集有train和test两个split
try:
    for split in ["train", "test"]:
        ds = load_dataset("aime2024", split=split, cache_dir="/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/math")
        print(f"MATH {split} 已缓存，共 {len(ds)} 条")
        
        # 查看数据格式
        if len(ds) > 0:
            sample = ds[0]
            print(f"{split} 样本字段: {list(sample.keys())}")
            print(f"问题: {sample['problem'][:100]}...")
            print(f"解答: {sample['solution'][:100]}...")
            print(f"类型: {sample['type']}")
            print(f"难度: {sample['level']}")
            print()
        
except Exception as e:
    print(f"加载MATH数据集时出错: {e}")
    print("可能需要先安装: pip install datasets")