"""
Hierarchical evaluator for structured model evaluation with incremental reporting
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm

from .unified_batch_evaluator import UnifiedBatchEvaluator
from ..utils.detailed_score_recorder import DetailedScoreRecorder
from ..utils.model_factory import ModelFactory
from ..utils.reward_server_checker import RewardServerChecker
from ..utils.score_collector import ScoreCollector
from ..utils.resource_manager import ModelResourceManager, GlobalResourceTracker
from ..utils.config_validator import ConfigValidator

logger = logging.getLogger(__name__)

class HierarchicalEvaluator(UnifiedBatchEvaluator):
    """
    Hierarchical evaluator that processes models -> benchmarks -> operator groups
    with incremental reporting at each level
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize hierarchical evaluator
        
        Args:
            config: Configuration dictionary with additional fields:
                - hierarchical_mode: Enable hierarchical evaluation
                - incremental_reporting: Enable incremental reports
                - save_sample_scores: Save individual sample scores
                - report_levels: List of report levels to generate
        """
        super().__init__(config)
        
        # Hierarchical evaluation settings
        self.hierarchical_mode = config.get('hierarchical_mode', True)
        self.incremental_reporting = config.get('incremental_reporting', True)
        self.save_sample_scores = config.get('save_sample_scores', True)
        self.report_levels = config.get('report_levels', ['operator', 'benchmark', 'model'])
        
        # Initialize detailed score recorder
        self.score_recorder = DetailedScoreRecorder(self.output_dir)
        
        # Tracking for hierarchical processing
        self.current_hierarchy = {
            'model': None,
            'benchmark': None,
            'operator_group': None
        }
        
        # Initialize incremental report generator (will be created later)
        self.incremental_reporter = None
        
        logger.info(f"分层评估器初始化完成")
        logger.info(f"  分层模式: {self.hierarchical_mode}")
        logger.info(f"  增量报告: {self.incremental_reporting}")
        logger.info(f"  保存样本分数: {self.save_sample_scores}")
        logger.info(f"  报告级别: {self.report_levels}")
    
    async def evaluate_models(self, model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multiple models using hierarchical approach
        
        Args:
            model_configs: List of model configurations
            
        Returns:
            Dictionary containing all reports and comparison
        """
        if self.hierarchical_mode:
            return await self.evaluate_by_hierarchy(model_configs)
        else:
            # Fall back to parent implementation
            return await super().evaluate_models(model_configs)
    
    async def evaluate_by_hierarchy(self, model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate models using hierarchical structure with incremental reporting
        
        Args:
            model_configs: List of model configurations
            
        Returns:
            Comprehensive evaluation results
        """
        start_time = datetime.now()
        logger.info(f"开始分层评估 {len(model_configs)} 个模型")
        
        # Step 1: Validate configurations
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
        
        # Step 3: Load and organize test data by benchmark
        logger.info(f"加载测试数据: {self.test_data_path}")
        self.test_samples = self._load_test_data()
        
        if self.max_samples:
            self.test_samples = self.test_samples[:self.max_samples]
            logger.info(f"限制评估样本数: {self.max_samples}")
        
        # Organize samples by benchmark and operator group
        organized_samples = self._organize_samples_by_hierarchy(self.test_samples)
        
        logger.info(f"数据组织完成:")
        for benchmark, groups in organized_samples.items():
            logger.info(f"  {benchmark}: {len(groups)} 个operator组")
            for group, samples in groups.items():
                logger.info(f"    - {group}: {len(samples)} 个样本")
        
        # Step 4: Process each model hierarchically
        successful_models = []
        failed_models = []
        
        for model_idx, model_config in enumerate(model_configs, 1):
            model_name = model_config.get('name', 'unnamed')
            
            logger.info(f"\n{'='*60}")
            logger.info(f"开始评估模型 {model_idx}/{len(model_configs)}: {model_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Set model context
                self.score_recorder.set_context(model=model_name)
                self.current_hierarchy['model'] = model_name
                
                # Evaluate model hierarchically
                model_report = await self._evaluate_model_hierarchically(
                    model_config, organized_samples
                )
                
                self.model_reports[model_name] = model_report
                successful_models.append(model_name)
                
                # Generate model-level report if enabled
                if 'model' in self.report_levels and self.incremental_reporting:
                    await self._generate_model_report(model_name, model_report)
                
                logger.info(f"✓ 模型 {model_name} 评估完成")
                logger.info(f"  总体分数: {model_report.get('overall_score', 0):.2%}")
                
            except Exception as e:
                logger.error(f"✗ 模型 {model_name} 评估失败: {e}")
                import traceback
                traceback.print_exc()
                
                failed_models.append(model_name)
                self.model_reports[model_name] = {
                    'model': model_config,
                    'error': str(e),
                    'overall_score': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
        
        # Step 5: Generate final comparison report
        logger.info(f"\n{'='*60}")
        logger.info("生成最终对比报告...")
        logger.info(f"{'='*60}")
        
        # Save final detailed scores
        if self.save_sample_scores:
            final_report_path = self.score_recorder.save_final_report()
            logger.info(f"详细评分已保存: {final_report_path}")
        
        # Generate comparison if we have successful models
        comparison = None
        if successful_models and self.report_generator:
            comparison = self.report_generator.generate_comparison_report(
                {name: report for name, report in self.model_reports.items() 
                 if name in successful_models}
            )
            
            # Generate detailed CSV
            self.report_generator.generate_detailed_csv(
                self.model_reports, self.test_samples
            )
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Print summary
        self._print_hierarchical_summary(successful_models, failed_models, total_time)
        
        # Clean up resources
        await self._cleanup_resources()
        
        return {
            'model_reports': self.model_reports,
            'comparison': comparison,
            'successful_models': successful_models,
            'failed_models': failed_models,
            'total_time': total_time,
            'output_dir': str(self.output_dir),
            'detailed_scores_path': final_report_path if self.save_sample_scores else None
        }
    
    def _organize_samples_by_hierarchy(self, samples: List[Dict]) -> Dict[str, Dict[str, List]]:
        """
        Organize samples by benchmark and operator group
        
        Args:
            samples: List of test samples
            
        Returns:
            Nested dictionary: benchmark -> operator_group -> samples
        """
        organized = {}
        
        for sample in samples:
            # Extract benchmark from data_source
            data_source = sample.get('data_source', 'unknown')
            if data_source.startswith('workflow_'):
                benchmark = data_source.replace('workflow_', '')
            else:
                benchmark = data_source
            
            # Extract operator group (if available in extra_info)
            extra_info = sample.get('extra_info', {})
            operator_group = extra_info.get('operator_group', 'default')
            
            # Initialize nested structure
            if benchmark not in organized:
                organized[benchmark] = {}
            if operator_group not in organized[benchmark]:
                organized[benchmark][operator_group] = []
            
            # Add sample to appropriate group
            organized[benchmark][operator_group].append(sample)
        
        return organized
    
    async def _evaluate_model_hierarchically(self, model_config: Dict, 
                                            organized_samples: Dict) -> Dict:
        """
        Evaluate a single model through the hierarchy
        
        Args:
            model_config: Model configuration
            organized_samples: Samples organized by benchmark and operator group
            
        Returns:
            Model evaluation report
        """
        model_name = model_config.get('name', 'unnamed')
        model_start_time = datetime.now()
        
        # Create model interface
        model_interface = ModelFactory.create_model(model_config)
        
        # Use resource manager
        async with ModelResourceManager(model_interface) as model:
            try:
                # Register with global tracker
                await GlobalResourceTracker.register(model)
                
                # Results storage
                all_scores = []
                benchmark_reports = {}
                
                # Process each benchmark
                for benchmark_idx, (benchmark, operator_groups) in enumerate(
                    organized_samples.items(), 1
                ):
                    logger.info(f"\n[{model_name}] 处理基准 {benchmark_idx}/{len(organized_samples)}: {benchmark}")
                    
                    # Set benchmark context
                    self.score_recorder.set_context(
                        model=model_name, 
                        benchmark=benchmark
                    )
                    self.current_hierarchy['benchmark'] = benchmark
                    
                    # Evaluate benchmark
                    benchmark_report = await self._evaluate_benchmark(
                        model, model_config, benchmark, operator_groups
                    )
                    
                    benchmark_reports[benchmark] = benchmark_report
                    all_scores.extend(benchmark_report['scores'])
                    
                    # Generate benchmark-level report if enabled
                    if 'benchmark' in self.report_levels and self.incremental_reporting:
                        await self._generate_benchmark_report(
                            model_name, benchmark, benchmark_report
                        )
                
                # Calculate overall statistics
                overall_score = self._calculate_overall_score(all_scores)
                success_rate = sum(1 for s in all_scores if s.get('success', False)) / len(all_scores) if all_scores else 0
                
                # Create model report
                model_report = {
                    'model': model_config,
                    'timestamp': datetime.now().isoformat(),
                    'duration': (datetime.now() - model_start_time).total_seconds(),
                    'total_samples': len(all_scores),
                    'benchmark_reports': benchmark_reports,
                    'overall_score': overall_score,
                    'success_rate': success_rate,
                    'evaluation_results': self._calculate_statistics(all_scores, self.test_samples)
                }
                
                return model_report
                
            finally:
                # Unregister from global tracker
                await GlobalResourceTracker.unregister(model)
    
    async def _evaluate_benchmark(self, model, model_config: Dict,
                                  benchmark: str, operator_groups: Dict) -> Dict:
        """
        Evaluate a single benchmark
        
        Args:
            model: Model interface
            model_config: Model configuration
            benchmark: Benchmark name
            operator_groups: Operator groups with samples
            
        Returns:
            Benchmark evaluation report
        """
        benchmark_start_time = datetime.now()
        all_benchmark_scores = []
        operator_reports = {}
        
        # Process each operator group
        for group_idx, (operator_group, samples) in enumerate(operator_groups.items(), 1):
            logger.info(f"  [{benchmark}] 评估operator组 {group_idx}/{len(operator_groups)}: {operator_group}")
            
            # Set operator group context
            self.score_recorder.set_context(
                model=self.current_hierarchy['model'],
                benchmark=benchmark,
                operator_group=operator_group
            )
            self.current_hierarchy['operator_group'] = operator_group
            
            # Evaluate operator group
            group_report = await self._evaluate_operator_group(
                model, model_config, operator_group, samples
            )
            
            operator_reports[operator_group] = group_report
            all_benchmark_scores.extend(group_report['scores'])
            
            # Generate operator-level report if enabled
            if 'operator' in self.report_levels and self.incremental_reporting:
                await self._generate_operator_report(
                    self.current_hierarchy['model'],
                    benchmark,
                    operator_group,
                    group_report
                )
            
            # Log progress
            stats = self.score_recorder.calculate_statistics(group_report['scores'])
            logger.info(f"    完成: 成功率 {stats['success_rate']:.1%}, 平均分 {stats['mean_score']:.3f}")
        
        # Create benchmark report
        benchmark_report = {
            'benchmark': benchmark,
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - benchmark_start_time).total_seconds(),
            'operator_reports': operator_reports,
            'scores': all_benchmark_scores,
            'statistics': self.score_recorder.calculate_statistics(all_benchmark_scores)
        }
        
        return benchmark_report
    
    async def _evaluate_operator_group(self, model, model_config: Dict,
                                       operator_group: str, samples: List[Dict]) -> Dict:
        """
        Evaluate a single operator group
        
        Args:
            model: Model interface
            model_config: Model configuration
            operator_group: Operator group name
            samples: Samples for this operator group
            
        Returns:
            Operator group evaluation report
        """
        group_start_time = datetime.now()
        
        # Generate solutions for all samples in the group
        logger.info(f"    生成 {len(samples)} 个样本的解决方案...")
        
        solutions = []
        max_concurrency = model_config.get('max_concurrency', 10)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def generate_with_semaphore(sample, index):
            """Generate solution with semaphore control"""
            async with semaphore:
                try:
                    gen_params = model_config.get('generation_params', {})
                    solution = await model.generate_solution(sample, **gen_params)
                    return index, solution
                except Exception as e:
                    logger.warning(f"样本 {index} 生成失败: {e}")
                    return index, ""
        
        # Generate all solutions concurrently
        tasks = [
            generate_with_semaphore(sample, i)
            for i, sample in enumerate(samples)
        ]
        
        results = await asyncio.gather(*tasks)
        results.sort(key=lambda x: x[0])
        solutions = [result[1] for result in results]
        
        # Evaluate solutions
        logger.info(f"    评估解决方案...")
        scores = await self.score_collector.batch_evaluate(
            samples, solutions, 
            batch_size=self.eval_batch_size,
            model_name=f"{self.current_hierarchy['model']}/{operator_group}"
        )
        
        # Record detailed scores if enabled
        if self.save_sample_scores:
            for i, (sample, solution, score) in enumerate(zip(samples, solutions, scores)):
                self.score_recorder.record_sample_score(
                    sample, solution, score, sample_index=i
                )
        
        # Create operator group report
        group_report = {
            'operator_group': operator_group,
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - group_start_time).total_seconds(),
            'num_samples': len(samples),
            'scores': scores,
            'statistics': self.score_recorder.calculate_statistics(scores)
        }
        
        return group_report
    
    async def _generate_operator_report(self, model: str, benchmark: str, 
                                       operator_group: str, report: Dict):
        """
        Generate incremental report for operator group
        
        Args:
            model: Model name
            benchmark: Benchmark name
            operator_group: Operator group name
            report: Operator group report
        """
        try:
            # Create directory structure
            report_dir = self.output_dir / model / benchmark / operator_group
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Save operator report
            report_path = report_dir / "operator_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Export detailed scores for this operator group
            if self.save_sample_scores:
                self.score_recorder.export_to_json(
                    report_dir / "detailed_scores.json",
                    model=model,
                    benchmark=benchmark,
                    operator_group=operator_group
                )
                
                self.score_recorder.export_to_csv(
                    report_dir / "scores.csv",
                    model=model,
                    benchmark=benchmark,
                    operator_group=operator_group
                )
            
            logger.debug(f"Operator组报告已生成: {report_path}")
            
        except Exception as e:
            logger.warning(f"生成operator报告失败: {e}")
    
    async def _generate_benchmark_report(self, model: str, benchmark: str, report: Dict):
        """
        Generate incremental report for benchmark
        
        Args:
            model: Model name
            benchmark: Benchmark name
            report: Benchmark report
        """
        try:
            # Create directory structure
            report_dir = self.output_dir / model / benchmark
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Save benchmark report
            report_path = report_dir / "benchmark_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Generate summary markdown
            md_path = report_dir / "benchmark_summary.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# Benchmark Report: {benchmark}\n\n")
                f.write(f"**Model**: {model}\n")
                f.write(f"**Date**: {report['timestamp']}\n")
                f.write(f"**Duration**: {report['duration']:.1f}s\n\n")
                
                stats = report['statistics']
                f.write("## Overall Statistics\n\n")
                f.write(f"- Total Samples: {stats['total']}\n")
                f.write(f"- Success Rate: {stats['success_rate']:.1%}\n")
                f.write(f"- Mean Score: {stats['mean_score']:.3f}\n\n")
                
                f.write("## Operator Groups\n\n")
                for op_name, op_report in report['operator_reports'].items():
                    op_stats = op_report['statistics']
                    f.write(f"### {op_name}\n")
                    f.write(f"- Samples: {op_stats['total']}\n")
                    f.write(f"- Success Rate: {op_stats['success_rate']:.1%}\n")
                    f.write(f"- Mean Score: {op_stats['mean_score']:.3f}\n\n")
            
            logger.debug(f"Benchmark报告已生成: {report_path}")
            
        except Exception as e:
            logger.warning(f"生成benchmark报告失败: {e}")
    
    async def _generate_model_report(self, model: str, report: Dict):
        """
        Generate incremental report for model
        
        Args:
            model: Model name
            report: Model report
        """
        try:
            # Create directory structure  
            report_dir = self.output_dir / model
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model report
            report_path = report_dir / "model_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Export all scores for this model
            if self.save_sample_scores:
                self.score_recorder.export_to_csv(
                    report_dir / "all_scores.csv",
                    model=model
                )
            
            logger.info(f"模型报告已生成: {report_path}")
            
        except Exception as e:
            logger.warning(f"生成模型报告失败: {e}")
    
    def _print_hierarchical_summary(self, successful_models: List[str],
                                   failed_models: List[str],
                                   total_time: float):
        """
        Print hierarchical evaluation summary
        
        Args:
            successful_models: List of successful model names
            failed_models: List of failed model names
            total_time: Total evaluation time
        """
        logger.info("\n" + "="*60)
        logger.info("分层评估总结")
        logger.info("="*60)
        
        logger.info(f"总耗时: {total_time:.1f} 秒")
        logger.info(f"成功评估: {len(successful_models)} 个模型")
        logger.info(f"失败: {len(failed_models)} 个模型")
        
        # Get progress summary from score recorder
        progress = self.score_recorder.get_progress_summary()
        logger.info(f"总样本数: {progress['total_samples']}")
        
        if successful_models:
            logger.info("\n成功的模型:")
            for name in successful_models:
                model_progress = progress['models'].get(name, {})
                logger.info(f"  ✓ {name}:")
                logger.info(f"    - 基准数: {model_progress.get('benchmarks_completed', 0)}")
                logger.info(f"    - 样本数: {model_progress.get('total_samples', 0)}")
                logger.info(f"    - 成功率: {model_progress.get('success_rate', 0):.1%}")
        
        if failed_models:
            logger.info("\n失败的模型:")
            for name in failed_models:
                logger.info(f"  ✗ {name}")
        
        logger.info(f"\n详细报告已保存至: {self.output_dir}")
        logger.info("目录结构:")
        logger.info("  模型/")
        logger.info("    └── 基准/")
        logger.info("        └── Operator组/")
        logger.info("            ├── operator_report.json")
        logger.info("            ├── detailed_scores.json")
        logger.info("            └── scores.csv")