"""
ScoreFlow Reward Server
Provides REST API for computing rewards in environments with MetaGPT installed
"""
import os
import sys
import json
import asyncio
import logging
import traceback
import yaml
from pathlib import Path
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import argparse

# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        service_config = config.get('services', {}).get('scoreflow_reward', {})
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    service_config = {}

# 添加必要路径
sys.path.insert(0, str(CURRENT_DIR))

# 导入scoreflow_reward模块
from scoreflow_reward_utils import compute_score, get_calculator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局配置（从config.yaml读取）
SERVER_CONFIG = {
    'host': service_config.get('host', '0.0.0.0'),
    'port': service_config.get('port', 8899),
    'debug': service_config.get('debug', False),
    'timeout': service_config.get('timeout', 300)  # 5分钟超时
}

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'scoreflow_reward_server',
        'version': '1.0.0'
    })

@app.route('/compute_score', methods=['POST'])
def compute_score_endpoint():
    """
    计算reward分数的API端点
    
    请求格式:
    {
        "data_source": "gsm8k",
        "solution_str": "<workflow code>",
        "ground_truth": "default",
        "extra_info": {
            "test_cases": [0, 1, 2],
            "data_path": "path/to/data.jsonl"
        }
    }
    
    响应格式:
    {
        "success": true,
        "score": 0.85,
        "message": "Score computed successfully"
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # 验证必需字段
        required_fields = ['data_source', 'solution_str', 'ground_truth', 'extra_info']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # 提取参数
        data_source = data['data_source']
        solution_str = data['solution_str']
        ground_truth = data['ground_truth']
        extra_info = data['extra_info']
        
        logger.info(f"Processing request for benchmark: {data_source}")
        logger.info(f"Extra info: {json.dumps(extra_info, indent=2)}")
        
        # 调用计算函数
        score = compute_score(data_source, solution_str, ground_truth, extra_info)
        
        logger.info(f"Computed score: {score}")
        
        return jsonify({
            'success': True,
            'score': float(score),
            'message': 'Score computed successfully'
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
    批量计算多个workflow的分数
    
    请求格式:
    {
        "tasks": [
            {
                "task_id": "task_1",
                "data_source": "gsm8k",
                "solution_str": "<workflow code>",
                "ground_truth": "default",
                "extra_info": {...}
            },
            ...
        ]
    }
    
    响应格式:
    {
        "success": true,
        "results": [
            {
                "task_id": "task_1",
                "score": 0.85,
                "success": true
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
        
        # 处理每个任务
        for task in tasks:
            task_id = task.get('task_id', 'unknown')
            try:
                score = compute_score(
                    task['data_source'],
                    task['solution_str'],
                    task['ground_truth'],
                    task['extra_info']
                )
                
                results.append({
                    'task_id': task_id,
                    'score': float(score),
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {e}")
                results.append({
                    'task_id': task_id,
                    'score': 0.0,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing batch request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_config():
    """获取服务器配置信息"""
    calculator = get_calculator()
    return jsonify({
        'server_config': SERVER_CONFIG,
        'llm_config': calculator.llm_config,
        'reward_config': calculator.reward_config,
        'benchmarks': list(calculator.benchmark_mapping.keys())
    })

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ScoreFlow Reward Server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8899,
                       help='Server port (default: 8899)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--config', type=str,
                       help='Path to config.yaml file (default: ../config.yaml)')
    
    args = parser.parse_args()
    
    # 更新服务器配置
    SERVER_CONFIG['host'] = args.host
    SERVER_CONFIG['port'] = args.port
    SERVER_CONFIG['debug'] = args.debug
    
    # 初始化calculator（传入配置文件路径）
    if args.config:
        _ = get_calculator()._init__(args.config)
    
    logger.info(f"Starting ScoreFlow Reward Server on {args.host}:{args.port}")
    logger.info(f"Debug mode: {args.debug}")
    
    # 启动服务器
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )

if __name__ == '__main__':
    main()