#!/usr/bin/env python3
"""
API代理服务 - 多API池负载均衡版本
支持Round-Robin分发请求到多个API endpoint
"""

import os
import sys
import json
import yaml
import requests
import time
import threading
import signal
import itertools
from flask import Flask, request, Response, jsonify
from pathlib import Path
from tqdm import tqdm
from collections import deque
from datetime import datetime
from typing import List, Dict, Any, Optional

# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除可能存在的代理设置（仅对本进程有效）
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"
API_POOL_CONFIG_FILE = Path(__file__).parent / "api_pool_config.yaml"

def load_configs():
    """加载主配置和API池配置"""
    # 加载主配置文件（只读取基础配置）
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        proxy_config = config.get('services', {}).get('metagpt_api_proxy', {})

    # 加载API池配置文件（包含速率和并发限制）
    api_pool = []
    if API_POOL_CONFIG_FILE.exists():
        try:
            with open(API_POOL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                pool_config = yaml.safe_load(f)
                api_pool = pool_config.get('api_pool', [])

                # 验证每个API配置的完整性
                for i, api in enumerate(api_pool):
                    if 'rate_per_second' not in api:
                        api['rate_per_second'] = 4.0  # 默认值
                    if 'max_concurrency' not in api:
                        api['max_concurrency'] = 20   # 默认值
                    # 添加模型参数的默认值
                    if 'model' not in api:
                        api['model'] = 'qwen-turbo'  # 默认模型
                    if 'temperature' not in api:
                        api['temperature'] = 0.9     # 默认温度
                    if 'max_tokens' not in api:
                        api['max_tokens'] = 4096     # 默认最大token数

                    # 类型转换
                    api['rate_per_second'] = float(api['rate_per_second'])
                    api['max_concurrency'] = int(api['max_concurrency'])
                    api['temperature'] = float(api['temperature'])
                    api['max_tokens'] = int(api['max_tokens'])

                print(f"✅ 加载API池配置: {API_POOL_CONFIG_FILE}")
                print(f"   发现 {len(api_pool)} 个API endpoints")
                # 计算总吞吐量
                total_rate = sum(api['rate_per_second'] for api in api_pool)
                print(f"   总吞吐量: {total_rate:.1f} req/s")
        except Exception as e:
            print(f"⚠️ 无法加载API池配置: {e}")

    # 如果没有API池配置，回退到主配置中的单个API
    if not api_pool:
        target_url = proxy_config.get('target_url')
        target_api_key = proxy_config.get('target_api_key')
        if target_url and target_api_key:
            # 使用主配置中的速率限制作为默认值
            api_pool = [{
                'target_url': target_url,
                'target_api_key': target_api_key,
                'rate_per_second': float(proxy_config.get('rate_per_second', 4.0)),
                'max_concurrency': int(proxy_config.get('max_concurrency', 20)),
                'model': 'qwen-turbo',         # 默认模型参数
                'temperature': 0.9,
                'max_tokens': 4096
            }]
            print(f"⚠️ 使用主配置文件中的单个API endpoint")
        else:
            raise ValueError("没有找到有效的API配置")

    return proxy_config, api_pool

# 加载配置
proxy_config, API_POOL = load_configs()

# 从主配置只读取基础参数（端口、主机、调试模式）
HOST = proxy_config.get('host', 'localhost')
PORT = proxy_config.get('port', 5059)
DEBUG_MODE = proxy_config.get('debug', False)
# 注意：rate_per_second和max_concurrency现在从API池配置中读取

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

# 负载均衡器
class LoadBalancer:
    """Round-Robin负载均衡器（每个API有独立的速率限制）"""
    def __init__(self, api_pool: List[Dict]):
        self.api_pool = api_pool
        self.pool_size = len(api_pool)
        self.api_cycle = itertools.cycle(range(self.pool_size))
        self.current_index = 0
        self.index_lock = threading.Lock()

        # 为每个API创建独立的速率限制器
        self.rate_limiters = [
            RateLimiter(
                api.get('rate_per_second', 4.0),
                api.get('max_concurrency', 20)
            )
            for api in api_pool
        ]

        # 每个API的统计信息
        self.api_stats = [
            {
                "success": 0,
                "failed": 0,
                "total": 0,
                "last_used": None,
                "response_times": deque(maxlen=20),
                "rate_limit": api.get('rate_per_second', 4.0),
                "max_concurrency": api.get('max_concurrency', 20)
            }
            for api in api_pool
        ]
        self.stats_lock = threading.Lock()

    def get_next_api(self) -> tuple[int, Dict]:
        """获取下一个API（Round-Robin）"""
        with self.index_lock:
            api_index = next(self.api_cycle)
            return api_index, self.api_pool[api_index]

    def update_stats(self, api_index: int, success: bool, response_time: float = None):
        """更新API统计信息"""
        with self.stats_lock:
            stats = self.api_stats[api_index]
            stats["total"] += 1
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            stats["last_used"] = datetime.now()
            if response_time:
                stats["response_times"].append(response_time)

    def get_stats_summary(self) -> str:
        """获取统计摘要"""
        with self.stats_lock:
            lines = []
            for i, stats in enumerate(self.api_stats):
                api_key = self.api_pool[i]['target_api_key']
                key_suffix = api_key[-4:] if api_key else 'None'
                success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
                avg_time = sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0
                rate_limiter = self.rate_limiters[i]
                lines.append(
                    f"  API #{i+1} (***{key_suffix}): "
                    f"成功率={success_rate:.1f}% ({stats['success']}/{stats['total']}), "
                    f"平均响应={avg_time:.2f}s, "
                    f"速率={stats['rate_limit']}req/s, "
                    f"并发={rate_limiter.current_concurrency}/{stats['max_concurrency']}"
                )
            return "\n".join(lines)

# 创建负载均衡器（每个API有独立的限制）
load_balancer = LoadBalancer(API_POOL)

# 全局请求统计
request_stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "in_progress": 0,
    "start_time": time.time()
}
stats_lock = threading.Lock()

