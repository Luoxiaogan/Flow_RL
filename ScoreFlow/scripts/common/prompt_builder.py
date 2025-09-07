"""
Dynamic prompt builder for generating operator-specific conditions
Constructs prompts based on selected operator groups
"""
from typing import List, Dict, Any, Set, Optional
import logging
from .operator_loader import OperatorRegistry, OperatorGroupManager
from .base_conditions import (
    BASE_SYSTEM_PROMPT,
    BASE_PYTHON_END,
    BASE_DESIGN_PRINCIPLES,
    BASE_PARAMETER_EXPLANATION,
    BASE_TASK_INSTRUCTIONS,
    BASE_OPERATOR_NOTES
)

logger = logging.getLogger(__name__)

class DynamicPromptBuilder:
    """Builder for constructing dynamic prompts based on operator configurations"""
    
    def __init__(self, benchmark_name: str, operator_group: str = 'default'):
        """
        Initialize the prompt builder
        
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
        
        logger.info(f"Initialized prompt builder for {benchmark_name} with group {operator_group}")
    
    def build_python_start(self) -> str:
        """
        Build the PYTHON_START section with appropriate imports
        
        Returns:
            String containing import statements
        """
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
                imports.append("import ScoreFlow.scripts.MATH.operator as math_operator")
            else:
                # Handle other custom modules
                module_parts = module.split('.')
                if len(module_parts) == 2:
                    imports.append(f"import ScoreFlow.scripts.{module} as {module_parts[0]}_operator")
                else:
                    imports.append(f"import ScoreFlow.scripts.{module}")
        
        imports.append("from metagpt.provider.llm_provider_registry import create_llm_instance as create")
        
        return '\n'.join(imports) + '\n\n'
    
    def build_operator_prompt(self) -> str:
        """
        Build the operator description section of the prompt
        
        Returns:
            String containing operator descriptions and usage instructions
        """
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            raise ValueError(f"Operator group '{self.operator_group}' not found")
        
        prompt_parts = [
            "### 2. Available Operators & Building Blocks\n\n",
            f"**Using Operator Group: {group['name']}**\n",
            f"**Description: {group['description']}**\n\n",
            "All operators follow a consistent interface pattern and are initialized with the problem text. ",
            "They are available as `self.operator_name`.\n\n",
            BASE_OPERATOR_NOTES,
            "\n\n"
        ]
        
        # Add parameter explanation
        prompt_parts.append(BASE_PARAMETER_EXPLANATION)
        prompt_parts.append("\n\n### Core Operators\n\n")
        
        # Add each operator's description
        for idx, op_name in enumerate(group['operators'], 1):
            op_info = self.registry.get_operator_info(op_name)
            if op_info:
                # Format signature based on operator type
                signature = op_info['signature']
                if op_name == 'Ensemble':
                    # Special handling for Ensemble operator
                    signature = signature.replace('contexts: List[str]', 'contexts_list: List[str]')
                
                prompt_parts.append(
                    f"**{idx}. {op_name}: {op_info['description']}**\n"
                    f"- **Signature:** `await self.{op_name.lower()}({signature}) -> str`\n"
                    f"- **Purpose:** {op_info['prompt_template']}\n\n"
                )
            else:
                logger.warning(f"Operator '{op_name}' not found in registry")
        
        # Add design principles
        prompt_parts.append(BASE_DESIGN_PRINCIPLES)
        
        # Add task instructions
        prompt_parts.append(self._get_task_instructions())
        
        return ''.join(prompt_parts)
    
    def _get_task_instructions(self) -> str:
        """
        Get the task instructions section
        
        Returns:
            String containing task instructions
        """
        # Customize based on operator group if needed
        instructions = BASE_TASK_INSTRUCTIONS
        
        # Add group-specific notes if applicable
        group = self.group_manager.get_group(self.operator_group)
        if group and group.get('special_init'):
            instructions = instructions.replace(
                "# [OPERATOR INITIALIZATION WILL BE DYNAMICALLY GENERATED]",
                self.build_init_code()
            )
        
        return instructions
    
    def build_init_code(self) -> str:
        """
        Build the __init__ method operator initialization code
        
        Returns:
            String containing Python code for operator initialization
        """
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            return "# Error: Operator group not found"
        
        lines = []
        
        # Check if special initialization is needed
        if group.get('special_init'):
            lines.append("self.gid = None  # For MATH operators")
        
        # Generate initialization for each operator
        for op_name in group['operators']:
            op_info = self.registry.get_operator_info(op_name)
            if not op_info:
                lines.append(f"# Warning: {op_name} not found in registry")
                continue
            
            var_name = op_name.lower()
            if op_name == 'ScEnsemble':
                var_name = 'sc_ensemble'  # Special case for ScEnsemble
            
            # Determine the correct module prefix
            module_prefix = "operator"
            if group.get('module') == 'mixed':
                # Mixed mode - check individual operator module
                if op_info['module_path'] == 'MATH.operator':
                    module_prefix = "math_operator"
                elif op_info['module_path'] != 'common.operator':
                    # Custom module
                    module_parts = op_info['module_path'].split('.')
                    if len(module_parts) == 2:
                        module_prefix = f"{module_parts[0]}_operator"
            elif group.get('module') == 'MATH.operator':
                module_prefix = "math_operator"
            
            # Build initialization line based on operator requirements
            if op_info['module_path'] == 'MATH.operator':
                # MATH operators need special parameters
                lines.append(f"self.{var_name} = {module_prefix}.{op_info['class_name']}(self.llm, self.gid, self.problem_text)")
            else:
                # Common operators
                lines.append(f"self.{var_name} = {module_prefix}.{op_info['class_name']}(self.llm, self.problem_text)")
        
        # Format with proper indentation
        return '\n        '.join([''] + lines)
    
    def build_start_prompt(self) -> str:
        """
        Build the complete START_PROMPT for conditions.py
        
        Returns:
            String containing the full start prompt
        """
        return self.build_operator_prompt()
    
    def build_complete_conditions(self, task_prompt: str = None) -> str:
        """
        Build a complete conditions.py file content
        
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
"""
from ScoreFlow.scripts.common.base_conditions import (
    BASE_SYSTEM_PROMPT,
    BASE_PYTHON_END,
    BASE_RESPONSE_FORMAT
)

# ========== Benchmark-specific task description ==========
TASK_PROMPT = \'\'\'{task_prompt}\'\'\'

# ========== System prompt (using common template) ==========
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT

# ========== Python start section with imports ==========
PYTHON_START = \'\'\'{self.build_python_start()}\'\'\'

# ========== Python end section (using common template) ==========
PYTHON_END = BASE_PYTHON_END

# ========== Operator descriptions and instructions ==========
START_PROMPT = \'\'\'{self.build_start_prompt()}\'\'\'

# ========== Operator initialization code for reference ==========
# This shows how operators should be initialized in the __init__ method
OPERATOR_INIT_CODE = \'\'\'{self.build_init_code()}\'\'\'

# ========== Configuration metadata ==========
OPERATOR_GROUP = "{self.operator_group}"
BENCHMARK_NAME = "{self.benchmark_name}"
'''
        return content
    
    def get_operator_list(self) -> List[str]:
        """
        Get list of operator names in the current group
        
        Returns:
            List of operator names
        """
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            return []
        return group.get('operators', [])
    
    def get_required_modules(self) -> Set[str]:
        """
        Get set of module paths required for the operator group
        
        Returns:
            Set of module path strings
        """
        return set(self.group_manager.get_modules_for_group(self.operator_group))
    
    def validate_for_benchmark(self) -> tuple:
        """
        Validate that the operator group is compatible with the benchmark
        
        Returns:
            Tuple of (is_valid: bool, issues: List[str])
        """
        issues = []
        
        # Check group exists
        group = self.group_manager.get_group(self.operator_group)
        if not group:
            return False, [f"Operator group '{self.operator_group}' not found"]
        
        # Check each operator supports the benchmark
        for op_name in group.get('operators', []):
            op_info = self.registry.get_operator_info(op_name)
            if not op_info:
                issues.append(f"Operator '{op_name}' not found in registry")
                continue
            
            supported = op_info['supported_benchmarks']
            if supported != 'all' and self.benchmark_name not in supported.split('|'):
                issues.append(f"Operator '{op_name}' does not support benchmark '{self.benchmark_name}'")
        
        return len(issues) == 0, issues


# Utility function for quick prompt generation
def generate_conditions_for_benchmark(
    benchmark_name: str,
    operator_group: str,
    task_prompt: str = None
) -> str:
    """
    Generate a complete conditions.py file for a benchmark
    
    Args:
        benchmark_name: Name of the benchmark
        operator_group: Name of the operator group
        task_prompt: Optional task-specific prompt
        
    Returns:
        String containing complete conditions.py content
    """
    builder = DynamicPromptBuilder(benchmark_name, operator_group)
    return builder.build_complete_conditions(task_prompt)