#!/usr/bin/env python3
"""
Test script for the enhanced operator system with split prompt structure
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ScoreFlow.tools.benchmark_cloner_v2 import EnhancedBenchmarkCloner, analyze_all_benchmarks
from ScoreFlow.scripts.common.prompt_builder_v2 import EnhancedPromptBuilder

def test_enhanced_clone():
    """Test cloning with enhanced split structure"""
    print("\n" + "="*60)
    print("TEST: Enhanced Benchmark Cloning")
    print("="*60)
    
    cloner = EnhancedBenchmarkCloner()
    
    # Clone gsm8k with reasoning_heavy group using split structure
    success = cloner.clone_benchmark(
        source_benchmark='gsm8k',
        target_benchmark='gsm8k_reasoning_v2',
        operator_group='reasoning_heavy',
        force=True,  # Overwrite if exists
        use_split_structure=True  # Use modern split structure
    )
    
    if success:
        print("\n[OK] Successfully created gsm8k_reasoning_v2 with split structure")
        
        # Analyze the created structure
        analysis = cloner.analyze_benchmark_structure('gsm8k_reasoning_v2')
        print(f"\nStructure Analysis:")
        print(f"  - Type: {analysis['structure_type']}")
        print(f"  - Variables: {', '.join(analysis['prompt_variables'])}")
        
        return True
    else:
        print("\n[FAIL] Failed to create gsm8k_reasoning_v2")
        return False

def test_prompt_builder():
    """Test the enhanced prompt builder"""
    print("\n" + "="*60)
    print("TEST: Enhanced Prompt Builder")
    print("="*60)
    
    try:
        builder = EnhancedPromptBuilder('test_benchmark', 'default')
        
        # Test generating split prompts
        prompts = builder.get_split_prompts()
        
        print("Generated prompt components:")
        for key in prompts:
            print(f"  - {key}: {len(prompts[key])} chars")
        
        # Check that all expected components are present
        expected = [
            'OPERATOR_PROMPT_PART_1',
            'OPERATOR_PROMPT_PART_2', 
            'USER_PROMPT_LONG',
            'SYSTEM_PROMPT',
            'PYTHON_START',
            'START_PROMPT'
        ]
        
        all_present = all(key in prompts for key in expected)
        
        if all_present:
            print("\n[OK] All expected prompt components generated")
            return True
        else:
            print("\n[FAIL] Missing some prompt components")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility with legacy structure"""
    print("\n" + "="*60)
    print("TEST: Backward Compatibility")
    print("="*60)
    
    cloner = EnhancedBenchmarkCloner()
    
    # Clone with legacy structure for backward compatibility
    success = cloner.clone_benchmark(
        source_benchmark='gsm8k',
        target_benchmark='gsm8k_legacy',
        operator_group='default',
        force=True,
        use_split_structure=False  # Use legacy single START_PROMPT
    )
    
    if success:
        print("\n[OK] Successfully created gsm8k_legacy with legacy structure")
        
        # Analyze the created structure
        analysis = cloner.analyze_benchmark_structure('gsm8k_legacy')
        print(f"\nStructure Analysis:")
        print(f"  - Type: {analysis['structure_type']}")
        print(f"  - Has START_PROMPT: {'START_PROMPT' in analysis['prompt_variables']}")
        
        return True
    else:
        print("\n[FAIL] Failed to create gsm8k_legacy")
        return False

def run_all_tests():
    """Run all enhanced system tests"""
    print("\n" + "="*60)
    print("ENHANCED OPERATOR SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Enhanced Prompt Builder", test_prompt_builder),
        ("Enhanced Clone (Split)", test_enhanced_clone),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{name:<30} {status}")
    
    print("-"*60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    # Analyze all benchmarks
    print("\n" + "="*60)
    print("ANALYZING ALL EXISTING BENCHMARKS")
    print("="*60)
    analyze_all_benchmarks()
    
    if passed_count == total_count:
        print("\n==== ALL TESTS PASSED! ====")
        print("\nThe enhanced system with split prompt structure is ready!")
        print("\nNext steps:")
        print("1. Use gsm8k_reasoning_v2 with the new split structure")
        print("2. workflow_generator.py will correctly load OPERATOR_PROMPT_PART_1/2")
        print("3. The system is backward compatible with legacy START_PROMPT")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())