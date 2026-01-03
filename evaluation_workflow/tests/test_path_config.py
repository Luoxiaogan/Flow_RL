#!/usr/bin/env python3
"""
测试路径配置是否正确
验证 processed_dataset 路径和其他配置
"""

import sys
import os
import yaml
from pathlib import Path

# 设置路径
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
sys.path.insert(0, str(PROJECT_ROOT))

def colored_print(text: str, color: str = "green"):
    """彩色输出"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def test_config_paths():
    """测试配置文件中的路径"""
    print("\n=== 测试路径配置 ===\n")
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    paths = config.get('paths', {})
    
    # 测试必需的路径
    required_paths = {
        'scoreflow_handlers': 'ScoreFlow处理器目录',
        'benchmark_mapping': '基准映射文件',
        'processed_dataset': '数据集根目录',
        'metagpt_config': 'MetaGPT配置文件'
    }
    
    all_ok = True
    for key, description in required_paths.items():
        path_str = paths.get(key)
        if path_str:
            path = Path(path_str)
            # 注意：在本地测试时路径可能不存在，这是正常的
            if path.exists():
                colored_print(f"✓ {description}: {path_str} (存在)", "green")
            else:
                colored_print(f"⚠ {description}: {path_str} (配置但不存在，服务器路径)", "yellow")
        else:
            colored_print(f"✗ {description}: 未配置", "red")
            all_ok = False
    
    return all_ok

def test_scoreflow_utils_import():
    """测试 scoreflow_reward_utils 的路径配置"""
    print("\n=== 测试 ScoreFlow 工具导入 ===\n")
    
    try:
        from scoreflow.scoreflow_reward_utils import (
            SCOREFLOW_HANDLERS_PATH,
            BENCHMARK_MAPPING_PATH,
            PROCESSED_DATASET_PATH,
            METAGPT_CONFIG_PATH
        )
        
        colored_print("✓ 成功导入路径配置", "green")
        print(f"  - ScoreFlow handlers: {SCOREFLOW_HANDLERS_PATH}")
        print(f"  - Benchmark mapping: {BENCHMARK_MAPPING_PATH}")
        print(f"  - Processed dataset: {PROCESSED_DATASET_PATH}")
        print(f"  - MetaGPT config: {METAGPT_CONFIG_PATH}")
        
        return True
    except ImportError as e:
        colored_print(f"✗ 导入失败: {e}", "red")
        return False

def test_data_path_resolution():
    """测试数据路径解析逻辑"""
    print("\n=== 测试数据路径解析 ===\n")
    
    # 模拟路径解析
    test_cases = [
        ("Processed_dataset/gsm8k/test.jsonl", "应该去掉前缀并拼接"),
        ("gsm8k/test.jsonl", "直接拼接"),
        ("/absolute/path/test.jsonl", "绝对路径不变"),
    ]
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    processed_dataset_path = Path(config['paths'].get('processed_dataset', '/nas/ganluo/Flow_RL/Processed_dataset'))
    
    for data_path, description in test_cases:
        if not os.path.isabs(data_path):
            if data_path.startswith("Processed_dataset/"):
                relative_path = data_path.replace("Processed_dataset/", "", 1)
                result_path = os.path.join(processed_dataset_path, relative_path)
            else:
                result_path = os.path.join(processed_dataset_path, data_path)
        else:
            result_path = data_path
        
        print(f"  输入: {data_path}")
        print(f"  输出: {result_path}")
        print(f"  说明: {description}")
        print()
    
    return True

def test_benchmark_mapping():
    """测试 benchmark_mapping.jsonl 的结构"""
    print("\n=== 测试 Benchmark Mapping ===\n")
    
    import json
    
    # 本地测试文件
    local_mapping = PROJECT_ROOT.parent / "ScoreFlow" / "benchmark_mapping.jsonl"
    
    if local_mapping.exists():
        with open(local_mapping, 'r') as f:
            lines = f.readlines()
        
        print(f"找到 {len(lines)} 个基准配置")
        
        for line in lines[:3]:  # 只显示前3个
            data = json.loads(line)
            print(f"  - {data['benchmark']}: {data.get('data_test_dir', 'N/A')}")
        
        colored_print("✓ Benchmark mapping 可读取", "green")
        return True
    else:
        colored_print("⚠ Benchmark mapping 文件不存在（本地路径）", "yellow")
        return True  # 不算失败

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    colored_print("路径配置测试", "blue")
    print("=" * 60)
    
    tests = [
        ("配置文件路径", test_config_paths),
        ("ScoreFlow导入", test_scoreflow_utils_import),
        ("数据路径解析", test_data_path_resolution),
        ("Benchmark映射", test_benchmark_mapping)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            colored_print(f"✗ 测试 '{name}' 执行失败: {e}", "red")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    colored_print("测试总结", "blue")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        color = "green" if result else "red"
        colored_print(f"{status} - {name}", color)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        colored_print("\n🎉 所有路径配置测试通过！", "green")
    else:
        colored_print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。", "yellow")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)