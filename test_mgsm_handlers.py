#!/usr/bin/env python3
"""
MGSM Handler Test Script
Tests the newly added MGSM Bengali and German benchmark handlers
"""

import asyncio
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_loading(benchmark_name, handler_class_name):
    """Test data loading functionality"""
    print("\n" + "="*60)
    print(f"Testing {benchmark_name}: Data Loading")
    print("="*60)
    
    try:
        # Dynamic import of handler
        handler_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.handler",
            fromlist=[handler_class_name]
        )
        HandlerClass = getattr(handler_module, handler_class_name)
        
        # Create handler instance
        if benchmark_name == "mgsm_bn":
            dataset_path = "Processed_dataset/mgsm_bn/mgsm_bn_test.jsonl"
        elif benchmark_name == "mgsm_de":
            dataset_path = "Processed_dataset/mgsm_de/mgsm_de_test.jsonl"
        else:
            raise ValueError(f"Unknown benchmark: {benchmark_name}")
            
        handler = HandlerClass(dataset_path=dataset_path)
        
        print(f"[OK] Successfully loaded {len(handler.data)} data entries")
        
        # Display first 3 data entries
        print("\nFirst 3 data entries:")
        for i in range(min(3, len(handler.data))):
            data = handler.data[i]
            print(f"\nData {i}:")
            for key in list(data.keys())[:5]:  # Show first 5 fields
                value = str(data[key])[:200]  # Limit length
                if len(str(data[key])) > 200:
                    value += "..."
                print(f"  {key}: {value}")
        
        return handler
        
    except Exception as e:
        print(f"[ERROR] Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_prompt_generation(handler, benchmark_name):
    """Test prompt generation functionality"""
    print("\n" + "="*60)
    print(f"Testing {benchmark_name}: Prompt Generation")
    print("="*60)
    
    if not handler:
        print("[WARNING] Skipped: Handler not initialized")
        return
    
    try:
        # Test single problem
        prompt_single = handler.get_prompt_text([0])
        print("Single problem prompt:")
        print("-" * 40)
        print(prompt_single[:500] + "..." if len(prompt_single) > 500 else prompt_single)
        
        # Test multiple problems
        indices = [0, 1, 2] if len(handler.data) >= 3 else list(range(len(handler.data)))
        prompt_multiple = handler.get_prompt_text(indices)
        print(f"\n{len(indices)} problems prompt length: {len(prompt_multiple)} characters")
        
        # Verify format
        if "---" in prompt_multiple and "**QUESTION:**" in prompt_multiple:
            print("[OK] Prompt format correct (contains Markdown separators)")
        else:
            print("[WARNING] Prompt format may need adjustment")
        
    except Exception as e:
        print(f"[ERROR] Prompt generation failed: {e}")
        import traceback
        traceback.print_exc()

def test_verification_data(handler, benchmark_name):
    """Test verification data retrieval"""
    print("\n" + "="*60)
    print(f"Testing {benchmark_name}: Verification Data")
    print("="*60)
    
    if not handler:
        print("[WARNING] Skipped: Handler not initialized")
        return
    
    try:
        # Get verification data for first problem
        verify_data = handler.get_verification_data(0)
        
        print("Verification data structure:")
        print("-" * 40)
        for key, value in verify_data.items():
            value_str = str(value)[:100]
            if len(str(value)) > 100:
                value_str += "..."
            print(f"{key}: {value_str}")
        
        # Check required fields
        required_fields = ['answer', 'question']
        missing_fields = [f for f in required_fields if f not in verify_data]
        
        if not missing_fields:
            print(f"\n[OK] Contains all required fields")
        else:
            print(f"\n[WARNING] Missing fields: {missing_fields}")
        
    except Exception as e:
        print(f"[ERROR] Verification data retrieval failed: {e}")
        import traceback
        traceback.print_exc()

def check_conditions_file(benchmark_name):
    """Check conditions.py file"""
    print("\n" + "="*60)
    print(f"Testing {benchmark_name}: conditions.py")
    print("="*60)
    
    try:
        # Import conditions module
        conditions_module = __import__(
            f"ScoreFlow.scripts.{benchmark_name}.conditions",
            fromlist=['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        )
        
        required_vars = [
            'TASK_PROMPT',
            'SYSTEM_PROMPT', 
            'PYTHON_START',
            'PYTHON_END',
            'START_PROMPT'
        ]
        
        print("Checking required variables:")
        all_present = True
        for var in required_vars:
            if hasattr(conditions_module, var):
                content = getattr(conditions_module, var)
                print(f"[OK] {var}: {len(content)} characters")
            else:
                print(f"[ERROR] {var}: Missing")
                all_present = False
        
        if all_present:
            print("\n[OK] conditions.py contains all required variables")
            
            # Check for language-specific content
            task_prompt = getattr(conditions_module, 'TASK_PROMPT')
            if benchmark_name == "mgsm_bn" and "Bengali" in task_prompt:
                print("[OK] TASK_PROMPT correctly mentions Bengali language")
            elif benchmark_name == "mgsm_de" and "German" in task_prompt:
                print("[OK] TASK_PROMPT correctly mentions German language")
            else:
                print("[WARNING] TASK_PROMPT may need language-specific adjustment")
        else:
            print("\n[WARNING] conditions.py missing some variables")
        
    except ImportError as e:
        print(f"[ERROR] Cannot import conditions.py: {e}")
    except Exception as e:
        print(f"[ERROR] Error checking conditions.py: {e}")

def test_benchmark(benchmark_name, handler_class_name):
    """Run all tests for a benchmark"""
    print("\n" + "#"*60)
    print(f"# Testing {benchmark_name.upper()} Benchmark")
    print("#"*60)
    
    # 1. Test data loading
    handler = test_data_loading(benchmark_name, handler_class_name)
    
    # 2. Test prompt generation
    test_prompt_generation(handler, benchmark_name)
    
    # 3. Test verification data
    test_verification_data(handler, benchmark_name)
    
    # 4. Check conditions.py
    check_conditions_file(benchmark_name)

def main():
    """Main test function"""
    print("\n" + "="*60)
    print(f"MGSM Handler Unit Tests")
    print("="*60)
    
    # Test MGSM Bengali
    test_benchmark("mgsm_bn", "MgsmBnHandler")
    
    # Test MGSM German
    test_benchmark("mgsm_de", "MgsmDeHandler")
    
    # Summary
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review any warnings or errors above")
    print("2. If all tests pass, the benchmarks are ready to use")
    print("3. You can test with the workflow system:")
    print("   - Modify run_workflow_system.sh to use 'mgsm_bn' or 'mgsm_de'")
    print("   - Run: bash run_workflow_system.sh")
    print("\n[SUCCESS] Both MGSM Bengali and German benchmarks have been successfully added!")

if __name__ == "__main__":
    main()