"""
Realtime data collector with checkpoint recovery support
实时数据采集器，支持断点续测
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
import aiofiles
import hashlib
from asyncio import Lock

logger = logging.getLogger(__name__)

class RealtimeDataCollector:
    """
    Realtime evaluation data collector with checkpoint recovery
    实时采集评测数据并支持断点续测
    """

    def __init__(self, output_dir: str = "evaluation_data",
                 checkpoint_interval: int = 10):
        """
        Initialize realtime data collector

        Args:
            output_dir: Directory to save evaluation data
            checkpoint_interval: Save checkpoint every N records
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_interval = checkpoint_interval

        # File paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_file = self.output_dir / f"evaluation_data_{timestamp}.jsonl"
        self.checkpoint_file = self.output_dir / f"checkpoint_{timestamp}.json"
        self.resume_file = self.output_dir / "resume_info.json"

        # Runtime state
        self.processed_samples: Set[str] = set()
        self.record_count = 0
        self.start_time = datetime.now()

        # Async write lock
        self.write_lock = Lock()

        # Load resume info if exists
        self._load_resume_info()

        logger.info(f"实时数据采集器初始化完成")
        logger.info(f"  数据文件: {self.data_file}")
        logger.info(f"  检查点文件: {self.checkpoint_file}")
        logger.info(f"  已处理样本数: {len(self.processed_samples)}")

    def _load_resume_info(self):
        """
        Load resume information from previous runs
        """
        if self.resume_file.exists():
            try:
                with open(self.resume_file, 'r', encoding='utf-8') as f:
                    resume_info = json.load(f)

                # Find the latest incomplete evaluation
                if resume_info.get('status') == 'incomplete':
                    previous_data_file = Path(resume_info['data_file'])
                    previous_checkpoint_file = Path(resume_info['checkpoint_file'])

                    if previous_data_file.exists() and previous_checkpoint_file.exists():
                        # Load checkpoint
                        with open(previous_checkpoint_file, 'r', encoding='utf-8') as f:
                            checkpoint = json.load(f)

                        self.processed_samples = set(checkpoint.get('processed_samples', []))
                        self.record_count = checkpoint.get('record_count', 0)

                        # Use previous files for continuation
                        self.data_file = previous_data_file
                        self.checkpoint_file = previous_checkpoint_file

                        logger.info(f"恢复之前的评测进度:")
                        logger.info(f"  已处理记录: {self.record_count}")
                        logger.info(f"  已处理样本: {len(self.processed_samples)}")
            except Exception as e:
                logger.warning(f"加载恢复信息失败: {e}")

    def _generate_sample_id(self, sample: Dict[str, Any]) -> str:
        """
        Generate unique ID for a sample

        Args:
            sample: Test sample

        Returns:
            Unique sample ID
        """
        # Create ID from sample content
        id_source = json.dumps({
            'prompt': sample.get('prompt', ''),
            'data_source': sample.get('data_source', ''),
            'ground_truth': sample.get('reward_model', {}).get('ground_truth', '')
        }, sort_keys=True)

        return hashlib.md5(id_source.encode()).hexdigest()

    def is_sample_processed(self, sample: Dict[str, Any]) -> bool:
        """
        Check if a sample has been processed

        Args:
            sample: Test sample

        Returns:
            True if already processed
        """
        sample_id = self._generate_sample_id(sample)
        return sample_id in self.processed_samples

    def get_unprocessed_samples(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out already processed samples

        Args:
            samples: List of test samples

        Returns:
            List of unprocessed samples
        """
        unprocessed = []
        for sample in samples:
            if not self.is_sample_processed(sample):
                unprocessed.append(sample)

        if len(unprocessed) < len(samples):
            logger.info(f"跳过已处理样本: {len(samples) - len(unprocessed)}/{len(samples)}")

        return unprocessed

    async def record_evaluation(self,
                               sample: Dict[str, Any],
                               model_name: str,
                               solution: str,
                               result: Dict[str, Any],
                               latency: float = None):
        """
        Record single evaluation result in realtime

        Args:
            sample: Test sample
            model_name: Name of the model
            solution: Generated solution
            result: Evaluation result from reward server
            latency: Response latency in seconds
        """
        async with self.write_lock:
            try:
                # Generate sample ID
                sample_id = self._generate_sample_id(sample)

                # Skip if already processed
                if sample_id in self.processed_samples:
                    logger.debug(f"样本 {sample_id[:8]} 已处理，跳过")
                    return

                # Prepare record
                record = {
                    'sample_id': sample_id,
                    'timestamp': datetime.now().isoformat(),
                    'model_name': model_name,
                    'benchmark': sample.get('data_source', 'unknown'),
                    'input': {
                        'prompt': sample.get('prompt', ''),
                        'extra_info': sample.get('extra_info', {})
                    },
                    'output': {
                        'solution': solution,
                        'truncated': len(solution) > 10000  # Mark if solution is too long
                    },
                    'evaluation': {
                        'success': result.get('success', False),
                        'score': result.get('score', 0.0),
                        'error': result.get('error', None),
                        'timeout': 'Timeout' in str(result.get('error', '')),
                        'execution_time': result.get('execution_time', None)
                    },
                    'performance': {
                        'latency': latency,
                        'total_time': result.get('total_time', None)
                    }
                }

                # Write to JSONL file
                async with aiofiles.open(self.data_file, 'a', encoding='utf-8') as f:
                    await f.write(json.dumps(record, ensure_ascii=False) + '\n')

                # Update state
                self.processed_samples.add(sample_id)
                self.record_count += 1

                # Log progress
                if self.record_count % 10 == 0:
                    logger.info(f"已记录 {self.record_count} 条评测数据")

                # Save checkpoint periodically
                if self.record_count % self.checkpoint_interval == 0:
                    await self._save_checkpoint()

            except Exception as e:
                logger.error(f"记录评测数据失败: {e}")

    async def batch_record(self,
                          samples: List[Dict[str, Any]],
                          model_name: str,
                          solutions: List[str],
                          results: List[Dict[str, Any]],
                          latencies: List[float] = None):
        """
        Record multiple evaluation results

        Args:
            samples: List of test samples
            model_name: Name of the model
            solutions: List of generated solutions
            results: List of evaluation results
            latencies: List of response latencies
        """
        if latencies is None:
            latencies = [None] * len(samples)

        tasks = []
        for sample, solution, result, latency in zip(samples, solutions, results, latencies):
            task = self.record_evaluation(sample, model_name, solution, result, latency)
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def _save_checkpoint(self):
        """
        Save checkpoint for recovery
        """
        try:
            checkpoint = {
                'timestamp': datetime.now().isoformat(),
                'data_file': str(self.data_file),
                'record_count': self.record_count,
                'processed_samples': list(self.processed_samples),
                'statistics': self.get_statistics()
            }

            # Write checkpoint atomically
            temp_file = self.checkpoint_file.with_suffix('.tmp')
            async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(checkpoint, ensure_ascii=False, indent=2))

            # Rename to final file
            temp_file.replace(self.checkpoint_file)

            logger.debug(f"保存检查点: {self.record_count} 条记录")

        except Exception as e:
            logger.error(f"保存检查点失败: {e}")

    async def mark_incomplete(self):
        """
        Mark current evaluation as incomplete for future resume
        """
        try:
            resume_info = {
                'status': 'incomplete',
                'data_file': str(self.data_file),
                'checkpoint_file': str(self.checkpoint_file),
                'timestamp': datetime.now().isoformat(),
                'record_count': self.record_count
            }

            async with aiofiles.open(self.resume_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(resume_info, ensure_ascii=False, indent=2))

            logger.info(f"标记评测为未完成状态，可断点续测")

        except Exception as e:
            logger.error(f"保存恢复信息失败: {e}")

    async def mark_complete(self):
        """
        Mark current evaluation as complete
        """
        try:
            # Save final checkpoint
            await self._save_checkpoint()

            # Update resume info
            resume_info = {
                'status': 'complete',
                'data_file': str(self.data_file),
                'checkpoint_file': str(self.checkpoint_file),
                'timestamp': datetime.now().isoformat(),
                'record_count': self.record_count,
                'duration': (datetime.now() - self.start_time).total_seconds()
            }

            async with aiofiles.open(self.resume_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(resume_info, ensure_ascii=False, indent=2))

            logger.info(f"评测完成，共记录 {self.record_count} 条数据")

        except Exception as e:
            logger.error(f"标记完成状态失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current collection statistics

        Returns:
            Statistics dictionary
        """
        return {
            'record_count': self.record_count,
            'unique_samples': len(self.processed_samples),
            'data_file': str(self.data_file),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'start_time': self.start_time.isoformat()
        }

    async def export_summary(self, output_file: str = None):
        """
        Export summary statistics from collected data

        Args:
            output_file: Optional output file path
        """
        if output_file is None:
            output_file = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            # Read all records
            records = []
            async with aiofiles.open(self.data_file, 'r', encoding='utf-8') as f:
                async for line in f:
                    records.append(json.loads(line))

            # Calculate statistics
            total = len(records)
            successful = sum(1 for r in records if r['evaluation']['success'])
            timeouts = sum(1 for r in records if r['evaluation']['timeout'])

            # Group by model and benchmark
            model_stats = {}
            benchmark_stats = {}

            for record in records:
                model = record['model_name']
                benchmark = record['benchmark']
                score = record['evaluation']['score']

                # Model statistics
                if model not in model_stats:
                    model_stats[model] = {'total': 0, 'successful': 0, 'scores': []}
                model_stats[model]['total'] += 1
                if record['evaluation']['success']:
                    model_stats[model]['successful'] += 1
                    model_stats[model]['scores'].append(score)

                # Benchmark statistics
                if benchmark not in benchmark_stats:
                    benchmark_stats[benchmark] = {'total': 0, 'successful': 0, 'scores': []}
                benchmark_stats[benchmark]['total'] += 1
                if record['evaluation']['success']:
                    benchmark_stats[benchmark]['successful'] += 1
                    benchmark_stats[benchmark]['scores'].append(score)

            # Calculate averages
            for stats in [model_stats, benchmark_stats]:
                for key in stats:
                    scores = stats[key]['scores']
                    stats[key]['avg_score'] = sum(scores) / len(scores) if scores else 0
                    stats[key]['success_rate'] = stats[key]['successful'] / stats[key]['total']
                    del stats[key]['scores']  # Remove raw scores from summary

            summary = {
                'total_records': total,
                'successful': successful,
                'failed': total - successful,
                'timeouts': timeouts,
                'success_rate': successful / total if total > 0 else 0,
                'model_statistics': model_stats,
                'benchmark_statistics': benchmark_stats,
                'collection_info': self.get_statistics()
            }

            # Save summary
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(summary, ensure_ascii=False, indent=2))

            logger.info(f"导出汇总统计到: {output_file}")

            return summary

        except Exception as e:
            logger.error(f"导出汇总失败: {e}")
            return None