#!/usr/bin/env python3
"""
计算parquet数据集中prompt的最大token长度
"""

import pandas as pd
from transformers import AutoTokenizer
from tqdm import tqdm
import json
import sys


def format_prompt(messages):
    """
    将消息列表格式化为单个字符串
    messages: [{"role": "system", "content": "xxx"}, {"role": "user", "content": "xxx"}]
    """
    formatted = ""
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        formatted += f"{role}: {content}\n"
    return formatted


def main():
    # 硬编码路径
    tokenizer_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/qwen3_8b_short"
    jsonl_or_parquet_path = "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all/test_cleared.jsonl"
    
    filter_length = 3330
    _filter = True
    
    print(f"Tokenizer路径: {tokenizer_path}")
    print(f"路径: {jsonl_or_parquet_path}")
    print("-" * 50)
    
    # 加载tokenizer
    print("加载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_path,
        trust_remote_code=True
    )
    
    # 读取parquet
    print("读取文件...") 
    parquet_path = jsonl_or_parquet_path
    if jsonl_or_parquet_path.endswith(".jsonl"):
        # 如果是jsonl，先转换为parquet
        df = pd.read_json(jsonl_or_parquet_path, lines=True)
        parquet_path = jsonl_or_parquet_path.replace(".jsonl", ".parquet")
        df.to_parquet(parquet_path, index=False)
        print(f"已将JSONL转换为Parquet: {parquet_path}")      
    df = pd.read_parquet(parquet_path)
    print(f"数据集大小: {len(df)} 条")
    
    max_length = 0
    max_sample_idx = -1
    token_lengths = []
    
    # 计算每个样本的token长度
    print("计算token长度...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        prompt_data = row['prompt']
        
        # 如果是字符串，尝试解析JSON
        if isinstance(prompt_data, str):
            try:
                prompt_data = json.loads(prompt_data)
            except:
                pass
        
        # 格式化prompt
        if isinstance(prompt_data, list):
            prompt_text = format_prompt(prompt_data)
        else:
            prompt_text = str(prompt_data)
        
        # tokenize并计算长度
        tokens = tokenizer.encode(prompt_text, add_special_tokens=True)
        token_length = len(tokens)
        token_lengths.append(token_length)
        
        if token_length > max_length:
            max_length = token_length
            max_sample_idx = idx
    
    # 计算统计信息
    token_lengths_sorted = sorted(token_lengths)
    avg_length = sum(token_lengths) / len(token_lengths)
    median_length = token_lengths_sorted[len(token_lengths_sorted) // 2]
    p95_length = token_lengths_sorted[int(len(token_lengths_sorted) * 0.95)]
    p99_length = token_lengths_sorted[int(len(token_lengths_sorted) * 0.99)]
    
    # 输出结果
    print("\n" + "="*50)
    print("📊 Token长度统计:")
    print(f"  最大长度: {max_length} (样本索引: {max_sample_idx})")
    print(f"  平均长度: {avg_length:.1f}")
    print(f"  中位数: {median_length}")
    print(f"  95分位数: {p95_length}")
    print(f"  99分位数: {p99_length}")
    print(f"  最小长度: {min(token_lengths)}")
    print("="*50)
    
    # 建议设置
    suggested_max = int(max_length * 1.1)
    print(f"\n💡 建议设置:")
    print(f"  max_prompt_length = {suggested_max}")
    print(f"  (基于最大值 {max_length} + 10% 余量)")
    
    # 长度分布
    print("\n📈 长度分布:")
    buckets = [1000, 2000, 3000,3100,3200,3300,3400,3500,3600,3700,3800,3900, 4000, 5000, 6000, 8000, 10000]
    for bucket in buckets:
        count = sum(1 for l in token_lengths if l <= bucket)
        percentage = count / len(token_lengths) * 100
        bar = "█" * int(percentage / 2)  # 简单的进度条
        print(f"  <= {bucket:5d}: {count:6d} ({percentage:5.1f}%) {bar}")

    if _filter:
        # 过滤样本
        print("\n" + "="*50)
        print(f"🔍 开始过滤：仅保留 prompt token 长度 ≤ {filter_length} 的样本")
        
        # 构造一个布尔 mask
        keep_mask = [l <= filter_length for l in token_lengths]
        filtered_df = df[keep_mask].copy().reset_index(drop=True)
        
        # 写出
        out_path = parquet_path.replace(".parquet", f"_le{filter_length}.parquet")
        filtered_df.to_parquet(out_path, index=False)
        
        print(f"  过滤前样本数: {len(df)}")
        print(f"  过滤后样本数: {len(filtered_df)}")
        print(f"  已写出文件: {out_path}")
        print("="*50)


if __name__ == "__main__":
    main()