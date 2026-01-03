#!/usr/bin/env python3
"""
Generate random DAGs from workflow dataset.
Creates both annotated DAG files and visualization images.
"""

import json
import random
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
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


class DAGGenerator:
    """Generate DAG with annotated source code."""

    def __init__(self):
        self.nodes = OrderedDict()
        self.edges = []

    def extract_dag(self, code: str) -> Tuple[Dict, List]:
        """Extract DAG structure from workflow code."""
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

                # Extract context dependencies
                context_deps = self._extract_context_deps(lines[i:min(i+10, len(lines))], var_to_node)

                if context_deps:
                    for dep in context_deps:
                        self.edges.append((dep, node_id, {'type': 'data'}))
                elif current_step == 1:
                    self.edges.append(('INPUT', node_id, {'type': 'input'}))

            # Pattern: asyncio.gather for parallel execution
            elif 'await asyncio.gather' in line_stripped:
                assign_match = re.match(r'(\w+)\s*=\s*await\s+asyncio\.gather', line_stripped)
                result_var = assign_match.group(1) if assign_match else f"gather_{node_counter}"

                # Find all operations in gather block
                gather_block = []
                j = i
                paren_count = 0
                while j < len(lines):
                    gather_line = lines[j]
                    gather_block.append(gather_line)
                    paren_count += gather_line.count('(') - gather_line.count(')')
                    if 'asyncio.gather' in gather_line:
                        paren_count = max(paren_count, 1)
                    if paren_count > 0 and ')' in gather_line:
                        if paren_count == gather_line.count(')'):
                            break
                    j += 1

                gather_text = '\n'.join(gather_block)
                gather_nodes = []

                # Find all self.operator calls
                op_pattern = re.compile(r'self\.(\w+)\s*\(')
                for op_match in op_pattern.finditer(gather_text):
                    operator = op_match.group(1)

                    node_id = f"{operator}_{node_counter}"
                    node_counter += 1

                    self.nodes[node_id] = {
                        'type': 'operator',
                        'operator': operator,
                        'label': f"{operator}\\n(parallel)",
                        'step': current_step,
                        'parallel': True,
                        'line': i + 1 + gather_text[:op_match.start()].count('\n')
                    }

                    gather_nodes.append(node_id)

                    # Extract context dependencies
                    call_start = op_match.start()
                    call_end = gather_text.find(')', call_start)
                    if call_end > 0:
                        call_text = gather_text[call_start:call_end]
                        context_deps = self._extract_context_from_text(call_text, var_to_node)

                        for dep in context_deps:
                            self.edges.append((dep, node_id, {'type': 'data'}))

                # Map results
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

        # Connect last operation to output
        last_op = None
        for node_id, info in reversed(list(self.nodes.items())):
            if info['type'] == 'operator':
                last_op = node_id
                break

        if last_op:
            self.edges.append((last_op, 'OUTPUT', {'type': 'output'}))

        return self.nodes, self.edges

    def _extract_context_deps(self, lines: List[str], var_to_node: Dict) -> List[str]:
        """Extract dependencies from context parameters."""
        deps = []
        text = '\n'.join(lines)

        # Look for context=variable patterns
        context_match = re.search(r'context\s*=\s*([^,\)]+)', text)
        if context_match:
            deps.extend(self._extract_context_from_text(context_match.group(1), var_to_node))

        # Look for contexts_list=variable patterns
        contexts_match = re.search(r'contexts_list\s*=\s*([^,\)]+)', text)
        if contexts_match:
            deps.extend(self._extract_context_from_text(contexts_match.group(1), var_to_node))

        return deps

    def _extract_context_from_text(self, text: str, var_to_node: Dict) -> List[str]:
        """Extract variable references from text."""
        deps = []
        text = text.strip()

        # Direct variable
        if text in var_to_node:
            deps.append(var_to_node[text])

        # Variables in f-strings
        var_refs = re.findall(r'\{(\w+)(?:\[(\d+)\])?\}', text)
        for var_ref in var_refs:
            var_name = var_ref[0]
            index = var_ref[1] if len(var_ref) > 1 and var_ref[1] else None

            if index:
                full_var = f"{var_name}[{index}]"
                if full_var in var_to_node:
                    deps.append(var_to_node[full_var])
            elif var_name in var_to_node:
                deps.append(var_to_node[var_name])

        # Simple variable references
        simple_vars = re.findall(r'\b(\w+)\b', text)
        for var_name in simple_vars:
            if var_name in var_to_node and var_to_node[var_name] not in deps:
                deps.append(var_to_node[var_name])

        return deps

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
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

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
                    node_colors.append('#F0E68C')  # Khaki
                else:
                    node_colors.append('#E0E0E0')  # Light gray

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=2000, alpha=0.9, ax=ax)

        # Draw edges with different styles
        data_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'data']
        input_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'input']
        output_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'output']
        other_edges = [(u, v) for u, v, d in G.edges(data=True)
                      if d.get('type') not in ['data', 'input', 'output']]

        nx.draw_networkx_edges(G, pos, edgelist=data_edges, edge_color='blue',
                              arrows=True, arrowsize=20, width=1.5, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=input_edges, edge_color='green',
                              arrows=True, arrowsize=20, width=1.5, style='dashed', ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=output_edges, edge_color='red',
                              arrows=True, arrowsize=20, width=1.5, style='dashed', ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=other_edges, edge_color='gray',
                              arrows=True, arrowsize=20, width=1, ax=ax)

        # Draw labels
        labels = {node: nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        # Title and legend
        ax.set_title(f'DAG: {workflow_id}', fontsize=14, fontweight='bold')
        ax.axis('off')

        legend_elements = [
            mpatches.Patch(color='#90EE90', label='Input'),
            mpatches.Patch(color='#FFB6C1', label='Output'),
            mpatches.Patch(color='#87CEEB', label='Generate'),
            mpatches.Patch(color='#DDA0DD', label='Revise'),
            mpatches.Patch(color='#F0E68C', label='Summarize'),
            mpatches.Patch(color='#FFE4B5', label='Ensemble')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

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
    parser = argparse.ArgumentParser(description='Generate random DAGs from workflows')
    parser.add_argument('--input', type=str, default='../data/extracted_python_code.jsonl',
                       help='Input JSONL file')
    parser.add_argument('--output-dir', type=str, default='../results/random_dags',
                       help='Output directory')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of random workflows to process')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')

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
    print(f"GENERATING RANDOM DAGS FROM WORKFLOWS")
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
    generator = DAGGenerator()
    successful = 0
    failed = 0

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

        except Exception as e:
            failed += 1
            print(f"  Error processing {workflow_id}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}\n")

    print(f"[SUCCESS] Successfully processed: {successful}")
    print(f"[FAILED] Failed: {failed}")
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
            'output_dirs': {
                'dag_files': str(dag_dir),
                'images': str(img_dir)
            }
        }, f, indent=2)

    print(f"\n[SUMMARY] Saved to: {summary_file}")


if __name__ == "__main__":
    main()