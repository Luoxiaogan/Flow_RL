#!/usr/bin/env python3
"""
HumanEval+ Handler unit test script
Tests basic functionality of the new humanevalplus benchmark
"""

import asyncio
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Replace with your benchmark name
BENCHMARK_NAME = "humanevalplus"
HANDLER_CLASS_NAME = "HumanevalplusHandler"

def test_data_loading():
    """Test data loading functionality"""
    print("\n" + "="*60)
    print("Test 1: Data Loading")
    print("="*60)
    
    try:
        # Dynamically import handler
        handler_module = __import__(
            f"ScoreFlow.scripts.{BENCHMARK_NAME}.handler",
            fromlist=[HANDLER_CLASS_NAME]
        )
        HandlerClass = getattr(handler_module, HANDLER_CLASS_NAME)
        
        # Create handler instance
        dataset_path = f"Processed_dataset/{BENCHMARK_NAME}/humanevalplus_test.jsonl"
        handler = HandlerClass(dataset_path=dataset_path)
        
        print(f"✅ Successfully loaded {len(handler.data)} data entries")
        
        # Show structure of first 3 data entries
        print("\nFirst 3 data samples:")
        for i in range(min(3, len(handler.data))):
            data = handler.data[i]
            print(f"\nData {i}:")
            for key in list(data.keys())[:5]:  # Show first 5 fields only
                value = str(data[key])[:100]  # Limit length
                print(f"  {key}: {value}...")
        
        return handler
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_prompt_generation(handler):
    """Test prompt generation functionality"""
    print("\n" + "="*60)
    print("Test 2: Prompt Generation")
    print("="*60)
    
    if not handler:
        print("⚠️ Skipped: Handler not initialized")
        return
    
    try:
        # Test single problem
        prompt_single = handler.get_prompt_text([0])
        print("Prompt for single problem:")
        print("-" * 40)
        print(prompt_single[:500] + "..." if len(prompt_single) > 500 else prompt_single)
        
        # Test multiple problems
        indices = [0, 1, 2] if len(handler.data) >= 3 else list(range(len(handler.data)))
        prompt_multiple = handler.get_prompt_text(indices)
        print(f"\nPrompt length for {len(indices)} problems: {len(prompt_multiple)} characters")
        
        # Verify format
        if "---" in prompt_multiple and "**FUNCTION SIGNATURE" in prompt_multiple:
            print("✅ Prompt format correct (contains Markdown separators)")
        else:
            print("⚠️ Prompt format may need adjustment")
        
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        import traceback
        traceback.print_exc()

def test_verification_data(handler):
    """Test verification data retrieval"""
    print("\n" + "="*60)
    print("Test 3: Verification Data Retrieval")
    print("="*60)
    
    if not handler:
        print("⚠️ Skipped: Handler not initialized")
        return
    
    try:
        # Get verification data for first problem
        verify_data = handler.get_verification_data(0)
        
        print("Verification data structure:")
        print("-" * 40)
        for key, value in list(verify_data.items())[:10]:  # Show first 10 items
            value_str = str(value)[:100]
            print(f"{key}: {value_str}...")
        
        # Check key fields
        required_fields = ['prompt', 'entry_point', 'test']  # Adjust based on needs
        missing_fields = [f for f in required_fields if f not in verify_data]
        
        if not missing_fields:
            print(f"\n✅ Contains all required fields")
        else:
            print(f"\n⚠️ Missing fields: {missing_fields}")
        
    except Exception as e:
        print(f"❌ Verification data retrieval failed: {e}")
        import traceback
        traceback.print_exc()

async def test_judge_logic(handler):
    """Test judging logic (optional)"""
    print("\n" + "="*60)
    print("Test 4: Judge Logic (requires LLM configuration)")
    print("="*60)
    
    if not handler:
        print("⚠️ Skipped: Handler not initialized")
        return
    
    # Check if LLM is configured
    if not handler.config:
        print("⚠️ Skipped: LLM not configured (requires config parameter)")
        print("\nTo test judge function, configure LLM:")
        print("handler.config = {'api_key': 'xxx', 'model': 'gpt-4', ...}")
        return
    
    try:
        # Get test data
        verify_data = handler.get_verification_data(0)
        canonical_solution = verify_data.get('canonical_solution', '')
        
        if canonical_solution:
            # Test with correct answer
            result_correct = await handler.judge(canonical_solution, verify_data)
            print(f"Judge correct answer: {result_correct}")
            
            # Test with wrong answer
            wrong_code = "def wrong_function(): return 'wrong'"
            result_wrong = await handler.judge(wrong_code, verify_data)
            print(f"Judge wrong answer: {result_wrong}")
            
            if result_correct and not result_wrong:
                print("✅ Judge logic working correctly")
            else:
                print("⚠️ Judge logic may need adjustment")
        else:
            print("⚠️ No canonical solution available for testing")
        
    except Exception as e:
        print(f"❌ Judge logic test failed: {e}")
        import traceback
        traceback.print_exc()

def check_conditions_file():
    """Check conditions.py file"""
    print("\n" + "="*60)
    print("Test 5: Check conditions.py")
    print("="*60)
    
    try:
        # Import conditions module
        conditions_module = __import__(
            f"ScoreFlow.scripts.{BENCHMARK_NAME}.conditions",
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
                print(f"✅ {var}: {len(content)} characters")
            else:
                print(f"❌ {var}: Missing")
                all_present = False
        
        if all_present:
            print("\n✅ conditions.py contains all required variables")
        else:
            print("\n⚠️ conditions.py missing some variables")
        
    except ImportError as e:
        print(f"❌ Cannot import conditions.py: {e}")
    except Exception as e:
        print(f"❌ Error checking conditions.py: {e}")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print(f"ScoreFlow Handler Unit Test")
    print(f"Benchmark: {BENCHMARK_NAME}")
    print("="*60)
    
    # 1. Test data loading
    handler = test_data_loading()
    
    # 2. Test prompt generation
    test_prompt_generation(handler)
    
    # 3. Test verification data
    test_verification_data(handler)
    
    # 4. Test judge logic (async)
    # asyncio.run(test_judge_logic(handler))
    
    # 5. Check conditions.py
    check_conditions_file()
    
    # Summary
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Adjust handler.py based on test results")
    print("2. Refine prompt content in conditions.py")
    print("3. Ensure dataset format is correct")
    print("4. Run full workflow test (optional)")

if __name__ == "__main__":
    main()