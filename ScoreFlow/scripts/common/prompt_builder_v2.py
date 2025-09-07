"""
Enhanced dynamic prompt builder that supports split prompt structure
Generates prompts in multiple parts matching the original ScoreFlow design
"""
from typing import List, Dict, Any, Set, Optional, Tuple
import logging
from .operator_loader import OperatorRegistry, OperatorGroupManager
from .base_conditions import BASE_SYSTEM_PROMPT, BASE_PYTHON_END

logger = logging.getLogger(__name__)

class EnhancedPromptBuilder:
    """Enhanced builder that generates split prompt structure"""
    
    def __init__(self, benchmark_name: str, operator_group: str = 'default'):
        """
        Initialize the enhanced prompt builder
        
        Args:
            benchmark_name: Name of the benchmark
            operator_group: Name of the operator group to use
        """
        self.benchmark_name = benchmark_name
        self.operator_group = operator_group
        self.registry = OperatorRegistry()
        self.group_manager = OperatorGroupManager()
        
        # Validate group exists
        if not self.group_manager.get_group(operator_group):
            raise ValueError(f"Operator group '{operator_group}' not found")
        
        logger.info(f"Initialized enhanced prompt builder for {benchmark_name} with group {operator_group}")
    
    def build_operator_prompt_part_1(self) -> str:
        """
        Build OPERATOR_PROMPT_PART_1 - basic operator descriptions
        
        Returns:
            String containing operator descriptions
        """
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            raise ValueError(f"Operator group '{self.operator_group}' not found")
        
        lines = [
            "### Available Operators\n",
            "\nAll operators follow a consistent interface pattern and are initialized with the problem text. ",
            "They are available as `self.operator_name`.\n",
            "\n**Important Note:** The operators are pre-initialized with `self.problem_text`. ",
            "Each operator automatically includes it in their prompts ",
            "(you'll see it as \"**Original Problem:**\" in their internal prompts). ",
            "You don't need to worry about losing the problem context - it's always available to every operator call ",
            "behind the scenes, regardless of what you pass as the context parameter.\n\n"
        ]
        
        # Add each operator's basic description
        for idx, op_name in enumerate(group['operators'], 1):
            op_info = self.registry.get_operator_info(op_name)
            if op_info:
                # Format the operator description
                lines.append(f"**{idx}. {op_name}: {self._get_operator_action_verb(op_name)} information**\n")
                lines.append(f"- **Signature:** `await self.{op_name.lower()}({op_info['signature']}) -> str`\n")
                lines.append(f"- **Purpose:** {op_info['prompt_template']}\n\n")
            else:
                logger.warning(f"Operator '{op_name}' not found in registry")
        
        return ''.join(lines)
    
    def _get_operator_action_verb(self, op_name: str) -> str:
        """Get action verb for operator (CREATE, IMPROVE, etc.)"""
        action_verbs = {
            'Generate': 'CREATE new',
            'Revise': 'IMPROVE existing',
            'Summarize': 'COMPRESS',
            'Ensemble': 'DECIDE between or synthesize',
            'CodeGenerate': 'GENERATE code',
            'Decompose': 'BREAK DOWN',
            'FormatAnswer': 'FORMAT',
            'Custom': 'CUSTOMIZE',
            'Review': 'REVIEW',
            'Programmer': 'PROGRAM',
            'ScEnsemble': 'SELECT best from'
        }
        return action_verbs.get(op_name, op_name.upper())
    
    def build_operator_prompt_part_2(self) -> str:
        """
        Build OPERATOR_PROMPT_PART_2 - parameter explanations and design principles
        
        Returns:
            String containing parameter details and design principles
        """
        lines = [
            "#### **CRITICAL: Understanding Operator Parameters**\n\n",
            "**The `instruction` Parameter (Required for all operators):**\n",
            "- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do\n",
            "- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous\n",
            "- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)\n",
            "- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, ",
            "detailed reasoning strategies, and formatted requirements\n",
            "- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded ",
            "in the workflow structure. While instructions can dynamically incorporate relevant extracted information ",
            "to guide the operation, the main data to be processed should remain in the context parameter.\n\n"
        ]
        
        # Add context parameter explanation
        lines.append("**The `context` Parameter (Required for all operators except `Ensemble`, which uses `contexts_list` instead of `context`):**\n")
        lines.append("- **Purpose:** Provides the INPUT DATA that the instruction will operate on\n")
        lines.append("- **Content:** The actual text, data, or results from previous operations - this is the primary information source\n")
        lines.append("- **Type:** String for Generate/Revise/Summarize operators\n")
        lines.append("- **Usage:** Think of it as the \"working material\" that the instruction processes\n")
        lines.append("- **Note:** Ensemble uses `contexts_list` which takes List[str] instead of a single string\n\n")
        
        # Add design principles
        lines.append(self._get_design_principles())
        
        return ''.join(lines)
    
    def _get_design_principles(self) -> str:
        """Get design principles section"""
        return """### Key Design Principles

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
```
"""
    
    def build_user_prompt_long(self) -> str:
        """
        Build USER_PROMPT_LONG - task instructions and template
        
        Returns:
            String containing user task instructions
        """
        lines = [
            "### Your Task: Complete the `run_workflow` Method\n\n",
            "Your task is to write the Python code for the `run_workflow` method within the provided template below. ",
            "Focus on creating a robust, reusable workflow that leverages detailed instructions.\n\n",
            "**Response Format:**\n",
            "1. Provide your reasoning in a `<think>...</think>` block\n",
            "2. Include a ```python``` code block with the complete workflow implementation\n\n",
            "**Base Template:**\n",
            "<think>\n",
            "Design a universal workflow for this problem domain. Consider:\n",
            "- Core patterns and variations across the domain\n",
            "- Multiple solution strategies and their trade-offs\n",
            "- For each operator in your workflow: why it's necessary, how to craft its instructions, ",
            "and how it connects with other operators\n",
            "- How your design ensures the workflow solves ANY problem in this domain (not just the examples shown)\n\n",
            "Write detailed reasoning (aim for 8-10 paragraphs) explaining your workflow design decisions.\n",
            "</think>\n",
            "Feel free to add any additional explanations before or after the code.\n"
        ]
        
        # Add code template with dynamic initialization
        lines.append("```python\n")
        lines.append("# --- DO NOT IMPORT HERE ---\n")
        lines.append("class Workflow:\n")
        lines.append("    def __init__(self, config, problem) -> None:\n")
        lines.append("        # --- DO NOT MODIFY THIS SECTION ---\n")
        lines.append("        self.config = config\n")
        lines.append("        self.problem_text = problem\n")
        lines.append("        self.llm = create(config)\n")
        lines.append("        \n")
        
        # Add operator initialization
        lines.append(self._build_init_code_section())
        
        lines.append("\n    async def run_workflow(self):\n")
        lines.append('        """\n')
        lines.append("        Implement the core problem-solving logic here.\n")
        lines.append("        Remember: \n")
        lines.append("        - Use detailed, comprehensive instructions\n")
        lines.append("        - Dynamic instruction construction is powerful\n")
        lines.append('        """\n')
        lines.append("        import asyncio\n")
        lines.append("        # --- YOUR WORKFLOW LOGIC HERE ---\n")
        lines.append("```\n")
        
        lines.append("Feel free to add any additional explanations before or after the code.\n\n")
        lines.append("**Critical Rules:**\n\n")
        lines.append("1. Generality: The workflow must be generic enough to handle ANY problem instance ")
        lines.append("from the described domain, not just the provided examples.\n")
        lines.append("2. Instructions: Use comprehensive, detailed instructions (100-500+ words OK)\n")
        lines.append("3. Parameters: `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble\n")
        lines.append("4. Control Flow: Branch on operator results, not direct problem_text parsing\n")
        lines.append("5. Complexity: Typically 3-8 operator calls, parallelize when possible")
        
        return ''.join(lines)
    
    def _build_init_code_section(self) -> str:
        """Build the operator initialization code for __init__ method"""
        group = self.group_manager.get_group(self.operator_group)
        lines = []
        
        # Check if special initialization is needed
        if group.get('special_init'):
            lines.append("        self.gid = None  # For MATH operators\n")
        
        # Generate initialization for each operator
        for op_name in group['operators']:
            op_info = self.registry.get_operator_info(op_name)
            if not op_info:
                lines.append(f"        # Warning: {op_name} not found in registry\n")
                continue
            
            var_name = op_name.lower()
            if op_name == 'ScEnsemble':
                var_name = 'sc_ensemble'  # Special case for ScEnsemble
            
            # Build initialization based on operator requirements
            if op_info['module_path'] == 'MATH.operator':
                # MATH operators need special parameters
                lines.append(f"        self.{var_name} = operator.{op_info['class_name']}(self.llm, self.gid, self.problem_text)\n")
            else:
                # Common operators
                lines.append(f"        self.{var_name} = operator.{op_info['class_name']}(self.llm, self.problem_text)\n")
        
        return ''.join(lines)
    
    def build_start_prompt(self) -> str:
        """
        Build the complete START_PROMPT by combining all parts
        This is for backward compatibility with systems expecting START_PROMPT
        
        Returns:
            String containing the full start prompt
        """
        parts = [
            self.build_operator_prompt_part_1(),
            self.build_operator_prompt_part_2(),
            self.build_user_prompt_long()
        ]
        return ''.join(parts)
    
    def build_python_start(self) -> str:
        """Build the PYTHON_START section with appropriate imports"""
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            raise ValueError(f"Operator group '{self.operator_group}' not found")
        
        # Collect unique modules needed
        modules = set()
        if group.get('module') == 'mixed':
            # Mixed mode - need to import multiple modules
            for op_name in group['operators']:
                op_info = self.registry.get_operator_info(op_name)
                if op_info:
                    modules.add(op_info['module_path'])
        else:
            # Single module mode
            modules.add(group.get('module', 'common.operator'))
        
        # Build import statements
        imports = [
            "import asyncio",
            "from typing import Literal, List, Dict, Any, Union"
        ]
        
        # Add module-specific imports
        for module in sorted(modules):
            if module == 'common.operator':
                imports.append("import ScoreFlow.scripts.common.operator as operator")
            elif module == 'MATH.operator':
                imports.append("import ScoreFlow.scripts.MATH.operator as operator")
            else:
                # Handle other custom modules
                imports.append(f"import ScoreFlow.scripts.{module} as operator")
        
        imports.append("from metagpt.provider.llm_provider_registry import create_llm_instance as create")
        
        return '\n'.join(imports) + '\n\n'
    
    def build_system_prompt(self) -> str:
        """
        Build the SYSTEM_PROMPT for the benchmark
        
        Returns:
            String containing system prompt
        """
        return """You are an expert System Architect specializing in designing universal workflow solutions. Your task is to create a generalizable Python workflow that can solve ALL problems within a specific domain, not just individual examples.

You will receive:
1. Domain overview and problem characteristics
2. 1-3 concrete problem examples from this domain
3. Available operators (your only building blocks)
4. Output requirements

Your goal: Design a robust workflow that handles the entire problem class by identifying common patterns and creating a reusable solution strategy.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples."""
    
    def build_complete_conditions_v2(self, task_prompt: str = None) -> str:
        """
        Build a complete conditions.py file with split prompt structure
        
        Args:
            task_prompt: Optional task-specific prompt to include
            
        Returns:
            String containing complete conditions.py content
        """
        from datetime import datetime
        
        if task_prompt is None:
            task_prompt = f"# TODO: Add task prompt for {self.benchmark_name} benchmark"
        
        content = f'''"""
Auto-generated conditions for {self.benchmark_name} benchmark
Using operator group: {self.operator_group}
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Split prompt structure for better modularity
"""

# ========== Task/Domain Description ==========
TASK_PROMPT = \'\'\'{task_prompt}\'\'\'

# ========== Operator Descriptions (Part 1) ==========
OPERATOR_PROMPT_PART_1 = \'\'\'{self.build_operator_prompt_part_1()}\'\'\'

# ========== System Prompt ==========
SYSTEM_PROMPT = \'\'\'{self.build_system_prompt()}\'\'\'

# ========== Operator Parameters and Design Principles (Part 2) ==========
OPERATOR_PROMPT_PART_2 = \'\'\'{self.build_operator_prompt_part_2()}\'\'\'

# ========== User Task Instructions ==========
USER_PROMPT_LONG = \'\'\'{self.build_user_prompt_long()}\'\'\'

# ========== Python Imports ==========
PYTHON_START = \'\'\'{self.build_python_start()}\'\'\'

# ========== Python End Template ==========
PYTHON_END = \'\'\'
    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {{time}}

        try:
            # Execute the LLM-generated workflow to get the raw result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            
            # Return the raw result directly - answer extraction is now handled in handler
            return raw_result

        except asyncio.TimeoutError:
            # Handle workflow execution timeout gracefully.
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            # Handle other potential errors during workflow execution.
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\\\n", "\\\\\\\\n").replace('"', '\\\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{{{escaped_error_details}}}}"
\'\'\'

# ========== Backward Compatibility ==========
# For systems expecting START_PROMPT (combines all operator-related prompts)
START_PROMPT = OPERATOR_PROMPT_PART_1 + OPERATOR_PROMPT_PART_2 + USER_PROMPT_LONG

# ========== Configuration Metadata ==========
OPERATOR_GROUP = "{self.operator_group}"
BENCHMARK_NAME = "{self.benchmark_name}"
'''
        return content
    
    def get_split_prompts(self) -> Dict[str, str]:
        """
        Get all prompt components as a dictionary
        
        Returns:
            Dictionary with all prompt components
        """
        return {
            'OPERATOR_PROMPT_PART_1': self.build_operator_prompt_part_1(),
            'OPERATOR_PROMPT_PART_2': self.build_operator_prompt_part_2(),
            'USER_PROMPT_LONG': self.build_user_prompt_long(),
            'SYSTEM_PROMPT': self.build_system_prompt(),
            'PYTHON_START': self.build_python_start(),
            'START_PROMPT': self.build_start_prompt()  # For backward compatibility
        }


# Utility function for enhanced conditions generation
def generate_conditions_v2(
    benchmark_name: str,
    operator_group: str,
    task_prompt: str = None
) -> str:
    """
    Generate a complete conditions.py file with split prompt structure
    
    Args:
        benchmark_name: Name of the benchmark
        operator_group: Name of the operator group
        task_prompt: Optional task-specific prompt
        
    Returns:
        String containing complete conditions.py content
    """
    builder = EnhancedPromptBuilder(benchmark_name, operator_group)
    return builder.build_complete_conditions_v2(task_prompt)