"""
ScoreFlow Reward Client
用于在没有MetaGPT环境中调用远程reward计算服务
"""
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ScoreFlowRewardClient:
    """
    ScoreFlow Reward计算的客户端
    通过HTTP API调用远程服务器进行reward计算
    """
    
    def __init__(self, server_url: str = "http://localhost:8899", timeout: int = 300):
        """
        初始化客户端
        
        Args:
            server_url: 服务器URL
            timeout: 请求超时时间（秒）
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 测试连接
        self._check_connection()
    
    def _check_connection(self):
        """检查与服务器的连接"""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Connected to {data['service']} v{data['version']}")
            else:
                logger.warning(f"Server returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to server: {e}")
            logger.warning("Make sure the server is running and accessible")
    
    def compute_score(self, data_source: str, solution_str: str, 
                     ground_truth: str, extra_info: Dict) -> float:
        """
        计算单个solution的reward分数
        
        Args:
            data_source: benchmark名称
            solution_str: 包含workflow的LLM响应
            ground_truth: ground truth信息
            extra_info: 额外信息（test_cases, data_path等）
        
        Returns:
            float: reward分数 (0.0 到 1.0)
        """
        try:
            # 准备请求数据
            request_data = {
                'data_source': data_source,
                'solution_str': solution_str,
                'ground_truth': ground_truth,
                'extra_info': extra_info
            }
            
            logger.info(f"Sending request for benchmark: {data_source}")
            
            # 发送POST请求
            response = self.session.post(
                f"{self.server_url}/compute_score",
                json=request_data,
                timeout=self.timeout
            )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    score = result['score']
                    logger.info(f"Received score: {score}")
                    return score
                else:
                    logger.error(f"Server error: {result.get('error', 'Unknown error')}")
                    return 0.0
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return 0.0
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {self.timeout} seconds")
            return 0.0
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 0.0
    
    def batch_compute(self, tasks: List[Dict]) -> List[Dict]:
        """
        批量计算多个workflow的分数
        
        Args:
            tasks: 任务列表，每个任务包含:
                - task_id: 任务ID
                - data_source: benchmark名称
                - solution_str: workflow代码
                - ground_truth: ground truth
                - extra_info: 额外信息
        
        Returns:
            结果列表，每个结果包含task_id和score
        """
        try:
            logger.info(f"Sending batch request with {len(tasks)} tasks")
            
            # 发送批量请求
            response = self.session.post(
                f"{self.server_url}/batch_compute",
                json={'tasks': tasks},
                timeout=self.timeout * len(tasks)  # 根据任务数量调整超时
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    return result['results']
                else:
                    logger.error(f"Batch processing failed: {result.get('error')}")
                    return []
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Batch compute failed: {e}")
            return []
    
    def get_server_config(self) -> Optional[Dict]:
        """获取服务器配置信息"""
        try:
            response = self.session.get(f"{self.server_url}/config", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get server config: {e}")
            return None
    
    def close(self):
        """关闭客户端连接"""
        self.session.close()


# 全局客户端实例
_global_client = None


def get_client(server_url: str = None) -> ScoreFlowRewardClient:
    """
    获取全局客户端实例
    
    Args:
        server_url: 服务器URL，如果为None则使用默认值或环境变量
    """
    global _global_client
    
    if _global_client is None:
        # 从环境变量或使用默认值
        if server_url is None:
            import os
            server_url = os.environ.get('SCOREFLOW_SERVER_URL', 'http://localhost:8899')
        
        _global_client = ScoreFlowRewardClient(server_url)
    
    return _global_client


def compute_score(data_source: str, solution_str: str, 
                 ground_truth: str, extra_info: Dict) -> float:
    """
    计算reward分数的便捷函数（兼容原始接口）
    
    这个函数提供与原始scoreflow_reward.py相同的接口，
    但通过HTTP请求将计算委托给远程服务器
    
    Args:
        data_source: benchmark名称
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息
        extra_info: 包含test_cases, data_path等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    client = get_client()
    return client.compute_score(data_source, solution_str, ground_truth, extra_info)


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ScoreFlow Reward Client')
    parser.add_argument('--server', type=str, default='http://localhost:8899',
                       help='Server URL')
    parser.add_argument('--test', action='store_true',
                       help='Run test with sample data')
    
    args = parser.parse_args()
    
    if args.test:
        # 测试示例
        client = ScoreFlowRewardClient(args.server)
        
        # 获取服务器配置
        config = client.get_server_config()
        if config:
            print("Server configuration:")
            print(json.dumps(config, indent=2))
        
        # 测试计算分数
        test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the math problem step by step.")
        return solution
</graph>
"""
        
        test_extra_info = {
            'data_path': 'Processed_dataset/gsm8k/test.jsonl',
            'test_cases': [0, 1, 2],
        }
        
        score = client.compute_score(
            'gsm8k',
            test_solution,
            'default',
            test_extra_info
        )
        
        print(f"Test score: {score}")
        
        # 测试批量计算
        tasks = [
            {
                'task_id': f'test_{i}',
                'data_source': 'gsm8k',
                'solution_str': test_solution,
                'ground_truth': 'default',
                'extra_info': {
                    'data_path': 'Processed_dataset/gsm8k/test.jsonl',
                    'test_cases': [i],
                }
            }
            for i in range(3)
        ]
        
        results = client.batch_compute(tasks)
        print("\nBatch results:")
        for result in results:
            print(f"  {result['task_id']}: {result.get('score', 'failed')}")
        
        client.close()