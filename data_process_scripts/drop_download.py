from datasets import load_dataset
import os

# 你可以选 "distractor" 或 "fullwiki" 子集；这里以 "distractor" 为例
for split in ["train", "validation"]:
    ds = load_dataset("drop", split=split, cache_dir="/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/drop")
    print(f"{split} 已缓存，共 {len(ds)} 条")