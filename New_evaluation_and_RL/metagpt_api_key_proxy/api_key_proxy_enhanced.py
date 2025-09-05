#!/usr/bin/env python3
# API代理服务 - 带速率限制和进度显示功能

import os
import sys
import json
import yaml
import requests
import time
import threading
import signal
from flask import Flask, request, Response, jsonify
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

# 加载配置文件
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    proxy_config = config.get('services', {}).get('metagpt_api_proxy', {})

# 配置参数
TARGET_URL = proxy_config.get('target_url')
TARGET_API_KEY = proxy_config.get('target_api_key')
HOST = proxy_config.get('host', 'localhost')
PORT = proxy_config.get('port', 5009)
RATE_PER_SECOND = float(proxy_config.get('rate_per_second', 1.0))
MAX_CONCURRENCY = int(proxy_config.get('max_concurrency', 20))  # 默认最大并发数为20
DEBUG_MODE = proxy_config.get('debug', False)

# 速率和并发限制器
class RateLimiter:
    """速率和并发限制器，控制请求发送频率和并发数"""
    def __init__(self, rate_per_second, max_concurrency):
        # 速率限制
        self.rate = rate_per_second
        self.interval = 1.0 / rate_per_second if rate_per_second > 0 else 0
        self.last_request_time = 0
        self.rate_lock = threading.Lock()
        
        # 并发限制
        self.max_concurrency = max_concurrency
        self.current_concurrency = 0
        self.concurrency_lock = threading.Lock()
        self.concurrency_condition = threading.Condition(self.concurrency_lock)
    
    def wait_if_needed(self):
        """同步等待函数（Flask路由中使用）- 包含速率和并发限制"""
        # 先检查并发限制
        with self.concurrency_condition:
            while self.current_concurrency >= self.max_concurrency:
                # 等待直到有空闲的并发槽位
                self.concurrency_condition.wait()
            # 获得并发槽位
            self.current_concurrency += 1
        
        # 再检查速率限制
        if self.interval > 0:
            with self.rate_lock:
                current_time = time.time()
                elapsed = current_time - self.last_request_time
                if elapsed < self.interval:
                    wait_time = self.interval - elapsed
                    time.sleep(wait_time)
                self.last_request_time = time.time()
    
    def release_concurrency(self):
        """释放一个并发槽位"""
        with self.concurrency_condition:
            self.current_concurrency -= 1
            self.concurrency_condition.notify()  # 通知等待的线程
    
    @property
    def queued_requests(self):
        """获取当前排队等待的请求数"""
        with self.concurrency_lock:
            # 通过检查等待的线程数来估算排队数
            return len(self.concurrency_condition._waiters) if hasattr(self.concurrency_condition, '_waiters') else 0

rate_limiter = RateLimiter(RATE_PER_SECOND, MAX_CONCURRENCY)

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
print(f"API代理服务启动中")
print(f"目标URL: {TARGET_URL}")
print(f"目标API密钥: ***{TARGET_API_KEY[-4:] if TARGET_API_KEY else '未配置'}")
print(f"监听地址: {HOST}:{PORT}")
print(f"速率限制: {RATE_PER_SECOND} req/s", end="")
if RATE_PER_SECOND < 1:
    print(f" (约{1.0/RATE_PER_SECOND:.1f}秒/请求)")
else:
    print()
print(f"并发限制: 最大 {MAX_CONCURRENCY} 个并发请求")
print(f"模式: {'调试模式 (显示详细信息)' if DEBUG_MODE else '正常模式 (仅显示进度和错误)'}")
print("="*60)
print()

