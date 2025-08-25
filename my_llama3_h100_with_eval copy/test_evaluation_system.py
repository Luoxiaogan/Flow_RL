#!/usr/bin/env python
"""
Test script for the automatic evaluation system
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_reward_server_checker():
    """Test the reward server checker"""
    print("\n" + "="*60)
    print("Testing Reward Server Checker")
    print("="*60)
    
    from evaluation.reward_server_checker import RewardServerChecker
    
    checker = RewardServerChecker("http://localhost:8899")
    
    # Check server status
    is_running = await checker.check_server()
    
    if is_running:
        print("✓ Reward Server is running")
    else:
        print("✗ Reward Server is not running")
        print("Please start the server manually:")
        print("  cd New_evaluation_and_RL/reward_server")
        print("  python scoreflow_reward_server.py")
        return False
    
    return True

async def test_model_evaluator():
    """Test the model evaluator"""
    print("\n" + "="*60)
    print("Testing Model Evaluator")
    print("="*60)
    
    from evaluation.model_evaluator import ModelEvaluator
    
    evaluator = ModelEvaluator()
    
    # Test code extraction
    test_text = """
    <think>Let me create a workflow...</think>
    <code>
    class Workflow:
        def __init__(self, config, problem):
            self.config = config
            self.problem_text = problem
        
        async def run_workflow(self):
            return "solution"
    </code>
    """
    
    code = evaluator._extract_code(test_text)
    
    if 'class Workflow' in code:
        print("✓ Code extraction working")
    else:
        print("✗ Code extraction failed")
        return False
    
    print(f"Extracted code length: {len(code)} characters")
    return True

async def test_score_collector():
    """Test the score collector"""
    print("\n" + "="*60)
    print("Testing Score Collector")
    print("="*60)
    
    from evaluation.score_collector import ScoreCollector
    
    collector = ScoreCollector("http://localhost:8899")
    
    # Test request
    test_request = {
        'data_source': 'workflow_gsm8k',
        'solution_str': '<code>class Workflow:\n    def __init__(self, config, problem):\n        pass\n\n    async def run_workflow(self):\n        return "42"\n</code>',
        'ground_truth': 'default',
        'extra_info': {
            'test_cases': [0],
            'data_path': 'test.jsonl'
        }
    }
    
    print("Sending test request to reward server...")
    result = await collector.compute_score(test_request)
    
    if result.get('success'):
        print(f"✓ Score received: {result.get('score', 0):.3f}")
    else:
        print(f"✗ Scoring failed: {result.get('error', 'Unknown error')}")
        return False
    
    return True

async def test_report_generator():
    """Test the report generator"""
    print("\n" + "="*60)
    print("Testing Report Generator")
    print("="*60)
    
    from evaluation.report_generator import ReportGenerator
    
    # Create test output directory
    test_dir = Path("test_evaluation_reports")
    generator = ReportGenerator(str(test_dir))
    
    # Test data
    scores = [
        {'success': True, 'score': 0.8},
        {'success': True, 'score': 0.9},
        {'success': False, 'score': 0.0, 'error': 'Test error'},
    ]
    
    test_samples = [
        {'data_source': 'workflow_gsm8k', 'extra_info': {'test_cases': [1, 2]}},
        {'data_source': 'workflow_gsm8k', 'extra_info': {'test_cases': [3, 4]}},
        {'data_source': 'workflow_drop', 'extra_info': {'test_cases': [5]}},
    ]
    
    checkpoint_info = {
        'step': 1000,
        'path': './test-checkpoint-1000',
        'output_dir': './test-output'
    }
    
    # Generate report
    report = await generator.generate_report(scores, checkpoint_info, test_samples)
    
    print(f"✓ Report generated:")
    print(f"  - Overall Score: {report['overall_score']:.2%}")
    print(f"  - Success Rate: {report['success_rate']:.2%}")
    print(f"  - Benchmarks: {list(report['benchmark_scores'].keys())}")
    
    # Check if files were created
    json_file = test_dir / f"eval_checkpoint_{checkpoint_info['step']}.json"
    md_file = test_dir / f"eval_checkpoint_{checkpoint_info['step']}.md"
    csv_file = test_dir / f"eval_checkpoint_{checkpoint_info['step']}_details.csv"
    
    files_exist = all([json_file.exists(), md_file.exists(), csv_file.exists()])
    
    if files_exist:
        print(f"✓ All report files created in {test_dir}")
    else:
        print("✗ Some report files missing")
        return False
    
    return True

async def test_full_evaluation_pipeline():
    """Test the full evaluation pipeline"""
    print("\n" + "="*60)
    print("Testing Full Evaluation Pipeline")
    print("="*60)
    
    # Load test data
    test_data_path = Path("New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl")
    
    if not test_data_path.exists():
        # Try relative path
        test_data_path = Path("../New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl")
    
    if not test_data_path.exists():
        print(f"✗ Test data not found: {test_data_path}")
        print("Creating sample test data...")
        
        # Create sample test data
        sample_data = {
            "data_source": "workflow_gsm8k",
            "prompt": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Solve this math problem: 2 + 2 = ?"}
            ],
            "ability": "workflow",
            "reward_model": {"ground_truth": "default"},
            "extra_info": {
                "test_cases": [0],
                "data_path": "test.jsonl"
            }
        }
        
        test_samples = [sample_data]
    else:
        # Load actual test data (first 3 samples)
        test_samples = []
        with open(test_data_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 3:  # Only load 3 samples for testing
                    break
                if line.strip():
                    test_samples.append(json.loads(line))
        
        print(f"✓ Loaded {len(test_samples)} test samples")
    
    # Test evaluation callback initialization
    from evaluation.evaluation_callback import EvaluationCallback
    
    eval_config = {
        'test_data_path': str(test_data_path) if test_data_path.exists() else 'test_data.jsonl',
        'reward_server_url': 'http://localhost:8899',
        'eval_batch_size': 2,
        'async_eval': False,  # Synchronous for testing
        'eval_interval': 1,
        'output_dir': 'test_evaluation_reports',
        'max_samples': 3
    }
    
    callback = EvaluationCallback(eval_config)
    print("✓ EvaluationCallback initialized")
    
    # Test loading test data
    if test_data_path.exists():
        loaded_samples = callback._load_test_data()
        print(f"✓ Loaded {len(loaded_samples)} samples from file")
    
    print("\n" + "="*60)
    print("All Tests Summary")
    print("="*60)
    
    return True

async def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# Evaluation System Test Suite")
    print("#"*60)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run tests
    tests = [
        ("Reward Server Checker", test_reward_server_checker),
        ("Model Evaluator", test_model_evaluator),
        ("Score Collector", test_score_collector),
        ("Report Generator", test_report_generator),
        ("Full Pipeline", test_full_evaluation_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print summary
    print("\n" + "#"*60)
    print("# Test Results Summary")
    print("#"*60)
    
    all_passed = True
    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "#"*60)
    
    if all_passed:
        print("# ✓ All tests passed! The evaluation system is ready.")
    else:
        print("# ✗ Some tests failed. Please check the errors above.")
    
    print("#"*60)
    
    return all_passed

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)