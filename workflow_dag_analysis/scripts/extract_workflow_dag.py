#!/usr/bin/env python3
"""
Extract correct DAG structure from workflow code.
Includes input and output nodes, tracks actual execution dependencies.
"""

import json
import re
import ast
import argparse
from typing import Dict, List, Tuple, Set, Optional
from pathlib import Path
import sys
import subprocess
from collections import OrderedDict, defaultdict

# Check and install dependencies
def check_dependencies():
    dependencies = ['networkx', 'matplotlib', 'graphviz']
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

import networkx as nx
import matplotlib.pyplot as plt
from graphviz import Digraph


class WorkflowDAGExtractor:
    """Extract correct DAG structure from workflow execution."""

    def __init__(self):
        self.nodes = OrderedDict()
        self.edges = []
        self.execution_order = []

    def extract_dag(self, code: str) -> Tuple[Dict, List]:
        """Extract complete DAG from workflow code."""

        # Reset state
        self.nodes = OrderedDict()
        self.edges = []
        self.execution_order = []

        # Add input node
        self.nodes['INPUT'] = {
            'type': 'input',
            'label': 'Problem Input',
            'step': 0
        }

        # Parse the workflow
        lines = code.split('\n')

        # Track variables and their sources
        var_to_node = {}
        node_counter = 0
        current_step = 0

        for i, line in enumerate(lines):
            line = line.strip()

            # Track step changes
            if re.search(r'#\s*Step\s+(\d+)', line):
                match = re.search(r'#\s*Step\s+(\d+)', line)
                current_step = int(match.group(1))
                continue

            # Pattern 1: Single await call with assignment
            # e.g., problem_structure = await self.generate(...)
            match = re.match(r'(\w+)\s*=\s*await\s+self\.(\w+)\s*\(', line)
            if match:
                var_name = match.group(1)
                operator = match.group(2)

                # Create node
                node_id = f"{operator}_{node_counter}"
                node_counter += 1

                self.nodes[node_id] = {
                    'type': 'operator',
                    'operator': operator,
                    'label': f"{operator}\n({var_name})",
                    'step': current_step,
                    'var_name': var_name
                }

                var_to_node[var_name] = node_id

                # Extract dependencies from context
                dependencies = self._extract_context_dependencies(lines[i:i+10], var_to_node)

                if dependencies:
                    for dep in dependencies:
                        self.edges.append((dep, node_id, {'type': 'data'}))
                else:
                    # If no context dependency, depends on input or previous step
                    if current_step == 1:
                        self.edges.append(('INPUT', node_id, {'type': 'input'}))

            # Pattern 2: asyncio.gather for parallel execution
            elif 'await asyncio.gather' in line or 'await gather' in line:
                # Find the assignment variable
                assign_match = re.match(r'(\w+)\s*=\s*await\s+asyncio\.gather', line)
                result_var = assign_match.group(1) if assign_match else f"gather_result_{node_counter}"

                # Collect all operations in the gather
                gather_nodes = []
                j = i
                while j < len(lines):
                    gather_line = lines[j].strip()

                    # Look for self.operator calls
                    op_match = re.search(r'self\.(\w+)\s*\(', gather_line)
                    if op_match:
                        operator = op_match.group(1)

                        # Create node for each parallel operation
                        node_id = f"{operator}_{node_counter}"
                        node_counter += 1

                        self.nodes[node_id] = {
                            'type': 'operator',
                            'operator': operator,
                            'label': f"{operator}\n(parallel)",
                            'step': current_step,
                            'parallel': True
                        }

                        gather_nodes.append(node_id)

                        # Extract context dependencies for this operation
                        context_deps = self._extract_context_dependencies(
                            lines[j:j+5], var_to_node
                        )

                        for dep in context_deps:
                            self.edges.append((dep, node_id, {'type': 'data'}))

                    # Check for end of gather
                    if ')' in gather_line and not gather_line.endswith(','):
                        break
                    j += 1

                # Map gather result to nodes
                if gather_nodes:
                    for idx, node_id in enumerate(gather_nodes):
                        var_to_node[f"{result_var}[{idx}]"] = node_id
                        var_to_node[f"{result_var}"] = node_id  # Allow reference to whole result

            # Pattern 3: Using variables in f-strings or as contexts
            elif 'f"' in line or "f'" in line or 'context=' in line:
                # Extract variable references
                var_refs = re.findall(r'{(\w+)(?:\[(\d+)\])?}', line)
                for var_ref in var_refs:
                    var_name = var_ref[0]
                    index = var_ref[1] if len(var_ref) > 1 and var_ref[1] else None

                    if index:
                        full_var = f"{var_name}[{index}]"
                        if full_var in var_to_node:
                            # This creates an implicit dependency
                            pass  # Will be handled when the operator using this is created

        # Add output node and connect final operations
        self.nodes['OUTPUT'] = {
            'type': 'output',
            'label': 'Workflow Output',
            'step': current_step + 1
        }

        # Find the last operation (usually revise or ensemble)
        last_operations = []
        for node_id, node_info in self.nodes.items():
            if node_info['type'] == 'operator':
                # Check if this node is not a dependency for any other operator node
                is_dependency = any(
                    edge[0] == node_id and self.nodes[edge[1]]['type'] == 'operator'
                    for edge in self.edges
                )
                if not is_dependency:
                    last_operations.append(node_id)

        # Connect last operations to output
        if last_operations:
            for last_op in last_operations[-1:]:  # Usually just the last one
                self.edges.append((last_op, 'OUTPUT', {'type': 'output'}))

        return self.nodes, self.edges

    def _extract_context_dependencies(self, lines: List[str], var_to_node: Dict) -> List[str]:
        """Extract dependencies from context parameters."""
        dependencies = []

        context_text = '\n'.join(lines)

        # Look for context= parameter
        context_match = re.search(r'context\s*=\s*([^,\)]+)', context_text)
        if context_match:
            context_value = context_match.group(1).strip()

            # Direct variable reference
            if context_value in var_to_node:
                dependencies.append(var_to_node[context_value])

            # f-string with variables
            var_refs = re.findall(r'{(\w+)(?:\[(\d+)\])?}', context_value)
            for var_ref in var_refs:
                var_name = var_ref[0]
                index = var_ref[1] if len(var_ref) > 1 and var_ref[1] else None

                if index:
                    full_var = f"{var_name}[{index}]"
                    if full_var in var_to_node:
                        dependencies.append(var_to_node[full_var])
                elif var_name in var_to_node:
                    dependencies.append(var_to_node[var_name])

        # Look for contexts_list parameter (for ensemble)
        contexts_match = re.search(r'contexts_list\s*=\s*([^,\)]+)', context_text)
        if contexts_match:
            contexts_value = contexts_match.group(1).strip()

            # If it's a variable name
            if contexts_value in var_to_node:
                dependencies.append(var_to_node[contexts_value])

            # If it's a list of variables
            var_names = re.findall(r'(\w+)', contexts_value)
            for var_name in var_names:
                if var_name in var_to_node:
                    dependencies.append(var_to_node[var_name])

        return dependencies

    def visualize_dag(self, nodes: Dict, edges: List, workflow_id: str, output_dir: Path):
        """Create DAG visualization using Graphviz."""

        dot = Digraph(comment=f'Workflow DAG: {workflow_id}', engine='dot')
        dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
        dot.attr('edge', fontname='Arial', fontsize='9')

        # Color scheme
        colors = {
            'input': '#90EE90',     # Light green
            'output': '#FFB6C1',    # Light pink
            'Generate': '#87CEEB',  # Sky blue
            'Revise': '#DDA0DD',    # Plum
            'Summarize': '#F0E68C', # Khaki
            'Ensemble': '#FFE4B5',  # Moccasin
            'default': '#E0E0E0'    # Light gray
        }

        # Group nodes by step
        steps = defaultdict(list)
        for node_id, node_info in nodes.items():
            steps[node_info.get('step', 0)].append((node_id, node_info))

        # Create nodes
        for step, step_nodes in sorted(steps.items()):
            with dot.subgraph(name=f'cluster_{step}') as cluster:
                cluster.attr(label=f'Step {step}' if step > 0 else '',
                           style='dotted' if step > 0 else 'invis',
                           color='gray')

                for node_id, node_info in step_nodes:
                    if node_info['type'] == 'input':
                        dot.node(node_id, node_info['label'],
                               fillcolor=colors['input'],
                               shape='ellipse')
                    elif node_info['type'] == 'output':
                        dot.node(node_id, node_info['label'],
                               fillcolor=colors['output'],
                               shape='ellipse')
                    else:
                        operator = node_info.get('operator', 'unknown')
                        color = colors.get(operator.capitalize(), colors['default'])

                        # Add parallel indicator
                        if node_info.get('parallel'):
                            dot.node(node_id, node_info['label'],
                                   fillcolor=color,
                                   penwidth='2',
                                   peripheries='2')
                        else:
                            dot.node(node_id, node_info['label'],
                                   fillcolor=color)

        # Add edges
        for source, target, attrs in edges:
            edge_type = attrs.get('type', 'data')
            if edge_type == 'input':
                dot.edge(source, target, color='green', style='dashed')
            elif edge_type == 'output':
                dot.edge(source, target, color='red', style='dashed')
            else:
                dot.edge(source, target, color='blue')

        # Save visualization
        output_path = output_dir / f"{workflow_id}_dag"
        dot.render(str(output_path), format='png', cleanup=True)

        return Path(f"{output_path}.png")

    def analyze_dag_properties(self, nodes: Dict, edges: List) -> Dict:
        """Analyze DAG properties and metrics."""

        G = nx.DiGraph()

        # Build NetworkX graph
        for node_id in nodes:
            G.add_node(node_id)

        for source, target, _ in edges:
            G.add_edge(source, target)

        # Calculate metrics
        metrics = {
            'num_nodes': len(nodes) - 2,  # Exclude INPUT/OUTPUT
            'num_edges': len(edges),
            'is_dag': nx.is_directed_acyclic_graph(G),
            'longest_path': 0,
            'max_parallelism': 0,
            'operator_counts': defaultdict(int)
        }

        # Count operators
        for node_info in nodes.values():
            if node_info['type'] == 'operator':
                metrics['operator_counts'][node_info['operator']] += 1

        # Calculate longest path
        if metrics['is_dag'] and 'INPUT' in G and 'OUTPUT' in G:
            try:
                longest = nx.dag_longest_path(G, weight=None)
                metrics['longest_path'] = len(longest) - 2  # Exclude INPUT/OUTPUT
            except:
                pass

        # Calculate max parallelism per step
        step_counts = defaultdict(int)
        for node_info in nodes.values():
            if node_info['type'] == 'operator':
                step = node_info.get('step', 0)
                step_counts[step] += 1

        if step_counts:
            metrics['max_parallelism'] = max(step_counts.values())

        return metrics


