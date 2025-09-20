"""
ScoreFlow Reward Client for RL Training
为VERL RL训练系统提供reward计算接口

架构说明:
- VERL训练期间会调用 compute_score(data_source, solution_str, ground_truth, extra_info)
- 我们的client作为适配器，将VERL的reward请求转换为HTTP API调用
- 等价于执行: curl -X POST http://localhost:8899/compute_score -d '{...}'
- 这确保了VERL训练与ScoreFlow reward_server的解耦

VERL接口规范:
- 函数签名: compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float
- 返回值: 0.0 到 1.0 的分数
- data_source: benchmark名称 (如 'gsm8k', 'mbpp') 
- solution_str: LLM生成的包含workflow的完整响应
- ground_truth: ground truth信息 (通常是 'default')
- extra_info: 包含test_cases, data_path等额外信息
"""

import os
import sys
import json
import logging
import requests
import yaml
from pathlib import Path
from typing import Dict, Any, List

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取当前文件目录和项目根目录
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# 读取配置文件获取reward_server配置
def get_reward_server_config() -> Dict[str, Any]:
    """从配置文件获取reward_server的完整配置"""
    default_config = {
        'url': 'http://localhost:7788',
        'client_http_timeout': 600  # 默认10分钟
    }
    
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
                scoreflow_config = config.get('services', {}).get('scoreflow_reward', {})
                
                host = scoreflow_config.get('host', 'localhost')
                port = scoreflow_config.get('port', 7788)
                
                # 如果host是0.0.0.0，转换为localhost用于客户端连接
                if host == '0.0.0.0':
                    host = 'localhost'
                
                return {
                    'url': f"http://{host}:{port}",
                    'client_http_timeout': scoreflow_config.get('client_http_timeout', 600)
                }
        else:
            logger.warning(f"配置文件不存在: {CONFIG_FILE}, 使用默认配置")
            return default_config
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}, 使用默认配置")
        return default_config

# 保留向后兼容的函数
def get_reward_server_url() -> str:
    """从配置文件获取reward_server的URL（向后兼容）"""
    return get_reward_server_config()['url']

def compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict[str, Any], **kwargs) -> float:
    """
    VERL标准reward计算接口
    
    将VERL的reward请求适配为ScoreFlow reward_server的HTTP API调用
    等价于: curl -X POST http://localhost:8899/compute_score -d '{请求数据}'
    
    Args:
        data_source: benchmark名称，如 'gsm8k', 'mbpp'，'high_level_math'
        solution_str: LLM生成的包含workflow的完整响应（应包含<code>标签）
        ground_truth: ground truth信息（VERL标准，通常是'default'）  
        extra_info: 包含test_cases, data_path等的字典
            - test_cases: List[int] - 要测试的案例索引
            - data_path: str - 数据集文件路径
            - 其他benchmark特定参数
    
    Returns:
        float: reward分数，范围 [0.0, 1.0]
               1.0 = 所有test cases都正确
               0.0 = 所有test cases都失败或发生错误
    
    VERL使用说明:
    - 在config.yaml中设置: reward_model.path: "path/to/this/file"
    - VERL会自动调用此函数计算每个生成response的reward
    """
    # 如果收到额外的kwargs（应该不会，因为config中reward_kwargs为空）
    if kwargs:
        logger.warning(f"Received unexpected kwargs (will be ignored): {kwargs}")
    
    # 参数验证
    if not isinstance(data_source, str) or not data_source.strip():
        logger.error(f"Invalid data_source: {data_source}")
        return 0.0
        
    if not isinstance(solution_str, str) or not solution_str.strip():
        logger.error(f"Invalid solution_str: empty or not string")
        return 0.0
        
    if not isinstance(extra_info, dict):
        logger.error(f"Invalid extra_info: {type(extra_info)}, expected dict")
        return 0.0
    
    # 确保test_cases存在且为列表
    test_cases = extra_info.get('test_cases', [])
    if not isinstance(test_cases, (list, tuple)):
        logger.error(f"Invalid test_cases: {test_cases}, expected list or tuple")
        return 0.0
    
    try:
        # 获取reward_server的配置
        server_config = get_reward_server_config()
        server_url = server_config['url']
        client_timeout = server_config['client_http_timeout']
        api_url = f"{server_url}/compute_score"
        
        logger.info(f"🚀 VERL Reward请求 - benchmark: {data_source}")
        logger.info(f"📊 测试用例: {test_cases} (共{len(test_cases)}个)")
        logger.info(f"🌐 API地址: {api_url}")
        logger.info(f"⏱️ HTTP超时: {client_timeout}秒")
        
        # 构建标准的reward_server API请求数据
        request_data = {
            "data_source": data_source,
            "solution_str": solution_str,
            "ground_truth": ground_truth,
            "extra_info": extra_info
        }
        
        # 发送HTTP请求到reward_server（使用配置的超时时间）
        response = requests.post(
            api_url,
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "VERL-ScoreFlow-Client/1.0"
            },
            timeout=client_timeout  # 使用配置文件中的超时时间
        )
        
        # 检查HTTP响应
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                score = result.get('score', 0.0)
                
                # 确保分数在合法范围内
                score = max(0.0, min(1.0, float(score)))
                
                logger.info(f"✅ Reward计算成功 - 分数: {score:.3f}")
                logger.info(f"📈 成功率: {score * 100:.1f}%")
                return score
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ ScoreFlow计算失败: {error_msg}")
                return 0.0
        else:
            logger.error(f"❌ HTTP请求失败: {response.status_code}")
            logger.error(f"响应内容: {response.text[:200]}...")
            return 0.0
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"🔌 无法连接到ScoreFlow reward_server: {e}")
        logger.error(f"请确保服务已启动: {get_reward_server_url()}")
        return 0.0
        
    except requests.exceptions.Timeout as e:
        logger.error(f"⏰ Reward计算超时: {e}")
        logger.error("workflow执行时间过长，可能存在性能问题")
        return 0.0
        
    except ValueError as e:
        logger.error(f"📊 数据格式错误: {e}")
        return 0.0
        
    except Exception as e:
        logger.error(f"💥 Reward计算异常: {e}")
        logger.error(f"数据源: {data_source}, 响应长度: {len(solution_str) if solution_str else 0}")
        return 0.0


