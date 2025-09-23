#!/usr/bin/env python3
"""
测试Token费用惩罚功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_scoreflow_penalty():
    """测试ScoreFlow的token惩罚功能"""
    print("\n" + "="*60)
    print("测试 ScoreFlow Token惩罚功能")
    print("="*60)
    
    from reward_server.scoreflow_reward_utils import ScoreFlowRewardCalculator
    
    # 创建计算器实例
    calculator = ScoreFlowRewardCalculator()
    
    # 检查配置是否加载
    print(f"\nToken惩罚配置已加载: {bool(calculator.token_penalty_config)}")
    print(f"Token惩罚已启用: {calculator.token_penalty_config.get('enabled', False)}")
    
    if calculator.token_penalty_config.get('enabled'):
        print(f"价格配置:")
        pricing = calculator.token_penalty_config.get('pricing', {})
        print(f"  输入价格: ${pricing.get('input_price_per_million', 0)}/M tokens")
        print(f"  输出价格: ${pricing.get('output_price_per_million', 0)}/M tokens")
        
        print(f"惩罚策略:")
        strategy = calculator.token_penalty_config.get('penalty_strategy', {})
        print(f"  模式: {strategy.get('mode', 'unknown')}")
        print(f"  惩罚率: {strategy.get('penalty_rate', 0)}")
        print(f"  最大惩罚: {strategy.get('max_penalty', 0)}")
    
    # 测试惩罚计算
    print("\n测试惩罚计算:")
    test_cases = [
        {"prompt_tokens": 500, "completion_tokens": 200},
        {"prompt_tokens": 2000, "completion_tokens": 1000},
        {"prompt_tokens": 5000, "completion_tokens": 3000},
    ]
    
    for i, token_stats in enumerate(test_cases, 1):
        base_score = 1.0
        final_score, penalty_details = calculator.calculate_token_cost_penalty(base_score, token_stats)
        
        print(f"\n测试案例 {i}:")
        print(f"  输入tokens: {token_stats['prompt_tokens']}")
        print(f"  输出tokens: {token_stats['completion_tokens']}")
        if penalty_details:
            print(f"  总费用: ${penalty_details.get('total_cost', 0):.6f}")
            print(f"  惩罚值: {penalty_details.get('penalty_value', 0):.4f}")
            print(f"  最终分数: {final_score:.4f} (基础: {base_score})")
        else:
            print(f"  Token惩罚未启用，分数保持: {final_score}")


async def test_internbootcamp_penalty():
    """测试InternBootcamp的token惩罚功能"""
    print("\n" + "="*60)
    print("测试 InternBootcamp Token惩罚功能")
    print("="*60)
    
    from internbootcamp_reward_server.internbootcamp_reward_utils import InternBootcampRewardCalculator
    
    # 创建计算器实例
    calculator = InternBootcampRewardCalculator()
    
    # 检查配置是否加载
    print(f"\nToken惩罚配置已加载: {bool(calculator.token_penalty_config)}")
    print(f"Token惩罚已启用: {calculator.token_penalty_config.get('enabled', False)}")
    
    if calculator.token_penalty_config.get('enabled'):
        print(f"价格配置:")
        pricing = calculator.token_penalty_config.get('pricing', {})
        print(f"  输入价格: ${pricing.get('input_price_per_million', 0)}/M tokens")
        print(f"  输出价格: ${pricing.get('output_price_per_million', 0)}/M tokens")
        
        print(f"惩罚策略:")
        strategy = calculator.token_penalty_config.get('penalty_strategy', {})
        print(f"  模式: {strategy.get('mode', 'unknown')}")
        print(f"  惩罚率: {strategy.get('penalty_rate', 0)}")
        print(f"  最大惩罚: {strategy.get('max_penalty', 0)}")
    
    # 测试惩罚计算
    print("\n测试惩罚计算:")
    test_cases = [
        {"prompt_tokens": 500, "completion_tokens": 200},
        {"prompt_tokens": 2000, "completion_tokens": 1000},
        {"prompt_tokens": 5000, "completion_tokens": 3000},
    ]
    
    for i, token_stats in enumerate(test_cases, 1):
        base_score = 1.0
        final_score, penalty_details = calculator.calculate_token_cost_penalty(base_score, token_stats)
        
        print(f"\n测试案例 {i}:")
        print(f"  输入tokens: {token_stats['prompt_tokens']}")
        print(f"  输出tokens: {token_stats['completion_tokens']}")
        if penalty_details:
            print(f"  总费用: ${penalty_details.get('total_cost', 0):.6f}")
            print(f"  惩罚值: {penalty_details.get('penalty_value', 0):.4f}")
            print(f"  最终分数: {final_score:.4f} (基础: {base_score})")
        else:
            print(f"  Token惩罚未启用，分数保持: {final_score}")


async def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("Token费用惩罚功能测试")
    print("🚀"*30)
    
    # 测试ScoreFlow
    await test_scoreflow_penalty()
    
    # 测试InternBootcamp
    await test_internbootcamp_penalty()
    
    print("\n" + "✅"*30)
    print("测试完成！")
    print("✅"*30)


if __name__ == "__main__":
    asyncio.run(main())