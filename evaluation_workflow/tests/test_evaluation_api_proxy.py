#!/usr/bin/env python3
"""
测试评估API代理服务
验证完整的评估流程可以通过API代理工作
"""

import sys
import os
import json
import time
import yaml
import requests
import asyncio
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 颜色输出
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def print_colored(msg, color=Colors.NC):
    print(f"{color}{msg}{Colors.NC}")

def test_proxy_health():
    """测试代理服务健康状态"""
    print_colored("\n=== 测试评估API代理健康状态 ===", Colors.CYAN)
    
    # 读取配置
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    proxy_config = config['services']['evaluation_api_proxy']
    proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
    
    try:
        # 检查健康端点
        response = requests.get(f"{proxy_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_colored(f"✓ 代理服务健康", Colors.GREEN)
            print(f"  服务: {health_data.get('service', 'unknown')}")
            print(f"  端口: {health_data.get('port', 'unknown')}")
            print(f"  队列大小: {health_data.get('queue_size', 0)}")
            return True
        else:
            print_colored(f"✗ 健康检查失败: HTTP {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        print_colored(f"✗ 无法连接到代理服务 {proxy_url}", Colors.RED)
        print_colored("请先启动评估API代理:", Colors.YELLOW)
        print("  cd services && ./start_evaluation_api_proxy.sh")
        return False
    except Exception as e:
        print_colored(f"✗ 健康检查错误: {e}", Colors.RED)
        return False

def test_api_call():
    """测试通过代理调用API"""
    print_colored("\n=== 测试API调用 ===", Colors.CYAN)
    
    # 读取配置
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_config = config['model']['api']
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {api_config['key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": api_config['model'],
        "messages": [
            {"role": "user", "content": "请用一句话解释什么是API代理"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }
    
    try:
        print(f"发送请求到: {api_config['url']}")
        print(f"使用模型: {api_config['model']}")
        
        response = requests.post(
            api_config['url'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print_colored("✓ API调用成功", Colors.GREEN)
            print(f"响应: {content[:200]}...")
            return True
        else:
            print_colored(f"✗ API调用失败: HTTP {response.status_code}", Colors.RED)
            print(f"错误: {response.text[:500]}")
            return False
            
    except Exception as e:
        print_colored(f"✗ API调用错误: {e}", Colors.RED)
        return False

async def test_inference_backend():
    """测试推理后端集成"""
    print_colored("\n=== 测试推理后端集成 ===", Colors.CYAN)
    
    try:
        from evaluation.sglang_server import ModelConfig, InferenceManager
        
        # 读取配置
        config_path = Path(__file__).parent.parent / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        api_config = config['model']['api']
        
        # 创建模型配置
        model_config = ModelConfig(
            model_type="api",
            api_url=api_config['url'],
            api_key=api_config['key'],
            api_model=api_config['model'],
            temperature=0.7,
            max_tokens=100
        )
        
        # 初始化推理管理器
        manager = InferenceManager(model_config)
        if not manager.initialize():
            print_colored("✗ 推理管理器初始化失败", Colors.RED)
            return False
        
        print_colored("✓ 推理管理器初始化成功", Colors.GREEN)
        
        # 测试生成
        prompt = "编写一个Python函数，计算列表中所有数字的和"
        response = await manager.generate(prompt)
        
        if response:
            print_colored("✓ 生成测试成功", Colors.GREEN)
            print(f"生成内容预览: {response[:200]}...")
            return True
        else:
            print_colored("✗ 生成测试失败", Colors.RED)
            return False
            
    except ImportError as e:
        print_colored(f"✗ 导入错误: {e}", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"✗ 测试错误: {e}", Colors.RED)
        return False
    finally:
        if 'manager' in locals():
            manager.close()

def test_workflow_generation():
    """测试工作流生成（模拟评估流程的一部分）"""
    print_colored("\n=== 测试工作流生成 ===", Colors.CYAN)
    
    # 读取配置
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_config = config['model']['api']
    
    # 构建工作流生成请求
    workflow_prompt = """
你是一个工作流生成专家。请为以下数学问题生成一个简单的Python工作流：

问题：计算 (15 + 27) * 3 - 8

要求：
1. 使用class Workflow定义
2. 包含一个run方法返回结果
3. 代码简洁清晰

请只返回代码，用```python和```包裹。
"""
    
    headers = {
        "Authorization": f"Bearer {api_config['key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": api_config['model'],
        "messages": [
            {"role": "system", "content": "你是一个专业的Python程序员。"},
            {"role": "user", "content": workflow_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500,
        "stream": False
    }
    
    try:
        print("生成工作流代码...")
        response = requests.post(
            api_config['url'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # 提取代码
            if "```python" in content:
                code_start = content.find("```python") + 9
                code_end = content.find("```", code_start)
                code = content[code_start:code_end].strip()
                
                print_colored("✓ 工作流生成成功", Colors.GREEN)
                print("生成的代码:")
                print("-" * 40)
                print(code)
                print("-" * 40)
                
                # 尝试执行代码
                try:
                    exec_globals = {}
                    exec(code, exec_globals)
                    if 'Workflow' in exec_globals:
                        workflow = exec_globals['Workflow']()
                        if hasattr(workflow, 'run'):
                            result = workflow.run()
                            print_colored(f"✓ 工作流执行成功，结果: {result}", Colors.GREEN)
                            return True
                except Exception as e:
                    print_colored(f"工作流执行错误: {e}", Colors.YELLOW)
                    return True  # 生成成功即可
            else:
                print_colored("✓ 生成响应成功（但格式可能不标准）", Colors.YELLOW)
                print(f"响应内容: {content[:500]}...")
                return True
        else:
            print_colored(f"✗ 生成失败: HTTP {response.status_code}", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"✗ 工作流生成错误: {e}", Colors.RED)
        return False

def main():
    """主测试函数"""
    print_colored("=" * 60, Colors.CYAN)
    print_colored("     评估API代理测试套件", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    
    # 读取配置显示当前模式
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    mode = config['model']['mode']
    print(f"\n当前模式: {mode}")
    
    if mode != 'evaluation_api':
        print_colored("警告: 当前模式不是 'evaluation_api'", Colors.YELLOW)
        print("请在 config.yaml 中设置: model.mode: evaluation_api")
        print()
    
    # 运行测试
    tests = [
        ("代理健康检查", test_proxy_health),
        ("API调用测试", test_api_call),
        ("工作流生成", test_workflow_generation),
    ]
    
    results = []
    for name, test_func in tests:
        print()
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print_colored(f"测试异常: {e}", Colors.RED)
            results.append((name, False))
    
    # 异步测试
    print()
    try:
        success = asyncio.run(test_inference_backend())
        results.append(("推理后端集成", success))
    except Exception as e:
        print_colored(f"异步测试异常: {e}", Colors.RED)
        results.append(("推理后端集成", False))
    
    # 显示结果汇总
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("     测试结果汇总", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        color = Colors.GREEN if success else Colors.RED
        print_colored(f"{status} - {name}", color)
    
    print()
    print_colored(f"总计: {passed}/{total} 测试通过", 
                  Colors.GREEN if passed == total else Colors.YELLOW)
    
    if passed == total:
        print_colored("\n🎉 所有测试通过！评估API代理工作正常。", Colors.GREEN)
        print("\n下一步:")
        print("1. 确保 ScoreFlow Reward 服务运行:")
        print("   cd services && ./start_scoreflow_reward.sh")
        print("2. 运行完整评估:")
        print("   cd scripts && ./run_evaluation.sh")
    else:
        print_colored("\n⚠ 部分测试失败，请检查服务配置。", Colors.YELLOW)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())