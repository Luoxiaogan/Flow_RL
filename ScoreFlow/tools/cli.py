#!/usr/bin/env python3
"""
ScoreFlow Benchmark Management CLI Tool
Provides commands for managing benchmarks and operator groups
"""
import argparse
import sys
import os
import json
from typing import List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ScoreFlow.tools.benchmark_cloner import BenchmarkCloner
from ScoreFlow.scripts.common.operator_loader import OperatorRegistry, OperatorGroupManager

def cmd_clone(args):
    """Handle the clone command"""
    cloner = BenchmarkCloner()
    
    # Prepare dataset paths if provided
    dataset_paths = {}
    if args.train_data:
        dataset_paths['train'] = args.train_data
    if args.test_data:
        dataset_paths['test'] = args.test_data
    
    # Execute cloning
    success = cloner.clone_benchmark(
        source_benchmark=args.source,
        target_benchmark=args.target,
        operator_group=args.operator_group,
        dataset_paths=dataset_paths if dataset_paths else None,
        force=args.force
    )
    
    return 0 if success else 1

def cmd_list_groups(args):
    """Handle the list-groups command"""
    manager = OperatorGroupManager()
    groups = manager.list_groups()
    
    print("\n" + "="*70)
    print("Available Operator Groups")
    print("="*70)
    
    for group_name in sorted(groups):
        group = manager.get_group(group_name)
        print(f"\n{group_name}:")
        print(f"  Name: {group.get('name', 'N/A')}")
        print(f"  Description: {group.get('description', 'N/A')}")
        
        if args.verbose:
            print(f"  Module: {group.get('module', 'common.operator')}")
            print(f"  Operators ({len(group.get('operators', []))}):")
            for op in group.get('operators', []):
                print(f"    - {op}")
            if group.get('special_init'):
                print(f"  Special Init: Yes")
    
    print("\n" + "="*70)
    print(f"Total: {len(groups)} operator groups")
    print("="*70 + "\n")
    
    return 0

def cmd_list_operators(args):
    """Handle the list-operators command"""
    registry = OperatorRegistry()
    operators = list(registry.operators.values())
    
    # Apply filters
    if args.category:
        operators = [op for op in operators if op['category'] == args.category]
    if args.benchmark:
        operators = [op for op in operators 
                    if args.benchmark in op['supported_benchmarks'].split('|') 
                    or op['supported_benchmarks'] == 'all']
    if args.module:
        operators = [op for op in operators if op['module_path'] == args.module]
    
    print("\n" + "="*80)
    print("Registered Operators")
    if args.category or args.benchmark or args.module:
        filters = []
        if args.category:
            filters.append(f"category={args.category}")
        if args.benchmark:
            filters.append(f"benchmark={args.benchmark}")
        if args.module:
            filters.append(f"module={args.module}")
        print(f"Filters: {', '.join(filters)}")
    print("="*80)
    
    # Print header
    print(f"\n{'Name':<15} {'Category':<12} {'Module':<20} {'Description':<35}")
    print("-"*80)
    
    # Print operators
    for op in sorted(operators, key=lambda x: x['operator_name']):
        print(f"{op['operator_name']:<15} {op['category']:<12} "
              f"{op['module_path']:<20} {op['description'][:35]:<35}")
    
    print("-"*80)
    print(f"Total: {len(operators)} operators")
    print("="*80 + "\n")
    
    return 0

def cmd_show_group(args):
    """Handle the show-group command"""
    manager = OperatorGroupManager()
    group = manager.get_group(args.group)
    
    if not group:
        print(f"\n[ERROR] Error: Operator group '{args.group}' not found")
        print(f"Available groups: {', '.join(manager.list_groups())}\n")
        return 1
    
    print("\n" + "="*70)
    print(f"Operator Group: {args.group}")
    print("="*70)
    
    print(f"\nName: {group.get('name', 'N/A')}")
    print(f"Description: {group.get('description', 'N/A')}")
    print(f"Module: {group.get('module', 'common.operator')}")
    
    if group.get('special_init'):
        print(f"Special Initialization: Required")
    
    print(f"\nOperators ({len(group.get('operators', []))}):")
    print("-"*70)
    
    registry = OperatorRegistry()
    for op_name in group.get('operators', []):
        op_info = registry.get_operator_info(op_name)
        if op_info:
            print(f"\n{op_name}:")
            print(f"  Category: {op_info['category']}")
            print(f"  Description: {op_info['description']}")
            print(f"  Signature: {op_info['signature']}")
            print(f"  Module: {op_info['module_path']}")
            print(f"  Supports: {op_info['supported_benchmarks']}")
        else:
            print(f"\n{op_name}: [NOT FOUND IN REGISTRY]")
    
    # Validate group
    is_valid, missing = manager.validate_group(args.group)
    if not is_valid:
        print(f"\n⚠ Warning: Group has missing operators: {missing}")
    else:
        print(f"\n[OK] All operators validated successfully")
    
    print("\n" + "="*70 + "\n")
    
    return 0

