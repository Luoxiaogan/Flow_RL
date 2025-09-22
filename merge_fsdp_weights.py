#!/usr/bin/env python3
"""
合并FSDP checkpoint为HuggingFace格式
"""

import torch
import os
import json
from pathlib import Path
import shutil

def merge_fsdp_checkpoint(fsdp_path, output_path):
    """合并FSDP分片权重"""

    fsdp_path = Path(fsdp_path)
    output_path = Path(output_path)

    print(f"从 {fsdp_path} 合并权重...")
    print(f"输出到 {output_path}")

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    # 复制HuggingFace配置文件
    hf_dir = fsdp_path / "huggingface"
    if hf_dir.exists():
        print("复制HuggingFace配置文件...")
        for file in hf_dir.glob("*"):
            shutil.copy2(file, output_path / file.name)

    # 合并模型权重
    print("合并模型权重分片...")
    merged_state_dict = {}

    # 查找所有rank文件
    rank_files = sorted(fsdp_path.glob("model_world_size_*_rank_*.pt"))
    print(f"找到 {len(rank_files)} 个分片文件")

    for rank_file in rank_files:
        print(f"  加载 {rank_file.name}...")
        state_dict = torch.load(rank_file, map_location="cpu")

        # FSDP可能会添加前缀，需要处理
        for key, value in state_dict.items():
            # 移除可能的FSDP前缀
            clean_key = key.replace("_fsdp_wrapped_module.", "")
            clean_key = clean_key.replace("_checkpoint_wrapped_module.", "")

            if clean_key in merged_state_dict:
                # 如果键已存在，可能需要合并张量
                print(f"    警告: 键 {clean_key} 已存在，跳过")
            else:
                merged_state_dict[clean_key] = value

    print(f"合并完成，共 {len(merged_state_dict)} 个参数")

    # 保存合并的权重
    output_file = output_path / "pytorch_model.bin"
    print(f"保存到 {output_file}...")
    torch.save(merged_state_dict, output_file)

    print(f"权重文件大小: {output_file.stat().st_size / 1024**3:.2f} GB")
    print("完成！")

    return str(output_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="合并FSDP checkpoint")
    parser.add_argument("--fsdp-checkpoint-path", type=str, required=True,
                        help="FSDP checkpoint路径")
    parser.add_argument("--hf-model-path", type=str, required=True,
                        help="输出的HuggingFace模型路径")

    args = parser.parse_args()

    merge_fsdp_checkpoint(args.fsdp_checkpoint_path, args.hf_model_path)