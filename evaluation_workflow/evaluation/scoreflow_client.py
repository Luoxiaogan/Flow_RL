#!/usr/bin/env python3
"""
ScoreFlow HTTP Client
通过 HTTP API 调用 scoreflow_reward_server，避免直接导入 MetaGPT
这样可以在不同的 conda 环境中运行评测和评分服务
"""

import requests
import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# 默认服务配置
DEFAULT_SCOREFLOW_URL = "http://localhost:8899"


class ScoreFlowClient:
    """ScoreFlow HTTP API 客户端"""
    
    def __init__(self, base_url: str = DEFAULT_SCOREFLOW_URL, timeout: int = 180):
        """
        初始化客户端
        
        Args:
            base_url: ScoreFlow 服务的基础 URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._check_connection()
    
    def _check_connection(self):
        """检查服务连接"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Connected to ScoreFlow server: {data.get('service', 'unknown')} v{data.get('version', 'unknown')}")
            else:
                logger.warning(f"ScoreFlow server returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to ScoreFlow server at {self.base_url}")
            logger.error("Please make sure scoreflow_reward_server.py is running")
            raise ConnectionError(f"ScoreFlow server not available at {self.base_url}")
        except Exception as e:
            logger.warning(f"Failed to check ScoreFlow server: {e}")
    
    def compute_score(
        self,
        data_source: str,
        solution_str: str,
        ground_truth: Optional[str] = None,
        extra_info: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        计算单个解决方案的分数
        
        Args:
            data_source: 数据源/基准名称 (如 'gsm8k', 'mbpp')
            solution_str: 解决方案字符串（workflow 代码）
            ground_truth: 真实答案（可选）
            extra_info: 额外信息字典
            
        Returns:
            分数 (0.0 到 1.0)
        """
        try:
            payload = {
                'data_source': data_source,
                'solution_str': solution_str
            }
            
            if ground_truth is not None:
                payload['ground_truth'] = ground_truth
            
            if extra_info:
                payload['extra_info'] = extra_info
            
            response = requests.post(
                f"{self.base_url}/compute_score",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('score', 0.0)
            else:
                logger.error(f"Score API returned status {response.status_code}: {response.text}")
                return 0.0
                
        except requests.exceptions.Timeout:
            logger.error(f"Score computation timed out after {self.timeout} seconds")
            return 0.0
        except requests.exceptions.ConnectionError:
            logger.error("Lost connection to ScoreFlow server")
            return 0.0
        except Exception as e:
            logger.error(f"Failed to compute score: {e}")
            return 0.0
    
    def batch_compute(
        self,
        tasks: List[Dict[str, Any]],
        max_workers: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量计算分数
        
        Args:
            tasks: 任务列表，每个任务包含 data_source, solution_str 等
            max_workers: 最大并发数
            
        Returns:
            结果列表
        """
        try:
            response = requests.post(
                f"{self.base_url}/batch_compute",
                json={
                    'tasks': tasks,
                    'max_workers': max_workers
                },
                timeout=self.timeout * len(tasks)  # 根据任务数调整超时
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                logger.error(f"Batch API returned status {response.status_code}: {response.text}")
                return [{'score': 0.0, 'error': 'API error'} for _ in tasks]
                
        except Exception as e:
            logger.error(f"Failed to batch compute scores: {e}")
            return [{'score': 0.0, 'error': str(e)} for _ in tasks]
    
    def get_config(self) -> Dict[str, Any]:
        """获取服务配置信息"""
        try:
            response = requests.get(f"{self.base_url}/config", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            return {}


# 便捷函数，兼容原有接口
def compute_score_via_api(
    data_source: str,
    solution_str: str,
    ground_truth: Optional[str] = None,
    extra_info: Optional[Dict[str, Any]] = None,
    base_url: str = DEFAULT_SCOREFLOW_URL
) -> float:
    """
    通过 HTTP API 计算分数（便捷函数）
    
    这个函数兼容原有的 compute_score 接口，
    但通过 HTTP API 而不是直接导入
    """
    try:
        client = ScoreFlowClient(base_url=base_url)
        return client.compute_score(data_source, solution_str, ground_truth, extra_info)
    except ConnectionError:
        logger.error("ScoreFlow server is not running. Scoring will be skipped.")
        return 0.0
    except Exception as e:
        logger.error(f"Failed to compute score via API: {e}")
        return 0.0


# 用于测试连接
def test_connection(base_url: str = DEFAULT_SCOREFLOW_URL) -> bool:
    """测试 ScoreFlow 服务连接"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    if test_connection():
        print("✓ ScoreFlow server is running")
        
        # 测试计算分数
        score = compute_score_via_api(
            data_source="gsm8k",
            solution_str="class Workflow: pass",
            extra_info={"test": True}
        )
        print(f"Test score: {score}")
    else:
        print("✗ ScoreFlow server is not running")
        print("Please start it with: cd services && ./start_scoreflow_reward.sh")