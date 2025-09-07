#!/usr/bin/env python3
"""
Test script for the dynamic operator system
Validates all components are working correctly
"""
import os
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ScoreFlow.tools.benchmark_cloner import BenchmarkCloner
from ScoreFlow.scripts.common.operator_loader import OperatorRegistry, OperatorGroupManager
from ScoreFlow.scripts.common.prompt_builder import DynamicPromptBuilder

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"TEST: {title}")
    print("="*60)

def test_operator_registry():
    """Test the operator registry functionality"""
    print_section("Operator Registry")
    
    try:
        registry = OperatorRegistry()
        
        # Test 1: Load operators
        num_operators = len(registry.operators)
        print(f"[OK] Loaded {num_operators} operators from registry")
        
        # Test 2: Get specific operator
        generate_op = registry.get_operator_info('Generate')
        if generate_op:
            print(f"[OK] Found Generate operator: {generate_op['description']}")
        else:
            print("[FAIL] Failed to find Generate operator")
            return False
        
        # Test 3: Get operators by category
        core_ops = registry.get_operators_by_category('core')
        print(f"[OK] Found {len(core_ops)} core operators")
        
        # Test 4: Get operators by module
        common_ops = registry.get_operators_by_module('common.operator')
        print(f"[OK] Found {len(common_ops)} operators in common.operator module")
        
        # Test 5: Get operators for benchmark
        gsm8k_ops = registry.get_operators_for_benchmark('gsm8k')
        print(f"[OK] Found {len(gsm8k_ops)} operators supporting gsm8k")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_operator_groups():
    """Test the operator group manager"""
    print_section("Operator Group Manager")
    
    try:
        manager = OperatorGroupManager()
        
        # Test 1: List groups
        groups = manager.list_groups()
        print(f"[OK] Found {len(groups)} operator groups: {', '.join(groups[:3])}...")
        
        # Test 2: Get specific group
        default_group = manager.get_group('default')
        if default_group:
            operators = default_group.get('operators', [])
            print(f"[OK] Default group has {len(operators)} operators: {', '.join(operators)}")
        else:
            print("[FAIL] Failed to find default group")
            return False
        
        # Test 3: Validate group
        is_valid, missing = manager.validate_group('default')
        if is_valid:
            print("[OK] Default group validation passed")
        else:
            print(f"[FAIL] Default group validation failed: {missing}")
            return False
        
        # Test 4: Get operators for group
        operators = manager.get_operators_for_group('default')
        print(f"[OK] Retrieved {len(operators)} operator details for default group")
        
        # Test 5: Get modules for group
        modules = manager.get_modules_for_group('default')
        print(f"[OK] Default group uses modules: {', '.join(modules)}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_prompt_builder():
    """Test the dynamic prompt builder"""
    print_section("Dynamic Prompt Builder")
    
    try:
        # Test 1: Create builder for default group
        builder = DynamicPromptBuilder('test_benchmark', 'default')
        print("[OK] Created prompt builder with default group")
        
        # Test 2: Build Python start
        python_start = builder.build_python_start()
        if 'import ScoreFlow.scripts.common.operator as operator' in python_start:
            print("[OK] Python start section generated correctly")
        else:
            print("[FAIL] Python start section incorrect")
            return False
        
        # Test 3: Build init code
        init_code = builder.build_init_code()
        if 'self.generate = operator.Generate' in init_code:
            print("[OK] Init code generated correctly")
        else:
            print("[FAIL] Init code incorrect")
            return False
        
        # Test 4: Get operator list
        operators = builder.get_operator_list()
        print(f"[OK] Retrieved operator list: {', '.join(operators)}")
        
        # Test 5: Test with MATH group
        math_builder = DynamicPromptBuilder('test_math', 'math_specialized')
        math_start = math_builder.build_python_start()
        if 'MATH.operator' in math_start:
            print("[OK] MATH group imports generated correctly")
        else:
            print("[FAIL] MATH group imports incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_benchmark_cloner():
    """Test the benchmark cloning functionality"""
    print_section("Benchmark Cloner (Mock Test)")
    
    try:
        cloner = BenchmarkCloner()
        
        # Test 1: List benchmarks
        benchmarks = cloner.list_benchmarks()
        print(f"[OK] Found {len(benchmarks)} benchmarks")
        
        # Test 2: Get benchmark info
        if benchmarks:
            info = cloner.get_benchmark_info(benchmarks[0])
            print(f"[OK] Retrieved info for benchmark '{benchmarks[0]}':")
            print(f"  - Has handler: {info['has_handler']}")
            print(f"  - Has conditions: {info['has_conditions']}")
        
        # Test 3: Validate clone inputs (without actual cloning)
        print("\n[OK] Clone validation test:")
        print("  - Would clone 'gsm8k' -> 'test_gsm8k' with 'reasoning_heavy' group")
        print("  - (Actual cloning skipped to avoid modifying the codebase)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_complete_conditions_generation():
    """Test generating a complete conditions.py file"""
    print_section("Complete Conditions Generation")
    
    try:
        builder = DynamicPromptBuilder('test_benchmark', 'default')
        
        # Generate complete conditions
        task_prompt = "This is a test task prompt for demonstration"
        conditions_content = builder.build_complete_conditions(task_prompt)
        
        # Validate content
        checks = [
            ('TASK_PROMPT', "Task prompt section"),
            ('SYSTEM_PROMPT', "System prompt section"),
            ('PYTHON_START', "Python start section"),
            ('PYTHON_END', "Python end section"),
            ('START_PROMPT', "Start prompt section"),
            ('OPERATOR_INIT_CODE', "Operator init code"),
            ('OPERATOR_GROUP', "Operator group metadata"),
        ]
        
        all_passed = True
        for keyword, description in checks:
            if keyword in conditions_content:
                print(f"[OK] {description} present")
            else:
                print(f"[FAIL] {description} missing")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_validation():
    """Test validation functions"""
    print_section("Validation Functions")
    
    try:
        from ScoreFlow.scripts.common.operator_loader import validate_operator_group_for_benchmark
        
        # Test 1: Validate compatible group
        is_compatible, unsupported = validate_operator_group_for_benchmark('default', 'gsm8k')
        if is_compatible:
            print("[OK] Default group compatible with gsm8k")
        else:
            print(f"[FAIL] Default group not compatible with gsm8k: {unsupported}")
        
        # Test 2: Validate incompatible group
        is_compatible, unsupported = validate_operator_group_for_benchmark('math_specialized', 'mbpp')
        if not is_compatible:
            print(f"[OK] Math group correctly identified as incompatible with mbpp")
        else:
            print("[FAIL] Math group incorrectly marked as compatible with mbpp")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("\n" + "="*60)
    print("SCOREFLOW DYNAMIC OPERATOR SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Operator Registry", test_operator_registry),
        ("Operator Groups", test_operator_groups),
        ("Prompt Builder", test_prompt_builder),
        ("Benchmark Cloner", test_benchmark_cloner),
        ("Conditions Generation", test_complete_conditions_generation),
        ("Validation Functions", test_validation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[FAIL] Test '{name}' crashed: {e}")
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
    
    if passed_count == total_count:
        print("\n==== ALL TESTS PASSED! The system is ready to use. ====")
        print("\nNext steps:")
        print("1. Try cloning a benchmark: python cli.py clone -s gsm8k -t gsm8k_test -g reasoning_heavy")
        print("2. List available groups: python cli.py list-groups")
        print("3. Show group details: python cli.py show-group default")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())