"""
Enhanced benchmark cloning tool that supports split prompt structure
Creates benchmarks with properly formatted conditions matching original ScoreFlow design
"""
import os
import shutil
import json
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ScoreFlow.scripts.common.prompt_builder_v2 import EnhancedPromptBuilder
from ScoreFlow.scripts.common.operator_loader import OperatorGroupManager

logger = logging.getLogger(__name__)

class EnhancedBenchmarkCloner:
    """Enhanced tool for cloning benchmarks with split prompt structure"""
    
    def __init__(self, scoreflow_root: str = None):
        """
        Initialize the enhanced benchmark cloner
        
        Args:
            scoreflow_root: Root directory of ScoreFlow (default: auto-detect)
        """
        if scoreflow_root is None:
            # Auto-detect ScoreFlow root
            scoreflow_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.root = scoreflow_root
        self.scripts_dir = os.path.join(self.root, 'scripts')
        self.mapping_file = os.path.join(self.root, 'benchmark_mapping.jsonl')
        self.group_manager = OperatorGroupManager()
        
        logger.info(f"Initialized EnhancedBenchmarkCloner with root: {self.root}")
    
    def clone_benchmark(
        self,
        source_benchmark: str,
        target_benchmark: str,
        operator_group: str,
        dataset_paths: Optional[Dict[str, str]] = None,
        force: bool = False,
        use_split_structure: bool = True
    ) -> bool:
        """
        Clone a benchmark with enhanced split prompt structure
        
        Args:
            source_benchmark: Name of the source benchmark to clone
            target_benchmark: Name for the new benchmark
            operator_group: Operator group to use
            dataset_paths: Optional custom dataset paths {'train': path, 'test': path}
            force: Force overwrite if target exists
            use_split_structure: Use split prompt structure (OPERATOR_PROMPT_PART_1/2) vs single START_PROMPT
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Enhanced Benchmark Cloning")
        print(f"Source: {source_benchmark} -> Target: {target_benchmark}")
        print(f"Operator Group: {operator_group}")
        print(f"Split Structure: {'Yes' if use_split_structure else 'No (Legacy)'}")
        print(f"{'='*60}\n")
        
        # Validate inputs
        if not self._validate_inputs(source_benchmark, operator_group):
            return False
        
        # Check and handle existing target
        source_dir = os.path.join(self.scripts_dir, source_benchmark)
        target_dir = os.path.join(self.scripts_dir, target_benchmark)
        
        if os.path.exists(target_dir):
            if not force:
                response = input(f"Warning: Target directory '{target_dir}' already exists. Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print("Operation cancelled.")
                    return False
            print(f"Removing existing directory: {target_dir}")
            shutil.rmtree(target_dir)
        
        try:
            # Step 1: Copy directory
            print(f"[1/6] Copying directory structure...")
            shutil.copytree(source_dir, target_dir)
            print(f"  [OK] Copied: {source_dir} -> {target_dir}")
            
            # Step 2: Update handler.py
            print(f"[2/6] Updating handler class...")
            self._update_handler_class(target_dir, source_benchmark, target_benchmark)
            
            # Step 3: Extract TASK_PROMPT from source
            print(f"[3/6] Extracting task prompt...")
            task_prompt = self._extract_task_prompt(os.path.join(target_dir, 'conditions.py'))
            
            # Step 4: Generate new conditions.py with split structure
            print(f"[4/6] Generating new conditions.py with split structure...")
            self._generate_split_conditions(target_dir, target_benchmark, operator_group, task_prompt, use_split_structure)
            
            # Step 5: Update benchmark_mapping.jsonl
            print(f"[5/6] Updating benchmark mapping...")
            self._update_benchmark_mapping(
                target_benchmark,
                dataset_paths or self._get_default_dataset_paths(target_benchmark)
            )
            
            # Step 6: Save configuration
            print(f"[6/6] Saving configuration...")
            self._save_benchmark_config(target_dir, operator_group, source_benchmark, use_split_structure)
            
            print(f"\n{'='*60}")
            print(f"[SUCCESS] Enhanced Benchmark '{target_benchmark}' created!")
            print(f"{'='*60}")
            print(f"\nDetails:")
            print(f"  - Location: {target_dir}")
            print(f"  - Operator Group: {operator_group}")
            print(f"  - Source: {source_benchmark}")
            print(f"  - Structure: {'Split (OPERATOR_PROMPT_PART_1/2)' if use_split_structure else 'Legacy (START_PROMPT)'}")
            
            # Show operator list
            group = self.group_manager.get_group(operator_group)
            if group:
                print(f"  - Operators ({len(group['operators'])}):")
                for op in group['operators']:
                    print(f"    * {op}")
            
            # Show generated prompt variables
            print(f"\n  - Generated Prompt Variables:")
            if use_split_structure:
                print(f"    * TASK_PROMPT")
                print(f"    * OPERATOR_PROMPT_PART_1")
                print(f"    * OPERATOR_PROMPT_PART_2")
                print(f"    * USER_PROMPT_LONG")
                print(f"    * SYSTEM_PROMPT")
                print(f"    * START_PROMPT (for backward compatibility)")
            else:
                print(f"    * TASK_PROMPT")
                print(f"    * START_PROMPT")
                print(f"    * SYSTEM_PROMPT")
            
            print(f"\nNext Steps:")
            print(f"  1. Review generated conditions.py")
            print(f"  2. Adjust TASK_PROMPT if needed")
            print(f"  3. Prepare dataset files")
            print(f"  4. Run: bash run_workflow_system.sh --benchmark {target_benchmark}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during cloning: {e}")
            print(f"\n[ERROR] {e}")
            # Clean up partial clone
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            return False
    
    def _validate_inputs(self, source_benchmark: str, operator_group: str) -> bool:
        """Validate that source benchmark and operator group exist"""
        # Check source benchmark exists
        source_dir = os.path.join(self.scripts_dir, source_benchmark)
        if not os.path.exists(source_dir):
            print(f"[ERROR] Source benchmark '{source_benchmark}' not found at {source_dir}")
            return False
        
        # Check operator group exists
        if not self.group_manager.get_group(operator_group):
            print(f"[ERROR] Operator group '{operator_group}' not found")
            print(f"Available groups: {', '.join(self.group_manager.list_groups())}")
            return False
        
        # Validate operator group
        is_valid, missing = self.group_manager.validate_group(operator_group)
        if not is_valid:
            print(f"[ERROR] Operator group '{operator_group}' has missing operators: {missing}")
            return False
        
        return True
    
    def _update_handler_class(self, target_dir: str, source_name: str, target_name: str):
        """Update handler.py with new class name"""
        handler_path = os.path.join(target_dir, 'handler.py')
        
        if not os.path.exists(handler_path):
            print(f"  [WARNING] handler.py not found, skipping class update")
            return
        
        with open(handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update class name (handle various naming patterns)
        replacements = [
            (f"{source_name.capitalize()}Handler", f"{target_name.capitalize()}Handler"),
            (f"{source_name.upper()}Handler", f"{target_name.capitalize()}Handler"),
            (f"{source_name}Handler", f"{target_name.capitalize()}Handler"),
            (f'benchmark_name = "{source_name}"', f'benchmark_name = "{target_name}"'),
            (f"benchmark_name = '{source_name}'", f"benchmark_name = '{target_name}'"),
        ]
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"  [OK] Updated: {old} -> {new}")
        
        with open(handler_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _extract_task_prompt(self, conditions_path: str) -> str:
        """Extract TASK_PROMPT from existing conditions file"""
        if not os.path.exists(conditions_path):
            return f"# TODO: Add task prompt for this benchmark"
        
        try:
            with open(conditions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try different quote patterns
            patterns = [
                ("TASK_PROMPT = '''", "'''"),
                ('TASK_PROMPT = """', '"""'),
                ("TASK_PROMPT = '", "'"),
                ('TASK_PROMPT = "', '"'),
            ]
            
            for start_pattern, end_pattern in patterns:
                if start_pattern in content:
                    start_idx = content.find(start_pattern) + len(start_pattern)
                    end_idx = content.find(end_pattern, start_idx)
                    if end_idx > start_idx:
                        task_prompt = content[start_idx:end_idx].strip()
                        print(f"  [OK] Extracted TASK_PROMPT ({len(task_prompt)} chars)")
                        return task_prompt
            
            print(f"  [WARNING] Could not extract TASK_PROMPT, using placeholder")
            return f"# TODO: Add task prompt for this benchmark"
            
        except Exception as e:
            logger.warning(f"Could not extract TASK_PROMPT: {e}")
            return f"# TODO: Add task prompt for this benchmark"
    
    def _generate_split_conditions(self, target_dir: str, target_name: str, operator_group: str, 
                                  task_prompt: str, use_split_structure: bool):
        """Generate new conditions.py file with split prompt structure"""
        # Create enhanced prompt builder
        builder = EnhancedPromptBuilder(target_name, operator_group)
        
        if use_split_structure:
            # Generate split structure (modern)
            new_conditions = builder.build_complete_conditions_v2(task_prompt)
        else:
            # Generate legacy structure (backward compatible)
            # This would use the original prompt_builder.py methods
            # For now, we'll generate split structure but combine them
            new_conditions = self._generate_legacy_conditions(builder, target_name, operator_group, task_prompt)
        
        # Write new conditions
        conditions_path = os.path.join(target_dir, 'conditions.py')
        with open(conditions_path, 'w', encoding='utf-8') as f:
            f.write(new_conditions)
        
        structure_type = "split structure" if use_split_structure else "legacy structure"
        print(f"  [OK] Generated conditions.py with {structure_type} and {operator_group} operators")
    
    def _generate_legacy_conditions(self, builder, target_name: str, operator_group: str, task_prompt: str) -> str:
        """Generate legacy format conditions (single START_PROMPT)"""
        from datetime import datetime
        
        # Generate all components
        prompts = builder.get_split_prompts()
        
        content = f'''"""
