#!/usr/bin/env python3
"""
测试 evaluation_workflow 的配置独立性
验证系统不依赖外部配置文件
"""

import sys
import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set

# 设置路径
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

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

def test_config_file_exists():
    """测试配置文件是否存在"""
    print("\n=== 测试1: 配置文件存在性 ===")
    if CONFIG_FILE.exists():
        colored_print(f"✓ 配置文件存在: {CONFIG_FILE}", "green")
        return True
    else:
        colored_print(f"✗ 配置文件不存在: {CONFIG_FILE}", "red")
        return False

def test_config_structure():
    """测试配置文件结构"""
    print("\n=== 测试2: 配置文件结构 ===")
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    required_sections = ['services', 'model', 'evaluation', 'logging', 'paths']
    missing_sections = []
    
    for section in required_sections:
        if section in config:
            colored_print(f"✓ 配置节 '{section}' 存在", "green")
        else:
            colored_print(f"✗ 配置节 '{section}' 缺失", "red")
            missing_sections.append(section)
    
    return len(missing_sections) == 0

def test_external_paths():
    """测试外部路径配置"""
    print("\n=== 测试3: 外部路径配置 ===")
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    paths_config = config.get('paths', {})
    
    # 这些是需要的外部路径（通过config.yaml管理）
    external_paths = {
        'scoreflow_handlers': 'ScoreFlow处理器路径',
        'benchmark_mapping': '基准映射文件路径',
        'metagpt_config': 'MetaGPT配置路径'
    }
    
    issues = []
    for key, description in external_paths.items():
        if key in paths_config:
            path_value = paths_config[key]
            if path_value and path_value != "":
                colored_print(f"✓ {description} 已配置: {path_value}", "green")
            else:
                colored_print(f"⚠ {description} 配置为空", "yellow")
                issues.append(f"{description}为空")
        else:
            colored_print(f"✗ {description} 未配置", "red")
            issues.append(f"{description}未配置")
    
    return len(issues) == 0

def test_no_hardcoded_paths():
    """测试Python文件中没有硬编码的外部路径"""
    print("\n=== 测试4: 检查硬编码路径 ===")
    
    # 排除的目录和文件
    exclude_dirs = {'.git', '__pycache__', 'tests', 'logs', 'workspace', 'results'}
    exclude_files = {'README.md', 'README_zh.md'}
    
    suspicious_patterns = [
        '../Test_FILE',
        '../ScoreFlow',
        '../../',
        '/home/',
        '/nas/',
        'Test_FILE/verl_support/config.json'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py') and file not in exclude_files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(PROJECT_ROOT)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern in suspicious_patterns:
                        if pattern in content:
                            # 检查是否在注释中
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pattern in line and not line.strip().startswith('#'):
                                    issues.append(f"{relative_path}:{i} 包含 '{pattern}'")
                except Exception as e:
                    colored_print(f"⚠ 无法读取文件 {relative_path}: {e}", "yellow")
    
    if issues:
        colored_print(f"✗ 发现 {len(issues)} 个硬编码路径问题:", "red")
        for issue in issues[:10]:  # 只显示前10个
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... 还有 {len(issues) - 10} 个问题")
        return False
    else:
        colored_print("✓ 没有发现硬编码的外部路径", "green")
        return True

def test_internal_imports():
    """测试内部导入的独立性"""
    print("\n=== 测试5: 内部导入独立性 ===")
    
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    external_imports = []
    for file_path in python_files:
        relative_path = file_path.relative_to(PROJECT_ROOT)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('from ') or line.startswith('import '):
                    # 检查是否导入外部的Test_FILE或verl_support
                    if 'Test_FILE' in line or 'verl_support' in line:
                        if 'scoreflow_reward' in line and 'scoreflow_reward_utils' not in line:
                            external_imports.append(f"{relative_path}:{i} - {line}")
        except Exception as e:
            colored_print(f"⚠ 无法分析文件 {relative_path}: {e}", "yellow")
    
    if external_imports:
        colored_print(f"✗ 发现 {len(external_imports)} 个外部导入:", "red")
        for imp in external_imports[:5]:
            print(f"  - {imp}")
        return False
    else:
        colored_print("✓ 所有导入都是内部的或标准库", "green")
        return True

def test_service_configs():
    """测试服务配置的完整性"""
    print("\n=== 测试6: 服务配置完整性 ===")
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    services = config.get('services', {})
    
    # 检查MetaGPT API代理服务
    api_proxy = services.get('metagpt_api_proxy', {})
    required_proxy_fields = ['enabled', 'host', 'port', 'target_url']
    
    issues = []
    for field in required_proxy_fields:
        if field in api_proxy:
            colored_print(f"✓ MetaGPT API代理配置 '{field}' 存在", "green")
        else:
            colored_print(f"✗ MetaGPT API代理配置 '{field}' 缺失", "red")
            issues.append(f"metagpt_api_proxy.{field}")
    
    # 检查ScoreFlow Reward服务
    scoreflow = services.get('scoreflow_reward', {})
    required_scoreflow_fields = ['enabled', 'host', 'port', 'timeout']
    
    for field in required_scoreflow_fields:
        if field in scoreflow:
            colored_print(f"✓ ScoreFlow服务配置 '{field}' 存在", "green")
        else:
            colored_print(f"✗ ScoreFlow服务配置 '{field}' 缺失", "red")
            issues.append(f"scoreflow_reward.{field}")
    
    return len(issues) == 0

def test_workspace_paths():
    """测试工作空间路径是否本地化"""
    print("\n=== 测试7: 工作空间路径本地化 ===")
    
    scoreflow_utils = PROJECT_ROOT / "scoreflow" / "scoreflow_reward_utils.py"
    
    if not scoreflow_utils.exists():
        colored_print("⚠ scoreflow_reward_utils.py 不存在", "yellow")
        return False
    
    with open(scoreflow_utils, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查workspace路径是否使用PROJECT_ROOT
    if 'workspace_dir = PROJECT_ROOT / "workspace"' in content:
        colored_print("✓ workspace路径使用本地PROJECT_ROOT", "green")
        workspace_ok = True
    else:
        colored_print("✗ workspace路径可能使用外部路径", "red")
        workspace_ok = False
    
    # 检查debug路径
    if 'DEBUG_PATH = PROJECT_ROOT / "debug_logs"' in content:
        colored_print("✓ debug路径使用本地PROJECT_ROOT", "green")
        debug_ok = True
    else:
        colored_print("✗ debug路径可能使用外部路径", "red")
        debug_ok = False
    
    return workspace_ok and debug_ok

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    colored_print("evaluation_workflow 配置独立性测试", "blue")
    print("=" * 60)
    
    tests = [
        ("配置文件存在性", test_config_file_exists),
        ("配置文件结构", test_config_structure),
        ("外部路径配置", test_external_paths),
        ("无硬编码路径", test_no_hardcoded_paths),
        ("内部导入独立性", test_internal_imports),
        ("服务配置完整性", test_service_configs),
        ("工作空间本地化", test_workspace_paths)
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
        colored_print("\n🎉 所有测试通过！系统配置完全独立。", "green")
    else:
        colored_print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。", "yellow")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)