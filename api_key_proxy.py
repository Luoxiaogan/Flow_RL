# rl_proxy_final_v3.py
import time, threading, requests, traceback, random
from flask import Flask, request, Response
from queue import Queue
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# ---------- 配置 ----------
# TARGET_BASE_URL = "https://idealab.alibaba-inc.com/api/openai/v1"
TARGET_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
HOST            = "localhost"
PORT            = 5009
RATE_PER_SECOND = 5      # 每秒分发10个任务
MAX_CONCURRENCY = 10      # 最多允许20个请求同时在执行 (并行数)
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
# 进度条现在表示已分发的任务数
bar = tqdm(total=0, desc="Dispatching Queue", unit="req")

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

# (新) 请求处理器：实际执行网络请求的函数，由线程池中的线程调用
# 在 rl_proxy_final_v3.py 中，替换整个 process_request 函数

def process_request(request_data, result_queue, path):
    target_url = f"{TARGET_BASE_URL}/{path}"
    try:
        headers = {k: v for k, v in request_data['headers'].items() if k.lower() != 'host'}
        
        # 为了调试，我们打印将要发送的请求信息
        # print(f"[DEBUG] Sending to {target_url} with headers: {headers}")

        resp = requests.request(
            method=request_data['method'],
            url=target_url,
            headers=headers,
            params=request_data['args'],
            data=request_data['data'],
            stream=True,
            timeout=60,  # 将超时设置为60秒，以防是慢响应导致的问题
            verify=False
        )

        # 无论如何，先打印一下收到的状态码，这很有用
        # print(f"[DEBUG] Received status {resp.status_code} from {target_url}")

        # 关键检查点
        resp.raise_for_status()
        
        # 成功，放入结果队列
        result_queue.put(resp)

    except requests.exceptions.HTTPError as e:
        # --- 这是最可能的分支，专门处理上游返回 4xx/5xx 的情况 ---
        print("\n" + "="*50)
        print(f"[!!!] HTTP ERROR for {request_data['method']} {target_url}")
        print(f"    Exception Type: {type(e).__name__}")
        if e.response is not None:
            print(f"    Upstream Status Code: {e.response.status_code}")
            # 打印上游服务器返回的完整错误信息，这通常是JSON格式的错误描述
            print(f"    Upstream Response Body:\n--- START RESPONSE ---\n{e.response.text}\n--- END RESPONSE ---")
        else:
            print("    Upstream response object is missing!")
        print("="*50 + "\n")
        result_queue.put(e)

    except requests.exceptions.RequestException as e:
        # --- 处理其他网络问题，如超时、连接失败等 ---
        print("\n" + "="*50)
        print(f"[!!!] NETWORK/REQUEST FAILED for {request_data['method']} {target_url}")
        print(f"    Exception Type: {type(e).__name__}")
        print(f"    Error Message: {e}")
        print("="*50 + "\n")
        result_queue.put(e)

    except Exception as e:
        # --- 捕获所有其他意外错误 ---
        print("\n" + "="*50)
        print(f"[!!!] UNEXPECTED PROXY ERROR for {request_data['method']} {target_url}")
        print(f"    Exception Type: {type(e).__name__}")
        print("    Traceback:")
        traceback.print_exc()
        print("="*50 + "\n")
        result_queue.put(e)

# (新) 调度器：按固定速率从队列取任务，并交给线程池
def dispatcher(executor):
    """
    这个函数扮演调度员的角色。
    它以固定的速率从队列中取出任务，然后提交给线程池去执行。
    它本身不等待网络请求的返回。
    """
    while True:
        # 1. 从队列获取任务 (如果队列空了，会在这里阻塞)
        request_data, result_queue, path = get_task_from_queue()
        
        # 2. 将任务提交给线程池，这是一个非阻塞操作
        executor.submit(process_request, request_data, result_queue, path)
        bar.update(1)

        # 3. 严格按照设定的速率等待，实现限流
        time.sleep(1 / RATE_PER_SECOND)

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
    
    # 主线程在这里阻塞，等待这个特定请求的结果
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
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("🤫 已禁用 SSL 证书验证警告 (因为 verify=False)")

    print(f"🚀 代理 (并发模式, v3) -> {TARGET_BASE_URL}")
    print(f"   监听 http://{HOST}:{PORT}")
    print(f"   分发速率: {RATE_PER_SECOND} req/s")
    print(f"   最大并发数: {MAX_CONCURRENCY} requests")

    # 创建一个线程池来管理并发的请求
    executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENCY)

    # 启动调度器线程
    threading.Thread(target=dispatcher, args=(executor,), daemon=True).start()
    
    app.run(host=HOST, port=PORT, threaded=True)