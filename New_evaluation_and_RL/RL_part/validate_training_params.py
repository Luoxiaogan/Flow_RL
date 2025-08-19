#!/usr/bin/env python3
"""
VERL Training Parameters Validator
验证VERL训练参数的约束条件并输出计算摘要
"""

import yaml
import sys
from pathlib import Path


def validate_and_analyze_params(config_file):
    """验证训练参数并输出分析结果"""
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # 获取RL训练配置
    rl_config = config.get('rl_training', {})

    # 提取关键参数
    train_batch_size = rl_config['data']['train_batch_size']
    ppo_mini_batch_size = rl_config['actor']['ppo_mini_batch_size']
    ppo_micro_batch_size = rl_config['actor']['ppo_micro_batch_size_per_gpu']
    tensor_model_parallel_size = rl_config['rollout']['tensor_model_parallel_size']
    n_gpus_per_node = rl_config['trainer']['n_gpus_per_node']
    rollout_n = rl_config['rollout']['n']  # 每个prompt生成的响应数量

    # ScoreFlow配置
    max_wf_data_pair = config['services']['scoreflow_reward'].get('max_wf_data_pair_running', 5)

    # 计算派生参数
    data_parallel_size = n_gpus_per_node // tensor_model_parallel_size
    real_train_batch_size = train_batch_size * rollout_n
    gradient_accumulation_steps = ppo_mini_batch_size // ppo_micro_batch_size

    # 默认test_cases数量（从data_generation配置读取）
    default_test_cases = config.get('data_generation', {}).get('default_test_cases_per_entry', 5)

    print("【参数计算】")
    print(f"  GPU总数: {n_gpus_per_node}")
    print(f"  张量并行度(TP): {tensor_model_parallel_size}")
    print(f"  数据并行度(DP): {data_parallel_size}")
    print(f"  训练批次大小: {train_batch_size}")
    print(f"  每个prompt生成: {rollout_n}个响应-----rollout_n")
    print(f"  真实批次大小: {real_train_batch_size} = {train_batch_size} × {rollout_n}-----train_batch_size*rollout_n")
    print(f"  PPO mini批次: {ppo_mini_batch_size}-----ppo_mini_batch_size")
    print(f"  PPO micro批次: {ppo_micro_batch_size}-----ppo_micro_batch_size")
    print(f"  梯度累积步数: {gradient_accumulation_steps}-----gradient_accumulation_steps")
    print()

    print("【数据流分析】")
    print(f"  每个prompt → 生成(rollout_n){rollout_n}个workflow")
    print(f"  每个workflow → 评估(default_test_cases){default_test_cases}个test cases (默认)")
    print(f"  总计: 每个prompt产生 (rollout_n * default_test_cases){rollout_n * default_test_cases} 个(workflow,test_case)对")
    print(f"  并发限制: 最多{max_wf_data_pair}个(workflow,test_case)对同时执行")
    print()

    # 验证约束
    errors = []
    warnings = []

    # 约束1: GPU数量必须能被TP整除
    if n_gpus_per_node % tensor_model_parallel_size != 0:
        errors.append(f"GPU数量(n_gpus_per_node)({n_gpus_per_node})必须能被tensor_model_parallel_size({tensor_model_parallel_size})整除")
        errors.append(f"  建议: 修改tensor_model_parallel_size为 1, 2, 4 或 8")

    # 约束2: 真实批次大小必须能被DP整除
    if real_train_batch_size % data_parallel_size != 0:
        errors.append(f"真实批次大小(real_train_batch_size)({real_train_batch_size})必须能被数据并行度(data_parallel_size)({data_parallel_size})整除")
        errors.append(f"  建议: 调整train_batch_size或rollout.n")

    # 约束3: mini批次必须能被micro批次整除
    if ppo_mini_batch_size % ppo_micro_batch_size != 0:
        errors.append(f"PPO mini批次({ppo_mini_batch_size})必须能被micro批次({ppo_micro_batch_size})整除")
        errors.append(f"  建议: 调整ppo_mini_batch_size为{ppo_micro_batch_size}的倍数")

    # 约束4: train_batch_size必须>=ppo_mini_batch_size
    if train_batch_size < ppo_mini_batch_size:
        errors.append(f"训练批次({train_batch_size})必须≥PPO mini批次({ppo_mini_batch_size})")
        errors.append(f"  建议: 增加train_batch_size或减少ppo_mini_batch_size")

    # 约束5: micro批次检查
    if ppo_micro_batch_size < n_gpus_per_node:
        warnings.append(f"PPO micro批次({ppo_micro_batch_size})小于GPU数量({n_gpus_per_node})，可能导致GPU利用率低")

    # 输出验证结果
    if errors:
        print("【❌ 参数约束错误】")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("【✅ 参数约束验证】")
        print(f"  ✓ GPU数量可被TP整除: {n_gpus_per_node} % {tensor_model_parallel_size} = 0")
        print(f"  ✓ 批次大小可被DP整除: {real_train_batch_size} % {data_parallel_size} = 0")
        print(f"  ✓ Mini批次可被Micro批次整除: {ppo_mini_batch_size} % {ppo_micro_batch_size} = 0")
        print(f"  ✓ 训练批次≥PPO mini批次: {train_batch_size} ≥ {ppo_mini_batch_size}")

    if warnings:
        print("\n【⚠️ 警告】")
        for warning in warnings:
            print(f"  {warning}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python validate_training_params.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    if not Path(config_file).exists():
        print(f"配置文件不存在: {config_file}")
        sys.exit(1)
    
    validate_and_analyze_params(config_file)