Auto-generated conditions for {target_name} benchmark
Using operator group: {operator_group}
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Legacy format with single START_PROMPT
"""

# ========== Task/Domain Description ==========
TASK_PROMPT = \'\'\'{task_prompt}\'\'\'

# ========== System Prompt ==========
SYSTEM_PROMPT = \'\'\'{prompts['SYSTEM_PROMPT']}\'\'\'

# ========== Combined Operator Prompt (Legacy) ==========
START_PROMPT = \'\'\'{prompts['START_PROMPT']}\'\'\'

# ========== Python Imports ==========
PYTHON_START = \'\'\'{prompts['PYTHON_START']}\'\'\'

# ========== Python End Template ==========
PYTHON_END = \'\'\'
    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {{time}}

        try:
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\\\n", "\\\\\\\\n").replace('"', '\\\\"')
            return f"Final Answer: Error - An exception occurred. Details: {{{{escaped_error_details}}}}"
\'\'\'

# ========== Configuration Metadata ==========
OPERATOR_GROUP = "{operator_group}"
BENCHMARK_NAME = "{target_name}"
'''
        return content
    
    def _update_benchmark_mapping(self, benchmark_name: str, dataset_paths: Dict[str, str]):
        """Update or add entry in benchmark_mapping.jsonl"""
        mappings = []
        
        # Read existing mappings
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        mappings.append(json.loads(line))
        
        # Check if benchmark already exists
        existing_idx = None
        for idx, mapping in enumerate(mappings):
            if mapping['benchmark'] == benchmark_name:
                existing_idx = idx
                break
        
        # Create new mapping entry
        new_mapping = {
            "benchmark": benchmark_name,
            "handler_class": f"{benchmark_name.capitalize()}Handler",
            "handler_dir": f"ScoreFlow/scripts/{benchmark_name}",
            "data_train_dir": dataset_paths.get('train'),
            "data_test_dir": dataset_paths.get('test')
        }
        
        # Update or append
        if existing_idx is not None:
            mappings[existing_idx] = new_mapping
            print(f"  [OK] Updated existing entry in benchmark_mapping.jsonl")
        else:
            mappings.append(new_mapping)
            print(f"  [OK] Added new entry to benchmark_mapping.jsonl")
        
        # Write back
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            for mapping in mappings:
                f.write(json.dumps(mapping, ensure_ascii=False) + '\n')
    
    def _save_benchmark_config(self, target_dir: str, operator_group: str, source_benchmark: str, 
                              use_split_structure: bool):
        """Save benchmark configuration metadata"""
        config = {
            'operator_group': operator_group,
            'source_benchmark': source_benchmark,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '2.0',
            'tool': 'EnhancedBenchmarkCloner',
            'prompt_structure': 'split' if use_split_structure else 'legacy',
            'features': {
                'split_prompts': use_split_structure,
                'operator_prompt_part_1': use_split_structure,
                'operator_prompt_part_2': use_split_structure,
                'user_prompt_long': use_split_structure,
                'backward_compatible': True
            }
        }
        
        config_path = os.path.join(target_dir, 'benchmark_config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"  [OK] Saved configuration to benchmark_config.yaml")
    
    def _get_default_dataset_paths(self, benchmark_name: str) -> Dict[str, str]:
        """Get default dataset paths for a benchmark"""
        return {
            'train': f"D:/temp/Flow_RL/Processed_dataset/{benchmark_name}/train.jsonl",
            'test': f"D:/temp/Flow_RL/Processed_dataset/{benchmark_name}/test.jsonl"
        }
    
    def list_benchmarks(self) -> List[str]:
        """List all available benchmarks"""
        benchmarks = []
        if os.path.exists(self.scripts_dir):
            for item in os.listdir(self.scripts_dir):
                item_path = os.path.join(self.scripts_dir, item)
                if os.path.isdir(item_path) and item not in ['common', '__pycache__', 'common_back_up']:
                    benchmarks.append(item)
        return sorted(benchmarks)
    
    def analyze_benchmark_structure(self, benchmark_name: str) -> Dict[str, Any]:
        """
        Analyze the prompt structure of an existing benchmark
        
        Returns:
            Dictionary with structure analysis
        """
        benchmark_dir = os.path.join(self.scripts_dir, benchmark_name)
        conditions_path = os.path.join(benchmark_dir, 'conditions.py')
        
        analysis = {
            'name': benchmark_name,
            'exists': os.path.exists(benchmark_dir),
            'has_conditions': os.path.exists(conditions_path),
            'structure_type': 'unknown',
            'prompt_variables': [],
            'has_split_structure': False,
            'has_legacy_structure': False
        }
        
        if not analysis['has_conditions']:
            return analysis
        
        try:
            with open(conditions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for various prompt variables
            variables_to_check = [
                'TASK_PROMPT',
                'OPERATOR_PROMPT_PART_1',
                'OPERATOR_PROMPT_PART_2',
                'USER_PROMPT_LONG',
                'START_PROMPT',
                'SYSTEM_PROMPT',
                'PYTHON_START',
                'PYTHON_END'
            ]
            
            for var in variables_to_check:
                if f'{var} = ' in content:
                    analysis['prompt_variables'].append(var)
            
            # Determine structure type
            if 'OPERATOR_PROMPT_PART_1' in analysis['prompt_variables']:
                analysis['has_split_structure'] = True
                analysis['structure_type'] = 'split'
            
            if 'START_PROMPT' in analysis['prompt_variables']:
                analysis['has_legacy_structure'] = True
                if not analysis['has_split_structure']:
                    analysis['structure_type'] = 'legacy'
                else:
                    analysis['structure_type'] = 'hybrid'  # Has both
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis


# Utility function
def analyze_all_benchmarks(scoreflow_root: str = None) -> None:
    """Analyze and report on all benchmark structures"""
    cloner = EnhancedBenchmarkCloner(scoreflow_root)
    benchmarks = cloner.list_benchmarks()
    
    print(f"\n{'='*70}")
    print("Benchmark Structure Analysis")
    print(f"{'='*70}\n")
    
    split_count = 0
    legacy_count = 0
    hybrid_count = 0
    
    for benchmark in benchmarks:
        analysis = cloner.analyze_benchmark_structure(benchmark)
        
        if analysis['has_conditions']:
            structure = analysis['structure_type']
            variables = ', '.join(analysis['prompt_variables'][:3])
            if len(analysis['prompt_variables']) > 3:
                variables += f" (+{len(analysis['prompt_variables'])-3} more)"
            
            print(f"{benchmark:<20} {structure:<10} [{variables}]")
            
            if structure == 'split':
                split_count += 1
            elif structure == 'legacy':
                legacy_count += 1
            elif structure == 'hybrid':
                hybrid_count += 1
        else:
            print(f"{benchmark:<20} {'no conditions':<10}")
    
    print(f"\n{'-'*70}")
    print(f"Summary: {len(benchmarks)} benchmarks")
    print(f"  - Split structure: {split_count}")
    print(f"  - Legacy structure: {legacy_count}")
    print(f"  - Hybrid structure: {hybrid_count}")
    print(f"{'='*70}\n")