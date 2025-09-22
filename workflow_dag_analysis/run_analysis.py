#!/usr/bin/env python3
"""
Quick analysis runner for workflow DAG extraction and visualization.
Run this script to perform complete analysis pipeline.
"""

import subprocess
import sys
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'='*60}")
    print(f"[Running] {description}")
    print(f"Command: {cmd}")
    print('='*60)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Success: {description}")
        if result.stdout:
            print(result.stdout[:500])  # Show first 500 chars of output
    else:
        print(f"❌ Failed: {description}")
        if result.stderr:
            print(f"Error: {result.stderr[:500]}")

    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Run workflow DAG analysis pipeline')
    parser.add_argument('--input', type=str, default='data/extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--limit', type=int, default=10,
                       help='Number of workflows to process')
    parser.add_argument('--skip-extraction', action='store_true',
                       help='Skip code extraction step')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed output')

    args = parser.parse_args()

    # Change to script directory
    script_dir = Path(__file__).parent / 'scripts'

    print("""
╔══════════════════════════════════════════════════════════╗
║         WORKFLOW DAG ANALYSIS PIPELINE                    ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Step 1: Extract Python code (if needed)
    if not args.skip_extraction:
        if not Path(args.input).exists():
            print(f"⚠️  Input file not found: {args.input}")
            print("Running code extraction first...")

            cmd = f"cd {script_dir} && python extract_python_code.py"
            if not run_command(cmd, "Extract Python code from workflows"):
                print("Failed to extract code. Please check the input file.")
                return 1

    # Step 2: Extract and visualize DAGs
    cmd = f"cd {script_dir} && python extract_workflow_dag_simple.py "
    cmd += f"--input ../{args.input} --output-dir ../results/ --limit {args.limit}"
    if args.verbose:
        cmd += " --verbose"

    if not run_command(cmd, "Extract and visualize DAGs"):
        print("Warning: DAG extraction had issues")

    # Step 3: Generate statistical analysis
    cmd = f"cd {script_dir} && python extract_workflow_summary.py "
    cmd += f"--input ../{args.input} --output-dir ../results/ --limit {args.limit}"

    if not run_command(cmd, "Generate statistical analysis"):
        print("Warning: Statistical analysis had issues")

    # Summary
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                    ANALYSIS COMPLETE                      ║
╚══════════════════════════════════════════════════════════╝

📊 Results saved to: workflow_dag_analysis/results/
📈 Check the following files:
   - DAG visualizations: *.png
   - Analysis reports: *.json
   - Summary statistics: workflow_analysis_report.json

To view results:
   - Open PNG files to see DAG visualizations
   - Open JSON files for detailed metrics
   - Check README.md for documentation
    """)

    return 0

if __name__ == "__main__":
    sys.exit(main())