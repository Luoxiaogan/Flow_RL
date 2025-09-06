#!/usr/bin/env python3
"""
Test script for SimpleQA benchmark
Tests world knowledge question answering functionality
"""

import sys
import os
import json

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simpleqa():
    """Test SimpleQA benchmark"""
    print("\n" + "="*60)
    print("Testing SimpleQA Benchmark")
    print("="*60)
    
    try:
        # Import handler
        from ScoreFlow.scripts.simpleqa.handler import SimpleqaHandler
        print("[OK] Successfully imported SimpleqaHandler")
        
        # Create handler instance
        dataset_path = "Processed_dataset/simpleqa/simpleqa_test.jsonl"
        handler = SimpleqaHandler(dataset_path=dataset_path)
        print(f"[OK] Loaded {len(handler.data)} test samples")
        
        # Show sample data structure
        if len(handler.data) > 0:
            sample = handler.data[0]
            print("\nSample data structure:")
            print("-" * 40)
            for key in sample.keys():
                value = str(sample[key])[:100] if len(str(sample[key])) > 100 else str(sample[key])
                print(f"  {key}: {value}")
        
        # Test prompt generation for single question
        if len(handler.data) > 0:
            prompt = handler.get_prompt_text([0])
            print(f"\n[OK] Generated prompt with {len(prompt)} characters")
            
            # Show the prompt
            print("\nGenerated prompt:")
            print("-" * 40)
            print(prompt)
        
        # Test prompt generation for multiple questions
        if len(handler.data) >= 3:
            multi_prompt = handler.get_prompt_text([0, 1, 2])
            print(f"\n[OK] Generated multi-question prompt with {len(multi_prompt)} characters")
            
            # Check format
            if "---" in multi_prompt and "**QUESTION:**" in multi_prompt:
                print("[OK] Prompt format correct")
            else:
                print("[WARN] Prompt format may need adjustment")
        
        # Test verification data
        verify_data = handler.get_verification_data(0)
        print(f"\n[OK] Retrieved verification data with answer: {verify_data.get('answer', 'N/A')}")
        
        # Check conditions file
        from ScoreFlow.scripts.simpleqa import conditions
        required = ['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        missing = [v for v in required if not hasattr(conditions, v)]
        
        if not missing:
            print("[OK] All required variables in conditions.py")
        else:
            print(f"[WARN] Missing variables in conditions.py: {missing}")
        
        # Test answer extraction (internal method)
        test_outputs = [
            "Final Answer: Paris",
            "The answer is London.",
            "Answer: Tokyo",
            "Based on my knowledge, the correct answer is Berlin.",
            "Madrid"
        ]
        
        print("\n[OK] Testing answer extraction:")
        for output in test_outputs:
            extracted = handler._extract_answer(output)
            print(f"  Input: '{output[:40]}...' -> Extracted: '{extracted}'")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_data_format():
    """Check SimpleQA data format"""
    print("\n" + "="*60)
    print("Checking SimpleQA Data Format")
    print("="*60)
    
    try:
        # Check training data
        with open("Processed_dataset/simpleqa/simpleqa_train.jsonl", "r", encoding="utf-8") as f:
            train_samples = [json.loads(f.readline()) for _ in range(3)]
        
        print(f"[OK] Training data sample fields:")
        for key in train_samples[0].keys():
            print(f"     - {key}")
        
        # Check test data
        with open("Processed_dataset/simpleqa/simpleqa_test.jsonl", "r", encoding="utf-8") as f:
            test_samples = [json.loads(f.readline()) for _ in range(3)]
        
        print(f"[OK] Test data sample fields:")
        for key in test_samples[0].keys():
            print(f"     - {key}")
        
        # Show sample questions and answers
        print("\n[OK] Sample questions and answers:")
        for i, sample in enumerate(train_samples, 1):
            q = sample.get('question', 'N/A')[:60]
            a = sample.get('answer', 'N/A')
            t = sample.get('topic', 'N/A')
            print(f"  {i}. Q: {q}...")
            print(f"     A: {a}")
            print(f"     Topic: {t}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error checking data format: {e}")
        return False

def check_benchmark_registration():
    """Check if SimpleQA is registered in benchmark_mapping.jsonl"""
    print("\n" + "="*60)
    print("Checking SimpleQA Registration")
    print("="*60)
    
    try:
        with open("ScoreFlow/benchmark_mapping.jsonl", "r", encoding="utf-8") as f:
            mappings = [json.loads(line) for line in f]
        
        benchmarks = {m['benchmark']: m for m in mappings}
        
        if 'simpleqa' in benchmarks:
            m = benchmarks['simpleqa']
            print(f"[OK] SimpleQA registered:")
            print(f"     Handler: {m['handler_class']}")
            print(f"     Dir: {m['handler_dir']}")
            print(f"     Train: {m['data_train_dir']}")
            print(f"     Test: {m['data_test_dir']}")
            return True
        else:
            print("[FAIL] SimpleQA not found in benchmark_mapping.jsonl")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error checking registration: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("SimpleQA Benchmark Test Suite")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Data Format Check", check_data_format()))
    results.append(("Benchmark Registration", check_benchmark_registration()))
    results.append(("Handler Functionality", test_simpleqa()))
    
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
        print("\nSimpleQA benchmark is ready to use:")
        print("  python workflow_generator.py --benchmark simpleqa --num_problems 3")
        print("  python workflow_executor.py --benchmark simpleqa")
    else:
        print("\n[WARNING] Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()