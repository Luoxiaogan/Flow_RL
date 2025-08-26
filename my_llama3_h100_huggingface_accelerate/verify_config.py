#!/usr/bin/env python3
"""
验证所有配置文件的一致性
确保run_training.sh、deepspeed_zero2.json和accelerate_config.yaml之间的参数匹配
"""

import json
import yaml
import re
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent

def load_configs():
    """加载所有配置文件"""
    configs = {}
    
    # 加载DeepSpeed配置
    with open(SCRIPT_DIR / "configs" / "deepspeed_zero2.json", 'r') as f:
        configs['deepspeed'] = json.load(f)
    
    # 加载Accelerate配置
    with open(SCRIPT_DIR / "configs" / "accelerate_config.yaml", 'r') as f:
        configs['accelerate'] = yaml.safe_load(f)
    
    # 解析Shell脚本
    with open(SCRIPT_DIR / "run_training.sh", 'r') as f:
        shell_content = f.read()
    
    configs['shell'] = {
        'PER_DEVICE_BATCH_SIZE': int(re.search(r'PER_DEVICE_BATCH_SIZE=(\d+)', shell_content).group(1)),
        'GRAD_ACCUM_STEPS': int(re.search(r'GRAD_ACCUM_STEPS=(\d+)', shell_content).group(1)),
        'LEARNING_RATE': float(re.search(r'LEARNING_RATE=([\d.e-]+)', shell_content).group(1)),
        'WARMUP_RATIO': float(re.search(r'WARMUP_RATIO=([\d.]+)', shell_content).group(1)),
    }
    
    return configs


def verify_consistency(configs):
    """验证配置一致性"""
    errors = []
    warnings = []
    
    # 1. 验证批次大小公式
    num_gpus = configs['accelerate']['num_processes']
    micro_batch = configs['deepspeed']['train_micro_batch_size_per_gpu']
    grad_accum_ds = configs['deepspeed']['gradient_accumulation_steps']
    grad_accum_sh = configs['shell']['GRAD_ACCUM_STEPS']
    batch_size_ds = configs['deepspeed']['train_batch_size']
    
    expected_batch = num_gpus * micro_batch * grad_accum_ds
    
    if batch_size_ds != expected_batch:
        errors.append(f"批次大小不一致: DeepSpeed设置为{batch_size_ds}, 但根据公式应该是{expected_batch}")
    
    if grad_accum_ds != grad_accum_sh:
        errors.append(f"梯度累积步数不一致: DeepSpeed={grad_accum_ds}, Shell={grad_accum_sh}")
    
    # 2. 验证学习率
    lr_ds = configs['deepspeed']['optimizer']['params']['lr']
    lr_sh = configs['shell']['LEARNING_RATE']
    lr_scheduler = configs['deepspeed']['scheduler']['params']['warmup_max_lr']
    
    if abs(lr_ds - lr_sh) > 1e-10:
        errors.append(f"学习率不一致: DeepSpeed={lr_ds}, Shell={lr_sh}")
    
    if abs(lr_ds - lr_scheduler) > 1e-10:
        warnings.append(f"调度器最大学习率与优化器不一致: {lr_scheduler} vs {lr_ds}")
    
    # 3. 验证预热比例
    warmup_steps = configs['deepspeed']['scheduler']['params']['warmup_num_steps']
    total_steps = configs['deepspeed']['scheduler']['params']['total_num_steps']
    warmup_ratio_sh = configs['shell']['WARMUP_RATIO']
    
    actual_ratio = warmup_steps / total_steps if total_steps > 0 else 0
    if abs(actual_ratio - warmup_ratio_sh) > 0.01:
        warnings.append(f"预热比例不精确: 实际{actual_ratio:.3f}, Shell设置{warmup_ratio_sh}")
    
    # 4. 验证GPU数量
    if num_gpus != 8:
        warnings.append(f"GPU数量不是8: {num_gpus}")
    
    return errors, warnings


def print_report(configs, errors, warnings):
    """打印验证报告"""
    print("\n" + "="*60)
    print("📊 配置一致性验证报告")
    print("="*60)
    
    # 显示关键参数
    print("\n🔍 当前配置:")
    print(f"  GPU数量: {configs['accelerate']['num_processes']}")
    print(f"  微批次大小: {configs['deepspeed']['train_micro_batch_size_per_gpu']}")
    print(f"  梯度累积: {configs['deepspeed']['gradient_accumulation_steps']}")
    print(f"  全局批次: {configs['deepspeed']['train_batch_size']}")
    print(f"  学习率: {configs['deepspeed']['optimizer']['params']['lr']}")
    print(f"  总步数: {configs['deepspeed']['scheduler']['params']['total_num_steps']}")
    print(f"  预热步数: {configs['deepspeed']['scheduler']['params']['warmup_num_steps']}")
    
    # 显示错误和警告
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("\n✅ 没有发现配置错误")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for warning in warnings:
            print(f"  • {warning}")
    
    # 批次大小验证
    num_gpus = configs['accelerate']['num_processes']
    micro = configs['deepspeed']['train_micro_batch_size_per_gpu']
    accum = configs['deepspeed']['gradient_accumulation_steps']
    batch = configs['deepspeed']['train_batch_size']
    
    print(f"\n📐 批次大小公式验证:")
    print(f"  {batch} = {num_gpus} × {micro} × {accum} = {num_gpus * micro * accum}")
    
    if batch == num_gpus * micro * accum:
        print("  ✅ 公式正确")
    else:
        print("  ❌ 公式错误！")
    
    print("="*60)
    
    return len(errors) == 0


def main():
    """主函数"""
    try:
        configs = load_configs()
        errors, warnings = verify_consistency(configs)
        success = print_report(configs, errors, warnings)
        
        if not success:
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()