def main():
    parser = argparse.ArgumentParser(description='Extract correct DAG from workflows')
    parser.add_argument('--input', type=str, default='extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--output-dir', type=str, default='workflow_dags',
                       help='Output directory')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of workflows to process')
    parser.add_argument('--workflow-id', type=str, default=None,
                       help='Process specific workflow by ID')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Initialize extractor
    extractor = WorkflowDAGExtractor()

    print(f"\n[DAG Extraction] Processing {args.input}\n")

    processed = 0
    all_metrics = []

    with open(args.input, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if args.limit and processed >= args.limit:
                break

            try:
                data = json.loads(line)
                workflow_id = data.get('workflow_id', f'workflow_{line_num}')

                # Skip if specific workflow requested and doesn't match
                if args.workflow_id and workflow_id != args.workflow_id:
                    continue

                print(f"Processing {workflow_id}...")

                # Process each code block
                for i, code_block in enumerate(data.get('python_code_blocks', [])):
                    # Extract DAG
                    nodes, edges = extractor.extract_dag(code_block)

                    if nodes:
                        # Analyze properties
                        metrics = extractor.analyze_dag_properties(nodes, edges)
                        metrics['workflow_id'] = workflow_id
                        all_metrics.append(metrics)

                        # Visualize DAG
                        dag_file = extractor.visualize_dag(nodes, edges, workflow_id, output_dir)

                        print(f"  [Extracted] {metrics['num_nodes']} operators, {metrics['num_edges']} edges")
                        print(f"  [Properties] Longest path: {metrics['longest_path']}, Max parallelism: {metrics['max_parallelism']}")
                        print(f"  [Saved] DAG visualization to {dag_file}")

                processed += 1

            except Exception as e:
                print(f"  [Error] Processing workflow at line {line_num}: {e}")

    # Save summary
    if all_metrics:
        summary_file = output_dir / 'dag_analysis_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_workflows': len(all_metrics),
                'metrics': all_metrics
            }, f, indent=2)

        print(f"\n[Complete] Extracted DAGs from {len(all_metrics)} workflows")
        print(f"[Summary] Saved to {summary_file}")


if __name__ == "__main__":
    main()