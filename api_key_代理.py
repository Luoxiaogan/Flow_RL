# rl_proxy_final_v2.py
import time, threading, requests, traceback, random
from flask import Flask, request, Response
from queue import Queue
from tqdm import tqdm

# ---------- 配置 ----------
TARGET_BASE_URL = "https://idealab.alibaba-inc.com/api/openai/v1"
HOST            = "localhost"
PORT            = 5001
RATE_PER_SECOND = 2
QUEUE_TYPE      = "default" # 可选: "default" | "random"
# --------------------------

# --- 初始化队列 ---
if QUEUE_TYPE == "random":
    print("🚀 队列模式: 随机 (Random)")
    task_list, lock = [], threading.Lock()
else:
    print("🚀 队列模式: 先进先出 (FIFO)")
    task_queue = Queue()

app = Flask(__name__)
bar = tqdm(total=0, desc="Processing Queue", unit="req")

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

def worker():
    while True:
        request_data, result_queue, path = get_task_from_queue()
        time.sleep(1 / RATE_PER_SECOND)
        
        try:
            headers = {k: v for k, v in request_data['headers'].items() if k.lower() != 'host'}
            target_url = f"{TARGET_BASE_URL}/{path}"
            
            # --- 关键修改在这里 ---
            # 对于内部 HTTPS 地址，需要禁用 SSL 验证
            resp = requests.request(
                method=request_data['method'], url=target_url, headers=headers,
                params=request_data['args'], data=request_data['data'],
                stream=True, timeout=300,
                verify=False # <--- 核心修复！告诉 requests 不要验证 SSL 证书
            )
            
            # 增加一个检查，如果上游服务器也返回了错误，我们可以看到
            resp.raise_for_status() # 如果状态码是 4xx 或 5xx，这里会抛出异常
            
            result_queue.put(resp)

        except Exception as e:
            print("\n" + "="*50 + f"\n[!!!] Worker thread caught an exception for {target_url}:\n")
            traceback.print_exc()
            print("="*50 + "\n")
            result_queue.put(e)
        finally:
            bar.update(1)

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    result_queue = Queue(maxsize=1)
    request_data = {
        'method': request.method, 'headers': dict(request.headers),
        'args': request.args, 'data': request.get_data()
    }
    put_task_into_queue((request_data, result_queue, path))
    
    current_size = get_queue_size()
    if bar.total < current_size + bar.n:
        bar.total = current_size + bar.n
    
    result = result_queue.get()

    if isinstance(result, requests.Response):
        resp = result
        def gen():
            for chunk in resp.iter_content(chunk_size=8192): yield chunk
        return Response(gen(), status=resp.status_code,
                        headers=[(k, v) for k, v in resp.headers.items()
                                 if k.lower() not in
                                 {'content-encoding', 'transfer-encoding', 'connection'}])
    else:
        return Response(f"Proxy encountered an internal error: {result}", status=502)

if __name__ == "__main__":
    # 增加一个关于禁用 SSL 验证的警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("🤫 已禁用 SSL 证书验证警告 (因为 verify=False)")

    print(f"🚀 代理 (Worker模式, v2) -> {TARGET_BASE_URL}")
    print(f"   监听 http://{HOST}:{PORT}")
    print(f"   处理速率: {RATE_PER_SECOND} req/s")
    
    threading.Thread(target=worker, daemon=True).start()
    app.run(host=HOST, port=PORT, threaded=True)