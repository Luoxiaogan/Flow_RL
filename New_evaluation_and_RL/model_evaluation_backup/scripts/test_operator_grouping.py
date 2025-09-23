#!/usr/bin/env python
"""
Test script to verify operator group recognition in hierarchical evaluation
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_operator_groups(jsonl_file):
    """Analyze operator groups in JSONL file"""
    
    file_path = Path(jsonl_file)
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return
    
    print(f"\n[ANALYZING] {file_path}")
    print("="*60)
    
    # Statistics
    operator_combinations = defaultdict(int)
    benchmark_operator_map = defaultdict(lambda: defaultdict(int))
    total_samples = 0
    samples_with_operators = 0
    
    # Read and analyze file
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                total_samples += 1
                
                # Extract data source (benchmark)
                data_source = data.get('data_source', 'unknown')
                if data_source.startswith('workflow_'):
                    benchmark = data_source.replace('workflow_', '')
                else:
                    benchmark = data_source
                
                # Extract operator group
                extra_info = data.get('extra_info', {})
                operator_group = extra_info.get('operator_group', [])
                
                if operator_group:
                    samples_with_operators += 1
                    # Sort for consistent key
                    operator_key = ','.join(sorted(operator_group))
                    operator_combinations[operator_key] += 1
                    benchmark_operator_map[benchmark][operator_key] += 1
                
            except json.JSONDecodeError as e:
                print(f"[WARNING] Line {line_num}: JSON parse error - {e}")
    
    # Print results
    print(f"\n[SUMMARY]")
    print(f"Total samples: {total_samples}")
    print(f"Samples with operator groups: {samples_with_operators}")
    print(f"Coverage: {samples_with_operators/total_samples*100:.1f}%")
    
    print(f"\n[OPERATOR COMBINATIONS]")
    for operators, count in sorted(operator_combinations.items(), 
                                  key=lambda x: x[1], reverse=True):
        operator_list = operators.split(',')
        percentage = count / total_samples * 100
        print(f"  {count:3d} samples ({percentage:5.1f}%): [{', '.join(operator_list)}]")
    
    print(f"\n[DISTRIBUTION BY BENCHMARK]")
    for benchmark in sorted(benchmark_operator_map.keys()):
        print(f"\n  {benchmark.upper()}:")
        operator_groups = benchmark_operator_map[benchmark]
        total_benchmark = sum(operator_groups.values())
        
        for operators, count in sorted(operator_groups.items(), 
                                      key=lambda x: x[1], reverse=True):
            operator_list = operators.split(',')
            percentage = count / total_benchmark * 100
            print(f"    {count:3d} samples ({percentage:5.1f}%): [{', '.join(operator_list)}]")
    
    print("\n[HIERARCHICAL STRUCTURE]")
    print("The data is now ready for hierarchical evaluation:")
    print("  1. Model level: Each model to be evaluated")
    print("  2. Benchmark level: ", end="")
    print(f"{', '.join(sorted(set(benchmark_operator_map.keys())))}")
    print("  3. Operator group level: ", end="")
    unique_operators = set()
    for ops in operator_combinations.keys():
        unique_operators.update(ops.split(','))
    print(f"{', '.join(sorted(unique_operators))}")
    print("  4. Sample level: Individual test samples")
    
    return {
        'total_samples': total_samples,
        'samples_with_operators': samples_with_operators,
        'operator_combinations': dict(operator_combinations),
        'benchmark_operator_map': {b: dict(ops) for b, ops in benchmark_operator_map.items()}
    }

def main():
    """Main function"""
    print("="*60)
    print("Operator Group Analysis for Hierarchical Evaluation")
    print("="*60)
    
    # Default file path
    jsonl_file = "test_scoreflow_data_all/test.jsonl"
    
    # Check if file exists in various locations
    possible_paths = [
        Path(jsonl_file),
        Path("..") / "generate_parquet_and_jsonl" / jsonl_file,
        Path("D:/temp/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl") / jsonl_file
    ]
    
    file_found = None
    for path in possible_paths:
        if path.exists():
            file_found = path
            break
    
    if not file_found:
        print(f"[ERROR] Cannot find test file")
        print(f"Tried paths:")
        for path in possible_paths:
            print(f"  - {path}")
        return 1
    
    # Analyze the file
    results = analyze_operator_groups(file_found)
    
    if results and results['samples_with_operators'] == results['total_samples']:
        print("\n[SUCCESS] All samples have operator groups!")
        print("The data is ready for hierarchical evaluation with operator-based grouping.")
    elif results and results['samples_with_operators'] > 0:
        print(f"\n[PARTIAL] {results['samples_with_operators']}/{results['total_samples']} samples have operator groups.")
        print("Consider updating remaining samples for complete coverage.")
    else:
        print("\n[WARNING] No operator groups found.")
        print("The hierarchical evaluation will use default grouping.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())