# 进度条（仅在非debug模式）
pbar = None

# 启动信息
print("="*60)
print(f"API代理服务启动中 (独立速率限制版本)")
print(f"监听地址: {HOST}:{PORT}")
print(f"API池大小: {len(API_POOL)} 个endpoints")
total_rate = 0
for i, api_config in enumerate(API_POOL):
    api_key = api_config['target_api_key']
    key_suffix = api_key[-4:] if api_key else 'None'
    rate = api_config.get('rate_per_second', 4.0)
    concurrency = api_config.get('max_concurrency', 20)
    total_rate += rate
    print(f"  API #{i+1} (***{key_suffix}): {rate}req/s, 并发{concurrency}")
print(f"负载均衡策略: Round-Robin (每个API独立限流)")
print(f"总吞吐量: {total_rate:.1f} req/s")
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
        ncols=140,  # 增加宽度以容纳更多信息
        total=0,
        bar_format="{desc}: 完成{n_fmt}/总{total_fmt} |{bar}| {rate_fmt} [{postfix}]"
    )

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点 - 不转发到上游"""
    # 计算总速率和总并发
    total_rate = sum(api.get('rate_per_second', 4.0) for api in API_POOL)
    total_max_concurrency = sum(api.get('max_concurrency', 20) for api in API_POOL)

    return jsonify({
        'status': 'healthy',
        'service': 'metagpt_api_proxy_pool',
        'port': PORT,
        'api_pool_size': len(API_POOL),
        'total_rate_limit': f'{total_rate:.1f} req/s',
        'total_max_concurrency': total_max_concurrency,
        'stats': {
            'total_requests': request_stats['total'],
            'success': request_stats['success'],
            'failed': request_stats['failed'],
            'in_progress': request_stats['in_progress']
        }
    }), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取详细统计信息"""
    elapsed = time.time() - request_stats["start_time"]
    # 收集每个API的并发状态
    api_concurrency_info = [
        {
            'api_index': i,
            'current_concurrency': load_balancer.rate_limiters[i].current_concurrency,
            'max_concurrency': API_POOL[i].get('max_concurrency', 20),
            'queued_requests': load_balancer.rate_limiters[i].queued_requests
        }
        for i in range(len(API_POOL))
    ]
    return jsonify({
        'uptime_seconds': elapsed,
        'global_stats': request_stats,
        'api_stats': load_balancer.api_stats,
        'api_concurrency_info': api_concurrency_info
    }), 200

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request(path):
    """处理代理请求"""
    # 获取下一个API（Round-Robin）
    api_index, api_config = load_balancer.get_next_api()
    target_url = api_config['target_url']
    target_api_key = api_config['target_api_key']

    # 使用该API的独立速率和并发限制
    load_balancer.rate_limiters[api_index].wait_if_needed()

    # 更新全局统计
    with stats_lock:
        request_stats["total"] += 1
        request_stats["in_progress"] += 1

    start_time = time.time()

    # Debug模式显示详细信息
    if DEBUG_MODE:
        print("\n" + "="*60)
        print("📥 收到客户端请求")
        print("="*60)
        print(f"🎯 选择API #{api_index + 1} (Round-Robin)")
        print(f"   URL: {target_url}")
        print(f"   Key: ***{target_api_key[-4:] if target_api_key else 'None'}")
        print(f"请求方法: {request.method}")
        print(f"请求路径: '{path}'")
    else:
        # Normal模式：更新进度条
        if pbar is not None:
            rate_limiter = load_balancer.rate_limiters[api_index]
            queued = rate_limiter.queued_requests
            max_conc = API_POOL[api_index].get('max_concurrency', 20)
            pbar.total = request_stats["total"]
            pbar.n = request_stats["success"] + request_stats["failed"]
            pbar.set_description(
                f"API#{api_index+1} | 并发: {rate_limiter.current_concurrency}/{max_conc} | 排队: {queued}"
            )
            pbar.refresh()

    # 获取请求体
    request_body = request.get_data()

    # 尝试解析并注入模型参数
    modified_body = request_body  # 默认使用原始请求体
    try:
        if request_body:
            body_json = json.loads(request_body)

            # 注入API配置中的模型参数（覆盖请求中的参数）
            body_json['model'] = api_config['model']
            body_json['temperature'] = api_config['temperature']
            body_json['max_tokens'] = api_config['max_tokens']

            if DEBUG_MODE:
                print(f"📝 注入模型参数:")
                print(f"   model: {api_config['model']}")
                print(f"   temperature: {api_config['temperature']}")
                print(f"   max_tokens: {api_config['max_tokens']}")

            # 重新序列化
            modified_body = json.dumps(body_json, ensure_ascii=False).encode('utf-8')

            if DEBUG_MODE:
                print(f"请求体 (JSON格式，已注入参数):")
                print(json.dumps(body_json, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        # 如果解析失败，使用原始请求体
        if DEBUG_MODE:
            print(f"⚠️ 无法解析请求体，使用原始数据: {e}")
            if request_body:
                print(f"请求体 (原始数据): {request_body[:500]}...")

    # 准备转发请求的头部
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length', 'connection']:
            headers[key] = value

    # 添加目标API密钥
    if target_api_key:
        headers['Authorization'] = f'Bearer {target_api_key}'

    # 确保有正确的Content-Type
    if request.method == 'POST' and request_body:
        headers['Content-Type'] = 'application/json'

    # 添加User-Agent
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'API-Proxy-Pool/1.0'

    # 决定最终的目标URL
    if target_url.endswith('/chat/completions'):
        final_url = target_url
    elif target_url.endswith('/v1') or target_url.endswith('/v4'):
        if path:
            final_url = f"{target_url}/{path}"
        else:
            final_url = f"{target_url}/chat/completions"
    else:
        final_url = target_url

    if DEBUG_MODE:
        print(f"最终URL: {final_url}")

    # 尝试发送请求，如果失败则尝试下一个API
    max_retries = 3  # 固定最多重试3次
    last_error = None
    last_status_code = None

    for retry in range(max_retries):
        if retry > 0:
            # 如果是重试，获取下一个API
            api_index, api_config = load_balancer.get_next_api()
            target_url = api_config['target_url']
            target_api_key = api_config['target_api_key']
            headers['Authorization'] = f'Bearer {target_api_key}'

            # 重新排队等待（关键！）
            load_balancer.rate_limiters[api_index].wait_if_needed()

            # 重新注入新API的模型参数
            try:
                if request_body:
                    body_json = json.loads(request_body)
                    # 使用新API的模型参数
                    body_json['model'] = api_config['model']
                    body_json['temperature'] = api_config['temperature']
                    body_json['max_tokens'] = api_config['max_tokens']
                    modified_body = json.dumps(body_json, ensure_ascii=False).encode('utf-8')

                    if DEBUG_MODE:
                        print(f"📝 重新注入API #{api_index + 1}的模型参数:")
                        print(f"   model: {api_config['model']}")
                        print(f"   temperature: {api_config['temperature']}")
                        print(f"   max_tokens: {api_config['max_tokens']}")
            except Exception as e:
                # 如果解析失败，使用原始请求体
                modified_body = request_body
                if DEBUG_MODE:
                    print(f"⚠️ 重试时无法重新注入参数: {e}")

            # 重新计算final_url
            if target_url.endswith('/chat/completions'):
                final_url = target_url
            elif target_url.endswith('/v1') or target_url.endswith('/v4'):
                if path:
                    final_url = f"{target_url}/{path}"
                else:
                    final_url = f"{target_url}/chat/completions"
            else:
                final_url = target_url

            if DEBUG_MODE:
                print(f"\n🔄 重试 #{retry} - 切换到API #{api_index + 1}")
                print(f"   URL: {target_url}")
                print(f"   原因: 上次返回状态码 {last_status_code}")
            else:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] 重试 #{retry}: API#{api_index+1} (上次状态码: {last_status_code})")

        try:
            # 发送请求到上游API
            response = requests.request(
                method=request.method,
                url=final_url,
                headers=headers,
                params=request.args,
                data=modified_body,  # 使用注入参数后的请求体
                timeout=600,
                verify=True,
                stream=True
            )

            response_time = time.time() - start_time

            # 检查响应状态码，决定是否重试
            if response.status_code != 200:
                last_status_code = response.status_code

                # 释放当前API的并发槽位（重要！）
                load_balancer.rate_limiters[api_index].release_concurrency()

                # 更新失败统计
                load_balancer.update_stats(api_index, False, response_time)

                # 输出错误信息
                if DEBUG_MODE:
                    print(f"\n❌ API #{api_index + 1} 返回非200状态码")
                    print(f"   状态码: {response.status_code}")
                    print(f"   响应时间: {response_time:.2f}秒")
                else:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] API#{api_index+1} 错误: 状态码 {response.status_code}")

                # 如果还有重试机会，继续下一轮
                if retry < max_retries - 1:
                    if DEBUG_MODE:
                        print(f"   准备重试...")
                    continue  # 继续下一轮重试
                else:
                    # 所有重试都失败了，返回最后的错误响应
                    with stats_lock:
                        request_stats["failed"] += 1
                        request_stats["in_progress"] -= 1

                    if pbar is not None:
                        pbar.set_postfix({
                            "成功": request_stats["success"],
                            "失败": request_stats["failed"]
                        })
                        pbar.update()

                    # 返回最后的错误响应
                    filtered_headers = {}
                    skip_headers = ['transfer-encoding', 'content-encoding', 'content-length', 'connection']
                    for key, value in response.headers.items():
                        if key.lower() not in skip_headers:
                            filtered_headers[key] = value

                    return Response(
                        response.content,
                        status=response.status_code,
                        headers=filtered_headers
                    )

            # 状态码200，成功响应
            load_balancer.update_stats(api_index, True, response_time)
            with stats_lock:
                request_stats["success"] += 1
                request_stats["in_progress"] -= 1

            # 输出成功信息
            if DEBUG_MODE:
                print(f"\n✅ API #{api_index + 1} 响应成功")
                print(f"状态码: {response.status_code}")
                print(f"响应时间: {response_time:.2f}秒")

            # 更新进度条
            if not DEBUG_MODE and pbar is not None:
                pbar.set_postfix({
                    "成功": request_stats["success"],
                    "失败": request_stats["failed"],
                    "API": f"#{api_index+1}"
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
                        load_balancer.rate_limiters[api_index].release_concurrency()

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
                load_balancer.rate_limiters[api_index].release_concurrency()
                return result

        except Exception as e:
            last_error = e

            # 释放当前API的并发槽位
            load_balancer.rate_limiters[api_index].release_concurrency()

            # 更新失败统计
            load_balancer.update_stats(api_index, False)

            timestamp = datetime.now().strftime('%H:%M:%S')
            if DEBUG_MODE:
                print(f"\n❌ API #{api_index + 1} 请求异常")
                print(f"   错误: {type(e).__name__}: {str(e)}")
            else:
                print(f"[{timestamp}] API#{api_index+1} 异常: {type(e).__name__}")

            if retry < max_retries - 1:
                if DEBUG_MODE:
                    print(f"   准备重试...")
                # 继续下一轮重试
                continue
            else:
                if DEBUG_MODE:
                    print(f"   所有重试失败")

    # 所有API都失败了（并发槽位已在重试循环中释放）

    with stats_lock:
        request_stats["failed"] += 1
        request_stats["in_progress"] -= 1

    if not DEBUG_MODE and pbar is not None:
        pbar.set_postfix({
            "成功": request_stats["success"],
            "失败": request_stats["failed"]
        })
        pbar.update()

    error_response = {
        "error": {
            "message": f"所有API请求失败: {str(last_error)}",
            "type": "AllAPIsFailed",
            "details": f"尝试了{max_retries}个API endpoints"
        }
    }

    return Response(
        json.dumps(error_response, ensure_ascii=False),
        status=502,
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
    print(f"总请求数: {request_stats['total']}")
    print(f"成功: {request_stats['success']}, 失败: {request_stats['failed']}")
    print(f"\nAPI池统计:")
    print(load_balancer.get_stats_summary())
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