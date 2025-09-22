#!/usr/bin/env python3
"""
Fixed version of DAG generator with improved dependency extraction.
Correctly extracts dependencies from instruction, context, and f-strings.
"""

import json
import random
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse
from collections import OrderedDict, defaultdict
import re

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

check_dependencies()

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class ImprovedDAGGenerator:
    """Generate DAG with correct dependency extraction."""

    def __init__(self):
        self.nodes = OrderedDict()
        self.edges = []
        self.debug = False  # Set to True for detailed debugging

    def extract_dag(self, code: str) -> Tuple[Dict, List]:
        """Extract DAG structure from workflow code with improved dependency detection."""
        self.nodes = OrderedDict()
        self.edges = []

        # Add input node
        self.nodes['INPUT'] = {
            'type': 'input',
            'label': 'INPUT',
            'step': 0
        }

        lines = code.split('\n')
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

            # Pattern: variable = await self.operator(...)
            match = re.match(r'(\w+)\s*=\s*await\s+self\.(\w+)\s*\(', line_stripped)
            if match:
                var_name = match.group(1)
                operator = match.group(2)

                node_id = f"{operator}_{node_counter}"
                node_counter += 1

                self.nodes[node_id] = {
                    'type': 'operator',
                    'operator': operator,
                    'label': f"{operator}\\n[{var_name}]",
                    'step': current_step,
                    'var_name': var_name,
                    'line': i + 1
                }

                var_to_node[var_name] = node_id

                # Extract complete call block (handles multi-line calls)
                call_block = self._extract_call_block(lines, i)

                # Extract dependencies from the entire call
                dependencies = self._extract_all_dependencies(call_block, var_to_node)

                if self.debug:
                    print(f"Node {node_id}: Found deps {dependencies} from block:\n{call_block[:100]}")

                if dependencies:
                    for dep in dependencies:
                        self.edges.append((dep, node_id, {'type': 'data'}))
                elif current_step == 1:
                    # First step operations depend on input
                    self.edges.append(('INPUT', node_id, {'type': 'input'}))

            # Pattern: asyncio.gather for parallel execution
            elif 'await asyncio.gather' in line_stripped:
                assign_match = re.match(r'(\w+)\s*=\s*await\s+asyncio\.gather', line_stripped)
                result_var = assign_match.group(1) if assign_match else f"gather_{node_counter}"

                # Extract complete gather block
                gather_block = self._extract_gather_block(lines, i)

                # Find all operations in the gather
                gather_nodes = []
                op_pattern = re.compile(r'self\.(\w+)\s*\(')

                # Split by 'self.' to find individual operations
                ops_in_gather = gather_block.split('self.')

                for op_text in ops_in_gather[1:]:  # Skip first empty split
                    op_match = re.match(r'(\w+)\s*\(', op_text)
                    if op_match:
                        operator = op_match.group(1)

                        node_id = f"{operator}_{node_counter}"
                        node_counter += 1

                        self.nodes[node_id] = {
                            'type': 'operator',
                            'operator': operator,
                            'label': f"{operator}\\n(parallel)",
                            'step': current_step,
                            'parallel': True,
                            'line': i + 1
                        }

                        gather_nodes.append(node_id)

                        # Extract dependencies for this specific operation
                        # Find the complete parameter block for this operation
                        op_params = self._extract_operation_params(op_text)
                        dependencies = self._extract_all_dependencies(op_params, var_to_node)

                        for dep in dependencies:
                            self.edges.append((dep, node_id, {'type': 'data'}))

                # Map gather result to nodes
                if gather_nodes:
                    for idx, node_id in enumerate(gather_nodes):
                        var_to_node[f"{result_var}[{idx}]"] = node_id
                        var_to_node[result_var] = node_id

        # Add output node
        self.nodes['OUTPUT'] = {
            'type': 'output',
            'label': 'OUTPUT',
            'step': current_step + 1
        }

        # Find and connect last operation to output
        last_operations = self._find_last_operations()
        if last_operations:
            for last_op in last_operations:
                self.edges.append((last_op, 'OUTPUT', {'type': 'output'}))

        return self.nodes, self.edges

    def _extract_call_block(self, lines: List[str], start_idx: int) -> str:
        """Extract complete function call block (handles multi-line)."""
        block = []
        paren_count = 0
        i = start_idx

        while i < len(lines):
            line = lines[i]
            block.append(line)

            # Count parentheses
            paren_count += line.count('(') - line.count(')')

            # If we've closed all parentheses, we're done
            if paren_count <= 0 and i > start_idx:
                break

            i += 1

        return '\n'.join(block)

    def _extract_gather_block(self, lines: List[str], start_idx: int) -> str:
        """Extract complete asyncio.gather block."""
        block = []
        paren_count = 0
        i = start_idx

        while i < len(lines):
            line = lines[i]
            block.append(line)

            if 'asyncio.gather' in line:
                paren_count = max(paren_count, 1)

            paren_count += line.count('(') - line.count(')')

            if paren_count <= 0 and i > start_idx:
                break

            i += 1

        return '\n'.join(block)

    def _extract_operation_params(self, op_text: str) -> str:
        """Extract parameter block for a specific operation."""
        # Find the opening parenthesis and extract until matching close
        paren_count = 0
        start = op_text.find('(')
        if start == -1:
            return ""

        result = []
        for i, char in enumerate(op_text[start:]):
            result.append(char)
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    break

        return ''.join(result)

    def _extract_all_dependencies(self, text: str, var_to_node: Dict) -> List[str]:
        """Extract all variable dependencies from a code block."""
        dependencies = set()

        # 1. Extract from instruction parameter (including f-strings)
        instruction_pattern = re.compile(r'instruction\s*=\s*(f?["\'][\s\S]*?["\'])', re.MULTILINE)
        for match in instruction_pattern.finditer(text):
            instruction_text = match.group(1)

            # Extract variables from f-string {variable} format
            f_string_vars = re.findall(r'\{(\w+)(?:\[[\w\d]+\])?\}', instruction_text)
            for var in f_string_vars:
                if var in var_to_node:
                    dependencies.add(var_to_node[var])

            # Also check for variable references in string concatenation
            concat_vars = re.findall(r'\+\s*(\w+)\s*\+', instruction_text)
            for var in concat_vars:
                if var in var_to_node:
                    dependencies.add(var_to_node[var])

        # 2. Extract from context parameter
        context_pattern = re.compile(r'context\s*=\s*([^,\)]+?)(?:,|\))')
        for match in context_pattern.finditer(text):
            context_text = match.group(1)
            deps = self._extract_variables_from_expression(context_text, var_to_node)
            dependencies.update(deps)

        # 3. Extract from contexts_list parameter
        contexts_pattern = re.compile(r'contexts_list\s*=\s*([^,\)]+?)(?:,|\))')
        for match in contexts_pattern.finditer(text):
            contexts_text = match.group(1)
            deps = self._extract_variables_from_expression(contexts_text, var_to_node)
            dependencies.update(deps)

        # 4. Extract from any f-string anywhere in the block
        f_string_pattern = re.compile(r'f["\'].*?\{(\w+)(?:\[[\w\d]+\])?\}.*?["\']')
        for match in f_string_pattern.finditer(text):
            var = match.group(1)
            if var in var_to_node:
                dependencies.add(var_to_node[var])

        return list(dependencies)

    def _extract_variables_from_expression(self, expr: str, var_to_node: Dict) -> Set[str]:
        """Extract variable references from an expression."""
        deps = set()
        expr = expr.strip()

        # Direct variable reference
        if expr in var_to_node:
            deps.add(var_to_node[expr])

        # Function calls: json.dumps(var), str(var), etc.
        func_pattern = re.compile(r'\w+\((\w+)\)')
        for match in func_pattern.finditer(expr):
            var = match.group(1)
            if var in var_to_node:
                deps.add(var_to_node[var])

        # List/dict indexing: var[0], var['key']
        index_pattern = re.compile(r'(\w+)\[')
        for match in index_pattern.finditer(expr):
            var = match.group(1)
            if var in var_to_node:
                deps.add(var_to_node[var])

        # Conditional expressions: x if condition else y
        if ' if ' in expr and ' else ' in expr:
            parts = expr.split(' if ')
            if len(parts) >= 2:
                # Check the value part
                value_part = parts[0].strip()
                if value_part in var_to_node:
                    deps.add(var_to_node[value_part])

                # Check the else part
                else_parts = expr.split(' else ')
                if len(else_parts) >= 2:
                    else_part = else_parts[-1].strip()
                    if else_part in var_to_node:
                        deps.add(var_to_node[else_part])

        # Method calls: var.method()
        method_pattern = re.compile(r'(\w+)\.\w+')
        for match in method_pattern.finditer(expr):
            var = match.group(1)
            if var in var_to_node:
                deps.add(var_to_node[var])

        # Simple word boundaries (catch remaining cases)
        word_pattern = re.compile(r'\b(\w+)\b')
        for match in word_pattern.finditer(expr):
            var = match.group(1)
            if var in var_to_node:
                deps.add(var_to_node[var])

        return deps

    def _find_last_operations(self) -> List[str]:
        """Find operations that have no outgoing edges."""
        last_ops = []

        for node_id, info in self.nodes.items():
            if info['type'] == 'operator':
                # Check if this node has any outgoing edges to other operators
                has_outgoing = any(
                    edge[0] == node_id and
                    self.nodes.get(edge[1], {}).get('type') == 'operator'
                    for edge in self.edges
                )

                if not has_outgoing:
                    last_ops.append(node_id)

        # If we found multiple last operations, return the one with highest step
        if len(last_ops) > 1:
            last_ops.sort(key=lambda x: self.nodes[x].get('step', 0), reverse=True)
            return [last_ops[0]]  # Return only the latest one

        return last_ops

    def generate_dag_file(self, nodes: Dict, edges: List, code: str,
                         workflow_id: str, output_dir: Path) -> Path:
        """Generate DAG file with source code as comments."""

        dag_file = output_dir / f"{workflow_id}.dag"

        with open(dag_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# DAG for workflow: {workflow_id}\n")
            f.write(f"# Generated from Python workflow code\n")
            f.write("#" * 80 + "\n\n")

            # Write original source code as comment
            f.write("# ORIGINAL SOURCE CODE:\n")
            f.write("#" * 80 + "\n")
            for line in code.split('\n'):
                f.write(f"# {line}\n")
            f.write("#" * 80 + "\n\n")

            # Write DAG structure
            f.write("# DAG STRUCTURE:\n")
            f.write("#" * 80 + "\n\n")

            # Write nodes
            f.write("NODES:\n")
            f.write("-" * 40 + "\n")
            for node_id, info in nodes.items():
                f.write(f"Node: {node_id}\n")
                f.write(f"  Type: {info['type']}\n")
                if 'operator' in info:
                    f.write(f"  Operator: {info['operator']}\n")
                if 'var_name' in info:
                    f.write(f"  Variable: {info['var_name']}\n")
                if 'step' in info:
                    f.write(f"  Step: {info['step']}\n")
                if 'parallel' in info and info['parallel']:
                    f.write(f"  Parallel: True\n")
                if 'line' in info:
                    f.write(f"  Source Line: {info['line']}\n")
                f.write("\n")

            # Write edges
            f.write("\nEDGES:\n")
            f.write("-" * 40 + "\n")
            for source, target, attrs in edges:
                edge_type = attrs.get('type', 'dependency')
                f.write(f"{source} -> {target} [{edge_type}]\n")

            # Write summary statistics
            f.write("\n" + "#" * 80 + "\n")
            f.write("# STATISTICS:\n")
            f.write("#" * 80 + "\n")

            num_operators = len([n for n in nodes if nodes[n]['type'] == 'operator'])
            num_parallel = len([n for n in nodes if nodes[n].get('parallel', False)])

            f.write(f"# Total Nodes: {len(nodes)}\n")
            f.write(f"# Total Edges: {len(edges)}\n")
            f.write(f"# Operators: {num_operators}\n")
            f.write(f"# Parallel Operations: {num_parallel}\n")

            # Check if it's a DAG
            G = nx.DiGraph()
            G.add_nodes_from(nodes.keys())
            G.add_edges_from([(e[0], e[1]) for e in edges])
            is_dag = nx.is_directed_acyclic_graph(G)

            f.write(f"# Is DAG: {is_dag}\n")

            if is_dag and 'INPUT' in G and 'OUTPUT' in G:
                try:
                    paths = list(nx.all_simple_paths(G, 'INPUT', 'OUTPUT'))
                    if paths:
                        longest = max(paths, key=len)
                        f.write(f"# Longest Path: {len(longest) - 2} (excluding INPUT/OUTPUT)\n")
                except:
                    pass

        return dag_file

    def visualize_dag(self, nodes: Dict, edges: List, workflow_id: str,
                      output_dir: Path) -> Path:
        """Create DAG visualization."""

        G = nx.DiGraph()
        for node_id, info in nodes.items():
            G.add_node(node_id, **info)
        for source, target, attrs in edges:
            G.add_edge(source, target, **attrs)

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))

        # Calculate layout
        pos = self._hierarchical_layout(G, nodes)

        # Color scheme
        node_colors = []
        for node in G.nodes():
            info = nodes[node]
            if info['type'] == 'input':
                node_colors.append('#90EE90')  # Light green
            elif info['type'] == 'output':
                node_colors.append('#FFB6C1')  # Light pink
            else:
                operator = info.get('operator', '').lower()
                if operator == 'generate':
                    node_colors.append('#87CEEB')  # Sky blue
                elif operator == 'revise':
                    node_colors.append('#DDA0DD')  # Plum
                elif operator == 'summarize':
                    node_colors.append('#F0E68C')  # Khaki
                elif operator == 'ensemble':
                    node_colors.append('#FFE4B5')  # Moccasin
                elif operator == 'decompose':
                    node_colors.append('#98FB98')  # Pale green
                elif operator == 'programmer':
                    node_colors.append('#FFA07A')  # Light salmon
                else:
                    node_colors.append('#E0E0E0')  # Light gray

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=1800, alpha=0.9, ax=ax)

        # Draw edges with different styles
        data_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'data']
        input_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'input']
        output_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'output']

        nx.draw_networkx_edges(G, pos, edgelist=data_edges, edge_color='blue',
                              arrows=True, arrowsize=15, width=1.2, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=input_edges, edge_color='green',
                              arrows=True, arrowsize=15, width=1.2, style='dashed', ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=output_edges, edge_color='red',
                              arrows=True, arrowsize=15, width=1.2, style='dashed', ax=ax)

        # Draw labels
        labels = {node: nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)

        # Title and legend
        ax.set_title(f'DAG: {workflow_id}\n{len(nodes)} nodes, {len(edges)} edges',
                    fontsize=12, fontweight='bold')
        ax.axis('off')

        legend_elements = [
            mpatches.Patch(color='#90EE90', label='Input'),
            mpatches.Patch(color='#FFB6C1', label='Output'),
            mpatches.Patch(color='#87CEEB', label='Generate'),
            mpatches.Patch(color='#DDA0DD', label='Revise'),
            mpatches.Patch(color='#F0E68C', label='Summarize'),
            mpatches.Patch(color='#FFE4B5', label='Ensemble'),
            mpatches.Patch(color='#98FB98', label='Decompose'),
            mpatches.Patch(color='#FFA07A', label='Programmer')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=8)

        # Save figure
        output_file = output_dir / f"{workflow_id}.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        return output_file

    def _hierarchical_layout(self, G: nx.DiGraph, nodes: Dict) -> Dict:
        """Create hierarchical layout."""
        steps = defaultdict(list)
        for node in G.nodes():
            step = nodes[node].get('step', 0)
            steps[step].append(node)

        pos = {}
        y_spacing = 1.0
        max_width = max(len(nodes_in_step) for nodes_in_step in steps.values()) if steps else 1

        for step, nodes_in_step in sorted(steps.items()):
            y = -step * y_spacing
            x_spacing = 3.0 / max(len(nodes_in_step), 1)

            for i, node in enumerate(nodes_in_step):
                x = -1.5 + (i + 0.5) * x_spacing
                pos[node] = (x, y)

        return pos


