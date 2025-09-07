#!/usr/bin/env python3
"""
Convert old style conditions.py to new modular style.
Old style: Single long START_PROMPT with all content mixed together
New style: Modular OPERATOR_PROMPT_PART_1, OPERATOR_PROMPT_PART_2, USER_PROMPT_LONG
"""

import re
import sys
from pathlib import Path


def extract_domain_info(task_prompt):
    """Extract domain name and description from TASK_PROMPT."""
    # Try to find domain name from patterns like "**LIMR**" or "**MGSM Bengali benchmark**"
    domain_match = re.search(r'\*\*([^*]+)\*\*', task_prompt)
    if domain_match:
        domain_name = domain_match.group(1)
        # Clean up domain name
        if 'benchmark' in domain_name.lower():
            domain_name = domain_name.replace(' benchmark', '').replace('Benchmark', '')
        return domain_name
    return "Unknown Domain"


def convert_task_prompt(old_task_prompt, domain_name):
    """Convert old style TASK_PROMPT to new style."""
    lines = old_task_prompt.strip().split('\n')
    new_lines = []
    
    # Start with clean header (no numbering)
    new_lines.append("### Problem Domain Overview")
    new_lines.append("")
    
    # Add simplified domain description
    if "LIMR" in domain_name:
        new_lines.append(f"{domain_name} tests advanced mathematical reasoning through competition-level problems requiring sophisticated proofs and multi-step solutions.")
    elif "MGSM" in domain_name and "Bengali" in domain_name:
        new_lines.append(f"MGSM Bengali (Multilingual Grade School Math - Bengali) tests mathematical word problem solving in Bengali language at elementary school level.")
    elif "MGSM" in domain_name and "German" in domain_name:
        new_lines.append(f"MGSM German (Multilingual Grade School Math - German) tests mathematical word problem solving in German language at elementary school level.")
    else:
        new_lines.append(f"{domain_name} tests problem-solving capabilities in the specified domain.")
    
    new_lines.append("")
    
    # Process existing content
    in_section = None
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Skip old headers and domain descriptions
        if "### 1. Problem Domain Overview" in line:
            continue
        if "The target domain is" in line:
            skip_next = True  # Skip the next line too
            continue
            
        # Convert section headers
        if "**Core Characteristics:**" in line:
            new_lines.append("#### Key Characteristics & Requirements")
            in_section = "characteristics"
        elif "**Common Problem Types:**" in line:
            new_lines.append("#### Common Problem Types & Solution Strategies")
            in_section = "problem_types"
        elif "**Mathematical Operations:**" in line or "**Mathematical Techniques:**" in line:
            # Include this content under problem types
            if in_section != "problem_types":
                new_lines.append("#### Common Problem Types & Solution Strategies")
                in_section = "problem_types"
            new_lines.append(line)
        elif "**Critical Challenges:**" in line:
            # Keep this as part of characteristics
            new_lines.append(line)
        elif "**Key Success Factors:**" in line:
            new_lines.append("")
            new_lines.append("#### Workflow Focus Points")
            # Convert success factors to numbered points
            in_section = "workflow_points"
        elif in_section == "workflow_points" and line.startswith("- "):
            # Convert to numbered points (max 5)
            # Count existing numbered points
            numbered_points = [l for l in new_lines if re.match(r'^\d+\.', l)]
            point_num = len(numbered_points) + 1
            if point_num <= 5:
                new_lines.append(f"{point_num}. {line[2:]}")
        else:
            # Keep other lines as is
            if line or (new_lines and new_lines[-1]):  # Avoid multiple blank lines
                new_lines.append(line)
    
    # Add Input Format section if not present
    if "#### Input Format" not in '\n'.join(new_lines):
        new_lines.append("")
        new_lines.append("#### Input Format")
        new_lines.append("```")
        new_lines.append("---")
        if "Bengali" in domain_name or "German" in domain_name:
            new_lines.append("**PROBLEM:**")
            new_lines.append("[Word problem in target language with numerical values and relationships]")
        else:
            new_lines.append("**PROBLEM:**")
            new_lines.append("[Complete problem statement]")
        new_lines.append("---")
        new_lines.append("```")
        new_lines.append("Multiple problems follow the same structure if provided.")
    
    return '\n'.join(new_lines)


