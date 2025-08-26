# -*- coding: utf-8 -*-
"""
Score collector for interfacing with reward server - 同步版本
使用requests替代aiohttp，移除async/await
"""
import os
import requests
import time
import logging
import json
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ScoreCollector:
    """
    Collects evaluation scores from reward server - 同步版本
    """
    
    def __init__(self, server_url: str = 'http://localhost:8899'):
        """
        Initialize score collector
        
        Args:
            server_url: URL of the reward server
        """
        self.server_url = server_url
        self.compute_endpoint = f"{server_url}/compute_score"
        
        # Clear proxy settings
        self._clear_proxy_settings()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
    
    def _clear_proxy_settings(self):
        """
        Clear proxy environment variables for localhost communication
        """
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        
        proxy_vars = ['http_proxy', 'https_proxy', 'all_proxy',
                      'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
        
        for proxy_var in proxy_vars:
            if proxy_var in os.environ:
                del os.environ[proxy_var]
    
    def compute_score(self, request_data: Dict) -> Dict:
        """
        Send single evaluation request to reward server - 同步版本
        
        Args:
            request_data: Request data containing solution and metadata
            
        Returns:
            Response from reward server
        """
        self.total_requests += 1
        
        try:
            # Clear proxy before request
            self._clear_proxy_settings()
            
            # Make synchronous request using requests
            response = requests.post(
                self.compute_endpoint,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=300,  # 5 minutes timeout
                proxies={'http': None, 'https': None}  # Ignore system proxy
            )
            
            result = response.json()
            
            if result.get('success', False):
                self.successful_requests += 1
                return result
            else:
                self.failed_requests += 1
                logger.warning(f"评估失败: {result.get('error', 'Unknown error')}")
                return result
                        
        except requests.exceptions.Timeout:
            self.failed_requests += 1
            logger.error("请求超时 (5分钟)")
            return {'success': False, 'error': 'Timeout', 'score': 0.0}
            
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"请求失败: {e}")
            return {'success': False, 'error': str(e), 'score': 0.0}
    
    def batch_evaluate(self, test_samples: List[Dict], 
                      solutions: List[str],
                      batch_size: int = 8) -> List[Dict]:
        """
        Evaluate multiple samples with threading for concurrency - 同步版本
        
        Args:
            test_samples: List of test samples
            solutions: List of generated solutions
            batch_size: Maximum concurrent requests
            
        Returns:
            List of evaluation results
        """
        if len(test_samples) != len(solutions):
            raise ValueError(f"样本数 ({len(test_samples)}) 与解决方案数 ({len(solutions)}) 不匹配")
        
        logger.info(f"开始批量评估 {len(test_samples)} 个样本 (并发数: {batch_size})")
        
        # Prepare all request data
        all_requests = []
        for i, (sample, solution) in enumerate(zip(test_samples, solutions)):
            # Skip if no solution was generated
            if not solution:
                all_requests.append((i, None))
                continue
            
            # Extract data source with fallback
            data_source = sample.get('data_source', 'unknown')
            
            # Prepare request
            request_data = {
                'data_source': data_source,
                'solution_str': solution,
                'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': sample.get('extra_info', {})
            }
            
            # 增强日志：记录生成文本的格式信息
            logger.debug(f"样本 {i} - 数据源: {data_source}")
            logger.debug(f"生成文本长度: {len(solution)} 字符")
            
            # 检查是否包含期望的格式标记
            if "```python" in solution:
                logger.debug("✓ 检测到```python格式标记")
            elif "<code>" in solution:
                logger.warning("⚠️ 检测到旧格式<code>标记（reward server可能不支持）")
            else:
                logger.warning("⚠️ 未检测到代码格式标记，可能导致提取失败")
            
            # 记录前500字符用于调试
            preview = solution[:500] + "..." if len(solution) > 500 else solution
            logger.debug(f"生成文本预览: {preview}")
            
            all_requests.append((i, request_data))
        
        # Process requests using ThreadPoolExecutor for concurrency
        results = [None] * len(test_samples)
        
        def process_request(item):
            """Process single request"""
            index, request_data = item
            
            if request_data is None:
                return index, {'success': False, 'error': 'No solution generated', 'score': 0.0}
            
            result = self.compute_score(request_data)
            
            # 增强日志：记录评估结果详情
            if result.get('success'):
                logger.debug(f"样本 {index} 评估成功: 分数={result.get('score', 0)}")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"样本 {index} 评估失败: {error_msg}")
                
                # 分析失败原因
                if 'no_workflow_code' in error_msg.lower() or 'no workflow' in error_msg.lower():
                    logger.warning(f"  → 原因: workflow代码提取失败")
                elif 'timeout' in error_msg.lower():
                    logger.warning(f"  → 原因: 执行超时")
                elif 'connection' in error_msg.lower() or 'network' in error_msg.lower():
                    logger.warning(f"  → 原因: 网络连接问题")
            
            return index, result
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(process_request, req): req[0] 
                for req in all_requests
            }
            
            # Process results with progress bar
            for future in tqdm(as_completed(future_to_index), 
                             desc="评估进度", 
                             total=len(future_to_index)):
                try:
                    index, result = future.result()
                    results[index] = result
                except Exception as e:
                    index = future_to_index[future]
                    logger.error(f"Task {index} failed: {e}")
                    results[index] = {'success': False, 'error': str(e), 'score': 0.0}
        
        # Log statistics
        self._log_statistics(results)
        
        return results
    
    def _log_statistics(self, results: List[Dict]):
        """
        Log evaluation statistics
        
        Args:
            results: List of evaluation results
        """
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        scores = [r.get('score', 0.0) for r in results if r.get('success', False)]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        logger.info(f"评估统计:")
        logger.info(f"  总数: {total}")
        logger.info(f"  成功: {successful} ({successful/total*100:.1f}%)")
        logger.info(f"  失败: {failed} ({failed/total*100:.1f}%)")
        logger.info(f"  平均分数: {avg_score:.3f}")
    
    def get_statistics(self) -> Dict:
        """
        Get collector statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / self.total_requests if self.total_requests > 0 else 0
        }


# Test function - 同步版本
def test_score_collector():
    """
    Test the score collector - 同步版本
    """
    collector = ScoreCollector()
    
    # Test request data
    test_request = {
        'data_source': 'workflow_gsm8k',
        'solution_str': '<code>class Workflow: pass</code>',
        'ground_truth': 'default',
        'extra_info': {
            'test_cases': [1, 2, 3],
            'data_path': 'test.jsonl'
        }
    }
    
    # Test single request
    print("Testing single request...")
    result = collector.compute_score(test_request)
    print(f"Result: {result}")
    
    # Test batch evaluation
    test_samples = [
        {
            'data_source': 'workflow_gsm8k',
            'reward_model': {'ground_truth': 'default'},
            'extra_info': {'test_cases': [i]}
        }
        for i in range(3)
    ]
    
    test_solutions = [
        '<code>class Workflow: pass</code>'
        for _ in range(3)
    ]
    
    print("\nTesting batch evaluation...")
    results = collector.batch_evaluate(test_samples, test_solutions, batch_size=2)
    
    for i, result in enumerate(results):
        print(f"Sample {i}: {result}")
    
    print("\nStatistics:", collector.get_statistics())


if __name__ == "__main__":
    test_score_collector()