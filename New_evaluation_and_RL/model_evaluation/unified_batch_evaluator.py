"""
Unified batch evaluator for both local and API models
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm

from .model_factory import ModelFactory
from .reward_server_checker import RewardServerChecker
from .score_collector import ScoreCollector
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class UnifiedBatchEvaluator:
    """
    Unified evaluator for testing multiple models (local and API) sequentially
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize unified batch evaluator
        
        Args:
            config: Configuration dictionary containing:
                - test_data_path: Path to test data JSONL file
                - reward_server_url: URL of reward server
                - output_dir: Directory for reports
                - eval_batch_size: Batch size for evaluation
                - max_samples: Maximum samples to evaluate
                - save_intermediate: Save results after each model
        """
        self.test_data_path = Path(config.get('test_data_path'))
        self.reward_server_url = config.get('reward_server_url', 'http://localhost:8899')
        self.output_dir = Path(config.get('output_dir', 'evaluation_reports'))
        self.eval_batch_size = config.get('eval_batch_size', 8)
        self.max_samples = config.get('max_samples', None)
        self.save_intermediate = config.get('save_intermediate', True)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.server_checker = RewardServerChecker(self.reward_server_url)
        self.score_collector = ScoreCollector(self.reward_server_url)
        self.report_generator = ReportGenerator(self.output_dir)
        
        # Storage
        self.model_reports = {}
        self.test_samples = None
        
        logger.info(f"UnifiedBatchEvaluator 初始化完成")
        logger.info(f"  测试数据: {self.test_data_path}")
        logger.info(f"  输出目录: {self.output_dir}")
        logger.info(f"  批次大小: {self.eval_batch_size}")
        logger.info(f"  最大样本: {self.max_samples or '全部'}")
    
    async def evaluate_models(self, model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multiple models sequentially
        
        Args:
            model_configs: List of model configurations
            
        Returns:
            Dictionary containing all reports and comparison
        """
        start_time = datetime.now()
        logger.info(f"开始评估 {len(model_configs)} 个模型")
        
        # Step 1: Validate all configurations
        logger.info("验证模型配置...")
        for config in model_configs:
            try:
                ModelFactory.validate_config(config)
            except Exception as e:
                logger.error(f"模型配置无效 [{config.get('name', 'unknown')}]: {e}")
                raise
        
        # Step 2: Check reward server
        logger.info("检查 Reward Server...")
        if not await self.server_checker.check_server():
            logger.error("Reward Server 未运行")
            raise RuntimeError("Reward Server not available")
        
        # Step 3: Load test data
        logger.info(f"加载测试数据: {self.test_data_path}")
        self.test_samples = self._load_test_data()
        
        if self.max_samples:
            self.test_samples = self.test_samples[:self.max_samples]
            logger.info(f"限制评估样本数: {self.max_samples}")
        
        logger.info(f"加载了 {len(self.test_samples)} 个测试样本")
        
        # Step 4: Evaluate each model
        successful_models = []
        failed_models = []
        
        for i, model_config in enumerate(model_configs, 1):
            model_name = model_config.get('name', 'unnamed')
            model_type = model_config.get('type', 'unknown')
            
            logger.info(f"\n{'='*60}")
            logger.info(f"评估模型 {i}/{len(model_configs)}: {model_name}")
            logger.info(f"模型类型: {model_type}")
            logger.info(f"{'='*60}")
            
            try:
                report = await self._evaluate_single_model(model_config)
                self.model_reports[model_name] = report
                successful_models.append(model_name)
                
                logger.info(f"✓ 模型 {model_name} 评估完成")
                logger.info(f"  总体分数: {report['overall_score']:.2%}")
                logger.info(f"  成功率: {report['success_rate']:.2%}")
                
                # Save intermediate results
                if self.save_intermediate:
                    self._save_intermediate_results(model_name, report)
                
            except Exception as e:
                logger.error(f"✗ 模型 {model_name} 评估失败: {e}")
                import traceback
                traceback.print_exc()
                
                failed_models.append(model_name)
                
                # Store failed evaluation
                self.model_reports[model_name] = {
                    'model': model_config,
                    'error': str(e),
                    'overall_score': 0.0,
                    'success_rate': 0.0,
                    'benchmark_scores': {},
                    'timestamp': datetime.now().isoformat()
                }
        
        # Step 5: Generate comparison report
        logger.info(f"\n{'='*60}")
        logger.info("生成对比报告...")
        logger.info(f"{'='*60}")
        
        comparison = None
        if successful_models:
            comparison = self.report_generator.generate_comparison_report(
                {name: report for name, report in self.model_reports.items() 
                 if name in successful_models}
            )
            
            # Generate detailed CSV
            self.report_generator.generate_detailed_csv(self.model_reports, self.test_samples)
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Summary
        self._print_summary(successful_models, failed_models, total_time)
        
        return {
            'model_reports': self.model_reports,
            'comparison': comparison,
            'successful_models': successful_models,
            'failed_models': failed_models,
            'total_time': total_time,
            'output_dir': str(self.output_dir)
        }
    
    async def _evaluate_single_model(self, model_config: Dict[str, Any]) -> Dict:
        """
        Evaluate a single model (local or API)
        
        Args:
            model_config: Model configuration
            
        Returns:
            Evaluation report
        """
        model_name = model_config.get('name', 'unnamed')
        
        # Create model interface using factory
        model = ModelFactory.create_model(model_config)
        
        try:
            # Initialize model
            logger.info(f"[{model_name}] 初始化模型...")
            await model.initialize()
            
            # Generate solutions
            logger.info(f"[{model_name}] 生成解决方案...")
            solutions = []
            
            # Process in batches for progress display
            batch_size = self.eval_batch_size
            total_batches = (len(self.test_samples) + batch_size - 1) // batch_size
            
            for i in tqdm(range(0, len(self.test_samples), batch_size),
                         desc=f"[{model_name}] 生成",
                         total=total_batches):
                batch = self.test_samples[i:i + batch_size]
                
                # Generate for each sample in batch
                batch_solutions = []
                for sample in batch:
                    try:
                        # Get generation parameters
                        gen_params = model_config.get('generation_params', {})
                        
                        # Generate solution
                        solution = await model.generate_solution(sample, **gen_params)
                        batch_solutions.append(solution)
                        
                    except Exception as e:
                        logger.warning(f"[{model_name}] 生成失败: {e}")
                        batch_solutions.append("")  # Empty solution for failed generation
                
                solutions.extend(batch_solutions)
                
                # Brief pause to avoid overwhelming API
                if model_config.get('type') == 'api':
                    await asyncio.sleep(0.1)
            
            # Evaluate solutions
            logger.info(f"[{model_name}] 计算评估分数...")
            scores = await self.score_collector.batch_evaluate(
                self.test_samples,
                solutions,
                batch_size=self.eval_batch_size,
                model_name=model_name
            )
            
            # Generate report
            logger.info(f"[{model_name}] 生成评估报告...")
            report = await self.report_generator.generate_model_report(
                scores,
                model_config,
                self.test_samples
            )
            
            return report
            
        finally:
            # Clean up model resources
            await model.cleanup()
    
    def _load_test_data(self) -> List[Dict]:
        """
        Load test data from JSONL file
        """
        test_samples = []
        
        if not self.test_data_path.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {self.test_data_path}")
        
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        sample = json.loads(line)
                        test_samples.append(sample)
                    except json.JSONDecodeError as e:
                        logger.warning(f"跳过无效 JSON 行 {line_num}: {e}")
        
        return test_samples
    
    def _save_intermediate_results(self, model_name: str, report: Dict):
        """
        Save intermediate results after each model
        """
        try:
            # Save to timestamped file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intermediate_{model_name}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"中间结果已保存: {filepath}")
            
        except Exception as e:
            logger.warning(f"保存中间结果失败: {e}")
    
    def _print_summary(self, successful_models: List[str], 
                      failed_models: List[str],
                      total_time: float):
        """
        Print evaluation summary
        """
        logger.info("\n" + "="*60)
        logger.info("评估总结")
        logger.info("="*60)
        
        logger.info(f"总耗时: {total_time:.1f} 秒")
        logger.info(f"成功评估: {len(successful_models)} 个模型")
        logger.info(f"失败: {len(failed_models)} 个模型")
        
        if successful_models:
            logger.info("\n成功的模型:")
            for name in successful_models:
                report = self.model_reports[name]
                logger.info(f"  ✓ {name}: {report['overall_score']:.2%}")
        
        if failed_models:
            logger.info("\n失败的模型:")
            for name in failed_models:
                logger.info(f"  ✗ {name}")
        
        # Print top 3 models
        if len(successful_models) >= 2:
            sorted_models = sorted(
                [(name, self.model_reports[name]['overall_score']) 
                 for name in successful_models],
                key=lambda x: x[1],
                reverse=True
            )
            
            logger.info("\nTop 3 模型:")
            for i, (name, score) in enumerate(sorted_models[:3], 1):
                logger.info(f"  {i}. {name}: {score:.2%}")
        
        logger.info(f"\n报告已保存至: {self.output_dir}")
        logger.info(f"  - 模型报告: {self.output_dir}/model_*.json")
        logger.info(f"  - 对比报告: {self.output_dir}/model_comparison.json")
        logger.info(f"  - 图表: {self.output_dir}/charts/")