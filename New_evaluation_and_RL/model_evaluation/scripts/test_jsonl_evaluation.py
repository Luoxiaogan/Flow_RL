#!/usr/bin/env python
"""
Test script for JSONL model evaluation
测试 JSONL 模型评估功能
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.utils.model_factory import ModelFactory
from core.interfaces.jsonl_model_interface import JSONLModelInterface

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_jsonl_interface():
    """Test JSONL model interface functionality"""
    
    print("\n" + "="*60)
    print("测试 JSONL 模型接口功能")
    print("="*60)
    
    # Test configuration
    test_configs = [
        {
            'name': 'RL-Step-100-Exact',
            'type': 'jsonl',
            'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/100.jsonl',
            'match_mode': 'exact'
        },
        {
            'name': 'RL-Step-500-Exact',
            'type': 'jsonl',
            'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/500.jsonl',
            'match_mode': 'exact'
        },
        {
            'name': 'RL-Step-500-Fuzzy',
            'type': 'jsonl',
            'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/500.jsonl',
            'match_mode': 'fuzzy',
            'similarity_threshold': 0.8
        }
    ]
    
    # Test prompts
    test_prompts = [
        "请编写一个workflow来解决以下GSM8K问题: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
        "请编写一个workflow来解决以下MBPP问题: Write a function to find the maximum sum of a subarray of size k.",
        "请编写一个workflow来解决以下GSM8K问题: Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
        "这是一个不存在的测试输入，应该返回错误"
    ]
    
    for config in test_configs:
        print(f"\n测试模型: {config['name']}")
        print("-" * 40)
        
        try:
            # Create model
            model = ModelFactory.create_model(config)
            
            # Validate config
            ModelFactory.validate_config(config)
            print(f"✓ 配置验证通过")
            
            # Initialize model
            await model.initialize()
            print(f"✓ 模型初始化成功")
            
            # Get statistics
            if isinstance(model, JSONLModelInterface):
                stats = model.get_statistics()
                print(f"\n数据统计:")
                print(f"  总条目数: {stats.get('total_entries', 0)}")
                print(f"  唯一输入数: {stats.get('unique_inputs', 0)}")
                print(f"  平均分数: {stats.get('avg_score', 0):.2f}")
                print(f"  平均准确率: {stats.get('avg_accuracy', 0):.2%}")
            
            # Test generation
            print(f"\n测试生成:")
            for i, prompt in enumerate(test_prompts, 1):
                print(f"\n  测试 {i}: {prompt[:50]}...")
                try:
                    response = await model.generate(prompt)
                    if "Error" in response:
                        print(f"    结果: ❌ {response[:100]}")
                    else:
                        print(f"    结果: ✓ 生成了 {len(response)} 字符的响应")
                        print(f"    预览: {response[:150]}...")
                except Exception as e:
                    print(f"    结果: ❌ 异常: {e}")
            
            # Cleanup
            await model.cleanup()
            print(f"\n✓ 资源清理完成")
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

async def test_model_factory():
    """Test ModelFactory with JSONL type"""
    
    print("\n" + "="*60)
    print("测试 ModelFactory JSONL 类型支持")
    print("="*60)
    
    # Test creating JSONL model
    config = {
        'name': 'Test-JSONL',
        'type': 'jsonl',
        'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/100.jsonl',
        'match_mode': 'exact'
    }
    
    try:
        model = ModelFactory.create_model(config)
        print(f"✓ 成功创建 JSONL 模型: {type(model).__name__}")
        
        # Test validation
        ModelFactory.validate_config(config)
        print(f"✓ 配置验证通过")
        
        # Test invalid config
        invalid_config = {
            'name': 'Invalid-JSONL',
            'type': 'jsonl'
            # Missing jsonl_path
        }
        
        try:
            ModelFactory.validate_config(invalid_config)
            print(f"✗ 应该抛出异常但没有")
        except ValueError as e:
            print(f"✓ 正确检测到无效配置: {e}")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

async def compare_training_steps():
    """Compare performance across different training steps"""
    
    print("\n" + "="*60)
    print("对比不同训练步数的性能")
    print("="*60)
    
    # Load both step 100 and step 500
    step_100_config = {
        'name': 'Step-100',
        'type': 'jsonl',
        'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/100.jsonl',
        'match_mode': 'exact'
    }
    
    step_500_config = {
        'name': 'Step-500',
        'type': 'jsonl',
        'jsonl_path': 'D:/temp/Flow_RL/New_evaluation_and_RL/val_logs/20241212_150000/500.jsonl',
        'match_mode': 'exact'
    }
    
    models = []
    for config in [step_100_config, step_500_config]:
        model = ModelFactory.create_model(config)
        await model.initialize()
        models.append((config['name'], model))
    
    # Test with same prompts
    test_prompt = "请编写一个workflow来解决以下GSM8K问题: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
    
    print(f"\n测试提示: {test_prompt[:80]}...")
    print("\n生成结果对比:")
    print("-" * 40)
    
    for name, model in models:
        response = await model.generate(test_prompt)
        print(f"\n{name}:")
        print(f"  长度: {len(response)} 字符")
        print(f"  预览: {response[:200]}...")
        
        if isinstance(model, JSONLModelInterface):
            stats = model.get_statistics()
            print(f"  平均分数: {stats.get('avg_score', 0):.2f}")
            print(f"  平均准确率: {stats.get('avg_accuracy', 0):.2%}")
    
    # Cleanup
    for _, model in models:
        await model.cleanup()
    
    print("\n✓ 对比完成")

async def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("JSONL 模型评估集成测试")
    print("="*60)
    print(f"开始时间: {datetime.now()}")
    
    # Run all tests
    await test_model_factory()
    await test_jsonl_interface()
    await compare_training_steps()
    
    print("\n" + "="*60)
    print("所有测试完成")
    print(f"结束时间: {datetime.now()}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())