#!/usr/bin/env python3
"""
Extract summary statistics and patterns from workflow code.
Generates a comprehensive report of workflow characteristics.
"""

import json
import re
import argparse
from typing import Dict, List, Tuple, Set
from pathlib import Path
from collections import defaultdict, Counter
import sys
import subprocess

# Check dependencies
def check_dependencies():
    dependencies = ['pandas', 'tabulate']
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    if missing:
        print(f"Installing missing dependencies: {missing}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Dependencies installed successfully!")

check_dependencies()

import pandas as pd
from tabulate import tabulate


class WorkflowAnalyzer:
    """Analyze workflow patterns and extract statistics."""

    def __init__(self):
        self.workflows = []
        self.operator_stats = Counter()
        self.pattern_stats = Counter()
        self.benchmark_stats = defaultdict(lambda: {
            'count': 0,
            'operators': Counter(),
            'patterns': Counter()
        })

    def analyze_file(self, filepath: str, limit: int = None):
        """Analyze workflows from JSONL file."""
        print(f"\\n[Analyzing] {filepath}\\n")

        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if limit and i > limit:
                    break

                try:
                    data = json.loads(line)
                    self.analyze_workflow(data)
                except json.JSONDecodeError as e:
                    print(f"[Error] Line {i}: {e}")

    def analyze_workflow(self, data: dict):
        """Analyze a single workflow."""
        workflow_id = data.get('workflow_id', 'unknown')
        benchmark = data.get('benchmark', 'unknown')
        data_indices = data.get('data_indices', [])
        code_blocks = data.get('python_code_blocks', [])

        workflow_info = {
            'id': workflow_id,
            'benchmark': benchmark,
            'num_problems': len(data_indices),
            'num_code_blocks': len(code_blocks),
            'operators': [],
            'patterns': []
        }

        for code in code_blocks:
            # Extract operators
            operators = self.extract_operators(code)
            workflow_info['operators'].extend(operators)

            # Extract patterns
            patterns = self.extract_patterns(code)
            workflow_info['patterns'].extend(patterns)

            # Update statistics
            for op in operators:
                self.operator_stats[op] += 1
                self.benchmark_stats[benchmark]['operators'][op] += 1

            for pattern in patterns:
                self.pattern_stats[pattern] += 1
                self.benchmark_stats[benchmark]['patterns'][pattern] += 1

        self.workflows.append(workflow_info)
        self.benchmark_stats[benchmark]['count'] += 1

    def extract_operators(self, code: str) -> List[str]:
        """Extract operator types from code."""
        pattern = re.compile(r'operator\.(\w+)\(')
        return list(set(pattern.findall(code)))

    def extract_patterns(self, code: str) -> List[str]:
        """Extract workflow patterns from code."""
        patterns = []

        # Check for specific patterns
        if 'asyncio.gather' in code:
            patterns.append('parallel_execution')

        if 'contexts_list' in code:
            patterns.append('ensemble_aggregation')

        if re.search(r'(Step|Phase)\s+\d+', code):
            patterns.append('multi_step_workflow')

        if 'analyses[' in code or 'results[' in code:
            patterns.append('array_indexing')

        if re.search(r'f["\'](.*?){.*?}', code):
            patterns.append('f_string_context')

        if 'for ' in code and 'in ' in code:
            patterns.append('iteration')

        if 'if ' in code:
            patterns.append('conditional_logic')

        if 'try:' in code:
            patterns.append('error_handling')

        if 'import ' in code and 'def run_workflow' in code:
            patterns.append('runtime_imports')

        return patterns

    def generate_report(self, output_dir: Path):
        """Generate comprehensive analysis report."""
        output_dir.mkdir(exist_ok=True)

        # 1. Overall Statistics
        print("\\n" + "="*60)
        print("WORKFLOW ANALYSIS REPORT")
        print("="*60)

        print(f"\\nTotal workflows analyzed: {len(self.workflows)}")
        print(f"Unique benchmarks: {len(self.benchmark_stats)}")

        # 2. Benchmark Distribution
        print("\\n[Benchmark Distribution]")
        benchmark_table = []
        for benchmark, stats in self.benchmark_stats.items():
            benchmark_table.append([
                benchmark,
                stats['count'],
                len(stats['operators']),
                len(stats['patterns'])
            ])

        print(tabulate(
            benchmark_table,
            headers=['Benchmark', 'Workflows', 'Unique Operators', 'Unique Patterns'],
            tablefmt='grid'
        ))

        # 3. Most Common Operators
        print("\\n[Most Common Operators]")
        top_operators = self.operator_stats.most_common(10)
        operator_table = [[op, count, f"{count/len(self.workflows)*100:.1f}%"]
                         for op, count in top_operators]

        print(tabulate(
            operator_table,
            headers=['Operator', 'Count', 'Coverage'],
            tablefmt='grid'
        ))

        # 4. Most Common Patterns
        print("\\n[Most Common Workflow Patterns]")
        top_patterns = self.pattern_stats.most_common(10)
        pattern_table = [[pattern, count, f"{count/len(self.workflows)*100:.1f}%"]
                        for pattern, count in top_patterns]

        print(tabulate(
            pattern_table,
            headers=['Pattern', 'Count', 'Coverage'],
            tablefmt='grid'
        ))

        # 5. Operator Combinations
        print("\\n[Common Operator Combinations]")
        operator_combos = Counter()
        for workflow in self.workflows:
            if workflow['operators']:
                combo = tuple(sorted(set(workflow['operators'])))
                operator_combos[combo] += 1

        top_combos = operator_combos.most_common(5)
        combo_table = []
        for combo, count in top_combos:
            combo_str = " + ".join(combo)
            combo_table.append([combo_str, count, f"{count/len(self.workflows)*100:.1f}%"])

        print(tabulate(
            combo_table,
            headers=['Operator Combination', 'Count', 'Frequency'],
            tablefmt='grid'
        ))

        # 6. Save detailed JSON report
        json_report = {
            'summary': {
                'total_workflows': len(self.workflows),
                'unique_benchmarks': len(self.benchmark_stats),
                'unique_operators': len(self.operator_stats),
                'unique_patterns': len(self.pattern_stats)
            },
            'operator_statistics': dict(self.operator_stats),
            'pattern_statistics': dict(self.pattern_stats),
            'benchmark_statistics': {
                benchmark: {
                    'count': stats['count'],
                    'operators': dict(stats['operators']),
                    'patterns': dict(stats['patterns'])
                }
                for benchmark, stats in self.benchmark_stats.items()
            },
            'workflows': self.workflows
        }

        report_file = output_dir / 'workflow_analysis_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)

        print(f"\\n[Saved] Detailed report to {report_file}")

        # 7. Save CSV for further analysis
        df = pd.DataFrame(self.workflows)
        csv_file = output_dir / 'workflow_summary.csv'
        df.to_csv(csv_file, index=False)
        print(f"[Saved] CSV summary to {csv_file}")

        return report_file


def main():
    parser = argparse.ArgumentParser(description='Extract workflow statistics and patterns')
    parser.add_argument('--input', type=str, default='extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--output-dir', type=str, default='workflow_reports',
                       help='Output directory for reports')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of workflows to analyze')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = WorkflowAnalyzer()

    # Analyze workflows
    analyzer.analyze_file(args.input, args.limit)

    # Generate report
    output_dir = Path(args.output_dir)
    analyzer.generate_report(output_dir)


if __name__ == "__main__":
    main()