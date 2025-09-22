#!/usr/bin/env python3
"""
合并FSDP checkpoint为HuggingFace格式
"""
# python /nas/ganluo/Flow_RL/merge_fsdp_weights.py --fsdp-checkpoint-path /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor --hf-model-path /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor_merged

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
        state_dict = torch.load(rank_file, map_location="cpu", weights_only=False)

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

    # 处理张量，确保它们可以被safetensors保存
    print("处理张量以确保兼容性...")
    processed_state_dict = {}

    for key, tensor in merged_state_dict.items():
        try:
            # 确保张量在CPU上
            if hasattr(tensor, 'device') and tensor.device.type != 'cpu':
                tensor = tensor.cpu()

            # 检查是否是meta张量或无效张量
            if hasattr(tensor, 'device') and tensor.device.type == 'meta':
                print(f"    跳过meta张量: {key}")
                continue

            # 尝试访问数据以确保张量有效
            try:
                # 创建新张量以确保有有效的存储
                if hasattr(tensor, 'data'):
                    # 使用detach和clone确保创建新的存储
                    new_tensor = tensor.detach().clone()
                    # 确保张量是连续的
                    if not new_tensor.is_contiguous():
                        new_tensor = new_tensor.contiguous()
                    processed_state_dict[key] = new_tensor
                else:
                    processed_state_dict[key] = tensor
            except RuntimeError as e:
                print(f"    警告: 无法处理张量 {key}: {e}")
                # 尝试通过numpy转换重建张量
                try:
                    numpy_array = tensor.numpy()
                    processed_state_dict[key] = torch.from_numpy(numpy_array.copy())
                except:
                    print(f"    错误: 完全跳过张量 {key}")
                    continue

        except Exception as e:
            print(f"    处理张量 {key} 时出错: {e}")
            continue

    print(f"处理完成，共 {len(processed_state_dict)} 个有效参数")

    # 同时保存pytorch格式和safetensors格式

    # 保存pytorch格式
    pytorch_file = output_path / "pytorch_model.bin"
    print(f"保存PyTorch格式到 {pytorch_file}...")
    torch.save(processed_state_dict, pytorch_file)
    print(f"PyTorch文件大小: {pytorch_file.stat().st_size / 1024**3:.2f} GB")

    # 保存safetensors格式
    try:
        from safetensors.torch import save_file
        safetensors_file = output_path / "model.safetensors"
        print(f"保存SafeTensors格式到 {safetensors_file}...")

        # 再次确保所有张量都是有效的
        final_dict = {}
        for k, v in processed_state_dict.items():
            if torch.is_tensor(v):
                # 确保张量在CPU上并且是连续的
                final_dict[k] = v.cpu().contiguous()
            else:
                final_dict[k] = v

        save_file(final_dict, safetensors_file)
        print(f"SafeTensors文件大小: {safetensors_file.stat().st_size / 1024**3:.2f} GB")
    except ImportError:
        print("警告: safetensors未安装，跳过safetensors格式保存")
        print("可以通过 'pip install safetensors' 安装")
    except Exception as e:
        print(f"保存safetensors时出错: {e}")
        print("但PyTorch格式已成功保存，可以正常使用")

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