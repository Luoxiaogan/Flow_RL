# API代理服务请求监控集成指南

## 概述
本方案通过在Python应用内部监控HTTP请求，替代不可靠的tcpdump TCP连接监控。主要监控`/v1/chat/completions`端点的请求活动。

## 核心改动

### 1. 在api_key_proxy_pool.py中添加监控功能

在文件开头添加全局变量和监控函数：

```python
# ========== 请求监控相关 ==========
import threading
import os

last_request_time = time.time()  # 最后一次chat/completions请求时间
request_monitor_lock = threading.Lock()
restart_timeout = 180  # 默认180秒，从配置文件读取
monitor_enabled = True
monitor_thread = None

def update_last_request_time():
    """更新最后请求时间"""
    global last_request_time
    with request_monitor_lock:
        last_request_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 收到chat/completions请求")

def monitor_requests():
    """监控线程：检查是否超时"""
    global monitor_enabled
    print(f"[监控线程] 已启动，超时时间: {restart_timeout}秒")

    while monitor_enabled:
        time.sleep(10)  # 每10秒检查一次

        with request_monitor_lock:
            idle_time = time.time() - last_request_time

        if idle_time >= restart_timeout:
            print(f"\n[{datetime.now()}] ⚠️  {restart_timeout}秒无chat/completions请求")
            print(f"[{datetime.now()}] 🔄 触发自动重启...")

            # 可选：通知reward_server准备重启
            try:
                requests.post("http://localhost:7788/prepare_restart", timeout=1)
                print(f"✓ 已通知Reward服务器准备重启")
            except:
                pass

            # 退出进程（返回码0表示正常重启）
            time.sleep(1)
            os._exit(0)
```

### 2. 修改load_configs函数

在load_configs函数中添加读取restart_timeout配置：

```python
def load_configs():
    """加载主配置和API池配置"""
    global restart_timeout  # 添加这行

    # 加载主配置文件
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        proxy_config = config.get('services', {}).get('metagpt_api_proxy', {})

        # 从scoreflow_reward配置读取restart_per_step
        scoreflow_config = config.get('services', {}).get('scoreflow_reward', {})
        restart_timeout = scoreflow_config.get('restart_per_step', 180)

    # ... 其余代码不变
```

### 3. 修改proxy_request函数

在proxy_request函数开头添加请求监控：

```python
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy_request(path):
    """处理代理请求"""

    # 监控chat/completions请求
    if 'chat/completions' in path or path == 'v1/chat/completions' or path == 'chat/completions':
        update_last_request_time()

    # ... 其余代码不变
```

### 4. 添加监控相关端点（可选）

```python
@app.route('/last_activity', methods=['GET'])
def last_activity():
    """获取最后活动时间（用于调试）"""
    idle = time.time() - last_request_time
    return jsonify({
        'last_request_time': datetime.fromtimestamp(last_request_time).isoformat(),
        'idle_seconds': int(idle),
        'restart_in': max(0, restart_timeout - int(idle))
    })
```

### 5. 在主函数中启动监控线程

在`if __name__ == '__main__':`部分添加：

```python
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    print("=" * 60)
    print("API代理服务启动 (带请求监控)")
    print("=" * 60)
    print(f"监控超时: {restart_timeout}秒")
    print("=" * 60)

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_requests, daemon=True)
    monitor_thread.start()

    print(f"\n🚀 Flask服务器启动在 {HOST}:{PORT}")
    print("按 Ctrl+C 停止服务\n")

    # ... 其余代码不变
```

### 6. 修改shutdown_handler

```python
def shutdown_handler(signum, frame):
    """优雅关闭处理"""
    global monitor_enabled
    monitor_enabled = False  # 停止监控线程

    print("\n\n正在关闭服务...")
    # ... 其余代码不变
```

## 使用方法

### 测试监控功能

1. 使用简化的启动脚本：
```bash
bash start_api_proxy_pool_restart_simple.sh
```

2. 查看最后活动时间（调试用）：
```bash
curl http://localhost:5059/last_activity
```

3. 监控日志会显示：
```
[监控线程] 已启动，超时时间: 180秒
[17:35:20] ✓ 收到chat/completions请求
[17:38:20] ⚠️  180秒无chat/completions请求
[17:38:20] 🔄 触发自动重启...
```

## 配置说明

在`config.yaml`中设置重启超时时间：

```yaml
services:
  scoreflow_reward:
    restart_per_step: 180   # 无连接自动重启时间（秒）
```

## 优势

1. **准确性**：直接监控HTTP请求，不受TCP连接复用影响
2. **简单性**：监控逻辑在Python内部，bash脚本大幅简化
3. **可调试性**：提供`/last_activity`端点便于查看状态
4. **协调性**：重启前可通知reward_server做准备

## 注意事项

1. 监控线程使用`daemon=True`，主进程退出时自动结束
2. 使用`os._exit(0)`确保干净退出，返回码0表示正常重启
3. bash脚本检查退出码，0表示正常重启，继续循环
4. 建议生产环境使用180秒或更长的超时时间