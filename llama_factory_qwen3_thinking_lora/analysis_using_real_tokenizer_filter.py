#!/usr/bin/env python3
"""
Exact token counter + filter for LLM training data.
1. 按真实 tokenizer 统计每条样本的 token；
2. 超过阈值则丢弃；
3. 结果写回同目录：原文件名_le{阈值}.jsonl。
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from tqdm import tqdm
from transformers import AutoTokenizer


# ---------- token 计算 ----------
def count_exact_tokens(messages: List[Dict[str, str]], tokenizer) -> int:
    """返回该对话真正的 token 数（含特殊 token）"""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        return len(tokenizer.encode(text, add_special_tokens=True))
    except Exception:
        # fallback：逐条简单相加
        return sum(
            len(tokenizer.encode(msg.get("content", ""), add_special_tokens=False))
            for msg in messages
        )


# ---------- 主流程 ----------
def filter_dataset(
    jsonl_path: str,
    model_path: str,
    filter_length: int,
) -> None:
    in_file = Path(jsonl_path)
    out_file = in_file.with_suffix(f".le{filter_length}.jsonl")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path, trust_remote_code=True, use_fast=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    kept_lines = []
    total = 0
    with open(in_file, "r", encoding="utf-8") as fin:
        for line in tqdm(fin, desc="Filtering"):
            line = line.rstrip("\n")
            if not line:
                continue
            total += 1
            data = json.loads(line)
            tokens = count_exact_tokens(data.get("messages", []), tokenizer)
            if tokens <= filter_length:
                kept_lines.append(line + "\n")

    with open(out_file, "w", encoding="utf-8") as fout:
        fout.writelines(kept_lines)

    print(
        f"✅ 完成！保留 {len(kept_lines)}/{total} 条样本（≤{filter_length} tokens）\n"
        f"    保存路径：{out_file}"
    )


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jsonl",
        type=str,
        required=True,
        help="原始 jsonl 路径",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="tokenizer 本地或 Hugging Face 路径",
    )
    parser.add_argument(
        "--filter_length",
        type=int,
        default=8192,
        help="token 阈值，超过即丢弃（默认 8192）",
    )
    args = parser.parse_args()
    filter_dataset(args.jsonl, args.model, args.filter_length)


# ---------- 直接运行 ----------
if __name__ == "__main__":
    # 若直接运行脚本且不带参数，用默认路径
    if len(sys.argv) == 1:
        filter_dataset(
            jsonl_path="/nas/ganluo/Flow_RL/training_data_0909_qwen3_max_and_qwen_max_different_operator.jsonl",
            model_path="/nas/models/Qwen3-8B",
            filter_length=8192,
        )
    else:
        main()
        
# python /nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/analysis_using_real_tokenizer_filter.py \
#   --jsonl /nas/ganluo/Flow_RL/ONLY_QWEN3_0910.jsonl \
#   --model /nas/models/Qwen3-8B \
#   --filter_length 6200