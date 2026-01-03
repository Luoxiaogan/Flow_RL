#!/usr/bin/env python3
"""
测试服务启动配置和脚本
验证服务可以正确读取配置并启动
"""

import sys
import os
import yaml
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Optional

# 设置路径
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
SERVICES_DIR = PROJECT_ROOT / "services"

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

def load_config() -> Dict:
    """加载配置文件"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def test_service_scripts_exist():
    """测试服务启动脚本是否存在"""
    print("\n=== 测试1: 服务脚本存在性 ===")
    
    scripts = [
        "start_api_proxy.sh",
        "start_scoreflow_reward.sh",
        "stop_all_services.sh"
    ]
    
    all_exist = True
    for script in scripts:
        script_path = SERVICES_DIR / script
        if script_path.exists():
            colored_print(f"✓ 脚本存在: {script}", "green")
            # 检查是否可执行
            if os.access(script_path, os.X_OK):
                colored_print(f"  ✓ 脚本可执行", "green")
            else:
                colored_print(f"  ⚠ 脚本不可执行，需要运行: chmod +x {script_path}", "yellow")
        else:
            colored_print(f"✗ 脚本不存在: {script}", "red")
            all_exist = False
    
    return all_exist

def test_python_modules():
    """测试Python服务模块是否可导入"""
    print("\n=== 测试2: Python服务模块 ===")
    
    sys.path.insert(0, str(PROJECT_ROOT / "services"))
    sys.path.insert(0, str(PROJECT_ROOT / "scoreflow"))
    
    modules = [
        ("api_key_proxy", "API代理基础版"),
        ("api_key_proxy_enhanced", "API代理增强版"),
        ("scoreflow_reward_utils", "ScoreFlow工具模块"),
        ("scoreflow_reward_server", "ScoreFlow服务器模块")
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            colored_print(f"✓ {description} ({module_name}) 可导入", "green")
        except ImportError as e:
            colored_print(f"✗ {description} ({module_name}) 导入失败: {e}", "red")
            all_ok = False
        except Exception as e:
            colored_print(f"⚠ {description} ({module_name}) 导入时有警告: {e}", "yellow")
    
    return all_ok

def test_config_reading():
    """测试服务配置读取"""
    print("\n=== 测试3: 服务配置读取 ===")
    
    config = load_config()
    
    # 测试MetaGPT API代理配置
    api_proxy = config.get('services', {}).get('metagpt_api_proxy', {})
    if api_proxy:
        colored_print("✓ MetaGPT API代理配置可读取", "green")
        print(f"  - 端口: {api_proxy.get('port', 'N/A')}")
        print(f"  - 主机: {api_proxy.get('host', 'N/A')}")
        print(f"  - 目标URL: {api_proxy.get('target_url', 'N/A')}")
        
        # 检查target_api_key配置
        if api_proxy.get('target_api_key') and api_proxy.get('target_api_key') != 'your-target-api-key-here':
            colored_print("  ✓ 目标API密钥已配置", "green")
        else:
            colored_print("  ⚠ 目标API密钥未配置（使用透传模式）", "yellow")
    else:
        colored_print("✗ MetaGPT API代理配置缺失", "red")
        return False
    
    # 测试ScoreFlow Reward配置
    scoreflow = config.get('services', {}).get('scoreflow_reward', {})
    if scoreflow:
        colored_print("✓ ScoreFlow Reward配置可读取", "green")
        print(f"  - 端口: {scoreflow.get('port', 'N/A')}")
        print(f"  - 主机: {scoreflow.get('host', 'N/A')}")
        print(f"  - 超时: {scoreflow.get('timeout', 'N/A')}秒")
    else:
        colored_print("✗ ScoreFlow Reward配置缺失", "red")
        return False
    
    return True

def test_port_availability():
    """测试服务端口是否可用"""
    print("\n=== 测试4: 端口可用性 ===")
    
    config = load_config()
    
    ports_to_check = []
    
    # API代理端口
    api_proxy = config.get('services', {}).get('metagpt_api_proxy', {})
    if api_proxy.get('enabled'):
        ports_to_check.append(('MetaGPT API代理', api_proxy.get('port', 5009)))
    
    # ScoreFlow端口
    scoreflow = config.get('services', {}).get('scoreflow_reward', {})
    if scoreflow.get('enabled'):
        ports_to_check.append(('ScoreFlow Reward', scoreflow.get('port', 8899)))
    
    import socket
    
    all_available = True
    for service_name, port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            colored_print(f"⚠ 端口 {port} ({service_name}) 已被占用", "yellow")
            # 尝试检查是否是我们的服务
            try:
                if port == api_proxy.get('port', 5009):
                    resp = requests.get(f"http://localhost:{port}/", timeout=1)
                    colored_print(f"  可能是API代理服务正在运行", "blue")
                elif port == scoreflow.get('port', 8899):
                    resp = requests.get(f"http://localhost:{port}/health", timeout=1)
                    if resp.json().get('service') == 'scoreflow_reward_server':
                        colored_print(f"  是ScoreFlow Reward服务正在运行", "blue")
            except:
                pass
        else:
            colored_print(f"✓ 端口 {port} ({service_name}) 可用", "green")
    
    return all_available

def test_path_configurations():
    """测试路径配置的有效性"""
    print("\n=== 测试5: 路径配置有效性 ===")
    
    config = load_config()
    paths = config.get('paths', {})
    
    # 检查关键路径
    critical_paths = {
        'scoreflow_handlers': '需要存在（ScoreFlow处理器）',
        'benchmark_mapping': '需要存在（基准映射文件）'
    }
    
    all_valid = True
    for key, description in critical_paths.items():
        path_str = paths.get(key)
        if path_str:
            path = Path(path_str)
            if path.exists():
                colored_print(f"✓ {description}: {path_str}", "green")
            else:
                colored_print(f"✗ {description} 不存在: {path_str}", "red")
                all_valid = False
        else:
            colored_print(f"✗ {description} 未配置", "red")
            all_valid = False
    
    # 检查相对路径（应该在项目内）
    internal_paths = {
        'data_dir': '数据目录',
        'workspace': '工作空间目录'
    }
    
    for key, description in internal_paths.items():
        path_str = paths.get(key)
        if path_str:
            # 这些可以是相对路径
            colored_print(f"✓ {description} 已配置: {path_str}", "green")
        else:
            colored_print(f"⚠ {description} 未配置（将使用默认值）", "yellow")
    
    return all_valid

def test_service_dry_run():
    """测试服务启动脚本（干运行）"""
    print("\n=== 测试6: 服务脚本干运行 ===")
    
    # 测试脚本语法
    scripts = [
        "start_api_proxy.sh",
        "start_scoreflow_reward.sh"
    ]
    
    all_ok = True
    for script in scripts:
        script_path = SERVICES_DIR / script
        if script_path.exists():
            # 使用bash -n进行语法检查
            result = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                colored_print(f"✓ {script} 语法正确", "green")
            else:
                colored_print(f"✗ {script} 语法错误: {result.stderr}", "red")
                all_ok = False
        else:
            colored_print(f"⚠ {script} 不存在，跳过", "yellow")
    
    return all_ok

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    colored_print("服务启动配置测试", "blue")
    print("=" * 60)
    
    tests = [
        ("服务脚本存在性", test_service_scripts_exist),
        ("Python模块导入", test_python_modules),
        ("配置文件读取", test_config_reading),
        ("端口可用性", test_port_availability),
        ("路径配置有效性", test_path_configurations),
        ("脚本语法检查", test_service_dry_run)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            colored_print(f"✗ 测试 '{name}' 执行失败: {e}", "red")
            import traceback
            traceback.print_exc()
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
        colored_print("\n🎉 所有服务配置测试通过！", "green")
    else:
        colored_print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。", "yellow")
    
    # 提供启动建议
    print("\n" + "=" * 60)
    colored_print("服务启动建议", "blue")
    print("=" * 60)
    print("1. 启动MetaGPT API代理服务:")
    print("   cd services && ./start_api_proxy.sh")
    print("\n2. 启动ScoreFlow Reward服务:")
    print("   cd services && ./start_scoreflow_reward.sh")
    print("\n3. 停止所有服务:")
    print("   cd services && ./stop_all_services.sh")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)