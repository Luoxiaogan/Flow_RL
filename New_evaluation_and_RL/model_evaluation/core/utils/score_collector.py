"""
Score collector for interfacing with reward server
"""
import os
import aiohttp
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from tqdm.asyncio import tqdm
from .realtime_data_collector import RealtimeDataCollector

logger = logging.getLogger(__name__)

class ScoreCollector:
    """
    Collects evaluation scores from reward server
    """
    
    def __init__(self, server_url: str = 'http://localhost:8899',
                 enable_realtime_collection: bool = False,
                 collection_output_dir: str = "evaluation_data",
                 checkpoint_interval: int = 10):
        """
        Initialize score collector

        Args:
            server_url: URL of the reward server
            enable_realtime_collection: Enable realtime data collection
            collection_output_dir: Directory for realtime data collection
            checkpoint_interval: Save checkpoint every N records
        """
        self.server_url = server_url
        self.compute_endpoint = f"{server_url}/compute_score"
        self._clear_proxy_settings()

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        # Realtime data collector
        self.enable_realtime_collection = enable_realtime_collection
        self.data_collector = None
        if enable_realtime_collection:
            self.data_collector = RealtimeDataCollector(
                output_dir=collection_output_dir,
                checkpoint_interval=checkpoint_interval
            )
            logger.info(f"实时数据采集已启用: {collection_output_dir}")
    
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
    
    async def compute_score(self, request_data: Dict) -> Dict:
        """
        Send single evaluation request to reward server
        
        Args:
            request_data: Request data containing solution and metadata
            
        Returns:
            Response from reward server
        """
        self.total_requests += 1
        
        try:
            self._clear_proxy_settings()
            
            # Create session with longer timeout for workflow execution
            timeout = aiohttp.ClientTimeout(total=1200)  # 5 minutes
            connector = aiohttp.TCPConnector(force_close=True)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                trust_env=False
            ) as session:
                async with session.post(
                    self.compute_endpoint,
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    
                    if result.get('success', False):
                        self.successful_requests += 1
                        return result
                    else:
                        self.failed_requests += 1
                        logger.warning(f"评估失败: {result.get('error', 'Unknown error')}")
                        return result
                        
        except asyncio.TimeoutError:
            self.failed_requests += 1
            logger.error("请求超时 (5分钟)")
            return {'success': False, 'error': 'Timeout', 'score': 0.0}
            
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"请求失败: {e}")
            return {'success': False, 'error': str(e), 'score': 0.0}
    
    async def batch_evaluate(self, test_samples: List[Dict],
                           solutions: List[str],
                           batch_size: int = 2,
                           model_name: str = None,
                           skip_processed: bool = True) -> List[Dict]:
        """
        Evaluate multiple samples with concurrency control

        Args:
            test_samples: List of test samples
            solutions: List of generated solutions
            batch_size: Maximum concurrent requests
            model_name: Optional model name for logging
            skip_processed: Skip already processed samples when using realtime collection

        Returns:
            List of evaluation results
        """
        if len(test_samples) != len(solutions):
            raise ValueError(f"样本数 ({len(test_samples)}) 与解决方案数 ({len(solutions)}) 不匹配")

        # Filter out already processed samples if realtime collection is enabled
        if self.enable_realtime_collection and skip_processed:
            unprocessed_indices = []
            for i, sample in enumerate(test_samples):
                if not self.data_collector.is_sample_processed(sample):
                    unprocessed_indices.append(i)

            if len(unprocessed_indices) < len(test_samples):
                logger.info(f"跳过已处理样本: {len(test_samples) - len(unprocessed_indices)}/{len(test_samples)}")

                # Filter samples and solutions
                test_samples = [test_samples[i] for i in unprocessed_indices]
                solutions = [solutions[i] for i in unprocessed_indices]

                if not test_samples:
                    logger.info("所有样本已处理完成")
                    return []

        model_label = f"[{model_name}] " if model_name else ""
        logger.info(f"{model_label}开始批量评估 {len(test_samples)} 个样本 (并发数: {batch_size})")

        # Mark evaluation as incomplete for recovery
        if self.enable_realtime_collection:
            await self.data_collector.mark_incomplete()
        
        # Prepare all request data
        all_requests = []
        print("🤣:",solutions)
        for sample, solution in zip(test_samples, solutions):
            if not solution:
                all_requests.append(None)
                continue
            
            data_source = sample.get('data_source', 'unknown')
            print("🤣v:",solution)
            request_data = {
                'data_source': data_source,
                'solution_str': solution,
                'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': sample.get('extra_info', {}),
                'model_name': model_name  # Add model name for tracking
            }
            all_requests.append(request_data)
        
        # Process with concurrency control
        results = []
        semaphore = asyncio.Semaphore(batch_size)
        latencies = []  # Track request latencies

        async def process_with_semaphore(request_data, index, sample, solution):
            """Process single request with semaphore control"""
            if request_data is None:
                result = {'success': False, 'error': 'No solution generated', 'score': 0.0, 'index': index}
                latency = 0
            else:
                async with semaphore:
                    start_time = time.time()
                    result = await self.compute_score(request_data)
                    latency = time.time() - start_time
                    result['index'] = index  # Add index for reordering

            # Record to realtime collector if enabled
            if self.enable_realtime_collection:
                await self.data_collector.record_evaluation(
                    sample=sample,
                    model_name=model_name or 'unknown',
                    solution=solution or '',
                    result=result,
                    latency=latency
                )

            return result, latency

        # Create tasks for all requests
        tasks = [
            process_with_semaphore(req, i, sample, solution)
            for i, (req, sample, solution) in enumerate(zip(all_requests, test_samples, solutions))
        ]

        # Process with progress bar
        desc = f"{model_label}评估进度"
        results_with_idx = []
        for task in tqdm.as_completed(tasks, desc=desc, total=len(tasks)):
            result, latency = await task
            results_with_idx.append(result)
            latencies.append(latency)
        
        # Reorder results to match input order
        ordered_results = sorted(results_with_idx, key=lambda x: x['index'])
        for r in ordered_results:
            r.pop('index', None)  # Remove index field
        
        # Log statistics
        self._log_statistics(ordered_results, model_name)

        # Mark evaluation as complete if realtime collection is enabled
        if self.enable_realtime_collection:
            await self.data_collector.mark_complete()
            logger.info(f"实时数据采集完成: {self.data_collector.get_statistics()}")

        return ordered_results
    
    def _log_statistics(self, results: List[Dict], model_name: str = None):
        """
        Log evaluation statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        scores = [r.get('score', 0.0) for r in results if r.get('success', False)]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        model_label = f"[{model_name}] " if model_name else ""
        logger.info(f"{model_label}评估统计:")
        logger.info(f"  总数: {total}")
        logger.info(f"  成功: {successful} ({successful/total*100:.1f}%)")
        logger.info(f"  失败: {failed} ({failed/total*100:.1f}%)")
        logger.info(f"  平均分数: {avg_score:.3f}")
    
    def get_statistics(self) -> Dict:
        """
        Get collector statistics
        """
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / self.total_requests if self.total_requests > 0 else 0
        }
    
    def reset_statistics(self):
        """
        Reset statistics counters
        """
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0