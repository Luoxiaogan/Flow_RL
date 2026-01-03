"""
Evaluation callback for automatic model evaluation during training
"""
import os
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationCallback(TrainerCallback):
    """
    Callback to automatically evaluate model checkpoints during training
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize evaluation callback
        
        Args:
            config: Configuration dictionary containing:
                - test_data_path: Path to test data JSONL file
                - reward_server_url: URL of reward server
                - eval_interval: Evaluate every N checkpoints (default: 1)
                - eval_batch_size: Batch size for evaluation (default: 8)
                - async_eval: Run evaluation asynchronously (default: True)
                - output_dir: Directory to save evaluation reports
                - max_samples: Maximum samples to evaluate (default: None for all)
        """
        self.test_data_path = config.get('test_data_path')
        self.reward_server_url = config.get('reward_server_url', 'http://localhost:8899')
        self.eval_interval = config.get('eval_interval', 1)
        self.eval_batch_size = config.get('eval_batch_size', 8)
        self.async_eval = config.get('async_eval', True)
        self.output_dir = Path(config.get('output_dir', 'evaluation_reports'))
        self.max_samples = config.get('max_samples', None)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track evaluation status
        self.evaluations_in_progress = {}
        self.evaluation_results = {}
        
        # Initialize components (lazy loading)
        self._server_checker = None
        self._model_evaluator = None
        self._score_collector = None
        self._report_generator = None
        
        logger.info(f"EvaluationCallback initialized with config: {config}")
    
    def on_save(self, args: TrainingArguments, state: TrainerState, 
                control: TrainerControl, **kwargs) -> TrainerControl:
        """
        Called when a checkpoint is saved
        """
        # Check if we should evaluate this checkpoint
        checkpoint_num = state.global_step // args.save_steps
        if checkpoint_num % self.eval_interval != 0:
            logger.info(f"Skipping evaluation for checkpoint {state.global_step} (interval: {self.eval_interval})")
            return control
        
        checkpoint_dir = f"{args.output_dir}/checkpoint-{state.global_step}"
        logger.info(f"Starting evaluation for checkpoint: {checkpoint_dir}")
        
        if self.async_eval:
            # Run evaluation in background thread
            thread = threading.Thread(
                target=self._run_evaluation_sync,
                args=(checkpoint_dir, state.global_step, args.output_dir)
            )
            thread.daemon = True
            thread.start()
            self.evaluations_in_progress[state.global_step] = thread
            logger.info(f"Started async evaluation for checkpoint {state.global_step}")
        else:
            # Run evaluation synchronously
            self._run_evaluation_sync(checkpoint_dir, state.global_step, args.output_dir)
        
        return control
    
    def on_train_end(self, args: TrainingArguments, state: TrainerState, 
                     control: TrainerControl, **kwargs) -> TrainerControl:
        """
        Called at the end of training
        """
        # Wait for any ongoing evaluations to complete
        if self.evaluations_in_progress:
            logger.info("Waiting for ongoing evaluations to complete...")
            for step, thread in self.evaluations_in_progress.items():
                if thread.is_alive():
                    logger.info(f"Waiting for evaluation of checkpoint {step}...")
                    thread.join(timeout=600)  # Wait max 10 minutes
        
        # Generate final summary report
        if self.evaluation_results:
            self._generate_summary_report()
        
        logger.info("Training and evaluation completed")
        return control
    
    def _run_evaluation_sync(self, checkpoint_dir: str, global_step: int, output_dir: str):
        """
        Run evaluation synchronously (wrapper for async function)
        """
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run async evaluation
            result = loop.run_until_complete(
                self._run_evaluation_async(checkpoint_dir, global_step, output_dir)
            )
            
            # Store result
            self.evaluation_results[global_step] = result
            
            # Clean up
            loop.close()
            
        except Exception as e:
            logger.error(f"Evaluation failed for checkpoint {global_step}: {e}")
            import traceback
            traceback.print_exc()
    
    async def _run_evaluation_async(self, checkpoint_dir: str, global_step: int, output_dir: str):
        """
        Run evaluation asynchronously
        """
        try:
            # Lazy load components
            if self._server_checker is None:
                from .reward_server_checker import RewardServerChecker
                self._server_checker = RewardServerChecker(self.reward_server_url)
            
            if self._model_evaluator is None:
                from .model_evaluator import ModelEvaluator
                self._model_evaluator = ModelEvaluator()
            
            if self._score_collector is None:
                from .score_collector import ScoreCollector
                self._score_collector = ScoreCollector(self.reward_server_url)
            
            if self._report_generator is None:
                from .report_generator import ReportGenerator
                self._report_generator = ReportGenerator(self.output_dir)
            
            # Step 1: Check reward server
            logger.info("检查 Reward Server 状态...")
            if not await self._server_checker.check_server():
                logger.error("Reward Server 未运行，请先启动 reward server")
                logger.error("运行命令: cd New_evaluation_and_RL/reward_server && python scoreflow_reward_server.py")
                return None
            
            logger.info("Reward Server 正常运行")
            
            # Step 2: Load test data
            logger.info(f"加载测试数据: {self.test_data_path}")
            test_samples = self._load_test_data()
            
            if self.max_samples:
                test_samples = test_samples[:self.max_samples]
                logger.info(f"限制评估样本数: {self.max_samples}")
            
            logger.info(f"加载了 {len(test_samples)} 个测试样本")
            
            # Step 3: Load model and generate solutions
            logger.info(f"加载模型: {checkpoint_dir}")
            await self._model_evaluator.load_model(checkpoint_dir)
            
            logger.info("生成解决方案...")
            solutions = await self._model_evaluator.generate_solutions(
                test_samples, 
                batch_size=self.eval_batch_size
            )
            
            # Step 4: Collect scores from reward server
            logger.info("计算评估分数...")
            scores = await self._score_collector.batch_evaluate(
                test_samples, 
                solutions,
                batch_size=self.eval_batch_size
            )
            
            # Step 5: Generate report
            logger.info("生成评估报告...")
            checkpoint_info = {
                'step': global_step,
                'path': checkpoint_dir,
                'output_dir': output_dir
            }
            
            report = await self._report_generator.generate_report(
                scores, 
                checkpoint_info,
                test_samples
            )
            
            logger.info(f"评估完成 - Checkpoint {global_step}")
            logger.info(f"总体得分: {report.get('overall_score', 0):.2%}")
            
            # Print benchmark scores
            for benchmark, stats in report.get('benchmark_scores', {}).items():
                logger.info(f"  {benchmark}: {stats['mean_score']:.2%} (n={stats['num_samples']})")
            
            return report
            
        except Exception as e:
            logger.error(f"评估过程出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_test_data(self):
        """
        Load test data from JSONL file
        """
        test_samples = []
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    sample = json.loads(line)
                    test_samples.append(sample)
        return test_samples
    
    def _generate_summary_report(self):
        """
        Generate summary report for all evaluations
        """
        if not self.evaluation_results:
            return
        
        summary = {
            'total_checkpoints': len(self.evaluation_results),
            'checkpoints': []
        }
        
        for step, result in sorted(self.evaluation_results.items()):
            if result:
                summary['checkpoints'].append({
                    'step': step,
                    'overall_score': result.get('overall_score', 0),
                    'benchmark_scores': result.get('benchmark_scores', {})
                })
        
        # Save summary
        summary_path = self.output_dir / 'evaluation_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"评估总结已保存: {summary_path}")