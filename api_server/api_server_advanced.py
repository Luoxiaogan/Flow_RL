import asyncio
import aiohttp
from flask import Flask, request, Response, jsonify
import threading
import queue
import time
from datetime import datetime
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
config_file = 'api_server_config.json'
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {
        "forward_url": "https://idealab.alibaba-inc.com/api/openai/v1",
        "local_port": 5000,
        "queue_interval": 0.1,
        "timeout": 30,
        "max_retries": 3
    }

FORWARD_URL = config['forward_url']
QUEUE_INTERVAL = config['queue_interval']
LOCAL_PORT = config['local_port']
TIMEOUT = config['timeout']
MAX_RETRIES = config.get('max_retries', 3)

# Request queue and response storage
request_queue = queue.Queue()
response_storage = {}

@dataclass
class RequestItem:
    id: str
    method: str
    path: str
    headers: Dict[str, str]
    data: bytes
    params: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0

    def to_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'path': self.path,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count
        }

async def forward_request_with_retry(item: RequestItem) -> Tuple[int, Dict, bytes]:
    """Forward a single request to the target server with retry logic"""
    url = FORWARD_URL + item.path
    
    # Clean headers
    headers = {k: v for k, v in item.headers.items() 
               if k.lower() not in ['host', 'content-length']}
    
    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=item.method,
                    url=url,
                    headers=headers,
                    data=item.data,
                    params=item.params,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)
                ) as response:
                    content = await response.read()
                    response_headers = dict(response.headers)
                    logger.info(f"Successfully forwarded {item.method} {item.path} -> Status: {response.status}")
                    return response.status, response_headers, content
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout on attempt {attempt + 1} for {item.method} {item.path}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)  # Wait before retry
            else:
                return 504, {}, b"Gateway Timeout"
                
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1} for {item.method} {item.path}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)  # Wait before retry
            else:
                return 502, {}, f"Bad Gateway: {str(e)}".encode()

def queue_processor():
    """Process requests from the queue with interval"""
    logger.info("Queue processor started")
    
    while True:
        try:
            if not request_queue.empty():
                item = request_queue.get()
                logger.info(f"Processing request {item.id}: {item.method} {item.path}")
                
                # Run async forward in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                status, headers, content = loop.run_until_complete(
                    forward_request_with_retry(item)
                )
                loop.close()
                
                # Store response
                response_storage[item.id] = {
                    'status': status,
                    'headers': headers,
                    'content': content,
                    'timestamp': datetime.now()
                }
                
                # Clean old responses (keep last 1000)
                if len(response_storage) > 1000:
                    oldest_keys = sorted(response_storage.keys())[:100]
                    for key in oldest_keys:
                        del response_storage[key]
                
                # Sleep for interval
                time.sleep(QUEUE_INTERVAL)
            else:
                time.sleep(0.01)  # Small sleep when queue is empty
                
        except Exception as e:
            logger.error(f"Error in queue processor: {e}")
            time.sleep(1)  # Wait a bit before continuing

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    """Catch all routes and queue the request"""
    # Generate request ID
    request_id = f"{datetime.now().timestamp()}_{request.remote_addr}"
    
    # Create request item
    item = RequestItem(
        id=request_id,
        method=request.method,
        path='/' + path if path else '/',
        headers=dict(request.headers),
        data=request.get_data(),
        params=dict(request.args),
        timestamp=datetime.now()
    )
    
    # Add to queue
    request_queue.put(item)
    queue_size = request_queue.qsize()
    
    logger.info(f"Queued request {request_id}: {request.method} {item.path} - Queue size: {queue_size}")
    
    # Return acknowledgment
    return jsonify({
        "status": "queued",
        "request_id": request_id,
        "queue_position": queue_size,
        "timestamp": item.timestamp.isoformat(),
        "estimated_wait": queue_size * QUEUE_INTERVAL
    }), 202

@app.route('/api/queue/status', methods=['GET'])
def queue_status():
    """Get current queue status"""
    return jsonify({
        "queue_size": request_queue.qsize(),
        "forward_url": FORWARD_URL,
        "interval_seconds": QUEUE_INTERVAL,
        "stored_responses": len(response_storage)
    })

@app.route('/api/request/<request_id>', methods=['GET'])
def get_request_status(request_id):
    """Get status of a specific request"""
    if request_id in response_storage:
        response_data = response_storage[request_id]
        return jsonify({
            "status": "completed",
            "http_status": response_data['status'],
            "timestamp": response_data['timestamp'].isoformat()
        })
    else:
        # Check if still in queue
        queue_items = list(request_queue.queue)
        for i, item in enumerate(queue_items):
            if item.id == request_id:
                return jsonify({
                    "status": "queued",
                    "position": i + 1,
                    "estimated_wait": (i + 1) * QUEUE_INTERVAL
                })
        
        return jsonify({"status": "not_found"}), 404

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify(config)
    else:
        new_config = request.get_json()
        if new_config:
            # Update global variables
            global FORWARD_URL, QUEUE_INTERVAL, TIMEOUT, MAX_RETRIES
            FORWARD_URL = new_config.get('forward_url', FORWARD_URL)
            QUEUE_INTERVAL = new_config.get('queue_interval', QUEUE_INTERVAL)
            TIMEOUT = new_config.get('timeout', TIMEOUT)
            MAX_RETRIES = new_config.get('max_retries', MAX_RETRIES)
            
            # Save to file
            config.update(new_config)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Configuration updated: {config}")
            return jsonify({"status": "updated", "config": config})
        else:
            return jsonify({"error": "Invalid configuration"}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "queue_size": request_queue.qsize(),
        "uptime": "running"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("API Relay Server with Queue")
    print("=" * 60)
    print(f"Local endpoint: http://localhost:{LOCAL_PORT}")
    print(f"Forwarding to: {FORWARD_URL}")
    print(f"Queue interval: {QUEUE_INTERVAL} seconds")
    print(f"Timeout: {TIMEOUT} seconds")
    print(f"Max retries: {MAX_RETRIES}")
    print("=" * 60)
    print("\nEndpoints:")
    print(f"  - All requests: http://localhost:{LOCAL_PORT}/*")
    print(f"  - Queue status: http://localhost:{LOCAL_PORT}/api/queue/status")
    print(f"  - Request status: http://localhost:{LOCAL_PORT}/api/request/<request_id>")
    print(f"  - Configuration: http://localhost:{LOCAL_PORT}/api/config")
    print(f"  - Health check: http://localhost:{LOCAL_PORT}/health")
    print("=" * 60)
    
    # Start queue processor thread
    processor_thread = threading.Thread(target=queue_processor, daemon=True)
    processor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=LOCAL_PORT, debug=False)