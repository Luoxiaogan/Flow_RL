#!/usr/bin/env python3
# parquet2jsonl.py
import pandas as pd
import json
import os
import numpy as np          # 新增

INPUT_PARQUET  = "/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/verl_support/data/gsm8k/test.parquet"
OUTPUT_JSONL   = "/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/verl_support/data/gsm8k/test.jsonl"

def np_encoder(obj):
    """NumPy 数组/数值 → 原生 Python"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not serializable")

def main():
    df = pd.read_parquet(INPUT_PARQUET)
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as fout:
        for record in df.to_dict(orient="records"):
            fout.write(json.dumps(record, ensure_ascii=False, default=np_encoder) + "\n")
    print(f"✅ 转换完毕：{INPUT_PARQUET} → {OUTPUT_JSONL} ({len(df)} 条)")

if __name__ == "__main__":
    main()
