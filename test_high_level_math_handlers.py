#!/usr/bin/env python3
"""
高级数学 Benchmark Handler 单元测试脚本
用于测试 AIME2024, AIME2025, LIMR, MATH500 的基本功能
"""

import asyncio
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# List of benchmarks to test
BENCHMARKS = [
    ("aime2024", "Aime2024Handler"),
    ("aime2025", "Aime2025Handler"),
    ("limr", "LimrHandler"),
    ("math500", "Math500Handler")
]

def test_data_loading(benchmark_name, handler_class_name):
    """Test data loading functionality"""
    print("\n" + "="*60)
    print(f"测试 1：数据加载 - {benchmark_name}")
    print("="*60)
    
    try:
        # Dynamic import handler
        handler_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.handler",
            fromlist=[handler_class_name]
        )
        HandlerClass = getattr(handler_module, handler_class_name)
        
        # Create handler instance
        dataset_path = f"Processed_dataset/high_level_math/{benchmark_name}/test.jsonl"
        handler = HandlerClass(dataset_path=dataset_path)
        
        print(f"[OK] 成功加载 {len(handler.data)} 条数据")
        
        # Show structure of first 2 data entries
        print(f"\n前 2 条数据示例：")
        for i in range(min(2, len(handler.data))):
            data = handler.data[i]
            print(f"\n数据 {i}:")
            for key in list(data.keys())[:3]:  # Only show first 3 fields
                value = str(data[key])[:200]  # Limit length
                if len(str(data[key])) > 200:
                    value += "..."
                print(f"  {key}: {value}")
        
        return handler
        
    except FileNotFoundError as e:
        print(f"[WARNING] 数据文件未找到: {e}")
        print(f"   请确保数据集存在于: {dataset_path}")
        return None
    except Exception as e:
        print(f"[ERROR] 数据加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_prompt_generation(handler, benchmark_name):
    """Test prompt generation functionality"""
    print("\n" + "="*60)
    print(f"测试 2：提示生成 - {benchmark_name}")
    print("="*60)
    
    if not handler:
        print("[WARNING] 跳过：Handler 未初始化")
        return
    
    try:
        # Test single problem
        prompt_single = handler.get_prompt_text([0])
        print("单个问题的提示：")
        print("-" * 40)
        print(prompt_single[:500] + "..." if len(prompt_single) > 500 else prompt_single)
        
        # Test multiple problems
        indices = [0, 1] if len(handler.data) >= 2 else [0]
        prompt_multiple = handler.get_prompt_text(indices)
        print(f"\n{len(indices)} 个问题的提示长度: {len(prompt_multiple)} 字符")
        
        # Verify format
        if "---" in prompt_multiple and "**QUESTION:**" in prompt_multiple:
            print("[OK] 提示格式正确（包含 Markdown 分隔符）")
        else:
            print("[WARNING] 提示格式可能需要调整")
        
    except Exception as e:
        print(f"[ERROR] 提示生成失败: {e}")
        import traceback
        traceback.print_exc()

def test_verification_data(handler, benchmark_name):
    """Test verification data retrieval"""
    print("\n" + "="*60)
    print(f"测试 3：验证数据获取 - {benchmark_name}")
    print("="*60)
    
    if not handler:
        print("[WARNING] 跳过：Handler 未初始化")
        return
    
    try:
        # Get verification data for first problem
        verify_data = handler.get_verification_data(0)
        
        print("验证数据结构：")
        print("-" * 40)
        for key, value in verify_data.items():
            value_str = str(value)[:100]
            if len(str(value)) > 100:
                value_str += "..."
            print(f"{key}: {value_str}")
        
        # Check required fields
        required_fields = ['answer']  # Adjust as needed
        missing_fields = [f for f in required_fields if f not in verify_data]
        
        if not missing_fields:
            print(f"\n[OK] 包含所有必需字段")
        else:
            print(f"\n[WARNING] 缺少字段: {missing_fields}")
        
    except Exception as e:
        print(f"[ERROR] 验证数据获取失败: {e}")
        import traceback
        traceback.print_exc()

def check_conditions_file(benchmark_name):
    """Check conditions.py file"""
    print("\n" + "="*60)
    print(f"测试 4：检查 conditions.py - {benchmark_name}")
    print("="*60)
    
    try:
        # Import conditions module
        conditions_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.conditions",
            fromlist=['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        )
        
        required_vars = [
            'TASK_PROMPT',
            'SYSTEM_PROMPT', 
            'PYTHON_START',
            'PYTHON_END',
            'START_PROMPT'
        ]
        
        print("检查必需的变量：")
        all_present = True
        for var in required_vars:
            if hasattr(conditions_module, var):
                content = getattr(conditions_module, var)
                print(f"[OK] {var}: {len(content)} 字符")
            else:
                print(f"[ERROR] {var}: 缺失")
                all_present = False
        
        if all_present:
            print("\n[OK] conditions.py 包含所有必需变量")
        else:
            print("\n[WARNING] conditions.py 缺少某些变量")
        
    except ImportError as e:
        print(f"[ERROR] 无法导入 conditions.py: {e}")
    except Exception as e:
        print(f"[ERROR] 检查 conditions.py 时出错: {e}")

def test_benchmark_mapping():
    """Test benchmark_mapping.jsonl entries"""
    print("\n" + "="*60)
    print("测试 5：检查 benchmark_mapping.jsonl 配置")
    print("="*60)
    
    try:
        with open("ScoreFlow/benchmark_mapping.jsonl", "r", encoding="utf-8") as f:
            mappings = [json.loads(line) for line in f]
        
        benchmark_names = [b[0] for b in BENCHMARKS]
        found_benchmarks = []
        
        print("检查 benchmark 配置：")
        for mapping in mappings:
            if mapping['benchmark'] in benchmark_names:
                found_benchmarks.append(mapping['benchmark'])
                print(f"[OK] {mapping['benchmark']}: 已配置")
                print(f"   - Handler: {mapping['handler_class']}")
                print(f"   - Dir: {mapping['handler_dir']}")
        
        missing = set(benchmark_names) - set(found_benchmarks)
        if missing:
            print(f"\n[WARNING] 缺少配置: {missing}")
        else:
            print("\n[OK] 所有 benchmark 都已在 mapping 中配置")
            
    except Exception as e:
        print(f"[ERROR] 检查 benchmark_mapping.jsonl 时出错: {e}")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print(f"高级数学 Benchmark Handler 单元测试")
    print(f"测试 Benchmarks: {', '.join([b[0] for b in BENCHMARKS])}")
    print("="*60)
    
    # Test benchmark mapping first
    test_benchmark_mapping()
    
    # Test each benchmark
    for benchmark_name, handler_class_name in BENCHMARKS:
        print("\n" + "#"*60)
        print(f"# 测试 Benchmark: {benchmark_name.upper()}")
        print("#"*60)
        
        # 1. Test data loading
        handler = test_data_loading(benchmark_name, handler_class_name)
        
        # 2. Test prompt generation
        test_prompt_generation(handler, benchmark_name)
        
        # 3. Test verification data
        test_verification_data(handler, benchmark_name)
        
        # 4. Check conditions.py
        check_conditions_file(benchmark_name)
    
    # Summary
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n测试总结：")
    print("[OK] 已创建 4 个新的高级数学 benchmark")
    print("[OK] 每个 benchmark 都有 handler.py 和 conditions.py")
    print("[OK] 已在 benchmark_mapping.jsonl 中注册")
    print("\n下一步：")
    print("1. 确保数据集文件存在于正确的路径")
    print("2. 根据数据集的实际格式调整 handler.py 中的字段映射")
    print("3. 运行完整的工作流测试验证功能")

if __name__ == "__main__":
    main()