def create_operator_prompt_part_1():
    """Create OPERATOR_PROMPT_PART_1 for new style."""
    return '''### Available Operators

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as "**Original Problem:**" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem

**4. Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions'''


def create_operator_prompt_part_2():
    """Create OPERATOR_PROMPT_PART_2 for new style."""
    return '''#### **CRITICAL: Understanding Operator Parameters**

**The `instruction` Parameter (Required for all operators):**
- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do
- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous
- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)
- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements
- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.

**The `context` Parameter (Required for all operators except `Ensemble`, which uses `contexts` instead of `context`):**
- **Purpose:** Provides the INPUT DATA that the instruction will operate on
- **Content:** The actual text, data, or results from previous operations - this is the primary information source
- **Type:** String for Generate/Revise/Summarize operators
- **Usage:** Think of it as the "working material" that the instruction processes
- **Note:** Ensemble uses `contexts` which takes List[str] instead of a single string

### Key Design Principles

**Dynamic Instruction Construction:**
Extract information early, then incorporate it into subsequent instructions using f-strings:
```python
extraction = await self.generate(instruction="Extract all numerical values...", context=self.problem_text)
analysis = await self.generate(
    instruction=f"Given these extracted values: {extraction}\\nNow solve step by step...",
    context=self.problem_text
)
```

**Parallel Execution:**
Use `asyncio.gather()` for independent operations:
```python
results = await asyncio.gather(
    self.generate(instruction="Approach 1...", context=...),
    self.generate(instruction="Approach 2...", context=...)
)
final = await self.ensemble(instruction="Select best...", contexts=results)
```

**Common Pitfalls:**
- Don't hardcode problem-specific data in workflow code
- Don't use `await` inside list comprehensions (blocks parallelism)
- Do use detailed instructions (100-500+ words when needed)
- Do extract info dynamically and incorporate into instructions

#### **Innovation Guidelines:**

**Maximize the power of instructions by:**
- Building multi-paragraph instructions that leave nothing to interpretation
- Dynamically incorporating ALL relevant extracted information
- Creating instruction templates that adapt based on detected patterns
- Using instructions to implement complex reasoning strategies
- Including specific formatting requirements and output structures

**Remember:**
- Instructions are mini-prompts - make them as detailed as needed
- Extract early, enrich instructions throughout
- The workflow provides structure; instructions provide intelligence
- Never hardcode problem-specific data in the workflow code itself
- Always pass context appropriately - empty string for initial Generate, List for Ensemble

#### **Common Pitfalls to Avoid:**

```python
# WRONG: Hardcoding problem-specific information
result = await self.generate(
    instruction="Count how many field goals the Patriots scored",  # Too specific!
    context=self.problem_text
)

# CORRECT: Generic instruction that works for any problem
result = await self.generate(
    instruction="Identify what the question is asking for, then count or calculate the requested value",
    context=self.problem_text
)

# WRONG: Sequential execution when parallel is possible
result1 = await self.generate(...)  # Waits
result2 = await self.generate(...)  # Then waits again

# CORRECT: Parallel execution for independent operations
results = await asyncio.gather(
    self.generate(...),
    self.generate(...)
)
```'''


def create_user_prompt_long():
    """Create USER_PROMPT_LONG for new style."""
    return '''### Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template below. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

**Base Template:**
<think>
Design a universal workflow for this problem domain. Consider:
- Core patterns and variations across the domain
- Multiple solution strategies and their trade-offs
- For each operator in your workflow: why it's necessary, how to craft its instructions, and how it connects with other operators
- How your design ensures the workflow solves ANY problem in this domain (not just the examples shown)

Write detailed reasoning (aim for 8-10 paragraphs) explaining your workflow design decisions.
</think>
Feel free to add any additional explanations before or after the code.
```python
# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        import asyncio
        # --- YOUR WORKFLOW LOGIC HERE ---
```
Feel free to add any additional explanations before or after the code.

**Critical Rules:**

1. Generality: The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples.
2. Instructions: Use comprehensive, detailed instructions (100-500+ words OK)
3. Parameters: `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble
4. Control Flow: Branch on operator results, not direct problem_text parsing
5. Complexity: Typically 3-8 operator calls, parallelize when possible'''


