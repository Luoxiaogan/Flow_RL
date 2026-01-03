#!/usr/bin/env python3
"""
Extract correct DAG structure from workflow code - simplified version.
Uses NetworkX and matplotlib for visualization (no Graphviz dependency).
"""

import json
import re
import argparse
from typing import Dict, List, Tuple, Set, Optional
from pathlib import Path
import sys
import subprocess
from collections import OrderedDict, defaultdict

# Check and install dependencies
def check_dependencies():
    dependencies = ['networkx', 'matplotlib']
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
import matplotlib.patches as mpatches


class WorkflowDAGExtractor:
    """Extract correct DAG structure from workflow execution."""

    def __init__(self):
        self.nodes = OrderedDict()
        self.edges = []

    def extract_dag(self, code: str) -> Tuple[Dict, List]:
        """Extract complete DAG from workflow code."""

        # Reset state
        self.nodes = OrderedDict()
        self.edges = []

        # Add input node
        self.nodes['INPUT'] = {
            'type': 'input',
            'label': 'INPUT',
            'step': 0
        }

        # Parse the workflow
        lines = code.split('\n')

        # Track variables and their sources
        var_to_node = {}
        node_counter = 0
        current_step = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Track step changes
            if re.search(r'#\s*Step\s+(\d+)', line_stripped):
                match = re.search(r'#\s*Step\s+(\d+)', line_stripped)
                current_step = int(match.group(1))
                continue

            # Pattern 1: Single await call with assignment
            # e.g., problem_structure = await self.generate(...)
            match = re.match(r'(\w+)\s*=\s*await\s+self\.(\w+)\s*\(', line_stripped)
            if match:
                var_name = match.group(1)
                operator = match.group(2)

                # Create unique node ID
                node_id = f"{operator}_{node_counter}"
                node_counter += 1

                self.nodes[node_id] = {
                    'type': 'operator',
                    'operator': operator,
                    'label': f"{operator}\\n[{var_name}]",
                    'step': current_step,
                    'var_name': var_name
                }

                var_to_node[var_name] = node_id

                # Extract dependencies from context parameter
                context_deps = self._extract_context_dependencies(lines[i:min(i+10, len(lines))], var_to_node)

                if context_deps:
                    for dep in context_deps:
                        self.edges.append((dep, node_id, {'type': 'data'}))
                else:
                    # If no context dependency and it's step 1, connect to INPUT
                    if current_step == 1:
                        self.edges.append(('INPUT', node_id, {'type': 'input'}))

            # Pattern 2: asyncio.gather for parallel execution
            elif 'await asyncio.gather' in line_stripped:
                # Find the assignment variable
                assign_match = re.match(r'(\w+)\s*=\s*await\s+asyncio\.gather', line_stripped)
                result_var = assign_match.group(1) if assign_match else f"gather_{node_counter}"

                # Extract the complete gather block
                gather_block = []
                j = i
                paren_count = 0
                while j < len(lines):
                    gather_line = lines[j]
                    gather_block.append(gather_line)
                    paren_count += gather_line.count('(') - gather_line.count(')')
                    if 'asyncio.gather' in gather_line:
                        paren_count = max(paren_count, 1)  # Ensure we count the gather parenthesis
                    if paren_count > 0 and ')' in gather_line:
                        if paren_count == gather_line.count(')'):
                            break
                    j += 1

                gather_text = '\n'.join(gather_block)

                # Find all self.operator calls in the gather
                gather_nodes = []
                op_pattern = re.compile(r'self\.(\w+)\s*\(')

                for op_match in op_pattern.finditer(gather_text):
                    operator = op_match.group(1)

                    # Create node for each parallel operation
                    node_id = f"{operator}_{node_counter}"
                    node_counter += 1

                    self.nodes[node_id] = {
                        'type': 'operator',
                        'operator': operator,
                        'label': f"{operator}\\n(parallel)",
                        'step': current_step,
                        'parallel': True
                    }

                    gather_nodes.append(node_id)

                    # Look for context dependencies in the specific call
                    call_start = op_match.start()
                    call_end = gather_text.find(')', call_start)
                    if call_end > 0:
                        call_text = gather_text[call_start:call_end]
                        context_deps = self._extract_context_from_text(call_text, var_to_node)

                        for dep in context_deps:
                            self.edges.append((dep, node_id, {'type': 'data'}))

                # Map gather result to nodes
                if gather_nodes:
                    for idx, node_id in enumerate(gather_nodes):
                        var_to_node[f"{result_var}[{idx}]"] = node_id
                        var_to_node[result_var] = node_id  # Allow reference to whole array

            # Pattern 3: Direct await without assignment
            elif re.search(r'await\s+self\.(\w+)\s*\(', line_stripped):
                match = re.search(r'await\s+self\.(\w+)\s*\(', line_stripped)
                operator = match.group(1)

                # Create node
                node_id = f"{operator}_{node_counter}"
                node_counter += 1

                self.nodes[node_id] = {
                    'type': 'operator',
                    'operator': operator,
                    'label': operator,
                    'step': current_step
                }

                # Extract dependencies
                context_deps = self._extract_context_dependencies(lines[i:min(i+10, len(lines))], var_to_node)

                for dep in context_deps:
                    self.edges.append((dep, node_id, {'type': 'data'}))

        # Add OUTPUT node
        self.nodes['OUTPUT'] = {
            'type': 'output',
            'label': 'OUTPUT',
            'step': current_step + 1
        }

        # Find the last operation node(s)
        last_operations = []
        for node_id, node_info in self.nodes.items():
            if node_info['type'] == 'operator':
                # Check if this node has no outgoing edges to other operators
                has_outgoing = any(
                    edge[0] == node_id and self.nodes.get(edge[1], {}).get('type') == 'operator'
                    for edge in self.edges
                )
                if not has_outgoing:
                    last_operations.append(node_id)

        # Connect the last operation to OUTPUT
        if last_operations:
            # Usually it's the last one in execution order
            last_op = last_operations[-1]
            self.edges.append((last_op, 'OUTPUT', {'type': 'output'}))
        elif len(self.nodes) > 2:  # Has operators but no clear last one
            # Find the operator with highest step number
            max_step = -1
            last_op = None
            for node_id, node_info in self.nodes.items():
                if node_info['type'] == 'operator' and node_info.get('step', 0) > max_step:
                    max_step = node_info['step']
                    last_op = node_id
            if last_op:
                self.edges.append((last_op, 'OUTPUT', {'type': 'output'}))

        return self.nodes, self.edges

    def _extract_context_dependencies(self, lines: List[str], var_to_node: Dict) -> List[str]:
        """Extract dependencies from context parameters in the given lines."""
        dependencies = []
        context_text = '\n'.join(lines[:10] if len(lines) > 10 else lines)

        # Look for context= parameter
        context_match = re.search(r'context\s*=\s*([^,\)]+)', context_text)
        if context_match:
            dependencies.extend(self._extract_context_from_text(context_match.group(1), var_to_node))

        # Look for contexts_list= parameter (for ensemble)
        contexts_match = re.search(r'contexts_list\s*=\s*([^,\)]+)', context_text)
        if contexts_match:
            dependencies.extend(self._extract_context_from_text(contexts_match.group(1), var_to_node))

        return dependencies

    def _extract_context_from_text(self, text: str, var_to_node: Dict) -> List[str]:
        """Extract variable references from context text."""
        dependencies = []
        text = text.strip()

        # Direct variable reference
        if text in var_to_node:
            dependencies.append(var_to_node[text])

        # f-string with variables {var} or {var[index]}
        var_refs = re.findall(r'\{(\w+)(?:\[(\d+)\])?\}', text)
        for var_ref in var_refs:
            var_name = var_ref[0]
            index = var_ref[1] if len(var_ref) > 1 and var_ref[1] else None

            if index:
                full_var = f"{var_name}[{index}]"
                if full_var in var_to_node:
                    dependencies.append(var_to_node[full_var])
            elif var_name in var_to_node:
                dependencies.append(var_to_node[var_name])

        # Simple variable references in lists or expressions
        simple_vars = re.findall(r'\b(\w+)\b', text)
        for var_name in simple_vars:
            if var_name in var_to_node and var_to_node[var_name] not in dependencies:
                dependencies.append(var_to_node[var_name])

        return dependencies

    def visualize_dag(self, nodes: Dict, edges: List, workflow_id: str, output_dir: Path):
        """Visualize DAG using NetworkX and matplotlib."""

        # Create NetworkX graph
        G = nx.DiGraph()

        # Add nodes
        for node_id, node_info in nodes.items():
            G.add_node(node_id, **node_info)

        # Add edges
        for source, target, attrs in edges:
            G.add_edge(source, target, **attrs)

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Calculate layout
        pos = self._hierarchical_layout(G, nodes)

        # Color scheme
        node_colors = []
        for node in G.nodes():
            node_info = nodes[node]
            if node_info['type'] == 'input':
                node_colors.append('#90EE90')  # Light green
            elif node_info['type'] == 'output':
                node_colors.append('#FFB6C1')  # Light pink
            else:
                operator = node_info.get('operator', '')
                if operator.lower() == 'generate':
                    node_colors.append('#87CEEB')  # Sky blue
                elif operator.lower() == 'revise':
                    node_colors.append('#DDA0DD')  # Plum
                elif operator.lower() == 'summarize':
                    node_colors.append('#F0E68C')  # Khaki
                elif operator.lower() == 'ensemble':
                    node_colors.append('#FFE4B5')  # Moccasin
                else:
                    node_colors.append('#E0E0E0')  # Light gray

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=2000, alpha=0.9, ax=ax)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray',
                              arrows=True, arrowsize=20,
                              arrowstyle='->', width=1.5, ax=ax)

        # Draw labels
        labels = {node: nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        # Add title
        ax.set_title(f'Workflow DAG: {workflow_id}', fontsize=14, fontweight='bold')
        ax.axis('off')

        # Add legend
        legend_elements = [
            mpatches.Patch(color='#90EE90', label='Input'),
            mpatches.Patch(color='#FFB6C1', label='Output'),
            mpatches.Patch(color='#87CEEB', label='Generate'),
            mpatches.Patch(color='#DDA0DD', label='Revise'),
            mpatches.Patch(color='#F0E68C', label='Summarize'),
            mpatches.Patch(color='#FFE4B5', label='Ensemble')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        # Save figure
        output_file = output_dir / f"{workflow_id}_dag.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        return output_file

    def _hierarchical_layout(self, G: nx.DiGraph, nodes: Dict) -> Dict:
        """Create hierarchical layout for the DAG."""

        # Group nodes by step
        steps = defaultdict(list)
        for node in G.nodes():
            step = nodes[node].get('step', 0)
            steps[step].append(node)

        # Calculate positions
        pos = {}
        y_spacing = 1.0
        max_width = max(len(nodes_in_step) for nodes_in_step in steps.values()) if steps else 1

        for step, nodes_in_step in sorted(steps.items()):
            y = -step * y_spacing
            x_spacing = 2.0 / max(len(nodes_in_step), 1)

            for i, node in enumerate(nodes_in_step):
                x = -1.0 + (i + 0.5) * x_spacing
                pos[node] = (x, y)

        return pos

    def analyze_dag(self, nodes: Dict, edges: List) -> Dict:
        """Analyze DAG properties."""

        # Build NetworkX graph
        G = nx.DiGraph()
        for node_id in nodes:
            G.add_node(node_id)
        for source, target, _ in edges:
            G.add_edge(source, target)

        # Calculate metrics
        metrics = {
            'num_operators': len([n for n in nodes if nodes[n]['type'] == 'operator']),
            'num_edges': len(edges),
            'is_dag': nx.is_directed_acyclic_graph(G),
            'operator_types': defaultdict(int)
        }

        # Count operator types
        for node_info in nodes.values():
            if node_info['type'] == 'operator':
                metrics['operator_types'][node_info.get('operator', 'unknown')] += 1

        # Calculate longest path (excluding INPUT/OUTPUT)
        if metrics['is_dag'] and 'INPUT' in G and 'OUTPUT' in G:
            try:
                paths = list(nx.all_simple_paths(G, 'INPUT', 'OUTPUT'))
                if paths:
                    longest_path = max(paths, key=len)
                    metrics['longest_path'] = len(longest_path) - 2  # Exclude INPUT/OUTPUT
                else:
                    metrics['longest_path'] = 0
            except:
                metrics['longest_path'] = 0
        else:
            metrics['longest_path'] = 0

        # Count parallel operations
        parallel_count = len([n for n in nodes if nodes[n].get('parallel', False)])
        metrics['parallel_operations'] = parallel_count

        return metrics


def main():
    parser = argparse.ArgumentParser(description='Extract DAG from workflows (simplified)')
    parser.add_argument('--input', type=str, default='extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--output-dir', type=str, default='workflow_dags',
                       help='Output directory')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of workflows')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed extraction info')

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

                if args.verbose:
                    print(f"\nProcessing {workflow_id}...")

                # Process first code block
                code_blocks = data.get('python_code_blocks', [])
                if code_blocks:
                    code = code_blocks[0]

                    # Extract DAG
                    nodes, edges = extractor.extract_dag(code)

                    # Analyze DAG
                    metrics = extractor.analyze_dag(nodes, edges)
                    metrics['workflow_id'] = workflow_id
                    metrics['benchmark'] = data.get('benchmark', 'unknown')
                    all_metrics.append(metrics)

                    print(f"{workflow_id}: {metrics['num_operators']} ops, {metrics['longest_path']} depth, {metrics['parallel_operations']} parallel")

                    # Visualize
                    if metrics['num_operators'] > 0:
                        dag_file = extractor.visualize_dag(nodes, edges, workflow_id, output_dir)

                        if args.verbose:
                            print(f"  Saved: {dag_file}")
                            print(f"  Operators: {dict(metrics['operator_types'])}")

                processed += 1

            except Exception as e:
                if args.verbose:
                    print(f"Error at line {line_num}: {e}")

    # Generate summary
    if all_metrics:
        # Summary statistics
        print(f"\n{'='*60}")
        print("DAG EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total workflows: {len(all_metrics)}")

        # Average metrics
        avg_operators = sum(m['num_operators'] for m in all_metrics) / len(all_metrics)
        avg_depth = sum(m['longest_path'] for m in all_metrics) / len(all_metrics)
        avg_parallel = sum(m['parallel_operations'] for m in all_metrics) / len(all_metrics)

        print(f"Average operators: {avg_operators:.1f}")
        print(f"Average depth: {avg_depth:.1f}")
        print(f"Average parallel ops: {avg_parallel:.1f}")

        # Operator distribution
        total_op_counts = defaultdict(int)
        for m in all_metrics:
            for op, count in m['operator_types'].items():
                total_op_counts[op] += count

        print(f"\nOperator distribution:")
        for op, count in sorted(total_op_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {op}: {count}")

        # Save summary
        summary_file = output_dir / 'dag_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_workflows': len(all_metrics),
                'metrics': all_metrics,
                'summary': {
                    'avg_operators': avg_operators,
                    'avg_depth': avg_depth,
                    'avg_parallel_operations': avg_parallel,
                    'operator_distribution': dict(total_op_counts)
                }
            }, f, indent=2)

        print(f"\n[Saved] Summary to {summary_file}")


if __name__ == "__main__":
    main()