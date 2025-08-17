#!/usr/bin/env python3
# API代理服务 - 评估模型专用版本（硬编码使用evaluation_api_proxy配置）

import os
import sys
import json
import yaml
import requests
import time
import threading
import signal
from flask import Flask, request, Response
from pathlib import Path
from tqdm import tqdm
from collections import deque
from datetime import datetime

# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除可能存在的代理设置（仅对本进程有效）
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]

# 加载配置文件 - 硬编码使用evaluation_api_proxy配置节
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    proxy_config = config.get('services', {}).get('evaluation_api_proxy', {})

# 配置参数
TARGET_URL = proxy_config.get('target_url')
TARGET_API_KEY = proxy_config.get('target_api_key')
HOST = proxy_config.get('host', 'localhost')
PORT = proxy_config.get('port', 5010)
RATE_PER_SECOND = float(proxy_config.get('rate_per_second', 3.0))
DEBUG_MODE = proxy_config.get('debug', False)

# 速率限制器
class RateLimiter:
    """速率限制器，控制请求发送频率"""
    def __init__(self, rate_per_second):
        self.rate = rate_per_second
        self.interval = 1.0 / rate_per_second if rate_per_second > 0 else 0
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """同步等待函数（Flask路由中使用）"""
        if self.interval > 0:
            with self.lock:
                current_time = time.time()
                elapsed = current_time - self.last_request_time
                if elapsed < self.interval:
                    wait_time = self.interval - elapsed
                    time.sleep(wait_time)
                self.last_request_time = time.time()

rate_limiter = RateLimiter(RATE_PER_SECOND)

# 请求统计
request_stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "in_progress": 0,
    "start_time": time.time(),
    "response_times": deque(maxlen=100)
}
stats_lock = threading.Lock()

# 进度条（仅在非debug模式）
pbar = None

# 启动信息
print("="*60)
print(f"评估API代理服务启动中")
print(f"配置节: evaluation_api_proxy")
print(f"目标URL: {TARGET_URL}")
print(f"目标API密钥: ***{TARGET_API_KEY[-4:] if TARGET_API_KEY else '未配置'}")
print(f"监听地址: {HOST}:{PORT}")
print(f"速率限制: {RATE_PER_SECOND} req/s", end="")
if RATE_PER_SECOND < 1:
    print(f" (约{1.0/RATE_PER_SECOND:.1f}秒/请求)")
else:
    print()
print(f"模式: {'调试模式 (显示详细信息)' if DEBUG_MODE else '正常模式 (仅显示进度和错误)'}")
print("="*60)
print()

