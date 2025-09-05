#!/usr/bin/env python3
"""测试智谱API直接连接"""

import requests
import json

# 智谱API配置
API_KEY = "c91ea71f06e1cc8a1fce56b538df692b.vduU99R0C7MUn4ED"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 测试请求
test_payload = {
    "model": "glm-4-flash",  # 使用智谱的模型名称
    "messages": [
        {
            "role": "user",
            "content": "你好"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Test-Script/1.0"
}

print("="*60)
print("测试智谱API直接连接")
print("="*60)
print(f"URL: {API_URL}")
print(f"API Key: ***{API_KEY[-4:]}")
print(f"请求体:")
print(json.dumps(test_payload, indent=2, ensure_ascii=False))
print("-"*60)

try:
    print("发送请求中...")
    response = requests.post(
        API_URL,
        headers=headers,
        json=test_payload,
        timeout=30,
        verify=True  # 使用SSL验证
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ 连接成功!")
        result = response.json()
        print("响应内容:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 请求失败!")
        print(f"错误响应: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接错误: {e}")
    print("可能的原因:")
    print("1. API密钥无效")
    print("2. 网络连接问题")
    print("3. API服务不可用")
    
except Exception as e:
    print(f"❌ 其他错误: {type(e).__name__}: {e}")

print("="*60)