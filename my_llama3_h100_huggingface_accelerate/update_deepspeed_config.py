#!/usr/bin/env python3
"""
自动更新DeepSpeed配置文件
根据run_training.sh中的参数和实际数据集大小动态生成deepspeed_zero2.json

使用方法：
    python update_deepspeed_config.py
    
该脚本会：
1. 读取run_training.sh中的训练参数
2. 统计数据集的实际样本数
3. 计算总训练步数和预热步数
4. 生成一致的DeepSpeed配置
"""

import json
import re
import os
import sys
from pathlib import Path
import yaml

# 配置文件路径
SCRIPT_DIR = Path(__file__).parent
RUN_SCRIPT = SCRIPT_DIR / "run_training.sh"
DEEPSPEED_CONFIG = SCRIPT_DIR / "configs" / "deepspeed_zero2.json"
DEEPSPEED_BACKUP = SCRIPT_DIR / "configs" / "deepspeed_zero2.json.backup"
ACCELERATE_CONFIG = SCRIPT_DIR / "configs" / "accelerate_config.yaml"


def parse_shell_script(script_path):
    """从shell脚本中提取训练参数"""
    params = {}
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # 定义要提取的参数模式
    patterns = {
        'DATASET_PATH': r'DATASET_PATH="([^"]+)"(?:\s*#[^\n]*)?$',
        'NUM_EPOCHS': r'NUM_EPOCHS=(\d+)',
        'PER_DEVICE_BATCH_SIZE': r'PER_DEVICE_BATCH_SIZE=(\d+)',
        'GRAD_ACCUM_STEPS': r'GRAD_ACCUM_STEPS=(\d+)',
        'LEARNING_RATE': r'LEARNING_RATE=([\d.e-]+)',
        'WARMUP_RATIO': r'WARMUP_RATIO=([\d.]+)',
        'MAX_GRAD_NORM': r'--max_grad_norm\s+([\d.]+)',
        'WEIGHT_DECAY': r'--weight_decay\s+([\d.]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1)
            # 转换数据类型
            if key in ['NUM_EPOCHS', 'PER_DEVICE_BATCH_SIZE', 'GRAD_ACCUM_STEPS']:
                params[key] = int(value)
            elif key in ['LEARNING_RATE', 'WARMUP_RATIO', 'MAX_GRAD_NORM', 'WEIGHT_DECAY']:
                params[key] = float(value)
            else:
                params[key] = value
    
    return params


def count_dataset_samples(dataset_path):
    """统计JSONL数据集的样本数"""
    if not os.path.exists(dataset_path):
        print(f"⚠️  警告: 数据集文件不存在: {dataset_path}")
        print("   使用默认值: 10000 samples")
        return 10000
    
    count = 0
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception as e:
        print(f"⚠️  警告: 读取数据集失败: {e}")
        print("   使用默认值: 10000 samples")
        return 10000
    
    return count


def verify_accelerate_config(config_path):
    """验证Accelerate配置中的GPU数量"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    num_processes = config.get('num_processes', 8)
    if num_processes != 8:
        print(f"⚠️  警告: accelerate_config.yaml中num_processes={num_processes}，预期为8")
        print("   请检查配置是否正确")
    
    return num_processes


def generate_deepspeed_config(params, dataset_size, num_gpus):
    """生成DeepSpeed配置"""
    
    # 计算批次大小相关参数
    micro_batch_per_gpu = params['PER_DEVICE_BATCH_SIZE']
    grad_accum = params['GRAD_ACCUM_STEPS']
    global_batch_size = num_gpus * micro_batch_per_gpu * grad_accum
    
    # 计算训练步数
    steps_per_epoch = dataset_size // global_batch_size
    if dataset_size % global_batch_size != 0:
        steps_per_epoch += 1  # 向上取整
    
    total_steps = steps_per_epoch * params['NUM_EPOCHS']
    warmup_steps = int(params['WARMUP_RATIO'] * total_steps)
    
    print("\n" + "="*60)
    print("📊 配置计算结果:")
    print("="*60)
    print(f"  数据集大小: {dataset_size} samples")
    print(f"  GPU数量: {num_gpus}")
    print(f"  每GPU微批次: {micro_batch_per_gpu}")
    print(f"  梯度累积步数: {grad_accum}")
    print(f"  全局批次大小: {global_batch_size}")
    print(f"  每轮步数: {steps_per_epoch}")
    print(f"  训练轮数: {params['NUM_EPOCHS']}")
    print(f"  总训练步数: {total_steps}")
    print(f"  预热步数: {warmup_steps}")
    print(f"  学习率: {params['LEARNING_RATE']}")
    print("="*60)
    
    # 验证批次大小公式
    expected_batch = num_gpus * micro_batch_per_gpu * grad_accum
    print(f"\n✅ 批次大小验证: {global_batch_size} = {num_gpus} × {micro_batch_per_gpu} × {grad_accum}")
    if global_batch_size != expected_batch:
        print(f"❌ 错误: 批次大小计算不一致！")
        sys.exit(1)
    
    # 构建DeepSpeed配置
    config = {
        "bf16": {"enabled": True},
        
        "optimizer": {
            "type": "AdamW",
            "params": {
                "lr": params['LEARNING_RATE'],
                "betas": [0.9, 0.999],
                "eps": 1e-8,
                "weight_decay": params.get('WEIGHT_DECAY', 0.01)
            }
        },
        
        "scheduler": {
            "type": "WarmupDecayLR",
            "params": {
                "warmup_min_lr": 0,
                "warmup_max_lr": params['LEARNING_RATE'],
                "warmup_num_steps": warmup_steps,
                "total_num_steps": total_steps
            }
        },
        
        "zero_optimization": {
            "stage": 2,
            "offload_optimizer": {"device": "none"},
            "allgather_partitions": True,
            "allgather_bucket_size": 5e8,
            "reduce_scatter": True,
            "reduce_bucket_size": 5e8,
            "overlap_comm": True,
            "contiguous_gradients": True
        },
        
        "gradient_accumulation_steps": grad_accum,
        "gradient_clipping": params.get('MAX_GRAD_NORM', 1.0),
        "steps_per_print": 10,
        "train_batch_size": global_batch_size,
        "train_micro_batch_size_per_gpu": micro_batch_per_gpu,
        "wall_clock_breakdown": False
    }
    
    return config


def main():
    """主函数"""
    print("\n🚀 开始自动更新DeepSpeed配置...")
    
    # 1. 解析shell脚本参数
    print("\n📝 解析run_training.sh参数...")
    params = parse_shell_script(RUN_SCRIPT)
    
    if not params:
        print("❌ 错误: 无法解析run_training.sh中的参数")
        sys.exit(1)
    
    # 2. 统计数据集大小
    dataset_path = params.get('DATASET_PATH', '')
    print(f"\n📊 统计数据集: {dataset_path}")
    
    # 处理本地路径映射（如果在本地运行）
    if dataset_path.startswith('/nas/'):
        local_path = dataset_path.replace('/nas/ganluo/Flow_RL', '/Users/luogan/Code/workflow_generation/Flow_RL')
        if os.path.exists(local_path):
            dataset_path = local_path
            print(f"   使用本地路径: {dataset_path}")
    
    dataset_size = count_dataset_samples(dataset_path)
    print(f"   样本数: {dataset_size}")
    
    # 3. 验证Accelerate配置
    print("\n🔍 验证accelerate_config.yaml...")
    num_gpus = verify_accelerate_config(ACCELERATE_CONFIG)
    
    # 4. 生成新的DeepSpeed配置
    config = generate_deepspeed_config(params, dataset_size, num_gpus)
    
    # 5. 保存配置
    print(f"\n💾 保存配置到: {DEEPSPEED_CONFIG}")
    with open(DEEPSPEED_CONFIG, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n✅ DeepSpeed配置更新成功！")
    
    # 6. 显示关键参数提醒
    print("\n" + "="*60)
    print("⚠️  重要提醒:")
    print("="*60)
    print("请确保以下参数在run_training.sh中保持一致:")
    print(f"  PER_DEVICE_BATCH_SIZE={params['PER_DEVICE_BATCH_SIZE']}")
    print(f"  GRAD_ACCUM_STEPS={params['GRAD_ACCUM_STEPS']}")
    print(f"  LEARNING_RATE={params['LEARNING_RATE']}")
    print(f"  WARMUP_RATIO={params['WARMUP_RATIO']}")
    print("="*60)


if __name__ == "__main__":
    main()