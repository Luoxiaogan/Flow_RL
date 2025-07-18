# 1. 在 shell 里先设置缓存目录（一次性即可）
# export HF_DATASETS_CACHE=/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/hotpotqa

# 2. 在 Python 里一次性把三个 split 都拉下来
from datasets import load_dataset
import os

# 你可以选 "distractor" 或 "fullwiki" 子集；这里以 "distractor" 为例
for split in ["train", "validation"]:
    ds = load_dataset("hotpot_qa", "distractor", split=split, cache_dir="/home/lg/workflow_tooluse/Flow_RL_luogan/Datasets/hotpotqa")
    print(f"{split} 已缓存，共 {len(ds)} 条")