"""
InternBootcamp Reward Server
REST API server for InternBootcamp reward calculation
Reuses ScoreFlow's server code with minimal modifications
"""
import os
import sys
import yaml
import json
import logging
import traceback
import argparse
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

print("-"*60)

# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除代理环境变量，确保本地服务通信正常
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]
        print(f"✓ 已清除环境变量: {proxy_var}")

print(f"✓ 已设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}'")
print("  InternBootcamp Server的localhost请求将绕过所有代理")

# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CONFIG_FILE = PROJECT_ROOT / "New_evaluation_and_RL" / "config.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        # 获取project_root，用于构建默认路径
        project_root = config.get('project_root', 'D:/temp/Flow_RL')
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    project_root = 'D:/temp/Flow_RL'

# 转换为Path对象
project_root_path = Path(project_root)

# 添加必要路径
sys.path.append(str(project_root_path))
sys.path.insert(0, str(CURRENT_DIR))

# Import InternBootcamp compute_score
from internbootcamp_reward_utils import compute_score, get_calculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Server configuration
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 8900,  # Different port for InternBootcamp
    'debug': False,
    'service_name': 'internbootcamp_reward_server',
    'version': '2.0.0'
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': SERVER_CONFIG['service_name'],
        'version': SERVER_CONFIG['version'],
        'port': SERVER_CONFIG['port']
    })


@app.route('/compute_score', methods=['POST'])
def compute_score_endpoint():
    """
    Compute reward score API endpoint
    
    Request format:
    {
        "data_source": "internbootcamp",
        "solution_str": "<workflow code>",
        "ground_truth": "default",
        "extra_info": {
            "task_name": "sudoku_4x4_easy",
            "test_cases": [0, 1, 2],
            "data_path": ""
        }
    }
    
    Response format:
    {
        "success": true,
        "score": 0.85,
        "message": "Score computed successfully"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['data_source', 'solution_str', 'ground_truth', 'extra_info']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract parameters
        data_source = data['data_source']
        solution_str = data['solution_str']
        ground_truth = data['ground_truth']
        extra_info = data['extra_info']
        
        # Log request info
        task_name = extra_info.get('task_name', 'unknown')
        logger.info(f"Processing request for InternBootcamp task: {task_name}")
        logger.info(f"Data source: {data_source}")
        logger.debug(f"Extra info: {json.dumps(extra_info, indent=2)}")
        
        # Compute score
        score = compute_score(data_source, solution_str, ground_truth, extra_info)
        
        logger.info(f"Computed score for {task_name}: {score}")
        
        return jsonify({
            'success': True,
            'score': float(score),
            'message': f'Score computed successfully for {task_name}',
            'task_name': task_name
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/batch_compute', methods=['POST'])
def batch_compute_endpoint():
    """
    Batch compute scores for multiple tasks
    
    Request format:
    {
        "tasks": [
            {
                "task_id": "task_1",
                "data_source": "internbootcamp",
                "solution_str": "<workflow code>",
                "ground_truth": "default",
                "extra_info": {...}
            },
            ...
        ]
    }
    
    Response format:
    {
        "success": true,
        "results": [
            {
                "task_id": "task_1",
                "score": 0.85,
                "success": true,
                "task_name": "sudoku_4x4_easy"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'tasks' not in data:
            return jsonify({
                'success': False,
                'error': 'No tasks provided'
            }), 400
        
        tasks = data['tasks']
        results = []
        
        logger.info(f"Processing batch request with {len(tasks)} tasks")
        
        # Process each task
        for task in tasks:
            task_id = task.get('task_id', 'unknown')
            task_name = task.get('extra_info', {}).get('task_name', 'unknown')
            
            try:
                score = compute_score(
                    task['data_source'],
                    task['solution_str'],
                    task['ground_truth'],
                    task['extra_info']
                )
                
                results.append({
                    'task_id': task_id,
                    'task_name': task_name,
                    'score': float(score),
                    'success': True
                })
                
                logger.info(f"Task {task_id} ({task_name}): score={score}")
                
            except Exception as e:
                logger.error(f"Error processing task {task_id} ({task_name}): {e}")
                results.append({
                    'task_id': task_id,
                    'task_name': task_name,
                    'score': 0.0,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_tasks': len(tasks),
            'successful_tasks': sum(1 for r in results if r['success'])
        })
        
    except Exception as e:
        logger.error(f"Error processing batch request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Get server configuration information"""
    try:
        calculator = get_calculator()
        
        # Get available InternBootcamp tasks
        available_tasks = []
        try:
            from internbootcamp_utils import InternBootcampManager
            manager = InternBootcampManager()
            available_tasks = manager.get_available_tasks()
        except Exception as e:
            logger.warning(f"Could not load InternBootcamp tasks: {e}")
        
        return jsonify({
            'server_config': SERVER_CONFIG,
            'llm_config': calculator.llm_config,
            'reward_config': calculator.reward_config,
            'internbootcamp_tasks': available_tasks,
            'workspace': str(calculator.workspace_path)
        })
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/tasks', methods=['GET'])
def get_available_tasks():
    """Get list of available InternBootcamp tasks"""
    try:
        from internbootcamp_utils import InternBootcampManager
        manager = InternBootcampManager()
        
        available_tasks = manager.get_available_tasks()
        failed_tasks = manager.get_failed_tasks()
        
        return jsonify({
            'success': True,
            'available_tasks': available_tasks,
            'failed_tasks': failed_tasks,
            'total_available': len(available_tasks),
            'total_failed': len(failed_tasks)
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def main():
    """Main function to start the server"""
    parser = argparse.ArgumentParser(description='InternBootcamp Reward Server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8900,
                       help='Server port (default: 8900)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--config', type=str,
                       help='Path to config file (default: internbootcamp_config.yaml)')
    
    args = parser.parse_args()
    
    # Update server configuration
    SERVER_CONFIG['host'] = args.host
    SERVER_CONFIG['port'] = args.port
    SERVER_CONFIG['debug'] = args.debug
    
    # Initialize calculator with config if provided
    if args.config:
        _ = get_calculator(args.config)
    else:
        # Try to use internbootcamp_config.yaml if it exists
        config_path = PROJECT_ROOT / "New_evaluation_and_RL" / "internbootcamp_config.yaml"
        if config_path.exists():
            _ = get_calculator(str(config_path))
            logger.info(f"Using config file: {config_path}")
    
    # Log startup information
    logger.info("=" * 60)
    logger.info(f"Starting InternBootcamp Reward Server")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug mode: {args.debug}")
    logger.info(f"Service: {SERVER_CONFIG['service_name']}")
    logger.info(f"Version: {SERVER_CONFIG['version']}")
    logger.info("=" * 60)
    
    # Start the server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True  # Enable threading for concurrent requests
    )


if __name__ == '__main__':
    main()