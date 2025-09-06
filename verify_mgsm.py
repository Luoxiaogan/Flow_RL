#!/usr/bin/env python3
"""
Simple verification script for MGSM benchmarks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_benchmark(benchmark_name, handler_class_name):
    """Verify a benchmark can be loaded and used"""
    print(f"\nVerifying {benchmark_name}...")
    
    try:
        # Import handler
        handler_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.handler",
            fromlist=[handler_class_name]
        )
        HandlerClass = getattr(handler_module, handler_class_name)
        
        # Load data
        if benchmark_name == "mgsm_bn":
            dataset_path = "Processed_dataset/mgsm_bn/mgsm_bn_test.jsonl"
        elif benchmark_name == "mgsm_de":
            dataset_path = "Processed_dataset/mgsm_de/mgsm_de_test.jsonl"
        
        handler = HandlerClass(dataset_path=dataset_path)
        
        # Test basic functionality
        print(f"  - Data loaded: {len(handler.data)} entries")
        
        # Get prompt for first problem
        prompt = handler.get_prompt_text([0])
        print(f"  - Prompt generation: OK ({len(prompt)} characters)")
        
        # Get verification data
        verify_data = handler.get_verification_data(0)
        print(f"  - Verification data: OK (answer: {verify_data.get('answer', 'N/A')})")
        
        # Check conditions module
        conditions_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.conditions",
            fromlist=['TASK_PROMPT']
        )
        print(f"  - Conditions module: OK")
        
        print(f"  [PASSED] {benchmark_name} is ready to use!")
        return True
        
    except Exception as e:
        print(f"  [FAILED] {benchmark_name}: {e}")
        return False

def main():
    print("="*60)
    print("MGSM Benchmark Verification")
    print("="*60)
    
    # Test both benchmarks
    bn_ok = verify_benchmark("mgsm_bn", "MgsmBnHandler")
    de_ok = verify_benchmark("mgsm_de", "MgsmDeHandler")
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    
    if bn_ok and de_ok:
        print("\n[SUCCESS] Both MGSM benchmarks are ready!")
        print("\nYou can now use them with the workflow system:")
        print("  - For Bengali: set BENCHMARK='mgsm_bn' in run_workflow_system.sh")
        print("  - For German: set BENCHMARK='mgsm_de' in run_workflow_system.sh")
    else:
        print("\n[WARNING] Some benchmarks need attention")
        
    # Show mapping entries
    print("\nBenchmark mapping entries added:")
    print('  {"benchmark": "mgsm_bn", "handler_class": "MgsmBnHandler", ...}')
    print('  {"benchmark": "mgsm_de", "handler_class": "MgsmDeHandler", ...}')

if __name__ == "__main__":
    main()