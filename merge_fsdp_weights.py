#!/usr/bin/env python3
"""
合并FSDP checkpoint为HuggingFace格式
支持SHARDED_STATE_DICT模式的分片合并
"""
# python /nas/ganluo/Flow_RL/merge_fsdp_weights.py --fsdp-checkpoint-path /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor --hf-model-path /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor_merged

import torch
import json
from pathlib import Path
import shutil
from collections import defaultdict
from tqdm import tqdm

def merge_fsdp_checkpoint(fsdp_path, output_path):
    """合并FSDP分片权重"""

    fsdp_path = Path(fsdp_path)
    output_path = Path(output_path)

    print(f"从 {fsdp_path} 合并权重...")
    print(f"输出到 {output_path}")
    print("="*60)

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    # 复制HuggingFace配置文件
    hf_dir = fsdp_path / "huggingface"
    if hf_dir.exists():
        print("复制HuggingFace配置文件...")
        for file in hf_dir.glob("*"):
            shutil.copy2(file, output_path / file.name)

    # 检查FSDP配置
    fsdp_config_file = fsdp_path / "fsdp_config.json"
    world_size = 8  # 默认值
    if fsdp_config_file.exists():
        with open(fsdp_config_file, 'r') as f:
            fsdp_config = json.load(f)
            world_size = fsdp_config.get('world_size', 8)
            print(f"FSDP world_size: {world_size}")

    # 收集所有rank文件
    rank_files = sorted(fsdp_path.glob("model_world_size_*_rank_*.pt"))
    print(f"找到 {len(rank_files)} 个分片文件")

    if len(rank_files) != world_size:
        print(f"警告: 期望 {world_size} 个分片，但找到 {len(rank_files)} 个")

    # 第一步：收集所有参数的分片
    print("\n第一步：收集参数分片...")
    param_shards = defaultdict(list)  # {param_name: [(rank, tensor), ...]}

    for rank_file in tqdm(rank_files, desc="加载分片"):
        # 从文件名提取rank号
        rank_str = rank_file.stem.split('_rank_')[1]
        rank = int(rank_str)

        # 加载分片
        state_dict = torch.load(rank_file, map_location="cpu", weights_only=False)

        # 收集每个参数的分片
        for key, value in state_dict.items():
            # 移除可能的FSDP前缀
            clean_key = key.replace("_fsdp_wrapped_module.", "")
            clean_key = clean_key.replace("_checkpoint_wrapped_module.", "")

            # 将分片添加到对应参数的列表中
            param_shards[clean_key].append((rank, value))

    # 第二步：合并分片
    print(f"\n第二步：合并 {len(param_shards)} 个参数的分片...")
    merged_state_dict = {}

    for param_name, shards in tqdm(param_shards.items(), desc="合并参数"):
        # 按rank排序分片
        shards.sort(key=lambda x: x[0])

        # 检查是否有所有rank的分片
        ranks = [rank for rank, _ in shards]
        if len(ranks) != world_size:
            print(f"  警告: {param_name} 只有 {len(ranks)} 个分片 (ranks: {ranks})")

        # 获取所有分片张量
        tensors = [tensor for _, tensor in shards]

        # 合并策略
        if len(tensors) == 1:
            # 只有一个分片，直接使用
            merged_tensor = tensors[0]
        elif len(tensors) == world_size:
            # 有完整的分片集合
            try:
                # 检查张量形状
                shapes = [t.shape for t in tensors]
                dtypes = [t.dtype for t in tensors]

                # 确保所有分片有相同的dtype
                if len(set(dtypes)) > 1:
                    print(f"  警告: {param_name} 的分片有不同的dtype: {set(dtypes)}")

                # 检查是否所有形状都相同（复制参数）
                if len(set(shapes)) == 1:
                    # 所有分片形状相同，这是复制参数（如LayerNorm weights）
                    # 直接使用第一个分片，避免process group错误
                    merged_tensor = tensors[0]
                    if 'norm' in param_name or 'layernorm' in param_name.lower():
                        # 这是预期的行为，LayerNorm通常不分片
                        pass
                    else:
                        # 其他参数如果形状相同可能需要注意
                        if tensors[0].numel() < 10000:  # 小参数通常是bias或norm
                            pass  # 预期的
                        else:
                            print(f"  注意: {param_name} 所有分片形状相同 {shapes[0]}，使用第一个分片")
                else:
                    # 形状不同，需要拼接（真正的分片参数）
                    # 判断拼接维度
                    if all(len(shape) > 0 for shape in shapes):
                        # 检查哪个维度不同
                        concat_dim = None
                        for dim in range(len(shapes[0])):
                            dim_sizes = [shape[dim] if dim < len(shape) else 1 for shape in shapes]
                            if len(set(dim_sizes)) > 1:
                                concat_dim = dim
                                break

                        if concat_dim is not None:
                            # 清理张量以避免process group错误
                            # 创建新的张量副本，去除分布式元数据
                            clean_tensors = []
                            for t in tensors:
                                # 使用.data访问底层数据，或clone()创建新张量
                                if hasattr(t, 'data'):
                                    clean_t = t.data.clone()
                                else:
                                    clean_t = t.clone()
                                clean_tensors.append(clean_t)

                            # 拼接清理后的张量
                            merged_tensor = torch.cat(clean_tensors, dim=concat_dim)

                            # 验证拼接后的形状
                            expected_size = sum(shape[concat_dim] for shape in shapes)
                            actual_size = merged_tensor.shape[concat_dim]
                            if actual_size != expected_size:
                                print(f"  形状验证失败: {param_name}")
                                print(f"    期望维度{concat_dim}大小: {expected_size}")
                                print(f"    实际维度{concat_dim}大小: {actual_size}")
                        else:
                            # 没有找到不同的维度，使用第一个
                            merged_tensor = tensors[0]
                    else:
                        # 0维张量（标量）或其他特殊情况
                        merged_tensor = tensors[0]  # 使用第一个

            except Exception as e:
                print(f"  合并失败: {param_name}")
                print(f"    错误: {e}")
                try:
                    print(f"    分片形状: {shapes}")
                except:
                    print(f"    分片数量: {len(tensors)}")
                # 失败时使用第一个分片的克隆版本
                try:
                    merged_tensor = tensors[0].clone()
                except:
                    merged_tensor = tensors[0]
        else:
            # 分片数量不匹配，使用第一个
            print(f"  跳过不完整分片: {param_name} (只有 {len(tensors)} 个分片)")
            merged_tensor = tensors[0]

        # 确保张量在CPU上并且是连续的
        if hasattr(merged_tensor, 'device') and merged_tensor.device.type != 'cpu':
            merged_tensor = merged_tensor.cpu()
        if hasattr(merged_tensor, 'is_contiguous') and not merged_tensor.is_contiguous():
            merged_tensor = merged_tensor.contiguous()

        merged_state_dict[param_name] = merged_tensor

    print(f"\n合并完成，共 {len(merged_state_dict)} 个参数")

    # 计算参数总量
    total_params = 0
    for _, tensor in merged_state_dict.items():
        if hasattr(tensor, 'numel'):
            total_params += tensor.numel()

    print(f"总参数量: {total_params:,} ({total_params/1e9:.2f}B)")
    print(f"预期模型大小 (BF16): {total_params * 2 / 1024**3:.2f} GB")

    # 保存PyTorch格式
    pytorch_file = output_path / "pytorch_model.bin"
    print(f"\n保存PyTorch格式到 {pytorch_file}...")
    torch.save(merged_state_dict, pytorch_file)
    file_size_gb = pytorch_file.stat().st_size / 1024**3
    print(f"PyTorch文件大小: {file_size_gb:.2f} GB")

    # 验证文件大小
    if file_size_gb < 10:  # 8B模型应该至少10GB+
        print(f"\n⚠️ 警告: 文件大小 ({file_size_gb:.2f}GB) 看起来太小了!")
        print(f"   8B模型预期大小: ~16GB (BF16) 或 ~32GB (FP32)")
        print(f"   请检查是否所有分片都已正确合并")

    # 尝试保存SafeTensors格式
    try:
        from safetensors.torch import save_file
        safetensors_file = output_path / "model.safetensors"
        print(f"\n保存SafeTensors格式到 {safetensors_file}...")

        # 确保所有张量都是有效的
        final_dict = {}
        for k, v in merged_state_dict.items():
            if torch.is_tensor(v):
                # 创建新的张量副本以确保有有效的存储
                final_dict[k] = v.detach().clone().cpu().contiguous()
            else:
                final_dict[k] = v

        save_file(final_dict, safetensors_file)
        print(f"SafeTensors文件大小: {safetensors_file.stat().st_size / 1024**3:.2f} GB")
    except ImportError:
        print("\n警告: safetensors未安装，跳过safetensors格式保存")
        print("可以通过 'pip install safetensors' 安装")
    except Exception as e:
        print(f"\n保存safetensors时出错: {e}")
        print("但PyTorch格式已成功保存，可以正常使用")

    print("\n✅ 完成！")

    # 打印摘要
    print("\n" + "="*60)
    print("合并摘要:")
    print(f"  输入路径: {fsdp_path}")
    print(f"  输出路径: {output_path}")
    print(f"  参数数量: {len(merged_state_dict)}")
    print(f"  总参数量: {total_params:,} ({total_params/1e9:.2f}B)")
    print(f"  文件大小: {file_size_gb:.2f} GB")
    print("="*60)

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