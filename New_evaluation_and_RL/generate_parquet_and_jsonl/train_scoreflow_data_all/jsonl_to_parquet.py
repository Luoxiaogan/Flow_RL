import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ✅ 硬编码输入目录（修改为你自己的路径）
INPUT_DIR = "/nas/ganluo/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all"

def jsonl_to_parquet(jsonl_path):
    parquet_path = jsonl_path.replace(".jsonl", ".parquet")
    try:
        df = pd.read_json(jsonl_path, lines=True)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_path)
        print(f"✅ 转换完成：{jsonl_path} → {parquet_path}")
    except Exception as e:
        print(f"❌ 转换失败：{jsonl_path}，错误：{e}")

def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".jsonl"):
            jsonl_path = os.path.join(INPUT_DIR, filename)
            jsonl_to_parquet(jsonl_path)

if __name__ == "__main__":
    main()
