#!/usr/bin/env python3
"""
Test script for Token Tracking functionality
测试Token追踪功能
"""
import os
import sys
import json
import asyncio
import requests
from pathlib import Path

# 添加必要路径
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

from token_tracker import MetaGPTTokenTracker
from cost_calculator import CostCalculator


def test_token_tracker():
    """测试Token追踪器"""
    print("=" * 60)
    print("Testing Token Tracker")
    print("=" * 60)
    
    # 加载配置
    config_path = CURRENT_DIR / "config_cost.yaml"
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        token_config = config.get('token_tracking', {})
    
    # 创建追踪器
    tracker = MetaGPTTokenTracker(token_config)
    
    # 模拟workflow执行
    workflow_id = "test_workflow_001"
    model_name = "qwen-turbo"
    
    # 创建workflow context
    context = tracker.create_workflow_context(workflow_id, model_name)
    print(f"✓ Created context for workflow: {workflow_id}")
    
    # 模拟token使用（需要实际的MetaGPT环境）
    # 这里我们手动设置一些统计数据进行测试
    if context and hasattr(context, 'cost_manager'):
        # 模拟设置token数据
        context.cost_manager.total_prompt_tokens = 1500
        context.cost_manager.total_completion_tokens = 500
        context.cost_manager.total_cost = 0.002
    
    # 获取统计
    stats = tracker.get_workflow_stats(workflow_id)
    print(f"\n📊 Workflow统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 打印统计
    tracker.print_workflow_stats(workflow_id)
    
    # 更新总体统计
    tracker.update_total_stats(workflow_id)
    
    # 获取总体统计
    total_stats = tracker.get_total_stats()
    print(f"\n📈 总体统计:")
    print(json.dumps(total_stats, indent=2, ensure_ascii=False))
    
    print("\n✅ Token Tracker测试完成")


def test_cost_calculator():
    """测试费用计算器"""
    print("\n" + "=" * 60)
    print("Testing Cost Calculator")
    print("=" * 60)
    
    # 创建计算器
    calculator = CostCalculator()
    
    # 测试费用计算
    test_cases = [
        {"prompt_tokens": 1000, "completion_tokens": 500, "model": "qwen-turbo"},
        {"prompt_tokens": 5000, "completion_tokens": 2000, "model": "gpt-4"},
        {"prompt_tokens": 10000, "completion_tokens": 5000, "model": "unknown-model"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"  模型: {case['model']}")
        print(f"  输入tokens: {case['prompt_tokens']:,}")
        print(f"  输出tokens: {case['completion_tokens']:,}")
        
        cost_details = calculator.calculate_token_cost(
            case['prompt_tokens'],
            case['completion_tokens'],
            case['model']
        )
        
        print(f"  💰 费用计算结果:")
        print(f"     输入费用: ${cost_details['input_cost']:.6f}")
        print(f"     输出费用: ${cost_details['output_cost']:.6f}")
        print(f"     总费用: ${cost_details['total_cost']:.6f}")
        print(f"     使用的模型定价: {cost_details['model_used']}")
    
    # 测试费用惩罚
    print("\n" + "-" * 40)
    print("测试费用惩罚机制:")
    
    base_score = 1.0
    token_stats = {
        'prompt_tokens': 10000,
        'completion_tokens': 5000,
        'total_tokens': 15000,
        'total_cost': 0.015
    }
    
    final_score, penalty_details = calculator.apply_cost_penalty(base_score, token_stats)
    
    print(f"  基础分数: {base_score:.3f}")
    print(f"  总费用: ${token_stats['total_cost']:.6f}")
    print(f"  惩罚模式: {penalty_details.get('penalty_mode', 'N/A')}")
    print(f"  惩罚值: {penalty_details.get('penalty_percentage', 0):.1f}%")
    print(f"  最终分数: {final_score:.3f}")
    
    # 生成费用报告
    report = calculator.generate_cost_report()
    print(f"\n📊 费用报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("\n✅ Cost Calculator测试完成")


def test_server_api():
    """测试服务器API（需要服务器运行）"""
    print("\n" + "=" * 60)
    print("Testing Server API")
    print("=" * 60)
    
    server_url = "http://localhost:8899"
    
    # 测试健康检查
    try:
        response = requests.get(f"{server_url}/health", timeout=2)
        if response.status_code == 200:
            print(f"✓ 健康检查通过: {response.json()}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"⚠️ 无法连接到服务器: {e}")
        print("  请先启动服务器: python scoreflow_reward_server_with_cost.py")
        return
    
    # 测试compute_score（带token统计）
    test_data = {
        "data_source": "gsm8k",
        "solution_str": """
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
    
    async def __call__(self):
        return "Test result: 42"
""",
        "ground_truth": "default",
        "extra_info": {
            "test_cases": [0],
            "data_path": "test_data.jsonl"
        }
    }
    
    print("\n测试/compute_score端点...")
    response = requests.post(f"{server_url}/compute_score", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 计算成功:")
        print(f"  分数: {result.get('score', 0)}")
        if 'token_stats' in result:
            print(f"  Token统计:")
            stats = result['token_stats']
            print(f"    输入tokens: {stats.get('prompt_tokens', 0)}")
            print(f"    输出tokens: {stats.get('completion_tokens', 0)}")
            print(f"    总tokens: {stats.get('total_tokens', 0)}")
            print(f"    总费用: ${stats.get('total_cost', 0):.6f}")
    else:
        print(f"✗ 计算失败: {response.status_code}")
        print(f"  错误: {response.json()}")
    
    # 测试token统计端点
    print("\n测试/token_stats端点...")
    response = requests.get(f"{server_url}/token_stats")
    if response.status_code == 200:
        stats = response.json()
        if stats.get('success'):
            print(f"✓ 获取统计成功")
            print(f"  总workflows: {stats.get('stats', {}).get('total_workflows', 0)}")
            print(f"  总tokens: {stats.get('stats', {}).get('total_tokens', 0)}")
            print(f"  总费用: ${stats.get('stats', {}).get('total_cost', 0):.6f}")
    else:
        print(f"✗ 获取统计失败: {response.status_code}")
    
    # 测试费用报告端点
    print("\n测试/cost_report端点...")
    response = requests.get(f"{server_url}/cost_report")
    if response.status_code == 200:
        report = response.json()
        if report.get('success'):
            print(f"✓ 获取费用报告成功")
            config = report.get('report', {}).get('configuration', {})
            print(f"  惩罚启用: {config.get('penalty_enabled', False)}")
            print(f"  惩罚模式: {config.get('penalty_mode', 'N/A')}")
            print(f"  警报启用: {config.get('alerts_enabled', False)}")
    else:
        print(f"✗ 获取费用报告失败: {response.status_code}")
    
    print("\n✅ Server API测试完成")


def main():
    """主测试函数"""
    print("\n🚀 开始Token追踪功能测试\n")
    
    # 测试各个组件
    test_token_tracker()
    test_cost_calculator()
    test_server_api()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()