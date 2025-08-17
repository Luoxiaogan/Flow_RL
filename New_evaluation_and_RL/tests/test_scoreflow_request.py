#!/usr/bin/env python3
# Test script to simulate ScoreFlow's request format to API proxy

import os
import sys
import asyncio
import json
import httpx
import requests
from openai import AsyncOpenAI

# 设置NO_PROXY来排除localhost（防止被Clash等系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除所有代理环境变量
print("="*60)
print("代理配置处理")
print("="*60)
print(f"设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}'")
print("localhost请求将绕过所有代理\n")

for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        print(f"删除环境变量: {proxy_var} = {os.environ[proxy_var]}")
        del os.environ[proxy_var]
    else:
        print(f"环境变量 {proxy_var} 未设置")
print()

async def test_with_httpx_root():
    """使用httpx直接请求根路径（模拟curl）"""
    print("\n" + "="*60)
    print("测试1: 使用httpx请求根路径 (模拟curl)")
    print("="*60)
    
    url = "http://localhost:5009"
    request_data = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": "Hello from httpx root"}],
        "max_tokens": 10
    }
    
    print(f"🔸 请求URL: {url}")
    print(f"🔸 请求方法: POST")
    print(f"🔸 请求体:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # 明确禁用代理
            client._proxies = {}
            
            response = await client.post(
                url,
                json=request_data,
                headers={
                    "Authorization": "Bearer sk-placeholder",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"\n✅ 响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应内容:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_with_httpx_full_path():
    """使用httpx请求完整路径（模拟OpenAI客户端）"""
    print("\n" + "="*60)
    print("测试2: 使用httpx请求完整路径 (模拟OpenAI客户端)")
    print("="*60)
    
    url = "http://localhost:5009/chat/completions"
    request_data = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": "Hello from httpx full path"}],
        "max_tokens": 10
    }
    
    print(f"🔸 请求URL: {url}")
    print(f"🔸 请求方法: POST")
    print(f"🔸 请求体:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # 明确禁用代理
            client._proxies = {}
            
            response = await client.post(
                url,
                json=request_data,
                headers={
                    "Authorization": "Bearer sk-placeholder",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"\n✅ 响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应内容:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

def test_with_requests():
    """使用requests库测试（同步）"""
    print("\n" + "="*60)
    print("测试3: 使用requests库 (同步)")
    print("="*60)
    
    # 测试根路径
    url = "http://localhost:5009"
    request_data = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": "Hello from requests"}],
        "max_tokens": 10
    }
    
    print(f"🔸 请求URL: {url}")
    print(f"🔸 请求方法: POST")
    
    try:
        response = requests.post(
            url,
            json=request_data,
            headers={
                "Authorization": "Bearer sk-placeholder",
                "Content-Type": "application/json"
            },
            timeout=30,
            verify=False,
            proxies={}  # 明确禁用代理
        )
        
        print(f"\n✅ 响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {str(e)}")

async def test_with_openai_client():
    """使用OpenAI客户端测试（带调试）"""
    print("\n" + "="*60)
    print("测试4: 使用OpenAI客户端 (带调试)")
    print("="*60)
    
    try:
        # 创建自定义的httpx客户端，明确禁用代理
        custom_http_client = httpx.AsyncClient(
            timeout=30.0,
            verify=False,
            proxies={},  # 明确禁用代理
            transport=httpx.AsyncHTTPTransport(retries=0)
        )
        
        # 使用自定义http客户端创建OpenAI客户端
        client = AsyncOpenAI(
            api_key="sk-placeholder-will-be-replaced-by-proxy",
            base_url="http://localhost:5009",
            http_client=custom_http_client
        )
        
        print(f"🔸 OpenAI客户端配置:")
        print(f"   - base_url: {client.base_url}")
        print(f"   - api_key: {client.api_key[:20]}...")
        print(f"   - 预期请求URL: {client.base_url}chat/completions")
        
        response = await client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": "Hello from OpenAI client"}],
            temperature=0.3,
            max_tokens=10,
            stream=False
        )
        
        print(f"\n✅ 成功!")
        print(f"响应: {response.choices[0].message.content}")
        print(f"Token使用: {response.usage}")
        
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {str(e)}")
        
        # 尝试获取更多错误信息
        if hasattr(e, '__dict__'):
            print("\n错误详情:")
            for key, value in e.__dict__.items():
                print(f"  {key}: {value}")
        
        import traceback
        traceback.print_exc()

async def test_network_connectivity():
    """测试网络连接性"""
    print("\n" + "="*60)
    print("测试0: 网络连接性测试")
    print("="*60)
    
    # 测试localhost:5009是否可达
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:5009")
            print(f"✅ localhost:5009 可达，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ localhost:5009 不可达: {e}")
    
    # 检查端口监听
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5009))
        sock.close()
        if result == 0:
            print("✅ 端口5009正在监听")
        else:
            print("❌ 端口5009未监听")
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")

if __name__ == "__main__":
    print("ScoreFlow请求格式测试 (增强版)")
    print("="*60)
    print("注意: 确保API代理正在 localhost:5009 运行")
    print()
    
    # 先测试网络连接
    asyncio.run(test_network_connectivity())
    
    # 测试不同的请求方式
    asyncio.run(test_with_httpx_root())
    asyncio.run(test_with_httpx_full_path())
    test_with_requests()
    asyncio.run(test_with_openai_client())
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)