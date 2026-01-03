#!/usr/bin/env python3
"""
测试导入路径和模块依赖
验证所有内部模块可以正确导入，不依赖外部路径
"""

import sys
import os
import ast
import yaml
from pathlib import Path
from typing import Set, List, Dict

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

def get_imports_from_file(file_path: Path) -> Set[str]:
    """从Python文件中提取所有导入的模块"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        colored_print(f"⚠ 无法解析文件 {file_path}: {e}", "yellow")
    
    return imports

def test_no_external_imports():
    """测试没有导入外部项目模块"""
    print("\n=== 测试1: 无外部项目导入 ===")
    
    # 禁止的导入（外部项目模块）
    forbidden_imports = {
        'Test_FILE',
        'verl_support',
        'scoreflow_reward'  # 应该使用 scoreflow_reward_utils
    }
    
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'tests', 'logs', 'workspace'}]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    issues = []
    for file_path in python_files:
        relative_path = file_path.relative_to(PROJECT_ROOT)
        imports = get_imports_from_file(file_path)
        
        forbidden_found = imports & forbidden_imports
        if forbidden_found:
            issues.append((relative_path, forbidden_found))
    
    if issues:
        colored_print(f"✗ 发现 {len(issues)} 个文件有外部导入:", "red")
        for path, imports in issues:
            print(f"  - {path}: {', '.join(imports)}")
        return False
    else:
        colored_print("✓ 没有发现外部项目导入", "green")
        return True

def test_internal_imports_valid():
    """测试内部导入路径的有效性"""
    print("\n=== 测试2: 内部导入有效性 ===")
    
    # 内部模块
    internal_modules = {
        'evaluation',
        'scoreflow_reward_utils',
        'scoreflow_reward_server'
    }
    
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "scoreflow"))
    
    all_ok = True
    for module in internal_modules:
        try:
            if module == 'evaluation':
                # 测试evaluation下的子模块
                sub_modules = ['utils', 'sglang_server', 'batch_inference', 'report_generator']
                for sub in sub_modules:
                    try:
                        __import__(f'evaluation.{sub}')
                        colored_print(f"✓ evaluation.{sub} 可导入", "green")
                    except ImportError as e:
                        colored_print(f"✗ evaluation.{sub} 导入失败: {e}", "red")
                        all_ok = False
            else:
                __import__(module)
                colored_print(f"✓ {module} 可导入", "green")
        except ImportError as e:
            colored_print(f"✗ {module} 导入失败: {e}", "red")
            all_ok = False
    
    return all_ok

def test_sys_path_manipulations():
    """测试sys.path操作的合理性"""
    print("\n=== 测试3: sys.path操作检查 ===")
    
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'tests', 'logs', 'workspace'}]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    issues = []
    for file_path in python_files:
        relative_path = file_path.relative_to(PROJECT_ROOT)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if 'sys.path' in line and not line.strip().startswith('#'):
                    # 检查是否添加外部路径
                    if 'Test_FILE' in line or '../..' in line:
                        issues.append(f"{relative_path}:{i} - {line.strip()}")
                    elif 'PROJECT_ROOT' in line or 'CURRENT_DIR' in line:
                        # 这些是合理的
                        pass
                    else:
                        # 检查其他可疑的路径操作
                        if 'append' in line or 'insert' in line:
                            colored_print(f"ℹ {relative_path}:{i} - {line.strip()}", "blue")
        except Exception as e:
            colored_print(f"⚠ 无法检查文件 {relative_path}: {e}", "yellow")
    
    if issues:
        colored_print(f"✗ 发现 {len(issues)} 个可疑的sys.path操作:", "red")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        colored_print("✓ 所有sys.path操作都是本地的", "green")
        return True

def test_config_path_usage():
    """测试配置路径的使用"""
    print("\n=== 测试4: 配置路径使用 ===")
    
    # 检查scoreflow_reward_utils.py是否正确使用配置
    utils_file = PROJECT_ROOT / "scoreflow" / "scoreflow_reward_utils.py"
    
    if not utils_file.exists():
        colored_print("✗ scoreflow_reward_utils.py 不存在", "red")
        return False
    
    with open(utils_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("CONFIG_FILE = PROJECT_ROOT / \"config.yaml\"", "使用本地config.yaml"),
        ("paths_config = config.get('paths', {})", "读取paths配置"),
        ("SCOREFLOW_HANDLERS_PATH = Path(paths_config.get", "使用配置的handlers路径"),
        ("BENCHMARK_MAPPING_PATH = Path(paths_config.get", "使用配置的mapping路径")
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            colored_print(f"✓ {description}", "green")
        else:
            colored_print(f"✗ {description} 未找到", "red")
            all_ok = False
    
    return all_ok

def test_metagpt_paths():
    """测试MetaGPT路径处理"""
    print("\n=== 测试5: MetaGPT路径处理 ===")
    
    utils_file = PROJECT_ROOT / "scoreflow" / "scoreflow_reward_utils.py"
    
    with open(utils_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查MetaGPT路径是否从配置推导
    if "METAGPT_CONFIG_PATH.exists():" in content:
        colored_print("✓ MetaGPT路径从配置文件推导", "green")
        
        if "METAGPT_LOCAL = METAGPT_CONFIG_PATH.parent / \"metagpt_local\"" in content:
            colored_print("✓ MetaGPT本地路径相对于配置路径", "green")
        else:
            colored_print("✗ MetaGPT本地路径不是相对于配置路径", "red")
            return False
    else:
        colored_print("✗ MetaGPT路径处理有问题", "red")
        return False
    
    # 检查工作目录设置
    if "METAGPT_PROJECT_ROOT / \"workspace\"" in content:
        colored_print("✓ MetaGPT工作目录使用本地路径", "green")
    else:
        colored_print("✗ MetaGPT工作目录可能使用外部路径", "red")
        return False
    
    return True

def test_relative_imports():
    """测试相对导入的使用"""
    print("\n=== 测试6: 相对导入检查 ===")
    
    # evaluation目录下的文件应该使用相对导入
    eval_dir = PROJECT_ROOT / "evaluation"
    
    if not eval_dir.exists():
        colored_print("⚠ evaluation目录不存在", "yellow")
        return True
    
    issues = []
    for file_path in eval_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('from evaluation'):
                # 这是合理的绝对导入
                pass
            elif line.strip().startswith('from .'):
                # 相对导入，检查是否合理
                if '../' in line:
                    issues.append(f"{file_path.name}:{i} - {line.strip()}")
    
    if issues:
        colored_print(f"✗ 发现 {len(issues)} 个可疑的相对导入:", "red")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        colored_print("✓ 相对导入使用正确", "green")
        return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    colored_print("导入路径验证测试", "blue")
    print("=" * 60)
    
    tests = [
        ("无外部项目导入", test_no_external_imports),
        ("内部导入有效性", test_internal_imports_valid),
        ("sys.path操作检查", test_sys_path_manipulations),
        ("配置路径使用", test_config_path_usage),
        ("MetaGPT路径处理", test_metagpt_paths),
        ("相对导入检查", test_relative_imports)
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
        colored_print("\n🎉 所有导入路径测试通过！系统模块完全独立。", "green")
    else:
        colored_print(f"\n⚠️  {total - passed} 个测试失败，请检查导入。", "yellow")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)