# 创建进度条
if not DEBUG_MODE:
    pbar = tqdm(
        desc="评估API请求",
        unit="req",
        position=0,
        leave=True,
        ncols=100,
        total=0,  # 初始化为0，会在第一个请求时更新
        bar_format="{desc}: {n_fmt}/{total_fmt} |{bar}| {rate_fmt} [{postfix}]"
    )

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request(path):
    """处理代理请求"""
    # 速率限制
    rate_limiter.wait_if_needed()
    
    # 更新统计
    with stats_lock:
        request_stats["total"] += 1
        request_stats["in_progress"] += 1
    
    start_time = time.time()
    
    # Debug模式显示详细信息
    if DEBUG_MODE:
        print("\n" + "="*60)
        print("📥 收到评估模型请求")
        print("="*60)
        
        # 判断请求来源
        if path == '':
            print("🔸 请求来源: 直接请求到 http://localhost:{} (无路径)".format(PORT))
            print("   可能是: curl 或其他直接HTTP请求")
        elif path == 'chat/completions':
            print("🔸 请求来源: 请求到 http://localhost:{}/chat/completions".format(PORT))
            print("   可能是: evaluation_runner.py")
        else:
            print(f"🔸 请求来源: 请求到 http://localhost:{PORT}/{path}")
            print("   可能是: 其他评估客户端")
        
        print(f"请求方法: {request.method}")
        print(f"请求URL: {request.url}")
        print(f"请求路径: '{path}'")
        print(f"请求头: {dict(request.headers)}")
    else:
        # Normal模式：更新进度条
        if pbar is not None:
            pbar.total = request_stats["total"]
            pbar.n = request_stats["success"] + request_stats["failed"]
            pbar.set_description(f"评估处理中: {request_stats['in_progress']}")
            pbar.refresh()
    
    # 获取请求体
    request_body = request.get_data()
    if DEBUG_MODE and request_body:
        try:
            body_json = json.loads(request_body)
            print(f"请求体 (JSON格式):")
            print(json.dumps(body_json, indent=2, ensure_ascii=False))
        except:
            print(f"请求体 (原始数据): {request_body[:500]}...")
    
    # 准备转发请求的头部
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value
    
    # 添加目标API密钥
    if TARGET_API_KEY:
        headers['Authorization'] = f'Bearer {TARGET_API_KEY}'
    
    # 决定最终的目标URL
    if TARGET_URL.endswith('/chat/completions'):
        final_url = TARGET_URL
        if DEBUG_MODE:
            print("\n📌 处理模式: 完整路径模式")
            print(f"   配置的target_url已包含/chat/completions")
            print(f"   忽略客户端路径 '{path}'，直接使用完整URL")
    elif TARGET_URL.endswith('/v1'):
        if path:
            final_url = f"{TARGET_URL}/{path}"
        else:
            final_url = f"{TARGET_URL}/chat/completions"
        if DEBUG_MODE:
            print("\n📌 处理模式: 基础URL模式")
            print(f"   配置的target_url是基础URL")
            print(f"   拼接路径 '{path}' 到基础URL")
    else:
        final_url = TARGET_URL
        if DEBUG_MODE:
            print("\n⚠️ 处理模式: 直接转发模式")
            print(f"   无法识别URL格式，直接使用配置的target_url")
    
    if DEBUG_MODE:
        print("\n" + "-"*40)
        print("📤 转发请求到上游评估API")
        print("-"*40)
        print(f"最终URL: {final_url}")
        print(f"请求方法: {request.method}")
    
    try:
        # 发送请求到上游API
        response = requests.request(
            method=request.method,
            url=final_url,
            headers=headers,
            params=request.args,
            data=request_body,
            timeout=60,
            verify=False,
            stream=True  # 使用流式响应
        )
        
        response_time = time.time() - start_time
        
        # 更新统计
        with stats_lock:
            request_stats["response_times"].append(response_time)
            if response.status_code == 200:
                request_stats["success"] += 1
            else:
                request_stats["failed"] += 1
            request_stats["in_progress"] -= 1
        
        # 根据模式输出
        if DEBUG_MODE:
            # Debug模式：显示所有响应
            print("\n" + "-"*40)
            print("📥 收到上游评估API响应")
            print("-"*40)
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {response_time:.2f}秒")
            print(f"响应头: {dict(response.headers)}")
            
            # 显示响应内容预览
            if response.headers.get('Content-Type', '').startswith('text/event-stream'):
                print("响应体 (流式数据): [实时传输中...]")
            else:
                # 读取前500字节作为预览
                content_preview = response.content[:500]
                try:
                    json_preview = json.loads(content_preview)
                    print(f"响应体 (JSON格式):")
                    print(json.dumps(json_preview, indent=2, ensure_ascii=False))
                except:
                    print(f"响应体 (原始数据): {content_preview.decode('utf-8', errors='ignore')}...")
            
            print("\n" + "-"*40)
            print(f"✅ 返回给评估客户端: 状态码 {response.status_code}")
            print("="*60)
        else:
            # Normal模式：仅显示错误
            if response.status_code != 200:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"\n❌ 评估API错误响应 [{timestamp}]")
                print(f"   状态码: {response.status_code}")
                print(f"   URL: {final_url}")
                print(f"   响应时间: {response_time:.2f}秒")
                try:
                    error_text = response.text[:200]
                    print(f"   响应: {error_text}...")
                except:
                    print(f"   响应: [无法解析]")
            
            # 更新进度条
            if pbar is not None:
                avg_time = sum(request_stats["response_times"]) / len(request_stats["response_times"]) if request_stats["response_times"] else 0
                pbar.set_postfix({
                    "成功": request_stats["success"],
                    "失败": request_stats["failed"],
                    "平均响应": f"{avg_time:.1f}s"
                })
                pbar.update()
        
        # 过滤响应头
        filtered_headers = {}
        skip_headers = ['transfer-encoding', 'content-encoding', 'content-length', 'connection']
        for key, value in response.headers.items():
            if key.lower() not in skip_headers:
                filtered_headers[key] = value
        
        # 对于流式响应，直接传递
        if response.headers.get('Content-Type', '').startswith('text/event-stream'):
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            return Response(
                generate(),
                status=response.status_code,
                headers=filtered_headers
            )
        else:
            # 非流式响应
            return Response(
                response.content,
                status=response.status_code,
                headers=filtered_headers
            )
        
    except Exception as e:
        with stats_lock:
            request_stats["failed"] += 1
            request_stats["in_progress"] -= 1
        
        # 所有模式都显示异常
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n❌ 评估代理错误 [{timestamp}]: {type(e).__name__}: {str(e)}")
        
        if not DEBUG_MODE and pbar is not None:
            pbar.set_postfix({
                "成功": request_stats["success"],
                "失败": request_stats["failed"]
            })
            pbar.update()
        
        error_response = {
            "error": {
                "message": f"评估代理错误: {str(e)}",
                "type": type(e).__name__
            }
        }
        
        return Response(
            json.dumps(error_response),
            status=500,
            content_type='application/json'
        )

def shutdown_handler(signum, frame):
    """优雅关闭处理"""
    print("\n\n正在关闭评估API代理服务...")
    if pbar is not None:
        pbar.close()
    
    # 显示最终统计
    print("\n" + "="*60)
    print("评估API代理服务统计")
    print("="*60)
    elapsed = time.time() - request_stats["start_time"]
    print(f"运行时间: {elapsed:.1f}秒")
    print(f"总请求数: {request_stats['total']}")
    print(f"成功: {request_stats['success']}")
    print(f"失败: {request_stats['failed']}")
    if request_stats["response_times"]:
        avg_time = sum(request_stats["response_times"]) / len(request_stats["response_times"])
        print(f"平均响应时间: {avg_time:.2f}秒")
    print("="*60)
    
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print(f"\n🚀 评估API代理服务器启动在 {HOST}:{PORT}")
    print("按 Ctrl+C 停止服务\n")
    
    # 关闭Flask的日志输出（在normal模式下）
    if not DEBUG_MODE:
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)