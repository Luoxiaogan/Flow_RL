#!/usr/bin/env python
"""
Quick test script to verify reward server connection and data availability
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_reward_server():
    """Test reward server connectivity"""
    print("1. 测试 Reward Server 连接...")
    try:
        response = requests.get("http://localhost:7788/health", timeout=5)
        if response.status_code == 200:
            print("   [OK] Reward Server 运行正常")
            data = response.json()
            print(f"   状态: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"   [FAIL] Reward Server 响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] 无法连接到 Reward Server")
        print("   请确保 Reward Server 正在运行:")
        print("     cd ../New_evaluation_and_RL/reward_server")
        print("     python scoreflow_reward_server.py")
        return False

def test_data_files():
    """Test if benchmark data files exist"""
    print("\n2. 检查测试数据文件...")
    # Load benchmark mapping to get correct paths
    benchmark_mapping = {}
    mapping_file = Path("../ScoreFlow/benchmark_mapping.jsonl")
    if mapping_file.exists():
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                benchmark_mapping[entry['benchmark']] = entry

    benchmarks = ['gsm8k', 'mbpp', 'humaneval']
    all_exist = True

    for benchmark in benchmarks:
        if benchmark in benchmark_mapping:
            data_path = Path(benchmark_mapping[benchmark]['data_test_dir'])
        else:
            # Fallback path
            data_path = Path(f"../Processed_dataset/{benchmark}/test.jsonl")
        if data_path.exists():
            # Count samples
            with open(data_path, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f)
            print(f"   [OK] {benchmark}: {count} 个样本")
        else:
            print(f"   [FAIL] {benchmark}: 文件不存在 ({data_path})")
            all_exist = False

    return all_exist

def test_imports():
    """Test if required modules can be imported"""
    print("\n3. 检查依赖模块...")
    required_modules = ['yaml', 'aiohttp', 'asyncio']
    all_imported = True

    for module in required_modules:
        try:
            __import__(module)
            print(f"   [OK] {module}")
        except ImportError:
            print(f"   [FAIL] {module} - 需要安装: pip install {module}")
            all_imported = False

    # Test workflow templates
    try:
        from workflow_templates import get_workflow_template
        print("   [OK] workflow_templates")
    except ImportError as e:
        print(f"   [FAIL] workflow_templates: {e}")
        all_imported = False

    return all_imported

def main():
    """Run all tests"""
    print("="*50)
    print("   CoT vs Self-Consistency 系统检查")
    print("="*50)

    results = []
    results.append(test_reward_server())
    results.append(test_data_files())
    results.append(test_imports())

    print("\n" + "="*50)
    if all(results):
        print("[SUCCESS] 所有检查通过! 系统已准备就绪")
        print("\n运行评估:")
        print("  python test_workflows.py")
    else:
        print("[ERROR] 部分检查失败，请解决问题后再运行评估")
    print("="*50)

if __name__ == "__main__":
    main()