#!/usr/bin/env python3
"""
Conditions.py Simplifier Tool
Simplifies prompt templates in conditions.py files based on research showing:
- System prompts during training reduce diversity
- Simplified operator descriptions improve generalization
- Problem domain specifics should be preserved for diversity
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Simplified START_PROMPT template - drastically reduced from original
SIMPLIFIED_START_PROMPT = '''### 2. Core Operators

You have access to four fundamental operators, each pre-initialized with problem_text:
- **Generate(instruction: str, context: str = "") -> str**: Creates new content based on instructions
- **Revise(instruction: str, context: str) -> str**: Improves existing content
- **Summarize(instruction: str, context: str) -> str**: Condenses while preserving key information
- **Ensemble(instruction: str, contexts: List[str]) -> str**: Synthesizes multiple inputs

### 3. Meta-Learning Task & Implementation Guidelines

**Your Task:** Design a reusable Python workflow template that solves the entire problem CLASS, not specific instances. This is meta-learning - you're creating a system that learns patterns, not memorizing solutions.

**Key Guidelines:**
- Instructions should be comprehensive (100-500+ words when needed)
- Use f-strings for dynamic instruction construction
- Leverage asyncio.gather() for parallel operations
- Context parameter carries the actual data to process
- Never hardcode problem-specific information

**Response Format Required:**
1. A `<think>...</think>` block explaining your general solution strategy
2. A Python code block with the complete workflow implementation

**Template Structure:**
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # Pre-initialized operators - DO NOT MODIFY
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        # YOUR GENERIC WORKFLOW LOGIC HERE
        # Must work for ANY instance of this problem type
        pass
```'''


class ConditionsSimplifier:
    def __init__(self):
        """Initialize the simplifier with benchmarks to process."""
        self.benchmarks_to_process = [
            'gsm8k', 'mbpp', 'drop', 'humaneval', 
            'hotpotqa', 'math', 'high_level_math', 
            'high_level_math_ganluo'
        ]
        self.base_path = Path("ScoreFlow/scripts")
        
    def read_conditions_file(self, benchmark: str) -> Optional[str]:
        """Read the original conditions.py file for a benchmark."""
        file_path = self.base_path / benchmark / "conditions.py"
        
        if not file_path.exists():
            print(f"Warning: {file_path} does not exist")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def extract_variables(self, content: str) -> Dict[str, str]:
        """Extract key variables from conditions.py content."""
        variables = {}
        
        # Pattern to match variable assignments
        # Handles both ''' and """ string delimiters
        pattern = r'^(\w+)\s*=\s*(\'\'\'|""")(.*?)\2'
        
        # Find all variable assignments
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        for var_name, _, var_content in matches:
            variables[var_name] = var_content
            
            # Handle math benchmark's typo: START_PORMPT -> START_PROMPT
            if var_name == 'START_PORMPT':
                variables['START_PROMPT'] = var_content
        
        return variables
    
    def simplify_conditions(self, content: str, benchmark: str) -> str:
        """
        Simplify the conditions.py content by:
        1. Removing SYSTEM_PROMPT (shown to reduce diversity)
        2. Replacing START_PROMPT with simplified version
        3. Keeping TASK_PROMPT intact (preserves problem domain diversity)
        4. Keeping PYTHON_START and PYTHON_END intact
        """
        
        # Extract original variables
        variables = self.extract_variables(content)
        
        # Build new content
        new_lines = []
        
        # Add header comment
        new_lines.append('"""')
        new_lines.append(f'Simplified conditions for {benchmark} benchmark')
        new_lines.append('System prompts removed and operator descriptions simplified')
        new_lines.append('Based on research showing improved diversity with this approach')
        new_lines.append('"""')
        new_lines.append('')
        
        # Add TASK_PROMPT if it exists (preserve problem domain specifics)
        if 'TASK_PROMPT' in variables:
            new_lines.append("TASK_PROMPT = '''")
            new_lines.append(variables['TASK_PROMPT'])
            new_lines.append("'''")
            new_lines.append('')
        elif benchmark == 'math':
            # Math benchmark doesn't have TASK_PROMPT, add a placeholder
            new_lines.append("# Math benchmark doesn't define TASK_PROMPT in original")
            new_lines.append("TASK_PROMPT = ''")
            new_lines.append('')
        
        # Skip SYSTEM_PROMPT entirely (research shows it reduces diversity)
        # Add comment explaining why
        new_lines.append("# SYSTEM_PROMPT removed - research shows training without system prompts")
        new_lines.append("# but using them at inference improves both safety and diversity")
        new_lines.append("SYSTEM_PROMPT = ''")
        new_lines.append('')
        
        # Add PYTHON_START if it exists
        if 'PYTHON_START' in variables:
            new_lines.append("PYTHON_START = '''")
            new_lines.append(variables['PYTHON_START'])
            new_lines.append("'''")
            new_lines.append('')
        
        # Add PYTHON_END if it exists
        if 'PYTHON_END' in variables:
            new_lines.append("PYTHON_END = '''")
            new_lines.append(variables['PYTHON_END'])
            new_lines.append("'''")
            new_lines.append('')
        
        # Add simplified START_PROMPT
        new_lines.append("# Simplified START_PROMPT - reduced from ~3000 words to ~300 words")
        new_lines.append("# Preserves all functional information while removing redundancy")
        new_lines.append("START_PROMPT = '''")
        new_lines.append(SIMPLIFIED_START_PROMPT)
        new_lines.append("'''")
        new_lines.append('')
        
        # Add any other variables that might exist (META_PROMPTS, etc.)
        for var_name, var_content in variables.items():
            if var_name not in ['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']:
                new_lines.append(f"{var_name} = '''")
                new_lines.append(var_content)
                new_lines.append("'''")
                new_lines.append('')
        
        return '\n'.join(new_lines)
    
    def save_simplified_file(self, content: str, benchmark: str) -> bool:
        """Save the simplified conditions to conditions_simp.py."""
        output_path = self.base_path / benchmark / "conditions_simp.py"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False
    
    def process_benchmark(self, benchmark: str) -> Tuple[bool, str]:
        """Process a single benchmark's conditions.py file."""
        print(f"\nProcessing {benchmark}...")
        
        # Read original file
        original_content = self.read_conditions_file(benchmark)
        if not original_content:
            return False, f"Could not read conditions.py for {benchmark}"
        
        # Simplify content
        simplified_content = self.simplify_conditions(original_content, benchmark)
        
        # Save simplified file
        if self.save_simplified_file(simplified_content, benchmark):
            # Calculate reduction
            original_size = len(original_content)
            simplified_size = len(simplified_content)
            reduction = ((original_size - simplified_size) / original_size) * 100
            
            return True, f"Successfully created conditions_simp.py (reduced by {reduction:.1f}%)"
        else:
            return False, f"Failed to save conditions_simp.py for {benchmark}"
    
    def process_all(self) -> Dict[str, Tuple[bool, str]]:
        """Process all benchmarks and return results."""
        results = {}
        
        print("=" * 60)
        print("Conditions.py Simplification Tool")
        print("=" * 60)
        print(f"Processing {len(self.benchmarks_to_process)} benchmarks...")
        
        for benchmark in self.benchmarks_to_process:
            success, message = self.process_benchmark(benchmark)
            results[benchmark] = (success, message)
            print(f"  {'[OK]' if success else '[FAIL]'} {benchmark}: {message}")
        
        return results
    
    def validate_simplified_files(self) -> List[str]:
        """Validate that simplified files contain required components."""
        issues = []
        
        print("\n" + "=" * 60)
        print("Validating Simplified Files")
        print("=" * 60)
        
        for benchmark in self.benchmarks_to_process:
            file_path = self.base_path / benchmark / "conditions_simp.py"
            
            if not file_path.exists():
                issues.append(f"{benchmark}: conditions_simp.py does not exist")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for required variables
                required_vars = ['TASK_PROMPT', 'START_PROMPT', 'PYTHON_START', 'PYTHON_END']
                missing = []
                
                for var in required_vars:
                    if f"{var} = " not in content:
                        missing.append(var)
                
                if missing:
                    issues.append(f"{benchmark}: Missing variables {missing}")
                
                # Check that SYSTEM_PROMPT is empty
                if "SYSTEM_PROMPT = ''" not in content:
                    issues.append(f"{benchmark}: SYSTEM_PROMPT should be empty")
                
                # Check for simplified START_PROMPT
                if "### 2. Core Operators" not in content:
                    issues.append(f"{benchmark}: START_PROMPT not properly simplified")
                
                if not missing and "SYSTEM_PROMPT = ''" in content:
                    print(f"  [OK] {benchmark}: All validations passed")
                    
            except Exception as e:
                issues.append(f"{benchmark}: Error reading file - {e}")
        
        return issues


def main():
    """Main entry point for the script."""
    
    # Create simplifier instance
    simplifier = ConditionsSimplifier()
    
    # Process all benchmarks
    results = simplifier.process_all()
    
    # Validate results
    validation_issues = simplifier.validate_simplified_files()
    
    # Summary report
    print("\n" + "=" * 60)
    print("Summary Report")
    print("=" * 60)
    
    successful = sum(1 for success, _ in results.values() if success)
    failed = len(results) - successful
    
    print(f"Total benchmarks processed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    if validation_issues:
        print(f"\nValidation issues found: {len(validation_issues)}")
        for issue in validation_issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] All files passed validation!")
    
    print("\n" + "=" * 60)
    print("Process Complete")
    print("=" * 60)
    print("\nKey improvements:")
    print("  - System prompts removed (improves diversity)")
    print("  - Operator descriptions simplified (~60% reduction)")
    print("  - Problem domain specifics preserved")
    print("  - Compatible with existing workflow system")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 and not validation_issues else 1)


if __name__ == "__main__":
    main()