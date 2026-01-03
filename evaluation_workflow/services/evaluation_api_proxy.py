# Evaluation API Proxy - 评估模型专用的API代理服务
# 基于api_key_proxy_enhanced.py，但使用独立的配置
import time, threading, requests, traceback, random
import yaml
import os
from flask import Flask, request, Response
from queue import Queue
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Load configuration from config.yaml
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
        # 使用evaluation_api_proxy配置而不是metagpt_api_proxy
        proxy_config = config.get('services', {}).get('evaluation_api_proxy', {})
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}, using defaults")
    proxy_config = {}

# ---------- Configuration from YAML ----------
TARGET_BASE_URL = proxy_config.get('target_url', "https://idealab.alibaba-inc.com/api/openai/v1")
TARGET_API_KEY = proxy_config.get('target_api_key', "")  # Target API key
HOST = proxy_config.get('host', "localhost")
PORT = proxy_config.get('port', 5010)  # 默认使用5010端口
RATE_PER_SECOND = proxy_config.get('rate_per_second', 5)  # 更高的速率
MAX_CONCURRENCY = proxy_config.get('max_concurrency', 10)  # 更高的并发
QUEUE_TYPE = proxy_config.get('queue_type', "default")
# ----------------------------------------------

print(f"🚀 Evaluation API Proxy Configuration:")
print(f"   Target URL: {TARGET_BASE_URL}")
print(f"   Target API Key: {'***' + TARGET_API_KEY[-4:] if TARGET_API_KEY else 'Not configured'}")
print(f"   Host: {HOST}:{PORT}")
print(f"   Rate: {RATE_PER_SECOND} req/s, Max Concurrency: {MAX_CONCURRENCY}")
print(f"   Queue Type: {QUEUE_TYPE}")
print(f"   Purpose: Model Evaluation (not MetaGPT)")

# --- Initialize queue ---
if QUEUE_TYPE == "random":
    print("🚀 Queue Mode: Random")
    task_list, lock = [], threading.Lock()
else:
    print("🚀 Queue Mode: FIFO")
    task_queue = Queue()

# --- Initialize counters ---
sent_to_api = 0
received_from_api = 0
sent_to_client = 0
counter_lock = threading.Lock()

app = Flask(__name__)
bar = tqdm(total=0, desc="Evaluation Queue", unit="req")

def put_task_into_queue(task):
    if QUEUE_TYPE == "random":
        with lock: task_list.append(task)
    else: task_queue.put(task)

def get_task_from_queue():
    if QUEUE_TYPE == "random":
        while True:
            with lock:
                if task_list: return task_list.pop(random.randint(0, len(task_list) - 1))
            time.sleep(0.1)
    else: return task_queue.get()

def get_queue_size():
    return len(task_list) if QUEUE_TYPE == "random" else task_queue.qsize()

def process_request(request_data, result_queue, path):
    global sent_to_api, received_from_api
    target_url = f"{TARGET_BASE_URL}/{path}"
    try:
        # Copy headers but remove host
        headers = {k: v for k, v in request_data['headers'].items() if k.lower() != 'host'}
        
        # Add or replace Authorization header with target API key if configured
        if TARGET_API_KEY:
            headers['Authorization'] = f'Bearer {TARGET_API_KEY}'
            # For Alibaba/Dashscope APIs that might use different header
            headers['X-DashScope-ApiKey'] = TARGET_API_KEY
        
        # Increment sent counter
        with counter_lock:
            sent_to_api += 1
            update_bar_description()

        resp = requests.request(
            method=request_data['method'],
            url=target_url,
            headers=headers,
            params=request_data['args'],
            data=request_data['data'],
            stream=True,
            timeout=60,
            verify=False
        )
        
        # Increment received counter
        with counter_lock:
            received_from_api += 1
            update_bar_description()
        
        # Return response
        result_queue.put({
            'status': resp.status_code,
            'headers': dict(resp.headers),
            'content': resp.content
        })
    except Exception as e:
        print(f"[Evaluation] Error processing request: {e}")
        traceback.print_exc()
        result_queue.put({
            'status': 500,
            'headers': {'Content-Type': 'application/json'},
            'content': f'{{"error": "Internal proxy error: {str(e)}"}}'.encode()
        })

def send_response_to_client(result_queue):
    global sent_to_client
    result = result_queue.get()
    
    # Increment sent to client counter
    with counter_lock:
        sent_to_client += 1
        update_bar_description()
    
    # Filter out problematic headers
    excluded_headers = {'content-encoding', 'content-length', 'transfer-encoding', 'connection'}
    headers = [(k, v) for k, v in result['headers'].items() if k.lower() not in excluded_headers]
    
    return Response(result['content'], status=result['status'], headers=headers)

def update_bar_description():
    bar.set_description(f"Queue: {get_queue_size()}, To API: {sent_to_api}, From API: {received_from_api}, To Client: {sent_to_client}")

def worker():
    while True:
        task = get_task_from_queue()
        process_request(task['request_data'], task['result_queue'], task['path'])
        time.sleep(1.0 / RATE_PER_SECOND)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
def proxy(path):
    # Prepare request data
    request_data = {
        'method': request.method,
        'headers': dict(request.headers),
        'args': request.args,
        'data': request.get_data()
    }
    
    # Create result queue
    result_queue = Queue()
    
    # Add task to queue
    put_task_into_queue({
        'request_data': request_data,
        'result_queue': result_queue,
        'path': path
    })
    
    # Wait for and return response
    return send_response_to_client(result_queue)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'evaluation_api_proxy',
        'port': PORT,
        'queue_size': get_queue_size(),
        'sent_to_api': sent_to_api,
        'received_from_api': received_from_api,
        'sent_to_client': sent_to_client
    }, 200

if __name__ == '__main__':
    # Start worker threads
    print(f"📡 Starting Evaluation API Proxy Server on {HOST}:{PORT}")
    print(f"📌 Proxying to: {TARGET_BASE_URL}")
    print(f"🔑 Using target API key: {'***' + TARGET_API_KEY[-4:] if TARGET_API_KEY else 'Not configured'}")
    print(f"--------------------------------------------------")
    
    # Create thread pool for workers
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        for _ in range(MAX_CONCURRENCY):
            executor.submit(worker)
        
        # Start Flask app
        try:
            app.run(host=HOST, port=PORT, threaded=True, debug=False)
        except KeyboardInterrupt:
            print("\n⚠️  Evaluation API Proxy shutting down...")
            bar.close()