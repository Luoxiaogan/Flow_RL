import asyncio
import aiohttp
from flask import Flask, request, Response
import threading
import queue
import time
from datetime import datetime
import json

app = Flask(__name__)

# Configuration
FORWARD_URL = "http://example.com/api"  # Change this to your target URL
QUEUE_INTERVAL = 0.1  # 0.1 seconds between requests
LOCAL_PORT = 5000

# Request queue
request_queue = queue.Queue()

class RequestItem:
    def __init__(self, method, path, headers, data, params):
        self.method = method
        self.path = path
        self.headers = dict(headers)
        self.data = data
        self.params = params
        self.timestamp = datetime.now()

async def forward_request(item):
    """Forward a single request to the target server"""
    url = FORWARD_URL + item.path
    
    # Remove host header to avoid conflicts
    headers = {k: v for k, v in item.headers.items() 
               if k.lower() not in ['host', 'content-length']}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=item.method,
                url=url,
                headers=headers,
                data=item.data,
                params=item.params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                content = await response.read()
                print(f"[{datetime.now()}] Forwarded {item.method} {item.path} -> Status: {response.status}")
                return response.status, dict(response.headers), content
        except Exception as e:
            print(f"[{datetime.now()}] Error forwarding request: {e}")
            return 500, {}, b"Error forwarding request"

def queue_processor():
    """Process requests from the queue with interval"""
    while True:
        if not request_queue.empty():
            item = request_queue.get()
            print(f"[{datetime.now()}] Processing queued request: {item.method} {item.path}")
            
            # Run async forward in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            status, headers, content = loop.run_until_complete(forward_request(item))
            loop.close()
            
            # Sleep for interval
            time.sleep(QUEUE_INTERVAL)
        else:
            time.sleep(0.01)  # Small sleep when queue is empty

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    """Catch all routes and queue the request"""
    # Create request item
    item = RequestItem(
        method=request.method,
        path='/' + path if path else '/',
        headers=request.headers,
        data=request.get_data(),
        params=dict(request.args)
    )
    
    # Add to queue
    request_queue.put(item)
    queue_size = request_queue.qsize()
    
    print(f"[{datetime.now()}] Queued {request.method} {item.path} - Queue size: {queue_size}")
    
    # Return acknowledgment
    return Response(
        json.dumps({
            "status": "queued",
            "queue_position": queue_size,
            "timestamp": item.timestamp.isoformat()
        }),
        status=202,
        mimetype='application/json'
    )

@app.route('/queue/status', methods=['GET'])
def queue_status():
    """Get current queue status"""
    return {
        "queue_size": request_queue.qsize(),
        "forward_url": FORWARD_URL,
        "interval_seconds": QUEUE_INTERVAL
    }

if __name__ == '__main__':
    print(f"Starting API Relay Server")
    print(f"Local endpoint: http://localhost:{LOCAL_PORT}")
    print(f"Forwarding to: {FORWARD_URL}")
    print(f"Queue interval: {QUEUE_INTERVAL} seconds")
    print("-" * 50)
    
    # Start queue processor thread
    processor_thread = threading.Thread(target=queue_processor, daemon=True)
    processor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=LOCAL_PORT, debug=False)