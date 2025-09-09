"""
ScoreFlow Reward Server
Provides REST API for computing rewards in environments with MetaGPT installed
"""
import sys
import json
import logging
from loguru import logger as loguru_logger
import traceback
import yaml
from pathlib import Path
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

# 导入scoreflow_reward模块（带token追踪版本）
from scoreflow_reward_utils_with_cost import compute_score, get_calculator
from token_tracker import get_global_tracker
from cost_calculator import CostCalculator

# 导入并发控制模块
from concurrency_limiter import init_limiter, get_limiter, with_concurrency_limit

if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        _config_for_debug = yaml.safe_load(f)
        # 从scoreflow_reward服务配置中读取debug和silent设置
        scoreflow_config = _config_for_debug.get('services', {}).get('scoreflow_reward', {})
        DEBUG = int(scoreflow_config.get('debug', False))
        SILENT = scoreflow_config.get('silent', False)
        print(f"[SERVER] 📝 Debug日志模式: {'开启' if DEBUG else '关闭'} (从config.yaml读取)")
        print(f"[SERVER] 🔇 静默模式: {'开启' if SILENT else '关闭'} (从config.yaml读取)")
else:
    DEBUG = 0  # 默认关闭debug
    SILENT = False  # 默认关闭静默模式
    print(f"[SERVER] 📝 Debug日志模式: 关闭 (默认值)")
    print(f"[SERVER] 🔇 静默模式: 关闭 (默认值)")

def silent_print(*args, **kwargs):
    """
    非静默模式下的条件打印函数
    只有当SILENT == False时才会输出到终端
    用于显示详细信息，在静默模式下会被屏蔽
    
    Usage:
        silent_print("详细执行信息")  # 静默模式下不显示
        print("关键结果信息")  # 始终显示
    """
    if not SILENT:
        # 添加flush=True确保立即输出
        print(*args, flush=True, **kwargs)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if SILENT:
    # 禁用特定库的日志
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)  # httpx 的底层库
    logging.getLogger("openai").setLevel(logging.ERROR)     # OpenAI SDK 的 HTTP 日志
    logging.getLogger("metagpt").setLevel(logging.ERROR)    # MetaGPT 的日志
    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # 禁用 Flask 访问日志
    # 禁用 loguru 的 metagpt 日志
    loguru_logger.disable("metagpt")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局配置（从config.yaml读取）
SERVER_CONFIG = {
    'host': service_config.get('host', '0.0.0.0'),
    'port': service_config.get('port', 8899),
    'debug': service_config.get('debug', False),
    'timeout': service_config.get('timeout', 300),  # 5分钟超时
    'max_concurrent_requests': service_config.get('max_concurrent_requests', 5),
    'request_queue_timeout': service_config.get('request_queue_timeout', 600)
}

# 初始化并发控制器
limiter = init_limiter(
    max_concurrent=SERVER_CONFIG['max_concurrent_requests'],
    queue_timeout=SERVER_CONFIG['request_queue_timeout']
)
logger.info(f"并发控制已启用: 最大并发数={SERVER_CONFIG['max_concurrent_requests']}, "
           f"排队超时={SERVER_CONFIG['request_queue_timeout']}秒")

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'scoreflow_reward_server',
        'version': '1.0.0'
    })

@app.route('/compute_score', methods=['POST'])
@with_concurrency_limit('data_source')
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
        
        # 调用计算函数
        score = compute_score(data_source, solution_str, ground_truth, extra_info)
        
        # 获取token统计（如果可用）
        token_stats = {}
        tracker = get_global_tracker()
        if tracker and tracker.enabled:
            # 获取最近的workflow统计
            if tracker.workflow_stats:
                # 获取最近的workflow
                latest_workflow_id = list(tracker.workflow_stats.keys())[-1] if tracker.workflow_stats else None
                if latest_workflow_id:
                    token_stats = tracker.get_workflow_stats(latest_workflow_id)
        
        response_data = {
            'success': True,
            'score': float(score),
            'message': 'Score computed successfully'
        }
        
        # 如果有token统计，添加到响应中
        if token_stats:
            response_data['token_stats'] = {
                'prompt_tokens': token_stats.get('prompt_tokens', 0),
                'completion_tokens': token_stats.get('completion_tokens', 0),
                'total_tokens': token_stats.get('total_tokens', 0),
                'total_cost': token_stats.get('total_cost', 0),
                'model_name': token_stats.get('model_name', 'unknown'),
                'cost_breakdown': token_stats.get('cost_breakdown', {})
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
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

@app.route('/status', methods=['GET'])
def get_status():
    """
    获取服务器并发状态和统计信息
    用于监控和调试
    """
    limiter = get_limiter()
    if limiter:
        return jsonify(limiter.get_status())
    else:
        return jsonify({
            'error': 'Concurrency limiter not initialized',
            'message': '并发控制器未初始化'
        }), 500

@app.route('/token_stats', methods=['GET'])
def get_token_stats():
    """获取token使用统计"""
    tracker = get_global_tracker()
    if tracker and tracker.enabled:
        stats = tracker.get_total_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Token tracker not enabled',
            'message': 'Token追踪器未启用'
        }), 500

@app.route('/cost_report', methods=['GET'])
def get_cost_report():
    """获取费用报告"""
    try:
        calculator = CostCalculator()
        report = calculator.generate_cost_report()
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reset_stats', methods=['POST'])
def reset_statistics():
    """重置统计信息（需要管理权限）"""
    # 重置并发限制器统计
    limiter = get_limiter()
    if limiter:
        limiter.reset_statistics()
    
    # 重置token统计
    tracker = get_global_tracker()
    if tracker:
        tracker.reset_stats()
    
    return jsonify({
        'success': True,
        'message': 'All statistics reset successfully'
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
    
    # 从配置文件读取flask_debug设置
    flask_debug = service_config.get('flask_debug', False)
    
    # 启动服务器
    app.run(
        host=args.host,
        port=args.port,
        debug=flask_debug,  # 从配置文件控制Flask debug模式
        threaded=True,
        use_reloader=False  # 即使在debug模式下也禁用自动重载器，避免双进程问题
    )

if __name__ == '__main__':
    main()