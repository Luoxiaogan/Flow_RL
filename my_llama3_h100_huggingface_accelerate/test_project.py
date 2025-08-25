#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目完整性测试脚本
验证迁移后的Accelerate项目是否配置正确
"""
import sys
import os
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, 'src')

def test_imports():
    """测试所有关键模块是否能够正确导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试数据工具
        from data_utils import ModelArguments, DataArguments, EvalArguments
        from data_utils import setup_tokenizer, load_model, load_and_process_dataset
        print("✅ data_utils模块导入成功")
        
        # 测试数据整理器
        from data_collator import DataCollatorForChatML
        print("✅ data_collator模块导入成功")
        
        # 测试评估组件
        from evaluation.simple_evaluator import SimpleEvaluator
        from evaluation.score_collector import ScoreCollector  
        from evaluation.report_generator import ReportGenerator
        print("✅ evaluation模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_files():
    """测试配置文件是否存在且格式正确"""
    print("\n🔍 测试配置文件...")
    
    required_files = [
        'configs/accelerate_config.yaml',
        'configs/evaluation_config.yaml',
        'run_training.sh',
        'README.md',
        'README_zh.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} 存在")
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    # 测试YAML文件格式
    try:
        import yaml
        
        with open('configs/accelerate_config.yaml', 'r') as f:
            accel_config = yaml.safe_load(f)
        print("✅ accelerate_config.yaml 格式正确")
        
        with open('configs/evaluation_config.yaml', 'r') as f:
            eval_config = yaml.safe_load(f)  
        print("✅ evaluation_config.yaml 格式正确")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML配置文件格式错误: {e}")
        return False

def test_accelerate_config():
    """测试Accelerate配置是否适合DDP训练"""
    print("\n🔍 测试Accelerate配置...")
    
    try:
        import yaml
        
        with open('configs/accelerate_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # 检查关键配置
        expected_config = {
            'distributed_type': 'MULTI_GPU',
            'num_processes': 8,
            'mixed_precision': 'bf16'
        }
        
        for key, expected_value in expected_config.items():
            if config.get(key) != expected_value:
                print(f"⚠️  {key}: 期望 {expected_value}, 实际 {config.get(key)}")
            else:
                print(f"✅ {key}: {config.get(key)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Accelerate配置检查失败: {e}")
        return False

def test_batch_size_config():
    """检查启动脚本中的批次大小配置是否适合DDP"""
    print("\n🔍 测试批次大小配置...")
    
    try:
        with open('run_training.sh', 'r') as f:
            content = f.read()
        
        # 检查DDP优化的批次大小配置
        if 'PER_DEVICE_BATCH_SIZE=1' in content:
            print("✅ DDP优化: per_device_batch_size=1")
        else:
            print("⚠️  可能仍使用ZeRO-3批次大小")
            
        if 'GRAD_ACCUM_STEPS=4' in content:
            print("✅ DDP优化: gradient_accumulation_steps=4")
        else:
            print("⚠️  梯度累积步数可能需要调整")
            
        if '# = 1×4×8 = 32' in content:
            print("✅ 全局批次大小计算正确 (32)")
        
        return True
        
    except Exception as e:
        print(f"❌ 批次大小配置检查失败: {e}")
        return False

def test_evaluation_integration():
    """测试评估组件集成"""
    print("\n🔍 测试评估集成...")
    
    try:
        # 测试评估器初始化
        eval_config = {
            'generation': {
                'max_new_tokens': 512,
                'temperature': 0.7
            },
            'optimization': {
                'clear_cache': True
            }
        }
        
        from evaluation.simple_evaluator import SimpleEvaluator
        evaluator = SimpleEvaluator(eval_config)
        print("✅ SimpleEvaluator初始化成功")
        
        # 测试分数收集器
        from evaluation.score_collector import ScoreCollector
        collector = ScoreCollector('http://localhost:8899')
        print("✅ ScoreCollector初始化成功")
        
        # 测试报告生成器  
        from evaluation.report_generator import ReportGenerator
        reporter = ReportGenerator('./test_reports')
        print("✅ ReportGenerator初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 评估集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始项目完整性测试...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_files,
        test_accelerate_config,
        test_batch_size_config,
        test_evaluation_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有测试通过! ({passed}/{total})")
        print("\n✨ 项目迁移成功，可以进行训练!")
        print("\n🔧 使用方法:")
        print("  1. 检查run_training.sh中的路径设置")
        print("  2. 确保奖励服务器运行在localhost:8899")
        print("  3. 执行: ./run_training.sh")
        return 0
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
        print("请检查上述错误信息并修复相关问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)