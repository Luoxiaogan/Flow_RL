#!/usr/bin/env python
"""
Mock evaluation test - simulates the full evaluation pipeline without actual model
This script creates a mock model API and tests the evaluation system
"""
import os
import sys
import json
import asyncio
import logging
import random
from pathlib import Path
from typing import List, Dict, Any
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..','..', 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockModelAPI:
    """
    Mock model API that simulates model loading and generation
    """
    
    def __init__(self, checkpoint_path: str):
        """Initialize mock model"""
        self.checkpoint_path = checkpoint_path
        self.model_loaded = False
        logger.info(f"[MOCK] 初始化模型 API: {checkpoint_path}")
    
    async def load_model(self):
        """Simulate model loading"""
        logger.info(f"[MOCK] 开始加载模型: {self.checkpoint_path}")
        
        # Simulate loading time
        await asyncio.sleep(2)
        
        self.model_loaded = True
        logger.info(f"[MOCK] ✓ 模型加载完成")
        return True
    
    async def generate_solution(self, prompt: List[Dict]) -> str:
        """
        Simulate solution generation
        
        Args:
            prompt: Chat format prompt
            
        Returns:
            Generated workflow code
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")
        
        # Simulate generation time
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Generate mock workflow code
        workflow_code = f"""<code>
class Workflow:
    def __init__(self, config, problem) -> None:
        # Mock generated workflow
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        '''Mock workflow implementation'''
        import asyncio
        
        # Step 1: Extract information
        extraction = await self.generate(
            instruction="Extract key information from the problem",
            context=self.problem_text
        )
        
        # Step 2: Generate solution
        solution = await self.generate(
            instruction=f"Based on extraction: {{extraction}}\\nSolve the problem",
            context=self.problem_text
        )
        
        # Step 3: Refine solution
        refined = await self.revise(
            instruction="Improve and verify the solution",
            context=solution
        )
        
        return refined
