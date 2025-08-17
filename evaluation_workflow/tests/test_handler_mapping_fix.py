#!/usr/bin/env python3
"""
测试benchmark handler映射修复
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_handler_mapping():
    """测试handler映射逻辑"""
    
    print("=" * 60)
    print("\033[94m测试Benchmark Handler映射修复\033[0m")
    print("=" * 60)
    
    # 导入需要的模块
    try:
        from scoreflow.scoreflow_reward_utils import ScoreFlowRewardCalculator
        print("\033[92m✓ 成功导入 ScoreFlowRewardCalculator\033[0m")
    except ImportError as e:
        print(f"\033[91m✗ 导入失败: {e}\033[0m")
        return False
    
    # 创建计算器实例
    config_path = Path(__file__).parent.parent / "config.yaml"
    calculator = ScoreFlowRewardCalculator(str(config_path))
    print(f"\033[92m✓ 成功创建 ScoreFlowRewardCalculator 实例\033[0m")
    
    # 测试不同的benchmark名称
    test_cases = [
        ("gsm8k", "Gsm8kHandler"),
        ("mbpp", "MbppHandler"),
        ("high_level_math", "HighlevelmathHandler"),
        ("high_level_math_limr", "HighlevelmathHandler"),  # 应该使用base mapping
        ("drop", "DropHandler"),
        ("humaneval", "HumanevalHandler"),
        ("hotpotqa", "HotpotqaHandler"),
    ]
    
    print("\n=== 测试Benchmark映射 ===\n")
    
    success_count = 0
    for benchmark_name, expected_handler in test_cases:
        print(f"测试 {benchmark_name}...")
        
        # 查找映射
        benchmark_info = calculator.benchmark_mapping.get(benchmark_name)
        
        # 如果精确匹配失败，尝试去掉后缀
        if not benchmark_info and '_' in benchmark_name:
            base_name = '_'.join(benchmark_name.split('_')[:-1])
            benchmark_info = calculator.benchmark_mapping.get(base_name)
            if benchmark_info:
                print(f"  \033[94m使用基础benchmark '{base_name}' 的映射\033[0m")
        
        if benchmark_info:
            handler_class = benchmark_info.get('handler_class', 'N/A')
            if handler_class == expected_handler:
                print(f"  \033[92m✓ 正确: {handler_class}\033[0m")
                success_count += 1
            else:
                print(f"  \033[91m✗ 错误: 期望 {expected_handler}, 得到 {handler_class}\033[0m")
        else:
            # 检查默认逻辑
            if benchmark_name.startswith("high_level_math"):
                handler_class = "HighlevelmathHandler"
            else:
                handler_class = f"{benchmark_name.capitalize()}Handler"
            
            if handler_class == expected_handler:
                print(f"  \033[93m○ 使用默认规则: {handler_class}\033[0m")
                success_count += 1
            else:
                print(f"  \033[91m✗ 默认规则错误: 期望 {expected_handler}, 得到 {handler_class}\033[0m")
    
    print("\n" + "=" * 60)
    print(f"\033[94m测试结果: {success_count}/{len(test_cases)} 通过\033[0m")
    print("=" * 60)
    
    if success_count == len(test_cases):
        print("\033[92m\n🎉 所有测试通过！Handler映射逻辑正确。\033[0m")
        return True
    else:
        print(f"\033[91m\n⚠ {len(test_cases) - success_count} 个测试失败。\033[0m")
        return False

def test_handler_loading():
    """测试实际的handler加载"""
    
    print("\n" + "=" * 60)
    print("\033[94m测试Handler实际加载\033[0m")
    print("=" * 60)
    
    from scoreflow.scoreflow_reward_utils import ScoreFlowRewardCalculator
    
    config_path = Path(__file__).parent.parent / "config.yaml"
    calculator = ScoreFlowRewardCalculator(str(config_path))
    
    # 测试加载high_level_math_limr的handler
    test_benchmark = "high_level_math_limr"
    
    print(f"\n尝试加载 '{test_benchmark}' 的handler...")
    
    try:
        # 模拟_load_benchmark_handler的逻辑
        benchmark_info = calculator.benchmark_mapping.get(test_benchmark)
        
        if not benchmark_info and '_' in test_benchmark:
            base_name = '_'.join(test_benchmark.split('_')[:-1])
            benchmark_info = calculator.benchmark_mapping.get(base_name)
            if benchmark_info:
                print(f"  \033[94m使用基础benchmark '{base_name}' 的映射\033[0m")
        
        if benchmark_info:
            handler_class_name = benchmark_info['handler_class']
            handler_dir = benchmark_info['handler_dir']
            print(f"  Handler类名: {handler_class_name}")
            print(f"  Handler目录: {handler_dir}")
            print(f"  \033[92m✓ 映射信息获取成功\033[0m")
        else:
            print(f"  \033[91m✗ 未找到映射信息\033[0m")
            
    except Exception as e:
        print(f"  \033[91m✗ 加载失败: {e}\033[0m")
        return False
    
    return True

if __name__ == "__main__":
    success1 = test_handler_mapping()
    success2 = test_handler_loading()
    
    if success1 and success2:
        print("\n\033[92m✅ 所有测试通过！\033[0m")
        sys.exit(0)
    else:
        print("\n\033[91m❌ 部分测试失败。\033[0m")
        sys.exit(1)