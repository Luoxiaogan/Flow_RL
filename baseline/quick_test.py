#!/usr/bin/env python
"""
Quick test script with reduced samples for faster validation
"""

import asyncio
import yaml
from pathlib import Path
from test_workflows import WorkflowEvaluator

async def quick_test():
    """Run a quick test with reduced samples"""

    # Create a temporary config with reduced samples
    quick_config = {
        'reward_server': {
            'url': 'http://localhost:7788',
            'timeout': 300
        },
        'test': {
            'samples_per_benchmark': 5,  # Only 5 samples for quick test
            'benchmarks': ['gsm8k']  # Only test GSM8K for quick validation
        },
        'data': {
            'base_path': '../Processed_dataset'
        },
        'output': {
            'results_dir': './quick_test_results',
            'save_intermediate': True
        }
    }

    # Save quick config
    config_file = Path('quick_test_config.yaml')
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(quick_config, f, default_flow_style=False, allow_unicode=True)

    print("="*60)
    print("    快速测试模式 - 仅测试GSM8K，5个样本")
    print("="*60)
    print()

    # Run evaluation
    evaluator = WorkflowEvaluator('quick_test_config.yaml')
    await evaluator.run()

    # Clean up
    config_file.unlink()
    print("\n快速测试完成！")

if __name__ == "__main__":
    print("启动快速测试...")
    print("注意：请确保Reward Server运行在 http://localhost:7788")
    print()
    asyncio.run(quick_test())