def compute_score_batch(data_sources: List[str], solution_strs: List[str], 
                       ground_truths: List[str], extra_infos: List[Dict[str, Any]]) -> List[float]:
    """
    批量计算reward分数（VERL可选接口）
    
    Args:
        data_sources: benchmark名称列表
        solution_strs: LLM响应列表  
        ground_truths: ground truth列表
        extra_infos: 额外信息列表
        
    Returns:
        List[float]: 对应的reward分数列表
    """
    logger.info(f"🔄 开始批量计算 - {len(data_sources)} 个请求")
    
    results = []
    for i, (data_source, solution_str, ground_truth, extra_info) in enumerate(
        zip(data_sources, solution_strs, ground_truths, extra_infos, strict=True)
    ):
        logger.info(f"📝 处理批量请求 {i+1}/{len(data_sources)}")
        score = compute_score(data_source, solution_str, ground_truth, extra_info)
        results.append(score)
    
    avg_score = sum(results) / len(results) if results else 0.0
    logger.info(f"📊 批量计算完成 - 平均分数: {avg_score:.3f}")
    
    return results


# 为了向后兼容，提供一些常用的工具函数
def test_connection() -> bool:
    """
    测试reward_server的连接性
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        server_url = get_reward_server_url()
        health_url = f"{server_url}/health"
        
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'healthy':
                logger.info(f"ScoreFlow reward服务器连接成功: {server_url}")
                return True
            else:
                logger.error(f"ScoreFlow reward服务器状态异常: {result}")
                return False
        else:
            logger.error(f"ScoreFlow reward服务器健康检查失败: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"ScoreFlow reward服务器连接失败: {e}")
        return False


def get_available_benchmarks() -> list:
    """
    获取可用的benchmark列表
    
    Returns:
        list: 可用的benchmark名称列表
    """
    try:
        server_url = get_reward_server_url()
        config_url = f"{server_url}/config"
        
        response = requests.get(config_url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result.get('benchmarks', [])
        else:
            logger.error(f"获取benchmark列表失败: {response.status_code}")
            return []
        
    except Exception as e:
        logger.error(f"获取benchmark列表失败: {e}")
        return []


if __name__ == "__main__":
    # 简单的测试代码
    print("ScoreFlow Reward Client Test")
    print("-" * 40)
    
    # 测试连接
    print(f"连接测试: {'成功' if test_connection() else '失败'}")
    
    # 获取可用benchmarks
    benchmarks = get_available_benchmarks()
    print(f"可用benchmarks: {benchmarks}")
    
    # 测试计算
    test_workflow = '''
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction='Solve the problem.')
        return solution
'''
    
    test_extra_info = {
        'test_cases': [0], 
        'data_path': 'Processed_dataset/gsm8k/test.jsonl'
    }
    
    try:
        score = compute_score('gsm8k', test_workflow, 'default', test_extra_info)
        print(f"测试计算结果: {score:.3f}")
    except Exception as e:
        print(f"测试计算失败: {e}")