# 创建进度条
if not DEBUG_MODE:
    pbar = tqdm(
        desc="API请求",
        unit="req",
        position=0,
        leave=True,
        ncols=120,  # 增加宽度以容纳更多信息
        total=0,  # 初始化为0，会在第一个请求时更新
        bar_format="{desc}: 完成{n_fmt}/总{total_fmt} |{bar}| {rate_fmt} [{postfix}]"
    )

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点 - 不转发到上游"""
    return jsonify({
        'status': 'healthy',
        'service': 'metagpt_api_proxy',
        'port': PORT,
        'target': TARGET_URL,
        'rate_limit': f'{RATE_PER_SECOND} req/s',
        'max_concurrency': MAX_CONCURRENCY
    }), 200

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request(path):
    """处理代理请求"""
    # 速率和并发限制
    rate_limiter.wait_if_needed()
    
    # 更新统计
    with stats_lock:
        request_stats["total"] += 1
        request_stats["in_progress"] += 1
    
    start_time = time.time()
    
    # Debug模式显示详细信息
    if DEBUG_MODE:
        print("\n" + "="*60)
        print("📥 收到客户端请求")
        print("="*60)
        
        # 判断请求来源
        if path == '':
            print("🔸 请求来源: 直接请求到 http://localhost:{} (无路径)".format(PORT))
            print("   可能是: curl 或其他直接HTTP请求")
        elif path == 'chat/completions':
            print("🔸 请求来源: 请求到 http://localhost:{}/chat/completions".format(PORT))
            print("   可能是: OpenAI Python客户端")
        else:
            print(f"🔸 请求来源: 请求到 http://localhost:{PORT}/{path}")
            print("   可能是: 其他客户端")
        
        print(f"请求方法: {request.method}")
        print(f"请求URL: {request.url}")
        print(f"请求路径: '{path}'")
        print(f"请求头: {dict(request.headers)}")
    else:
        # Normal模式：更新进度条
        if pbar is not None:
            # 获取排队数
            queued = rate_limiter.queued_requests
            # 总接收的请求数（包括正在处理和排队的）
            pbar.total = request_stats["total"]  
            # 已完成数 = 成功 + 失败
            pbar.n = request_stats["success"] + request_stats["failed"]
            pbar.set_description(f"并发: {rate_limiter.current_concurrency}/{MAX_CONCURRENCY} | 排队: {queued}")
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
        if key.lower() not in ['host', 'content-length', 'connection']:
            headers[key] = value
    
    # 添加目标API密钥
    if TARGET_API_KEY:
        headers['Authorization'] = f'Bearer {TARGET_API_KEY}'
    
    # 确保有正确的Content-Type（智谱API要求）
    if request.method == 'POST' and request_body:
        headers['Content-Type'] = 'application/json'
    
    # 添加User-Agent（某些API需要）
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'API-Proxy/1.0'
    
    # 决定最终的目标URL
    if TARGET_URL.endswith('/chat/completions'):
        final_url = TARGET_URL
        if DEBUG_MODE:
            print("\n📌 处理模式: 完整路径模式")
            print(f"   配置的target_url已包含/chat/completions")
            print(f"   忽略客户端路径 '{path}'，直接使用完整URL")
    elif TARGET_URL.endswith('/v1') or TARGET_URL.endswith('/v4'):
        # 支持OpenAI格式(/v1)和智谱格式(/v4)
        if path:
            final_url = f"{TARGET_URL}/{path}"
        else:
            final_url = f"{TARGET_URL}/chat/completions"
        if DEBUG_MODE:
            print("\n📌 处理模式: 基础URL模式")
            print(f"   配置的target_url是基础URL (v1或v4)")
            print(f"   拼接路径 '{path}' 到基础URL")
    else:
        final_url = TARGET_URL
        if DEBUG_MODE:
            print("\n⚠️ 处理模式: 直接转发模式")
            print(f"   无法识别URL格式，直接使用配置的target_url")
    
    if DEBUG_MODE:
        print("\n" + "-"*40)
        print("📤 转发请求到上游API")
        print("-"*40)
        print(f"最终URL: {final_url}")
        print(f"请求方法: {request.method}")
    
    try:
        # 发送请求到上游API
        # 智谱API需要启用SSL验证
        response = requests.request(
            method=request.method,
            url=final_url,
            headers=headers,
            params=request.args,
            data=request_body,
            timeout=600,
            verify=True,  # 智谱API需要SSL验证
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
            print("📥 收到上游API响应")
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
            print(f"✅ 返回给客户端: 状态码 {response.status_code}")
            print("="*60)
        else:
            # Normal模式：仅显示错误
            if response.status_code != 200:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"\n❌ 错误响应 [{timestamp}]")
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
                    "并发": rate_limiter.current_concurrency,
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
                try:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                finally:
                    # 流式响应结束后释放并发槽位
                    rate_limiter.release_concurrency()
            
            return Response(
                generate(),
                status=response.status_code,
                headers=filtered_headers
            )
        else:
            # 非流式响应
            result = Response(
                response.content,
                status=response.status_code,
                headers=filtered_headers
            )
            # 释放并发槽位
            rate_limiter.release_concurrency()
            return result
        
    except requests.exceptions.ConnectionError as e:
        # 连接错误的详细处理
        rate_limiter.release_concurrency()
        
        with stats_lock:
            request_stats["failed"] += 1
            request_stats["in_progress"] -= 1
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n❌ 连接错误 [{timestamp}]")
        print(f"   目标URL: {final_url}")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        print(f"   请求头: Authorization=***{TARGET_API_KEY[-4:] if TARGET_API_KEY else 'None'}")
        print(f"   可能原因:")
        print(f"   1. API密钥无效或格式错误")
        print(f"   2. URL路径不正确")
        print(f"   3. 网络连接问题")
        print(f"   4. API服务暂时不可用")
        
        if not DEBUG_MODE and pbar is not None:
            pbar.set_postfix({
                "成功": request_stats["success"],
                "失败": request_stats["failed"],
                "并发": rate_limiter.current_concurrency
            })
            pbar.update()
        
        error_response = {
            "error": {
                "message": f"连接错误: 无法连接到智谱API - {str(e)}",
                "type": "ConnectionError",
                "details": "请检查API密钥和网络连接"
            }
        }
        
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            status=502,  # Bad Gateway
            content_type='application/json'
        )
    
    except Exception as e:
        # 其他异常的处理
        rate_limiter.release_concurrency()
        
        with stats_lock:
            request_stats["failed"] += 1
            request_stats["in_progress"] -= 1
        
        # 所有模式都显示异常
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n❌ 代理错误 [{timestamp}]: {type(e).__name__}: {str(e)}")
        
        if not DEBUG_MODE and pbar is not None:
            pbar.set_postfix({
                "成功": request_stats["success"],
                "失败": request_stats["failed"],
                "并发": rate_limiter.current_concurrency
            })
            pbar.update()
        
        error_response = {
            "error": {
                "message": f"代理错误: {str(e)}",
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
    print("\n\n正在关闭服务...")
    if pbar is not None:
        pbar.close()
    
    # 显示最终统计
    print("\n" + "="*60)
    print("服务统计")
    print("="*60)
    elapsed = time.time() - request_stats["start_time"]
    print(f"运行时间: {elapsed:.1f}秒")
    print(f"总接收请求数: {request_stats['total']}")
    print(f"已完成: {request_stats['success'] + request_stats['failed']} (成功: {request_stats['success']}, 失败: {request_stats['failed']})")
    print(f"未完成: {request_stats['in_progress']}")
    print(f"最大并发数: {MAX_CONCURRENCY}")
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
    
    print(f"\n🚀 Flask服务器启动在 {HOST}:{PORT}")
    print("按 Ctrl+C 停止服务\n")
    
    # 关闭Flask的日志输出（在normal模式下）
    if not DEBUG_MODE:
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)