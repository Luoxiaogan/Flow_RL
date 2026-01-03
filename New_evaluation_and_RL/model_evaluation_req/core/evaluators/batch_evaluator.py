"""
Batch model evaluator for testing multiple models
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import torch

from ..utils.reward_server_checker import RewardServerChecker
from .model_evaluator import ModelEvaluator
from ..utils.score_collector import ScoreCollector
from ..utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class BatchModelEvaluator:
    """
    Evaluates multiple models on the same test set and generates comparison reports
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize batch evaluator
        
        Args:
            config: Configuration dictionary containing:
                - test_data_path: Path to test data JSONL file
                - reward_server_url: URL of reward server (default: http://localhost:8899)
                - output_dir: Directory for reports (default: evaluation_reports)
                - eval_batch_size: Batch size for evaluation (default: 8)
                - max_samples: Maximum samples to evaluate (default: None for all)
                - generation_params: Parameters for text generation
        """
        self.test_data_path = Path(config.get('test_data_path'))
        self.reward_server_url = config.get('reward_server_url', 'http://localhost:8899')
        self.output_dir = Path(config.get('output_dir', 'evaluation_reports'))
        self.eval_batch_size = config.get('eval_batch_size', 8)
        self.max_samples = config.get('max_samples', None)
        
        # Generation parameters
        self.generation_params = config.get('generation_params', {})
        self.generation_params.setdefault('max_new_tokens', 4096)
        self.generation_params.setdefault('temperature', 0.7)
        self.generation_params.setdefault('top_p', 0.9)
        
        # Initialize components
        self.server_checker = RewardServerChecker(self.reward_server_url)
        self.score_collector = ScoreCollector(self.reward_server_url)
        self.report_generator = ReportGenerator(self.output_dir)
        
        # Storage for results
        self.model_reports = {}
        self.test_samples = None
        
        logger.info(f"BatchModelEvaluator initialized")
        logger.info(f"  Test data: {self.test_data_path}")
        logger.info(f"  Output dir: {self.output_dir}")
        logger.info(f"  Batch size: {self.eval_batch_size}")
        logger.info(f"  Max samples: {self.max_samples or 'all'}")
    
    def evaluate_models(self, model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multiple models and generate comparison report
        
        Args:
            model_configs: List of model configurations, each containing:
                - name: Model identifier/name
                - path: Path to model checkpoint or HuggingFace model ID
                - type: Model type (optional, for special handling)
                - generation_params: Override generation parameters (optional)
        
        Returns:
            Dictionary containing all reports and comparison
        """
        logger.info(f"开始评估 {len(model_configs)} 个模型")
        
        # Step 1: Check reward server
        logger.info("检查 Reward Server...")
        if not self.server_checker.check_server():
            logger.error("Reward Server 未运行，请先启动")
            logger.error("运行: bash New_evaluation_and_RL/servers_and_proxy/start_scoreflow_reward.sh")
            raise RuntimeError("Reward Server not available")
        
        # Step 2: Load test data
        logger.info(f"加载测试数据: {self.test_data_path}")
        self.test_samples = self._load_test_data()
        
        if self.max_samples:
            self.test_samples = self.test_samples[:self.max_samples]
            logger.info(f"限制评估样本数: {self.max_samples}")
        
        logger.info(f"加载了 {len(self.test_samples)} 个测试样本")
        
        # Step 3: Evaluate each model
        for i, model_config in enumerate(model_configs, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"评估模型 {i}/{len(model_configs)}: {model_config['name']}")
            logger.info(f"{'='*60}")
            
            try:
                report = self._evaluate_single_model(model_config)
                self.model_reports[model_config['name']] = report
                logger.info(f"✓ 模型 {model_config['name']} 评估完成")
                logger.info(f"  Overall Score: {report['overall_score']:.2%}")
                logger.info(f"  Success Rate: {report['success_rate']:.2%}")
            except Exception as e:
                logger.error(f"✗ 模型 {model_config['name']} 评估失败: {e}")
                import traceback
                traceback.print_exc()
                # Store failed evaluation
                self.model_reports[model_config['name']] = {
                    'model': model_config,
                    'error': str(e),
                    'overall_score': 0.0,
                    'success_rate': 0.0,
                    'benchmark_scores': {}
                }
        
        # Step 4: Generate comparison report
        logger.info(f"\n{'='*60}")
        logger.info("生成对比报告...")
        logger.info(f"{'='*60}")
        
        comparison = self.report_generator.generate_comparison_report(self.model_reports)
        
        # Step 5: Generate detailed CSV
        self.report_generator.generate_detailed_csv(self.model_reports, self.test_samples)
        
        # Summary
        self._print_summary(comparison)
        
        return {
            'model_reports': self.model_reports,
            'comparison': comparison,
            'output_dir': str(self.output_dir)
        }
    
    def _evaluate_single_model(self, model_config: Dict[str, Any]) -> Dict:
        """
        Evaluate a single model
        
        Args:
            model_config: Model configuration
            
        Returns:
            Evaluation report
        """
        model_name = model_config['name']
        model_path = model_config['path']
        
        # Create model evaluator
        evaluator = ModelEvaluator(model_name=model_name)
        
        try:
            # Load model
            evaluator.load_model(model_path)

            # Get generation parameters (merge with defaults)
            gen_params = {**self.generation_params}
            if 'generation_params' in model_config:
                gen_params.update(model_config['generation_params'])

            # Generate solutions
            logger.info(f"[{model_name}] 生成解决方案...")
            solutions = evaluator.generate_solutions(
                self.test_samples,
                batch_size=self.eval_batch_size,
                **gen_params
            )

            # Evaluate solutions
            logger.info(f"[{model_name}] 计算评估分数...")
            scores = self.score_collector.batch_evaluate(
                self.test_samples,
                solutions,
                batch_size=self.eval_batch_size,
                model_name=model_name
            )

            # Generate report
            logger.info(f"[{model_name}] 生成评估报告...")
            report = self.report_generator.generate_model_report(
                scores,
                model_config,
                self.test_samples
            )
            
            return report
            
        finally:
            # Clear model from memory
            evaluator.clear_cache()
            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def _load_test_data(self) -> List[Dict]:
        """
        Load test data from JSONL file
        """
        test_samples = []
        
        if not self.test_data_path.exists():
            raise FileNotFoundError(f"Test data file not found: {self.test_data_path}")
        
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        sample = json.loads(line)
                        sample['ground_truth'] = sample['reward_model']['ground_truth']
                        del sample['reward_model']
                        test_samples.append(sample)
                    except json.JSONDecodeError as e:
                        logger.warning(f"跳过无效 JSON 行 {line_num}: {e}")
        
        return test_samples
    
    def _print_summary(self, comparison: Dict):
        """
        Print evaluation summary
        """
        logger.info("\n" + "="*60)
        logger.info("评估总结")
        logger.info("="*60)
        
        if comparison and 'models' in comparison:
            logger.info(f"评估模型数: {comparison['num_models']}")
            logger.info(f"最佳模型: {comparison['rankings']['best_model']}")
            logger.info(f"最差模型: {comparison['rankings']['worst_model']}")
            
            logger.info("\n模型排名:")
            for i, model in enumerate(comparison['models'][:5], 1):  # Top 5
                logger.info(f"  {i}. {model['name']}: {model['overall_score']:.2%}")
            
            if len(comparison['models']) > 5:
                logger.info(f"  ... ({len(comparison['models']) - 5} more models)")
        
        logger.info(f"\n报告已保存至: {self.output_dir}")
        logger.info(f"  - 模型报告: {self.output_dir}/model_*.json")
        logger.info(f"  - 对比报告: {self.output_dir}/model_comparison.json")
        logger.info(f"  - 图表: {self.output_dir}/charts/")


def main():
    """
    Example usage of BatchModelEvaluator
    """
    # Configuration
    config = {
        'test_data_path': 'test_data.jsonl',
        'reward_server_url': 'http://localhost:8899',
        'output_dir': 'evaluation_reports',
        'eval_batch_size': 4,
        'max_samples': 10,  # For testing
        'generation_params': {
            'max_new_tokens': 2048,
            'temperature': 0.7,
            'top_p': 0.9
        }
    }

    # Model configurations
    model_configs = [
        {
            'name': 'Qwen2.5-7B',
            'path': 'Qwen/Qwen2.5-7B-Instruct'
        },
        {
            'name': 'LLaMA3-8B',
            'path': 'meta-llama/Llama-3.1-8B-Instruct'
        },
        {
            'name': 'Fine-tuned-v1',
            'path': './checkpoints/checkpoint-1000',
            'generation_params': {
                'temperature': 0.8  # Override for this model
            }
        }
    ]

    # Run evaluation
    evaluator = BatchModelEvaluator(config)
    results = evaluator.evaluate_models(model_configs)

    print(f"\nEvaluation complete! Reports saved to: {results['output_dir']}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    main()