def cmd_list_benchmarks(args):
    """Handle the list-benchmarks command"""
    cloner = BenchmarkCloner()
    
    # Get benchmarks from directory
    benchmarks = cloner.list_benchmarks()
    
    # Get benchmark mappings
    mappings = {}
    if os.path.exists(cloner.mapping_file):
        with open(cloner.mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    mapping = json.loads(line)
                    mappings[mapping['benchmark']] = mapping
    
    print("\n" + "="*90)
    print("Available Benchmarks")
    print("="*90)
    
    print(f"\n{'Benchmark':<20} {'Handler Class':<25} {'Operator Group':<20} {'Source':<15}")
    print("-"*90)
    
    for benchmark in benchmarks:
        info = cloner.get_benchmark_info(benchmark)
        mapping = mappings.get(benchmark, {})
        
        handler_class = mapping.get('handler_class', f"{benchmark.capitalize()}Handler")
        operator_group = info.get('operator_group', '-')
        source = info.get('source_benchmark', '-')
        
        print(f"{benchmark:<20} {handler_class:<25} {operator_group:<20} {source:<15}")
        
        if args.verbose:
            print(f"  Has handler: {info['has_handler']}")
            print(f"  Has conditions: {info['has_conditions']}")
            print(f"  Has config: {info['has_config']}")
            if mapping:
                print(f"  Train data: {mapping.get('data_train_dir', 'N/A')}")
                print(f"  Test data: {mapping.get('data_test_dir', 'N/A')}")
    
    print("-"*90)
    print(f"Total: {len(benchmarks)} benchmarks")
    print("="*90 + "\n")
    
    return 0

def cmd_validate(args):
    """Handle the validate command"""
    manager = OperatorGroupManager()
    
    # Validate operator group exists
    group = manager.get_group(args.group)
    if not group:
        print(f"\n[ERROR] Error: Operator group '{args.group}' not found")
        return 1
    
    print(f"\nValidating operator group '{args.group}' for benchmark '{args.benchmark}'...")
    print("-"*60)
    
    # Check each operator
    registry = OperatorRegistry()
    issues = []
    
    for op_name in group.get('operators', []):
        op_info = registry.get_operator_info(op_name)
        if not op_info:
            issues.append(f"Operator '{op_name}' not found in registry")
            continue
        
        supported = op_info['supported_benchmarks']
        if supported != 'all' and args.benchmark not in supported.split('|'):
            issues.append(f"Operator '{op_name}' does not support benchmark '{args.benchmark}'")
    
    if issues:
        print("\n[ERROR] Validation failed with issues:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print(f"\n[OK] All operators in group '{args.group}' support benchmark '{args.benchmark}'")
        return 0

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        prog='scoreflow',
        description='ScoreFlow Benchmark Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s clone -s gsm8k -t gsm8k_reasoning -g reasoning_heavy
  %(prog)s list-groups -v
  %(prog)s list-operators --category core
  %(prog)s show-group default
  %(prog)s validate -g code_focused -b mbpp
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ========== Clone command ==========
    clone_parser = subparsers.add_parser(
        'clone',
        help='Clone a benchmark with a new operator group',
        description='Create a new benchmark based on an existing one with different operators'
    )
    clone_parser.add_argument('-s', '--source', required=True,
                            help='Source benchmark name')
    clone_parser.add_argument('-t', '--target', required=True,
                            help='Target benchmark name')
    clone_parser.add_argument('-g', '--operator-group', required=True,
                            help='Operator group to use')
    clone_parser.add_argument('--train-data',
                            help='Custom training data path')
    clone_parser.add_argument('--test-data',
                            help='Custom test data path')
    clone_parser.add_argument('-f', '--force', action='store_true',
                            help='Force overwrite if target exists')
    
    # ========== List groups command ==========
    list_groups_parser = subparsers.add_parser(
        'list-groups',
        help='List all available operator groups'
    )
    list_groups_parser.add_argument('-v', '--verbose', action='store_true',
                                   help='Show detailed information')
    
    # ========== List operators command ==========
    list_ops_parser = subparsers.add_parser(
        'list-operators',
        help='List all registered operators'
    )
    list_ops_parser.add_argument('-c', '--category',
                                help='Filter by category (core/code/reasoning/specialized)')
    list_ops_parser.add_argument('-b', '--benchmark',
                                help='Filter by benchmark support')
    list_ops_parser.add_argument('-m', '--module',
                                help='Filter by module path')
    
    # ========== Show group command ==========
    show_group_parser = subparsers.add_parser(
        'show-group',
        help='Show details of an operator group'
    )
    show_group_parser.add_argument('group',
                                  help='Operator group name')
    
    # ========== List benchmarks command ==========
    list_bench_parser = subparsers.add_parser(
        'list-benchmarks',
        help='List all available benchmarks'
    )
    list_bench_parser.add_argument('-v', '--verbose', action='store_true',
                                  help='Show detailed information')
    
    # ========== Validate command ==========
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate operator group compatibility with benchmark'
    )
    validate_parser.add_argument('-g', '--group', required=True,
                                help='Operator group name')
    validate_parser.add_argument('-b', '--benchmark', required=True,
                                help='Benchmark name')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if not args.command:
        parser.print_help()
        return 0
    
    # Command dispatch
    commands = {
        'clone': cmd_clone,
        'list-groups': cmd_list_groups,
        'list-operators': cmd_list_operators,
        'show-group': cmd_show_group,
        'list-benchmarks': cmd_list_benchmarks,
        'validate': cmd_validate,
    }
    
    try:
        return commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        if os.environ.get('DEBUG'):
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())