#!/usr/bin/env python3
"""
Final verification for MGSM benchmarks with corrected naming
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_benchmark(benchmark_name, handler_class_name, data_path):
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
        handler = HandlerClass(dataset_path=data_path)
        
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
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("Final MGSM Benchmark Verification")
    print("="*60)
    
    # Test both benchmarks with corrected names
    bn_ok = verify_benchmark("mgsmbn", "MgsmbnHandler", 
                             "Processed_dataset/mgsm_bn/mgsm_bn_test.jsonl")
    de_ok = verify_benchmark("mgsmde", "MgsmdeHandler", 
                             "Processed_dataset/mgsm_de/mgsm_de_test.jsonl")
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    
    if bn_ok and de_ok:
        print("\n[SUCCESS] Both MGSM benchmarks are configured correctly!")
        print("\nYou can now use them with the workflow system:")
        print("  - For Bengali: set BENCHMARK='mgsmbn' in run_workflow_system.sh")
        print("  - For German: set BENCHMARK='mgsmde' in run_workflow_system.sh")
        print("\nNote: The benchmark names are 'mgsmbn' and 'mgsmde' (without underscore)")
    else:
        print("\n[WARNING] Some benchmarks need attention")
        
    # Show mapping entries
    print("\nBenchmark mapping entries in benchmark_mapping.jsonl:")
    print('  {"benchmark": "mgsmbn", "handler_class": "MgsmbnHandler", ...}')
    print('  {"benchmark": "mgsmde", "handler_class": "MgsmdeHandler", ...}')

if __name__ == "__main__":
    main()