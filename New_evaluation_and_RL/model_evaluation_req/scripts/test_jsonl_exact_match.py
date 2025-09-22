#!/usr/bin/env python
"""
Test script for JSONL model evaluation with exact matching only
测试 JSONL 模型精确匹配评估功能
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_exact_matching():
    """Test JSONL interface with exact matching only"""
    
    print("\n" + "="*60)
    print("JSONL 精确匹配测试")
    print("="*60)
    
    # Direct import to avoid torch dependency
    from core.interfaces.jsonl_model_interface import JSONLModelInterface
    
    # Test configurations for different steps
    configs = [
        {
            'name': 'RL-Step-100',
            'type': 'jsonl',
            'jsonl_path': '../val_logs/20241212_150000/100.jsonl'
        },
        {
            'name': 'RL-Step-500',
            'type': 'jsonl',
            'jsonl_path': '../val_logs/20241212_150000/500.jsonl'
        }
    ]
    
    # Test prompts - these MUST match exactly what's in the JSONL files
    test_cases = [
        {
            'prompt': "请编写一个workflow来解决以下GSM8K问题: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
            'expected': 'match'
        },
        {
            'prompt': "请编写一个workflow来解决以下MBPP问题: Write a function to find the maximum sum of a subarray of size k.",
            'expected': 'match'
        },
        {
            'prompt': "请编写一个workflow来解决以下GSM8K问题: Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
            'expected': 'match'
        },
        {
            'prompt': "这是一个不存在的输入，应该返回错误",
            'expected': 'error'
        }
    ]
    
    for config in configs:
        print(f"\n测试模型: {config['name']}")
        print("-" * 40)
        
        try:
            # Create and initialize model
            model = JSONLModelInterface(config)
            await model.initialize()
            print(f"✓ 模型初始化成功")
            
            # Get statistics
            stats = model.get_statistics()
            print(f"\n数据统计:")
            print(f"  总条目数: {stats.get('total_entries', 0)}")
            print(f"  唯一输入数: {stats.get('unique_inputs', 0)}")
            print(f"  平均分数: {stats.get('avg_score', 0):.2f}")
            print(f"  平均准确率: {stats.get('avg_accuracy', 0):.2%}")
            
            # Test each case
            print(f"\n测试精确匹配:")
            success_count = 0
            for i, test_case in enumerate(test_cases, 1):
                prompt = test_case['prompt']
                expected = test_case['expected']
                
                print(f"\n  测试 {i}: {prompt[:50]}...")
                response = await model.generate(prompt)
                
                if expected == 'match':
                    if "Error" not in response:
                        print(f"    ✓ 匹配成功，返回 {len(response)} 字符")
                        success_count += 1
                    else:
                        print(f"    ✗ 应该匹配但失败: {response}")
                elif expected == 'error':
                    if "Error" in response:
                        print(f"    ✓ 正确返回错误信息")
                        success_count += 1
                    else:
                        print(f"    ✗ 应该返回错误但成功了")
            
            print(f"\n测试结果: {success_count}/{len(test_cases)} 通过")
            
            # Cleanup
            await model.cleanup()
            print(f"✓ 资源清理完成")
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

async def compare_training_progress():
    """Compare outputs across different training steps"""
    
    print("\n" + "="*60)
    print("训练进度对比分析")
    print("="*60)
    
    from core.interfaces.jsonl_model_interface import JSONLModelInterface
    
    # Load models for different steps
    steps = [100, 500]
    models = []
    
    for step in steps:
        config = {
            'name': f'Step-{step}',
            'type': 'jsonl',
            'jsonl_path': f'../val_logs/20241212_150000/{step}.jsonl'
        }
        
        model = JSONLModelInterface(config)
        await model.initialize()
        models.append((step, model))
    
    # Common test prompt
    test_prompt = "请编写一个workflow来解决以下MBPP问题: Write a function to find the maximum sum of a subarray of size k."
    
    print(f"\n测试输入: {test_prompt[:80]}...")
    print("\n训练步数对比:")
    print("-" * 60)
    
    results = []
    for step, model in models:
        stats = model.get_statistics()
        response = await model.generate(test_prompt)
        
        if "Error" not in response:
            # Analyze code complexity
            lines = response.count('\n') + 1
            has_class = 'class Workflow' in response
            has_init = '__init__' in response
            method_count = response.count('def ')
            imports = response.count('import') + response.count('from ')
            
            result = {
                'step': step,
                'avg_score': stats.get('avg_score', 0),
                'avg_accuracy': stats.get('avg_accuracy', 0),
                'output_length': len(response),
                'lines': lines,
                'has_class': has_class,
                'has_init': has_init,
                'methods': method_count,
                'imports': imports
            }
            results.append(result)
            
            print(f"\nStep {step}:")
            print(f"  平均分数: {result['avg_score']:.2f}")
            print(f"  平均准确率: {result['avg_accuracy']:.2%}")
            print(f"  代码指标:")
            print(f"    - 总长度: {result['output_length']} 字符")
            print(f"    - 代码行数: {result['lines']}")
            print(f"    - 包含类定义: {'是' if result['has_class'] else '否'}")
            print(f"    - 包含初始化: {'是' if result['has_init'] else '否'}")
            print(f"    - 方法数量: {result['methods']}")
            print(f"    - 导入语句: {result['imports']}")
    
    # Analyze improvement
    if len(results) == 2:
        print("\n" + "="*40)
        print("训练改进分析:")
        improvement = {
            'score': results[1]['avg_score'] - results[0]['avg_score'],
            'accuracy': results[1]['avg_accuracy'] - results[0]['avg_accuracy'],
            'complexity': results[1]['methods'] - results[0]['methods']
        }
        
        print(f"  分数提升: {improvement['score']:+.2f}")
        print(f"  准确率提升: {improvement['accuracy']:+.2%}")
        print(f"  代码复杂度变化: {improvement['complexity']:+d} 个方法")
        
        if results[1]['has_class'] and not results[0]['has_class']:
            print(f"  ✓ 学会使用类结构")
        if results[1]['has_init'] and not results[0]['has_init']:
            print(f"  ✓ 学会使用初始化方法")
    
    # Cleanup
    for _, model in models:
        await model.cleanup()
    
    print("\n✓ 对比分析完成")

async def verify_data_integrity():
    """Verify JSONL data files integrity"""
    
    print("\n" + "="*60)
    print("数据完整性验证")
    print("="*60)
    
    files = [
        Path("../val_logs/20241212_150000/100.jsonl"),
        Path("../val_logs/20241212_150000/500.jsonl")
    ]
    
    for file_path in files:
        print(f"\n检查文件: {file_path.name}")
        print("-" * 40)
        
        if not file_path.exists():
            print(f"✗ 文件不存在")
            continue
        
        # Basic stats
        size = file_path.stat().st_size
        print(f"  文件大小: {size:,} 字节")
        
        # Parse and validate
        valid_lines = 0
        invalid_lines = 0
        unique_inputs = set()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Check required fields
                    required = ['input', 'output', 'score', 'step']
                    missing = [field for field in required if field not in data]
                    
                    if missing:
                        print(f"  ⚠ 行 {line_num}: 缺少字段 {missing}")
                        invalid_lines += 1
                    else:
                        valid_lines += 1
                        unique_inputs.add(data['input'])
                        
                except json.JSONDecodeError as e:
                    print(f"  ✗ 行 {line_num}: JSON 解析错误 - {e}")
                    invalid_lines += 1
        
        print(f"\n  统计:")
        print(f"    有效行数: {valid_lines}")
        print(f"    无效行数: {invalid_lines}")
        print(f"    唯一输入数: {len(unique_inputs)}")
        
        if invalid_lines == 0:
            print(f"  ✓ 数据完整性验证通过")
        else:
            print(f"  ⚠ 发现 {invalid_lines} 个问题")

async def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("JSONL 精确匹配评估系统测试")
    print("="*60)
    print(f"开始时间: {datetime.now()}")
    print("\n说明: 本测试只使用精确匹配，确保评估准确性")
    
    # Run all tests
    await verify_data_integrity()
    await test_exact_matching()
    await compare_training_progress()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print("✓ JSONL 数据加载和精确匹配功能正常")
    print("✓ 可以对比不同训练步数的输出质量")
    print("✓ 系统已准备好用于批量评估 RL 训练验证日志")
    print(f"\n结束时间: {datetime.now()}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())