def main():
    parser = argparse.ArgumentParser(description='Generate random DAGs with fixed extraction')
    parser.add_argument('--input', type=str, default='../data/extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--output-dir', type=str, default='../results/fixed_dags',
                       help='Output directory')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of random workflows to process')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')

    args = parser.parse_args()

    # Set random seed
    random.seed(args.seed)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    dag_dir = output_dir / 'dag_files'
    img_dir = output_dir / 'images'
    dag_dir.mkdir(exist_ok=True)
    img_dir.mkdir(exist_ok=True)

    # Read all workflows
    print(f"\n{'='*60}")
    print(f"GENERATING RANDOM DAGS (FIXED ALGORITHM)")
    print(f"{'='*60}\n")

    print(f"Reading workflows from: {args.input}")

    workflows = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                workflows.append(json.loads(line))
            except:
                continue

    print(f"Total workflows available: {len(workflows)}")

    # Select random workflows
    num_to_select = min(args.count, len(workflows))
    selected = random.sample(workflows, num_to_select)

    print(f"Selected {num_to_select} random workflows\n")

    # Process each workflow
    generator = ImprovedDAGGenerator()
    generator.debug = args.debug

    successful = 0
    failed = 0
    edge_counts = []

    print(f"{'='*60}")
    print("Processing workflows...")
    print(f"{'='*60}\n")

    for i, workflow in enumerate(selected, 1):
        workflow_id = workflow.get('workflow_id', f'workflow_{i}')

        # Progress indicator
        if i % 10 == 0:
            print(f"Progress: {i}/{num_to_select} ({i*100/num_to_select:.1f}%)")

        try:
            # Get first code block
            code_blocks = workflow.get('python_code_blocks', [])
            if not code_blocks:
                continue

            code = code_blocks[0]

            # Extract DAG
            nodes, edges = generator.extract_dag(code)

            # Skip if no operators found
            if len([n for n in nodes if nodes[n]['type'] == 'operator']) == 0:
                continue

            # Generate DAG file with annotations
            dag_file = generator.generate_dag_file(nodes, edges, code, workflow_id, dag_dir)

            # Generate visualization
            img_file = generator.visualize_dag(nodes, edges, workflow_id, img_dir)

            successful += 1
            edge_counts.append(len(edges))

            # Show detailed info for first few
            if i <= 3 or args.debug:
                print(f"  {workflow_id}: {len(nodes)} nodes, {len(edges)} edges")

        except Exception as e:
            failed += 1
            print(f"  Error processing {workflow_id}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}\n")

    print(f"[SUCCESS] Successfully processed: {successful}")
    print(f"[FAILED] Failed: {failed}")

    if edge_counts:
        avg_edges = sum(edge_counts) / len(edge_counts)
        print(f"[STATS] Average edges per DAG: {avg_edges:.1f}")
        print(f"[STATS] Min edges: {min(edge_counts)}, Max edges: {max(edge_counts)}")

    print(f"\n[OUTPUT] Locations:")
    print(f"   DAG files: {dag_dir}")
    print(f"   Images: {img_dir}")

    # Create summary file
    summary_file = output_dir / 'generation_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_available': len(workflows),
            'requested': args.count,
            'selected': num_to_select,
            'successful': successful,
            'failed': failed,
            'random_seed': args.seed,
            'average_edges': avg_edges if edge_counts else 0,
            'min_edges': min(edge_counts) if edge_counts else 0,
            'max_edges': max(edge_counts) if edge_counts else 0,
            'output_dirs': {
                'dag_files': str(dag_dir),
                'images': str(img_dir)
            }
        }, f, indent=2)

    print(f"\n[SUMMARY] Saved to: {summary_file}")


if __name__ == "__main__":
    main()