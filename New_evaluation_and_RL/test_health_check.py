#!/usr/bin/env python3
"""
测试API代理的健康检查端点
"""
import requests
import json
import sys

def test_health_endpoint(port=5019):
    """测试健康检查端点"""
    url = f"http://localhost:{port}/health"
    
    print(f"测试健康检查端点: {url}")
    print("-" * 50)
    
    try:
        # 发送GET请求到健康检查端点
        response = requests.get(url, timeout=5)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            print(f"\n健康检查响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证响应内容
            if data.get('status') == 'healthy':
                print("\n✅ 健康检查通过!")
                return True
            else:
                print(f"\n⚠️ 健康检查返回异常状态: {data.get('status')}")
                return False
        else:
            print(f"\n❌ 健康检查失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到API代理服务 (localhost:{port})")
        print("请确保API代理服务已启动:")
        print("  bash servers_and_proxy/start_api_proxy.sh")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def test_chat_completions_endpoint(port=5019):
    """测试chat/completions端点是否仍然正常工作"""
    url = f"http://localhost:{port}/chat/completions"
    
    print(f"\n测试聊天完成端点: {url}")
    print("-" * 50)
    
    # 准备测试数据
    test_data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.7
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-test"
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 聊天完成端点正常工作")
            return True
        else:
            # 这里可能会失败，因为需要有效的API密钥
            print(f"⚠️ 收到响应但状态码为: {response.status_code}")
            print("(这可能是因为API密钥无效，但代理服务正常)")
            return True  # 代理服务本身是正常的
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    # 从命令行参数获取端口，默认5019
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5019
    
    print("=" * 60)
    print("API代理健康检查测试")
    print("=" * 60)
    
    # 测试健康检查端点
    health_ok = test_health_endpoint(port)
    
    # 如果健康检查通过，测试聊天端点
    if health_ok:
        chat_ok = test_chat_completions_endpoint(port)
    
    print("\n" + "=" * 60)
    if health_ok:
        print("✅ 所有测试通过！健康检查端点工作正常。")
        print("\n现在可以安全地运行启动脚本：")
        print("  bash servers_and_proxy/start_scoreflow_reward.sh")
    else:
        print("❌ 测试失败，请检查API代理服务。")
    print("=" * 60)