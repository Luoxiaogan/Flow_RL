#!/usr/bin/env python3
"""
Test script for new mbppplus and humanevalplus benchmarks
"""

import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mbppplus():
    """Test mbppplus benchmark"""
    print("\n" + "="*60)
    print("Testing MBPPPLUS Benchmark")
    print("="*60)
    
    try:
        # Import handler
        from ScoreFlow.scripts.mbppplus.handler import MbppplusHandler
        print("[OK] Successfully imported MbppplusHandler")
        
        # Create handler instance
        dataset_path = "Processed_dataset/mbppplus/mbppplus_test.jsonl"
        handler = MbppplusHandler(dataset_path=dataset_path)
        print(f"[OK] Loaded {len(handler.data)} test samples")
        
        # Test prompt generation
        if len(handler.data) > 0:
            prompt = handler.get_prompt_text([0])
            print(f"[OK] Generated prompt with {len(prompt)} characters")
            
            # Show first part of prompt
            print("\nSample prompt (first 300 chars):")
            print("-" * 40)
            print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        
        # Check conditions file
        from ScoreFlow.scripts.mbppplus import conditions
        required = ['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        missing = [v for v in required if not hasattr(conditions, v)]
        
        if not missing:
            print("[OK] All required variables in conditions.py")
        else:
            print(f"[WARN] Missing variables in conditions.py: {missing}")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_humanevalplus():
    """Test humanevalplus benchmark"""
    print("\n" + "="*60)
    print("Testing HUMANEVALPLUS Benchmark")
    print("="*60)
    
    try:
        # Import handler
        from ScoreFlow.scripts.humanevalplus.handler import HumanevalplusHandler
        print("[OK] Successfully imported HumanevalplusHandler")
        
        # Create handler instance
        dataset_path = "Processed_dataset/humanevalplus/humanevalplus_test.jsonl"
        handler = HumanevalplusHandler(dataset_path=dataset_path)
        print(f"[OK] Loaded {len(handler.data)} test samples")
        
        # Test prompt generation
        if len(handler.data) > 0:
            prompt = handler.get_prompt_text([0])
            print(f"[OK] Generated prompt with {len(prompt)} characters")
            
            # Show first part of prompt
            print("\nSample prompt (first 300 chars):")
            print("-" * 40)
            print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        
        # Check conditions file
        from ScoreFlow.scripts.humanevalplus import conditions
        required = ['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        missing = [v for v in required if not hasattr(conditions, v)]
        
        if not missing:
            print("[OK] All required variables in conditions.py")
        else:
            print(f"[WARN] Missing variables in conditions.py: {missing}")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_benchmark_mapping():
    """Check if benchmarks are registered in benchmark_mapping.jsonl"""
    print("\n" + "="*60)
    print("Checking Benchmark Registration")
    print("="*60)
    
    try:
        import json
        
        with open("ScoreFlow/benchmark_mapping.jsonl", "r", encoding="utf-8") as f:
            mappings = [json.loads(line) for line in f]
        
        benchmarks = {m['benchmark']: m for m in mappings}
        
        # Check mbppplus
        if 'mbppplus' in benchmarks:
            m = benchmarks['mbppplus']
            print(f"[OK] mbppplus registered:")
            print(f"     Handler: {m['handler_class']}")
            print(f"     Dir: {m['handler_dir']}")
        else:
            print("[FAIL] mbppplus not found in benchmark_mapping.jsonl")
        
        # Check humanevalplus
        if 'humanevalplus' in benchmarks:
            m = benchmarks['humanevalplus']
            print(f"[OK] humanevalplus registered:")
            print(f"     Handler: {m['handler_class']}")
            print(f"     Dir: {m['handler_dir']}")
        else:
            print("[FAIL] humanevalplus not found in benchmark_mapping.jsonl")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Error checking benchmark_mapping.jsonl: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Testing New Benchmarks: MBPPPLUS and HUMANEVALPLUS")
    print("="*60)
    
    results = []
    
    # Test benchmark registration
    results.append(("Benchmark Registration", check_benchmark_mapping()))
    
    # Test mbppplus
    results.append(("MBPPPLUS", test_mbppplus()))
    
    # Test humanevalplus
    results.append(("HUMANEVALPLUS", test_humanevalplus()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Please check the output above.")
    
    print("\nNext steps:")
    print("1. If all tests pass, the benchmarks are ready to use")
    print("2. You can run workflow generation with: --benchmark mbppplus")
    print("3. Or test with: python workflow_generator.py --benchmark humanevalplus")

if __name__ == "__main__":
    main()