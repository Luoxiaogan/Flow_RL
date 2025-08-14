"""
Main Evaluation Script - Orchestrates the complete evaluation pipeline
Supports both local models (via SGLang) and external API models
"""
import os
import sys
import json
import time
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Add parent directory to path
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR.parent))

# Import evaluation modules
from sglang_server import InferenceManager, ModelConfig
from batch_inference import BatchInferenceEngine, ConcurrentScorer, InferenceTask
from utils import DataLoader, WorkflowExtractor, PromptFormatter, ConfigManager, MetricsCalculator
from report_generator import ReportGenerator

# Import scoreflow reward
from scoreflow_reward import compute_score as scoreflow_compute_score

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Main evaluator class"""
    
    def __init__(
        self,
        model_config: ModelConfig,
        output_dir: str = "./evaluation_results",
        max_inference_workers: int = 10,
        max_scoring_workers: int = 5,
        batch_size: int = 100
    ):
        """
        Initialize evaluator
        
        Args:
            model_config: Model configuration
            output_dir: Directory for results
            max_inference_workers: Max concurrent inference requests
            max_scoring_workers: Max concurrent scoring requests
            batch_size: Batch size for processing
        """
        self.model_config = model_config
        self.output_dir = Path(output_dir)
        self.max_inference_workers = max_inference_workers
        self.max_scoring_workers = max_scoring_workers
        self.batch_size = batch_size
        
        # Initialize components
        self.inference_manager = None
        self.inference_engine = None
        self.scorer = None
        self.report_generator = None
        
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize inference manager
            logger.info("Initializing inference manager...")
            self.inference_manager = InferenceManager(self.model_config)
            if not self.inference_manager.initialize():
                logger.error("Failed to initialize inference manager")
                return False
            
            # Initialize inference engine
            logger.info("Initializing batch inference engine...")
            self.inference_engine = BatchInferenceEngine(
                inference_fn=self.inference_manager.generate,
                max_workers=self.max_inference_workers,
                batch_size=self.batch_size
            )
            
            # Initialize scorer
            logger.info("Initializing concurrent scorer...")
            self.scorer = ConcurrentScorer(
                score_fn=scoreflow_compute_score,
                max_workers=self.max_scoring_workers
            )
            
            # Initialize report generator
            model_name = self.model_config.model_path or self.model_config.api_model or "unknown"
            self.report_generator = ReportGenerator(
                output_dir=self.output_dir,
                model_name=model_name
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def evaluate_dataset(
        self,
        data_path: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a dataset
        
        Args:
            data_path: Path to test data (parquet file)
            limit: Limit number of samples (for testing)
            
        Returns:
            Evaluation results
        """
        try:
            # Load data
            logger.info(f"Loading data from {data_path}")
            df = DataLoader.load_parquet(data_path)
            
            if limit:
                df = df.head(limit)
                logger.info(f"Limited to {limit} samples")
            
            # Group by benchmark
            benchmark_groups = DataLoader.group_by_benchmark(df)
            
            # Process each benchmark
            all_results = {}
            
            for benchmark_name, benchmark_df in benchmark_groups.items():
                logger.info(f"\n{'='*50}")
                logger.info(f"Evaluating benchmark: {benchmark_name}")
                logger.info(f"Samples: {len(benchmark_df)}")
                
                benchmark_results = await self._evaluate_benchmark(
                    benchmark_name,
                    benchmark_df
                )
                
                all_results[benchmark_name] = benchmark_results
                
                # Save intermediate results
                self.report_generator.save_detailed_results(
                    benchmark_results,
                    benchmark_name
                )
            
            # Generate reports
            logger.info("\nGenerating evaluation reports...")
            
            # Save configuration
            config_dict = {
                'model_type': self.model_config.model_type,
                'model': self.model_config.model_path or self.model_config.api_model,
                'max_inference_workers': self.max_inference_workers,
                'max_scoring_workers': self.max_scoring_workers,
                'batch_size': self.batch_size,
                'data_path': data_path,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate summary report
            self.report_generator.generate_summary_report(all_results, config_dict)
            
            # Generate CSV export
            self.report_generator.generate_csv_export(all_results)
            
            # Generate plots
            try:
                self.report_generator.generate_plots(all_results)
            except Exception as e:
                logger.warning(f"Failed to generate plots: {e}")
            
            # Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics(all_results)
            
            logger.info("\n" + "="*50)
            logger.info("EVALUATION COMPLETE")
            logger.info(f"Results saved to: {self.report_generator.output_dir}")
            logger.info(f"Overall average score: {overall_metrics['overall_avg']:.3f}")
            
            return {
                'results': all_results,
                'metrics': overall_metrics,
                'output_dir': str(self.report_generator.output_dir)
            }
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise
    
    async def _evaluate_benchmark(
        self,
        benchmark_name: str,
        df: Any
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a single benchmark
        
        Args:
            benchmark_name: Name of benchmark
            df: DataFrame with test data
            
        Returns:
            List of evaluation results
        """
        results = []
        
        # Prepare inference tasks
        inference_tasks = []
        for idx, row in df.iterrows():
            task_id = str(idx)
            prompt = row['prompt']
            
            # Format prompt for chat API if needed
            if self.model_config.model_type == "api":
                prompt = PromptFormatter.format_for_chat(prompt)
            
            inference_tasks.append(InferenceTask(
                task_id=task_id,
                prompt=prompt,
                metadata=row.to_dict()
            ))
        
        # Run inference
        logger.info(f"Running inference for {len(inference_tasks)} samples...")
        inference_start = time.time()
        
        inference_results = await self.inference_engine.process_batch(
            inference_tasks,
            progress_bar=True
        )
        
        inference_time = time.time() - inference_start
        logger.info(f"Inference completed in {inference_time:.2f}s")
        
        # Extract workflows and score
        logger.info("Extracting workflows and computing scores...")
        scoring_start = time.time()
        
        scoring_tasks = []
        for inf_result in inference_results:
            # Extract workflow
            workflow = WorkflowExtractor.extract_workflow(inf_result.response)
            
            if not workflow:
                logger.warning(f"Failed to extract workflow for task {inf_result.task_id}")
                workflow = ""
            
            # Prepare scoring task
            metadata = inf_result.metadata
            data_source = metadata.get('data_source', f'workflow_{benchmark_name}')
            
            # Remove 'workflow_' prefix if present
            clean_benchmark = data_source.replace('workflow_', '')
            
            scoring_tasks.append({
                'data_source': clean_benchmark,
                'solution_str': inf_result.response,  # Use full response for scoring
                'ground_truth': metadata.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': metadata.get('extra_info', {}),
                'task_id': inf_result.task_id,
                'workflow': workflow,
                'response': inf_result.response,
                'prompt': metadata.get('prompt', ''),
                'inference_time': inf_result.inference_time,
                'inference_success': inf_result.success,
                'inference_error': inf_result.error
            })
        
        # Score all solutions
        scores = await self.scorer.score_batch(
            [
                {
                    'data_source': task['data_source'],
                    'solution_str': task['solution_str'],
                    'ground_truth': task['ground_truth'],
                    'extra_info': task['extra_info']
                }
                for task in scoring_tasks
            ],
            progress_bar=True
        )
        
        scoring_time = time.time() - scoring_start
        logger.info(f"Scoring completed in {scoring_time:.2f}s")
        
        # Combine results
        for task, score in zip(scoring_tasks, scores):
            results.append({
                'prompt': task['prompt'],
                'response': task['response'],
                'workflow': task['workflow'],
                'score': score,
                'success': task['inference_success'] and score > 0,
                'error': task.get('inference_error'),
                'inference_time': task['inference_time'],
                'scoring_time': scoring_time / len(scoring_tasks),  # Average
                'metadata': {
                    'task_id': task['task_id'],
                    'data_source': task['data_source']
                }
            })
        
        # Log statistics
        scores_list = [r['score'] for r in results]
        stats = MetricsCalculator.calculate_stats(scores_list)
        
        logger.info(f"Benchmark {benchmark_name} results:")
        logger.info(f"  Average score: {stats['mean']:.3f}")
        logger.info(f"  Success rate: {stats['success_rate']:.1%}")
        logger.info(f"  Std deviation: {stats['std']:.3f}")
        
        return results
    
    def _calculate_overall_metrics(
        self,
        all_results: Dict[str, List[Dict]]
    ) -> Dict[str, float]:
        """Calculate overall metrics across all benchmarks"""
        all_scores = []
        benchmark_averages = {}
        
        for benchmark, results in all_results.items():
            scores = [r['score'] for r in results]
            all_scores.extend(scores)
            
            if scores:
                benchmark_averages[benchmark] = sum(scores) / len(scores)
        
        return {
            'overall_avg': sum(all_scores) / max(len(all_scores), 1),
            'overall_success_rate': sum(1 for s in all_scores if s > 0) / max(len(all_scores), 1),
            'benchmark_averages': benchmark_averages,
            'total_samples': len(all_scores)
        }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.inference_manager:
            self.inference_manager.close()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Evaluate model on workflow generation')
    
    # Model configuration
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument('--model-path', type=str,
                            help='Path to local model checkpoint')
    model_group.add_argument('--api-config', type=str,
                            help='Path to API configuration JSON file')
    
    # Data configuration
    parser.add_argument('--test-data', type=str, required=True,
                       help='Path to test data (parquet file)')
    parser.add_argument('--limit', type=int,
                       help='Limit number of samples for testing')
    
    # Output configuration
    parser.add_argument('--output-dir', type=str, default='./evaluation_results',
                       help='Directory to save results')
    
    # Performance configuration
    parser.add_argument('--max-inference-workers', type=int, default=10,
                       help='Maximum concurrent inference workers')
    parser.add_argument('--max-scoring-workers', type=int, default=5,
                       help='Maximum concurrent scoring workers')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for processing')
    
    # SGLang configuration (for local models)
    parser.add_argument('--port', type=int, default=30000,
                       help='Port for SGLang server')
    parser.add_argument('--tensor-parallel', type=int, default=1,
                       help='Tensor parallel size')
    parser.add_argument('--data-parallel', type=int, default=1,
                       help='Data parallel size')
    
    # Generation parameters
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='Sampling temperature')
    parser.add_argument('--max-tokens', type=int, default=4096,
                       help='Maximum tokens to generate')
    
    args = parser.parse_args()
    
    # Create model configuration
    if args.model_path:
        # Local model configuration
        model_config = ModelConfig(
            model_type="local",
            model_path=args.model_path,
            port=args.port,
            tensor_parallel=args.tensor_parallel,
            data_parallel=args.data_parallel,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
    else:
        # API model configuration
        with open(args.api_config, 'r') as f:
            api_config = json.load(f)
        
        model_config = ModelConfig(
            model_type="api",
            api_url=api_config['api_url'],
            api_key=api_config['api_key'],
            api_model=api_config['api_model'],
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model_config=model_config,
        output_dir=args.output_dir,
        max_inference_workers=args.max_inference_workers,
        max_scoring_workers=args.max_scoring_workers,
        batch_size=args.batch_size
    )
    
    try:
        # Initialize
        if not await evaluator.initialize():
            logger.error("Failed to initialize evaluator")
            return 1
        
        # Run evaluation
        results = await evaluator.evaluate_dataset(
            data_path=args.test_data,
            limit=args.limit
        )
        
        # Print final summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Output directory: {results['output_dir']}")
        print(f"Total samples: {results['metrics']['total_samples']}")
        print(f"Overall average score: {results['metrics']['overall_avg']:.3f}")
        print(f"Overall success rate: {results['metrics']['overall_success_rate']:.1%}")
        print("\nBenchmark averages:")
        for benchmark, avg in results['metrics']['benchmark_averages'].items():
            print(f"  {benchmark}: {avg:.3f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await evaluator.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)