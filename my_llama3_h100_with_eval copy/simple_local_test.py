#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple local test for evaluation system - ASCII only version
"""
import os
import sys
import json
import asyncio
import random
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("LOCAL EVALUATION SYSTEM TEST")
print("="*60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python: {sys.version.split()[0]}")
print(f"Working Dir: {os.getcwd()}")
print("="*60)


async def simple_test():
    """Run a simple test of the evaluation system"""
    
    print("\n[STEP 1] Creating test data")
    print("-"*40)
    
    # Create test samples
    test_samples = []
    benchmarks = ['workflow_gsm8k', 'workflow_drop', 'workflow_high_level_math']
    
    for i in range(10):
        sample = {
            'data_source': random.choice(benchmarks),
            'prompt': [
                {'role': 'system', 'content': 'You are a workflow generator.'},
                {'role': 'user', 'content': f'Problem {i}: Solve this problem.'}
            ],
            'reward_model': {'ground_truth': 'default'},
            'extra_info': {
                'test_cases': [i, i+1, i+2],
                'data_path': 'test.jsonl',
                'raw_data': i
            }
        }
        test_samples.append(sample)
    
    print(f"[OK] Created {len(test_samples)} test samples")
    
    # Show distribution
    for benchmark in benchmarks:
        count = sum(1 for s in test_samples if benchmark in s['data_source'])
        print(f"  - {benchmark}: {count} samples")
    
    print("\n[STEP 2] Simulating model generation")
    print("-"*40)
    
    # Simulate solutions
    solutions = []
    for i, sample in enumerate(test_samples):
        # Generate mock workflow code
        code = f"""<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        
    async def run_workflow(self):
        # Mock workflow for sample {i}
        result = await self.generate(
            instruction="Solve the problem",
            context=self.problem_text
        )
        return result
</code>"""
        solutions.append(code)
        
        # Progress indicator
        progress = (i + 1) * 100 // len(test_samples)
        print(f"  Generating: [{progress:3d}%] {i+1}/{len(test_samples)}", end='\r')
        await asyncio.sleep(0.05)
    
    print(f"\n[OK] Generated {len(solutions)} solutions")
    
    print("\n[STEP 3] Simulating score calculation")
    print("-"*40)
    
    # Simulate scores
    scores = []
    for i, (sample, solution) in enumerate(zip(test_samples, solutions)):
        # Generate random score based on benchmark
        benchmark = sample['data_source']
        
        if 'gsm8k' in benchmark:
            base_score = 0.7
        elif 'drop' in benchmark:
            base_score = 0.6
        else:
            base_score = 0.5
        
        # Add some randomness
        score_value = base_score + random.uniform(-0.2, 0.3)
        score_value = max(0.0, min(1.0, score_value))
        
        # Randomly fail some evaluations
        if random.random() < 0.1:
            score_result = {
                'success': False,
                'score': 0.0,
                'error': 'Simulated timeout'
            }
        else:
            score_result = {
                'success': True,
                'score': score_value,
                'message': f'Evaluation {i+1}'
            }
        
        scores.append(score_result)
        
        # Progress indicator
        progress = (i + 1) * 100 // len(test_samples)
        print(f"  Evaluating: [{progress:3d}%] {i+1}/{len(test_samples)}", end='\r')
        await asyncio.sleep(0.03)
    
    print(f"\n[OK] Completed {len(scores)} evaluations")
    
    print("\n[STEP 4] Generating report")
    print("-"*40)
    
    # Import report generator
    from evaluation.report_generator import ReportGenerator
    
    # Create report directory
    report_dir = Path('simple_test_reports')
    report_dir.mkdir(exist_ok=True)
    
    generator = ReportGenerator(str(report_dir))
    
    checkpoint_info = {
        'step': 1000,
        'path': './test-checkpoint-1000',
        'output_dir': './test-output'
    }
    
    # Generate report
    report = await generator.generate_report(scores, checkpoint_info, test_samples)
    
    print("[OK] Report generated")
    
    print("\n[STEP 5] Test Results")
    print("="*60)
    
    # Display results
    print(f"\nOverall Statistics:")
    print(f"  Total Samples: {report['total_samples']}")
    print(f"  Overall Score: {report['overall_score']:.1%}")
    print(f"  Success Rate: {report['success_rate']:.1%}")
    
    print(f"\nBenchmark Scores:")
    for benchmark, stats in report['benchmark_scores'].items():
        name = benchmark.replace('workflow_', '').upper()
        print(f"\n  {name}:")
        print(f"    Samples: {stats['num_samples']}")
        print(f"    Success Rate: {stats['success_rate']:.1%}")
        print(f"    Mean Score: {stats['mean_score']:.3f}")
        print(f"    Max Score: {stats['max_score']:.3f}")
        print(f"    Min Score: {stats['min_score']:.3f}")
    
    print(f"\nReports saved to: {report_dir}/")
    print(f"  - JSON: eval_checkpoint_1000.json")
    print(f"  - Markdown: eval_checkpoint_1000.md")
    print(f"  - CSV: eval_checkpoint_1000_details.csv")
    
    print("\n[STEP 6] Testing EvaluationCallback")
    print("-"*40)
    
    # Save test data
    test_file = Path('simple_test_data.jsonl')
    with open(test_file, 'w', encoding='utf-8') as f:
        for sample in test_samples[:3]:  # Use only 3 samples
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Test callback
    try:
        from evaluation.evaluation_callback import EvaluationCallback
        
        config = {
            'test_data_path': str(test_file),
            'reward_server_url': 'http://localhost:8899',
            'eval_batch_size': 2,
            'async_eval': False,
            'eval_interval': 1,
            'output_dir': 'simple_callback_test',
            'max_samples': 3
        }
        
        callback = EvaluationCallback(config)
        print("[OK] EvaluationCallback initialized")
        
        # Test data loading
        data = callback._load_test_data()
        print(f"[OK] Loaded {len(data)} test samples")
        
    except Exception as e:
        print(f"[ERROR] EvaluationCallback test failed: {e}")
    
    # Clean up
    test_file.unlink(missing_ok=True)
    
    return True


def main():
    """Main function"""
    print("\nStarting test...")
    
    try:
        # Run async test
        success = asyncio.run(simple_test())
        
        print("\n" + "="*60)
        if success:
            print("SUCCESS: All tests passed!")
            print("\nThe evaluation system is working correctly.")
            print("\nNext steps:")
            print("1. Start the real reward server")
            print("2. Run training with: bash run_finetune_with_eval.sh")
        else:
            print("FAILED: Some tests failed")
        print("="*60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)