def create_new_system_prompt():
    """Create simplified SYSTEM_PROMPT for new style."""
    return '''You are an expert System Architect specializing in designing universal workflow solutions. Your task is to create a generalizable Python workflow that can solve ALL problems within a specific domain, not just individual examples.

You will receive:
1. Domain overview and problem characteristics
2. 1-3 concrete problem examples from this domain
3. Available operators (your only building blocks)
4. Output requirements

Your goal: Design a robust workflow that handles the entire problem class by identifying common patterns and creating a reusable solution strategy.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples.'''


def convert_python_end(old_python_end):
    """Convert PYTHON_END to use Chinese comments."""
    # Replace English comments with Chinese
    new_python_end = old_python_end.replace(
        "# Error details are defined and used here, not exposed to external .format()",
        "# 错误详情在这里被定义和使用，不暴露给外部.format()"
    )
    return new_python_end


def convert_file(file_path):
    """Convert a single conditions.py file from old style to new style."""
    print(f"\nConverting file: {file_path}")
    
    # Read the original file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract existing variables using regex
    task_prompt_match = re.search(r"TASK_PROMPT = '''(.*?)'''", content, re.DOTALL)
    system_prompt_match = re.search(r"SYSTEM_PROMPT = '''(.*?)'''", content, re.DOTALL)
    python_start_match = re.search(r"PYTHON_START = '''(.*?)'''", content, re.DOTALL)
    python_end_match = re.search(r"PYTHON_END = '''(.*?)'''", content, re.DOTALL)
    start_prompt_match = re.search(r"START_PROMPT = '''(.*?)'''", content, re.DOTALL)
    
    if not all([task_prompt_match, system_prompt_match, python_start_match, python_end_match]):
        print(f"  ERROR: Cannot extract all required variables")
        return False
    
    # Extract domain name
    domain_name = extract_domain_info(task_prompt_match.group(1))
    print(f"  Domain detected: {domain_name}")
    
    # Convert each part
    new_task_prompt = convert_task_prompt(task_prompt_match.group(1), domain_name)
    new_system_prompt = create_new_system_prompt()
    new_operator_prompt_part_1 = create_operator_prompt_part_1()
    new_operator_prompt_part_2 = create_operator_prompt_part_2()
    new_user_prompt_long = create_user_prompt_long()
    new_python_end = convert_python_end(python_end_match.group(1))
    
    # Build new file content
    new_content = f"""TASK_PROMPT = '''{new_task_prompt}'''


OPERATOR_PROMPT_PART_1 = '''{new_operator_prompt_part_1}'''

SYSTEM_PROMPT = '''{new_system_prompt}'''

OPERATOR_PROMPT_PART_2 = '''{new_operator_prompt_part_2}'''


USER_PROMPT_LONG ='''{new_user_prompt_long}'''


PYTHON_START = '''{python_start_match.group(1)}'''

PYTHON_END = '''{new_python_end}'''
"""
    
    # Write the new content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  SUCCESS: Conversion completed")
    return True


def main():
    """Main function to convert specified files."""
    files_to_convert = [
        # "limr/conditions.py",
        # "mgsmbn/conditions.py"
        "mgsmde/conditions.py",
        "mbppplus/conditions.py",
        "humanevalplus/conditions.py",
        "simpleqa/conditions.py",
        "aime2025/conditions.py",
        "aime2024/conditions.py",
    ]
    
    print("=" * 60)
    print("Conditions File Style Converter")
    print("From old style (single START_PROMPT) to new style (modular)")
    print("=" * 60)
    
    for file_path in files_to_convert:
        path = Path(file_path)
        if not path.exists():
            print(f"\nERROR: File does not exist: {file_path}")
            continue
        
        # Check if backup exists
        backup_path = path.with_suffix('.py.bak')
        if not backup_path.exists():
            print(f"\nWARNING: Backup file not found: {backup_path}")
            print(f"   Please create backup first")
            continue
        
        # Convert the file
        success = convert_file(file_path)
        if success:
            print(f"  Backup file location: {backup_path}")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("Please check the converted files. To restore, use the .bak backup files")
    print("=" * 60)


if __name__ == "__main__":
    main()