#!/usr/bin/env python3
"""
API代理服务 - 多API池负载均衡版本（带请求监控）
支持Round-Robin分发请求到多个API endpoint
监控chat/completions请求，超时自动重启
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
import logging
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

# ========== 请求监控相关 ==========
last_request_time = time.time()  # 最后一次chat/completions请求时间
request_monitor_lock = threading.Lock()
restart_timeout = 180  # 默认180秒，会从配置文件读取
monitor_enabled = True  # 是否启用监控
monitor_thread = None

def update_last_request_time():
    """更新最后请求时间"""
    global last_request_time
    with request_monitor_lock:
        last_request_time = time.time()
        if not DEBUG_MODE:
            # print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 收到chat/completions请求")
            pass

def monitor_requests():
    """监控线程：检查是否超时"""
    global monitor_enabled
    print(f"[监控线程] 已启动，超时时间: {restart_timeout}秒")

    while monitor_enabled:
        time.sleep(1)  # 每1秒检查一次，更频繁地更新进度条

        with request_monitor_lock:
            idle_time = time.time() - last_request_time

        # 每秒更新进度条显示（如果存在）
        if pbar is not None and not DEBUG_MODE:
            with request_monitor_lock:
                idle_seconds = int(idle_time)
                last_time_str = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')

            # 更新进度条的后缀信息，但不增加计数
            with stats_lock:
                # 重要：更新total和n以显示进度条
                pbar.total = request_stats["total"]
                pbar.n = request_stats["success"] + request_stats["failed"]

                pbar.set_postfix_str(
                    f"成功={request_stats['success']}, "
                    f"失败={request_stats['failed']}, "
                    f"最后请求={last_time_str}, "
                    f"空闲={idle_seconds}s"
                )
                # 使用refresh而不是update，只刷新显示而不增加计数
                pbar.refresh()

        # 检查是否需要重启（每秒检查，但只在超时时触发）
        if idle_time >= restart_timeout:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  {restart_timeout}秒无chat/completions请求")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 触发自动重启...")

            # 可选：通知reward_server准备重启
            try:
                reward_notify_url = "http://localhost:7788/prepare_restart"
                requests.post(reward_notify_url, timeout=1)
                print(f"✓ 已通知Reward服务器准备重启")
            except Exception as e:
                # 忽略错误，reward_server可能未运行
                pass

            # 退出进程（返回码0表示正常重启）
            time.sleep(1)
            os._exit(0)

# ========== 原有的API池代码（从api_key_proxy_pool.py复制） ==========

def load_configs():
    """加载主配置和API池配置"""
    global restart_timeout

    # 加载主配置文件（只读取基础配置）
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        proxy_config = config.get('services', {}).get('metagpt_api_proxy', {})

        # 从scoreflow_reward配置读取restart_per_step
        scoreflow_config = config.get('services', {}).get('scoreflow_reward', {})
        restart_timeout = scoreflow_config.get('restart_per_step', 180)

    # 加载API池配置文件（包含速率和并发限制）
    api_pool = []
    if API_POOL_CONFIG_FILE.exists():
        try:
            with open(API_POOL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                pool_config = yaml.safe_load(f)
                api_pool = pool_config.get('api_pool', [])
                print(f"✅ 加载API池配置: {API_POOL_CONFIG_FILE}")
                print(f"   发现 {len(api_pool)} 个API endpoints")

                # 计算总吞吐量
                total_rate = sum(api.get('rate_per_second', 4.0) for api in api_pool)
                print(f"   总吞吐量: {total_rate} req/s")
        except Exception as e:
            print(f"⚠️ 加载API池配置失败: {e}")
            print(f"   将使用主配置文件中的单个API")
    else:
        print(f"⚠️ API池配置文件不存在: {API_POOL_CONFIG_FILE}")
        print(f"   将使用主配置文件中的单个API")

    # 如果没有API池配置，使用主配置中的单个API
    if not api_pool:
        api_pool = [{
            'target_url': proxy_config.get('target_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
            'target_api_key': proxy_config.get('target_api_key', ''),
            'rate_per_second': proxy_config.get('rate_per_second', 4.0),
            'max_concurrency': proxy_config.get('max_concurrency', 20),
            'model': proxy_config.get('model', 'qwen-turbo'),
            'temperature': proxy_config.get('temperature', 0.9),
            'max_tokens': proxy_config.get('max_tokens', 4096)
        }]
        print("   使用主配置文件中的单个API")

    return proxy_config, api_pool

# 加载配置
CONFIG, API_POOL = load_configs()

# 基础配置
HOST = CONFIG.get('host', 'localhost')
PORT = CONFIG.get('port', 5059)
DEBUG_MODE = CONFIG.get('debug', False)

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

# 创建负载均衡器
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

# 启动时创建进度条（如果需要）
def create_progress_bar():
    global pbar
    if not DEBUG_MODE:
        pbar = tqdm(
            desc="API请求",
            unit="req",
            position=0,
            leave=True,
            ncols=140,  # 增加宽度以容纳更多信息
            total=0,  # 初始为0，后续动态更新
            bar_format="{desc}: 完成{n_fmt}/总{total_fmt} |{bar}| {rate_fmt} [{postfix}]"
        )

# Flask应用
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-proxy-pool-monitor',
        'last_request': datetime.fromtimestamp(last_request_time).isoformat(),
        'idle_seconds': int(time.time() - last_request_time),
        'restart_timeout': restart_timeout
    })

@app.route('/last_activity', methods=['GET'])
def last_activity():
    """获取最后活动时间（用于调试）"""
    idle = time.time() - last_request_time
    return jsonify({
        'last_request_time': datetime.fromtimestamp(last_request_time).isoformat(),
        'idle_seconds': int(idle),
        'restart_in': max(0, restart_timeout - int(idle))
    })

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request(path):
    """处理代理请求"""

    # 监控chat/completions请求
    if 'chat/completions' in path or path == 'v1/chat/completions' or path == 'chat/completions':
        update_last_request_time()

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

    # 记录开始时间
    start_time = time.time()

    # 获取请求体
    request_body = request.data
    modified_body = request_body  # 默认使用原始请求体

    # 尝试解析并注入模型参数
    try:
        if request_body:
            body_json = json.loads(request_body)
            # 注入API特定的模型参数
            body_json['model'] = api_config['model']
            body_json['temperature'] = api_config['temperature']
            body_json['max_tokens'] = api_config['max_tokens']
            # 重新序列化
            modified_body = json.dumps(body_json, ensure_ascii=False).encode('utf-8')
    except Exception as e:
        # 如果解析失败，使用原始请求体
        pass

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

    # 尝试发送请求，如果失败则尝试下一个API
    max_retries = 5  # 固定最多重试5次
    last_error = None
    last_status_code = None

    for retry in range(max_retries):
        if retry > 0:
            # 如果是重试，获取下一个API
            api_index, api_config = load_balancer.get_next_api()
            target_url = api_config['target_url']
            target_api_key = api_config['target_api_key']
            headers['Authorization'] = f'Bearer {target_api_key}'

            # 重新排队等待
            load_balancer.rate_limiters[api_index].wait_if_needed()

            # 重新注入新API的模型参数
            try:
                if request_body:
                    body_json = json.loads(request_body)
                    body_json['model'] = api_config['model']
                    body_json['temperature'] = api_config['temperature']
                    body_json['max_tokens'] = api_config['max_tokens']
                    modified_body = json.dumps(body_json, ensure_ascii=False).encode('utf-8')
            except Exception as e:
                modified_body = request_body

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

        try:
            # 发送请求到上游API
            response = requests.request(
                method=request.method,
                url=final_url,
                headers=headers,
                params=request.args,
                data=modified_body,
                timeout=60,
                verify=True
            )

            response_time = time.time() - start_time

            # 检查响应状态码
            if response.status_code != 200:
                last_status_code = response.status_code
                # 释放当前API的并发槽位
                load_balancer.rate_limiters[api_index].release_concurrency()
                # 更新失败统计
                load_balancer.update_stats(api_index, False, response_time)

                # 如果还有重试机会，继续下一轮
                if retry < max_retries - 1:
                    continue
                else:
                    # 所有重试都失败了
                    with stats_lock:
                        request_stats["failed"] += 1
                        request_stats["in_progress"] -= 1

                    # 更新进度条（失败情况）
                    if pbar is not None:
                        with request_monitor_lock:
                            idle_seconds = int(time.time() - last_request_time)
                            last_time_str = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')

                        # 动态更新总数和当前值
                        pbar.total = request_stats["total"]
                        pbar.n = request_stats["success"] + request_stats["failed"]

                        pbar.set_postfix_str(
                            f"成功={request_stats['success']}, "
                            f"失败={request_stats['failed']}, "
                            f"最后请求={last_time_str}, "
                            f"空闲={idle_seconds}s"
                        )
                        pbar.refresh()

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

            # 更新进度条
            if pbar is not None:
                with request_monitor_lock:
                    idle_seconds = int(time.time() - last_request_time)
                    last_time_str = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')

                # 动态更新总数和当前值
                pbar.total = request_stats["total"]
                pbar.n = request_stats["success"] + request_stats["failed"]

                pbar.set_postfix_str(
                    f"成功={request_stats['success']}, "
                    f"失败={request_stats['failed']}, "
                    f"最后请求={last_time_str}, "
                    f"空闲={idle_seconds}s"
                )
                pbar.refresh()  # 使用refresh而不是update避免重复计数

            # 释放并发槽位
            load_balancer.rate_limiters[api_index].release_concurrency()

            # 准备响应
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

        except requests.Timeout:
            last_error = "Timeout"
            load_balancer.rate_limiters[api_index].release_concurrency()
            load_balancer.update_stats(api_index, False, time.time() - start_time)
            if retry < max_retries - 1:
                continue
        except Exception as e:
            last_error = str(e)
            load_balancer.rate_limiters[api_index].release_concurrency()
            load_balancer.update_stats(api_index, False, time.time() - start_time)
            if retry < max_retries - 1:
                continue

    # 所有重试都失败了
    with stats_lock:
        request_stats["failed"] += 1
        request_stats["in_progress"] -= 1

    # 更新进度条（最终失败）
    if pbar is not None:
        with request_monitor_lock:
            idle_seconds = int(time.time() - last_request_time)
            last_time_str = datetime.fromtimestamp(last_request_time).strftime('%H:%M:%S')

        # 动态更新总数和当前值
        pbar.total = request_stats["total"]
        pbar.n = request_stats["success"] + request_stats["failed"]

        pbar.set_postfix_str(
            f"成功={request_stats['success']}, "
            f"失败={request_stats['failed']}, "
            f"最后请求={last_time_str}, "
            f"空闲={idle_seconds}s"
        )
        pbar.refresh()

    # 返回错误响应
    error_response = {
        'error': {
            'message': f'All API endpoints failed after {max_retries} attempts',
            'type': 'proxy_error',
            'last_error': last_error
        }
    }
    return Response(
        json.dumps(error_response, ensure_ascii=False),
        status=502,
        content_type='application/json'
    )

def shutdown_handler(signum, frame):
    """优雅关闭处理"""
    global monitor_enabled
    monitor_enabled = False

    print("\n正在关闭服务...")
    if pbar is not None:
        pbar.close()

    # 显示最终统计
    print("\n" + "="*60)
    print("服务统计")
    print("="*60)
    print(f"总请求数: {request_stats['total']}")
    print(f"成功: {request_stats['success']}")
    print(f"失败: {request_stats['failed']}")
    print(f"进行中: {request_stats['in_progress']}")
    uptime = time.time() - request_stats['start_time']
    print(f"运行时间: {uptime:.1f}秒")

    # 显示每个API的统计
    print("\n" + "="*60)
    print("API池统计")
    print("="*60)
    print(load_balancer.get_stats_summary())
    print("="*60)

    # 等待监控线程结束
    if monitor_thread and monitor_thread.is_alive():
        monitor_thread.join(timeout=2)

    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    print("=" * 60)
    print("API代理服务启动 (带请求监控)")
    print("=" * 60)
    print(f"监听地址: {HOST}:{PORT}")
    print(f"监控超时: {restart_timeout}秒")
    print(f"调试模式: {DEBUG_MODE}")
    print("=" * 60)

    # 创建进度条（非DEBUG模式）
    create_progress_bar()

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_requests, daemon=True)
    monitor_thread.start()

    print(f"\n🚀 Flask服务器启动在 {HOST}:{PORT}")
    print("按 Ctrl+C 停止服务\n")

    # 关闭Flask的日志输出（在normal模式下）
    if not DEBUG_MODE:
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    app.run(host=HOST, port=PORT, debug=False, threaded=True)