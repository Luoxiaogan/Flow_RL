#!/usr/bin/env python3
"""
Test DAG extraction on a single workflow to debug dependency extraction.
"""

import json
import sys
import re
from pathlib import Path

# Import the fixed DAG generator
from generate_random_dags_fixed import ImprovedDAGGenerator


def analyze_workflow(jsonl_file: str, workflow_id: str):
    """Analyze a specific workflow."""

    # Find the workflow
    found = None
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            if data.get('workflow_id') == workflow_id:
                found = data
                break

    if not found:
        print(f"Workflow {workflow_id} not found")
        return

    code = found['python_code_blocks'][0]

    # Extract all await calls for reference
    print(f"\n{'='*60}")
    print(f"ANALYZING WORKFLOW: {workflow_id}")
    print(f"{'='*60}\n")

    print("ALL AWAIT CALLS IN CODE:")
    print("-" * 40)

    lines = code.split('\n')
    await_calls = []

    for i, line in enumerate(lines, 1):
        if 'await self.' in line:
            # Extract the variable being assigned
            var_match = re.match(r'\s*(\w+)\s*=\s*await\s+self\.(\w+)', line.strip())
            if var_match:
                var_name = var_match.group(1)
                operator = var_match.group(2)
                await_calls.append((i, var_name, operator))
                print(f"Line {i:3}: {var_name} = await self.{operator}(...)")

    print(f"\nTotal await calls: {len(await_calls)}")

    # Now analyze dependencies
    print(f"\n{'='*60}")
    print("EXPECTED DEPENDENCIES:")
    print("-" * 40)

    # Manual analysis of key dependencies
    for i, line in enumerate(lines, 1):
        if '= await self.' in line:
            # Look for context and instruction parameters
            block_end = i
            while block_end < len(lines) and ')' not in lines[block_end]:
                block_end += 1

            block = '\n'.join(lines[i-1:block_end+1])

            # Find dependencies in context
            context_match = re.search(r'context\s*=\s*([^,\)]+)', block)
            if context_match:
                ctx = context_match.group(1).strip()
                if ctx and ctx != '""':
                    var_match = re.match(r'\s*(\w+)\s*=', lines[i-1])
                    if var_match:
                        target = var_match.group(1)
                        print(f"{target}: context={ctx}")

            # Find dependencies in instruction (f-strings)
            if 'instruction=' in block:
                # Extract all {variable} references
                f_string_vars = re.findall(r'\{(\w+)[^\}]*\}', block)
                if f_string_vars:
                    var_match = re.match(r'\s*(\w+)\s*=', lines[i-1])
                    if var_match:
                        target = var_match.group(1)
                        print(f"{target}: f-string vars={f_string_vars}")

    # Run the DAG extraction
    print(f"\n{'='*60}")
    print("EXTRACTED DAG:")
    print("-" * 40)

    generator = ImprovedDAGGenerator()
    generator.debug = True

    nodes, edges = generator.extract_dag(code)

    print(f"\nNodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")

    print("\nEdge list:")
    for source, target, attrs in edges:
        print(f"  {source} -> {target} [{attrs.get('type', 'unknown')}]")

    # Analyze what's missing
    print(f"\n{'='*60}")
    print("ANALYSIS:")
    print("-" * 40)

    # Expected edges based on manual inspection
    expected_deps = len(await_calls) - 1  # At least sequential dependencies

    print(f"Expected minimum edges: {expected_deps}")
    print(f"Actual edges: {len(edges)}")

    if len(edges) < expected_deps:
        print(f"⚠️ Missing at least {expected_deps - len(edges)} dependencies")
    else:
        print(f"✓ Dependency count seems reasonable")


if __name__ == "__main__":
    # Test on a specific workflow
    jsonl_file = "../data/extracted_python_code.jsonl"

    # Test on drop_12_0 which we know has issues
    workflow_id = "drop_12_0"

    if len(sys.argv) > 1:
        workflow_id = sys.argv[1]

    analyze_workflow(jsonl_file, workflow_id)