</code>"""
        
        return workflow_code
    
    def clear_cache(self):
        """Simulate clearing model cache"""
        logger.info("[MOCK] 清理模型缓存")
        self.model_loaded = False


class MockRewardServerAPI:
    """
    Mock reward server API that simulates scoring
    """
    
    def __init__(self):
        """Initialize mock reward server"""
        self.request_count = 0
        logger.info("[MOCK] 初始化 Reward Server API")
    
    async def compute_score(self, request_data: Dict) -> Dict:
        """
        Simulate score computation
        
        Args:
            request_data: Request with solution and metadata
            
        Returns:
            Score response
        """
        self.request_count += 1
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Extract benchmark type
        data_source = request_data.get('data_source', 'unknown')
        solution = request_data.get('solution_str', '')
        
        # Generate mock score based on benchmark
        if 'gsm8k' in data_source:
            score = random.uniform(0.6, 0.95)
        elif 'drop' in data_source:
            score = random.uniform(0.5, 0.85)
        elif 'high_level_math' in data_source:
            score = random.uniform(0.4, 0.75)
        else:
            score = random.uniform(0.3, 0.7)
        
        # Randomly simulate failures (10% chance)
        if random.random() < 0.1:
            return {
                'success': False,
                'score': 0.0,
                'error': 'Mock evaluation timeout'
            }
        
        return {
            'success': True,
            'score': score,
            'message': f'Mock score computed for request #{self.request_count}'
        }


async def mock_evaluation_pipeline(checkpoint_path: str, num_samples: int = 10):
    """
    Run mock evaluation pipeline
    
    Args:
        checkpoint_path: Path to mock checkpoint
        num_samples: Number of test samples to evaluate
    """
    logger.info("\n" + "="*60)
    logger.info("开始模拟评估流程")
    logger.info("="*60)
    
    # Step 1: Initialize components
    logger.info("\n步骤 1: 初始化组件")
    
    model_api = MockModelAPI(checkpoint_path)
    reward_api = MockRewardServerAPI()
    
    # Import real evaluation components
    from evaluation.report_generator import ReportGenerator
    
    # Step 2: Load model
    logger.info("\n步骤 2: 加载模型")
    await model_api.load_model()
    
    # Step 3: Generate test samples
    logger.info(f"\n步骤 3: 生成 {num_samples} 个测试样本")
    
    test_samples = []
    benchmarks = ['workflow_gsm8k', 'workflow_drop', 'workflow_high_level_math']
    
    for i in range(num_samples):
        benchmark = random.choice(benchmarks)
        sample = {
            'data_source': benchmark,
            'prompt': [
                {'role': 'system', 'content': 'You are a workflow generator.'},
                {'role': 'user', 'content': f'Test problem #{i}: Solve this problem...'}
            ],
            'reward_model': {'ground_truth': 'default'},
            'extra_info': {
                'test_cases': [i, i+100, i+200],
                'data_path': f'mock_data/{benchmark}.jsonl',
                'raw_data': i
            }
        }
        test_samples.append(sample)
    
    logger.info(f"✓ 生成了 {len(test_samples)} 个测试样本")
    
    # Step 4: Generate solutions
    logger.info("\n步骤 4: 生成解决方案")
    
    solutions = []
    for i, sample in enumerate(test_samples):
        logger.info(f"  生成解决方案 {i+1}/{num_samples}")
        solution = await model_api.generate_solution(sample['prompt'])
        solutions.append(solution)
    
    logger.info(f"✓ 生成了 {len(solutions)} 个解决方案")
    
    # Step 5: Compute scores
    logger.info("\n步骤 5: 计算评估分数")
    
    scores = []
    for i, (sample, solution) in enumerate(zip(test_samples, solutions)):
        logger.info(f"  评估样本 {i+1}/{num_samples}")
        
        request_data = {
            'data_source': sample['data_source'],
            'solution_str': solution,
            'ground_truth': sample['reward_model']['ground_truth'],
            'extra_info': sample['extra_info']
        }
        
        score_result = await reward_api.compute_score(request_data)
        scores.append(score_result)
    
    logger.info(f"✓ 完成 {len(scores)} 个评估")
    
    # Step 6: Generate report
    logger.info("\n步骤 6: 生成评估报告")
    
    report_generator = ReportGenerator('mock_evaluation_reports')
    
    checkpoint_info = {
        'step': 1000,
        'path': checkpoint_path,
        'output_dir': './mock_output'
    }
    
    report = await report_generator.generate_report(
        scores, 
        checkpoint_info,
        test_samples
    )
    
    # Step 7: Display results
    logger.info("\n" + "="*60)
    logger.info("评估结果")
    logger.info("="*60)
    
    print(f"\n总体统计:")
    print(f"  - 总样本数: {report['total_samples']}")
    print(f"  - 总体得分: {report['overall_score']:.2%}")
    print(f"  - 成功率: {report['success_rate']:.2%}")
    
    print(f"\n各 Benchmark 成绩:")
    for benchmark, stats in report['benchmark_scores'].items():
        print(f"\n  {benchmark}:")
        print(f"    - 样本数: {stats['num_samples']}")
        print(f"    - 平均分: {stats['mean_score']:.3f}")
        print(f"    - 最高分: {stats['max_score']:.3f}")
        print(f"    - 最低分: {stats['min_score']:.3f}")
        print(f"    - 成功率: {stats['success_rate']:.1%}")
    
    # Clean up
    model_api.clear_cache()
    
    logger.info("\n✓ 模拟评估完成")
    
    return report


async def test_with_real_callback():
    """
    Test with real EvaluationCallback but mock model/server
    """
    logger.info("\n" + "#"*60)
    logger.info("# 测试真实 EvaluationCallback（使用 Mock API）")
    logger.info("#"*60)
    
    # Monkey-patch the evaluation modules to use mock APIs
    import evaluation.model_evaluator as model_module
    import evaluation.score_collector as score_module
    
    # Save original classes
    original_model_evaluator = model_module.ModelEvaluator
    original_score_collector = score_module.ScoreCollector
    
    # Create mock replacements
    class MockedModelEvaluator:
        def __init__(self):
            self.mock_api = None
        
        async def load_model(self, checkpoint_path):
            self.mock_api = MockModelAPI(checkpoint_path)
            await self.mock_api.load_model()
        
        async def generate_solutions(self, test_samples, batch_size=8):
            solutions = []
            for sample in test_samples:
                solution = await self.mock_api.generate_solution(sample['prompt'])
                solutions.append(solution)
            return solutions
        
        def _extract_code(self, text):
            return text
        
        def clear_cache(self):
            if self.mock_api:
                self.mock_api.clear_cache()
    
    class MockedScoreCollector:
        def __init__(self, server_url):
            self.mock_api = MockRewardServerAPI()
            self.server_url = server_url
        
        async def batch_evaluate(self, test_samples, solutions, batch_size=8):
            scores = []
            for sample, solution in zip(test_samples, solutions):
                request_data = {
                    'data_source': sample['data_source'],
                    'solution_str': solution,
                    'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                    'extra_info': sample.get('extra_info', {})
                }
                score = await self.mock_api.compute_score(request_data)
                scores.append(score)
            return scores
    
    # Replace with mocks
    model_module.ModelEvaluator = MockedModelEvaluator
    score_module.ScoreCollector = MockedScoreCollector
    
    try:
        # Import and test real callback
        from evaluation.evaluation_callback import EvaluationCallback
        
        # Create mock test data
        test_data = []
        for i in range(5):
            benchmark = random.choice(['workflow_gsm8k', 'workflow_drop'])
            test_data.append({
                'data_source': benchmark,
                'prompt': [
                    {'role': 'system', 'content': 'You are a helper.'},
                    {'role': 'user', 'content': f'Problem {i}'}
                ],
                'reward_model': {'ground_truth': 'default'},
                'extra_info': {'test_cases': [i]}
            })
        
        # Save test data
        test_file = Path('mock_test_data.jsonl')
        with open(test_file, 'w') as f:
            for item in test_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Create callback with mock configuration
        eval_config = {
            'test_data_path': str(test_file),
            'reward_server_url': 'http://localhost:8899',  # Not actually used
            'eval_batch_size': 2,
            'async_eval': False,
            'eval_interval': 1,
            'output_dir': 'mock_callback_reports',
            'max_samples': 5
        }
        
        callback = EvaluationCallback(eval_config)
        
        # Mock reward server checker
        class MockChecker:
            async def check_server(self):
                return True
        
        callback._server_checker = MockChecker()
        
        # Run evaluation
        logger.info("\n运行 EvaluationCallback 评估...")
        result = await callback._run_evaluation_async(
            './mock-checkpoint-500',
            500,
            './mock-output'
        )
        
        if result:
            logger.info("\n✓ EvaluationCallback 测试成功")
            logger.info(f"  总体得分: {result['overall_score']:.2%}")
        else:
            logger.info("\n✗ EvaluationCallback 测试失败")
        
        # Clean up
        test_file.unlink(missing_ok=True)
        
    finally:
        # Restore original classes
        model_module.ModelEvaluator = original_model_evaluator
        score_module.ScoreCollector = original_score_collector
    
    return result


async def main():
    """
    Run all mock tests
    """
    print("\n" + "#"*60)
    print("# 模拟评估系统测试")
    print("#"*60)
    print(f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {os.getcwd()}")
    
    # Test 1: Basic mock pipeline
    print("\n测试 1: 基础模拟流程")
    print("-"*40)
    
    report1 = await mock_evaluation_pipeline(
        checkpoint_path='./mock-checkpoint-1000',
        num_samples=15
    )
    
    # Test 2: With real callback
    print("\n测试 2: 使用真实 Callback")
    print("-"*40)
    
    report2 = await test_with_real_callback()
    
    # Summary
    print("\n" + "#"*60)
    print("# 测试总结")
    print("#"*60)
    
    if report1 and report2:
        print("\n✓ 所有模拟测试通过！")
        print("\n系统已准备就绪，可以进行实际部署。")
        print("\n下一步:")
        print("1. 启动真实的 Reward Server")
        print("2. 运行: bash run_finetune_with_eval.sh")
    else:
        print("\n✗ 部分测试失败，请检查日志")
    
    return report1 and report2


if __name__ == "__main__":
    # Run mock tests
    success = asyncio.run(main())
    
    print("\n" + "#"*60)
    print(f"# 测试完成 - {'成功' if success else '失败'}")
    print("#"*60)
    
    sys.exit(0 if success else 1)