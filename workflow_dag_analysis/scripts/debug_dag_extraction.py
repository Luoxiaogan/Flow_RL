#!/usr/bin/env python3
"""
Debug DAG extraction to understand why dependencies are not created.
"""

import json
import re

def debug_extraction():
    """Debug the extraction process."""

    # Simplified test case
    test_code = """
decomposition = await self.decompose(
    instruction="Break down the problem",
    context=""
)

problem_profile = await self.generate(
    instruction="Analyze the question",
    context=json.dumps(decomposition) if isinstance(decomposition, list) else str(decomposition)
)

resolved_entities = await self.generate(
    instruction=f\"\"\"Given the problem profile:
    {problem_profile}

    Extract entities.\"\"\",
    context=""
)
    """

    lines = test_code.strip().split('\n')
    var_to_node = {}
    node_counter = 0

    print("STEP-BY-STEP EXTRACTION:")
    print("=" * 60)

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Check for variable = await self.operator(...)
        match = re.match(r'(\w+)\s*=\s*await\s+self\.(\w+)\s*\(', line_stripped)
        if match:
            var_name = match.group(1)
            operator = match.group(2)

            node_id = f"{operator}_{node_counter}"
            node_counter += 1

            print(f"\nLine {i+1}: Found {var_name} = await self.{operator}")
            print(f"  Created node: {node_id}")
            print(f"  Mapping: {var_name} -> {node_id}")

            var_to_node[var_name] = node_id

            # Extract the complete call block
            call_block = []
            j = i
            paren_count = 0
            while j < len(lines):
                call_line = lines[j]
                call_block.append(call_line)
                paren_count += call_line.count('(') - call_line.count(')')
                if paren_count <= 0 and j > i:
                    break
                j += 1

            block_text = '\n'.join(call_block)
            print(f"  Call block:\n{block_text[:200]}")

            # Check for dependencies in context
            context_match = re.search(r'context\s*=\s*([^,\)]+)', block_text)
            if context_match:
                context_text = context_match.group(1).strip()
                print(f"  Found context: {context_text}")

                # Check for function calls like json.dumps(var)
                func_match = re.search(r'\w+\((\w+)\)', context_text)
                if func_match:
                    ref_var = func_match.group(1)
                    print(f"    Function call references: {ref_var}")
                    if ref_var in var_to_node:
                        print(f"    ✓ Found in var_to_node: {ref_var} -> {var_to_node[ref_var]}")
                    else:
                        print(f"    ✗ NOT found in var_to_node: {ref_var}")

                # Direct variable reference
                if context_text in var_to_node:
                    print(f"    ✓ Direct reference found: {context_text} -> {var_to_node[context_text]}")

            # Check for f-string dependencies in instruction
            if 'instruction=' in block_text:
                # Find f-string variables
                f_string_vars = re.findall(r'\{(\w+)\}', block_text)
                if f_string_vars:
                    print(f"  Found f-string variables: {f_string_vars}")
                    for f_var in f_string_vars:
                        if f_var in var_to_node:
                            print(f"    ✓ Found in var_to_node: {f_var} -> {var_to_node[f_var]}")
                        else:
                            print(f"    ✗ NOT found in var_to_node: {f_var}")

    print("\n" + "=" * 60)
    print("FINAL VARIABLE MAPPING:")
    for var, node in var_to_node.items():
        print(f"  {var} -> {node}")


if __name__ == "__main__":
    debug_extraction()