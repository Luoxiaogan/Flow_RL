"""
Benchmark cloning and configuration tool
Allows creating new benchmarks with different operator groups
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

from ScoreFlow.scripts.common.prompt_builder import DynamicPromptBuilder
from ScoreFlow.scripts.common.operator_loader import OperatorGroupManager

logger = logging.getLogger(__name__)

class BenchmarkCloner:
    """Tool for cloning and configuring benchmarks with custom operator groups"""
    
    def __init__(self, scoreflow_root: str = None):
        """
        Initialize the benchmark cloner
        
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
        
        logger.info(f"Initialized BenchmarkCloner with root: {self.root}")
    
    def clone_benchmark(
        self,
        source_benchmark: str,
        target_benchmark: str,
        operator_group: str,
        dataset_paths: Optional[Dict[str, str]] = None,
        force: bool = False
    ) -> bool:
        """
        Clone a benchmark and configure it with a new operator group
        
        Args:
            source_benchmark: Name of the source benchmark to clone
            target_benchmark: Name for the new benchmark
            operator_group: Operator group to use
            dataset_paths: Optional custom dataset paths {'train': path, 'test': path}
            force: Force overwrite if target exists
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Cloning Benchmark: {source_benchmark} -> {target_benchmark}")
        print(f"Operator Group: {operator_group}")
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
            print(f"[1/5] Copying directory structure...")
            shutil.copytree(source_dir, target_dir)
            print(f"  ✓ Copied: {source_dir} -> {target_dir}")
            
            # Step 2: Update handler.py
            print(f"[2/5] Updating handler class...")
            self._update_handler_class(target_dir, source_benchmark, target_benchmark)
            
            # Step 3: Generate new conditions.py
            print(f"[3/5] Generating new conditions.py...")
            self._generate_conditions(target_dir, source_benchmark, target_benchmark, operator_group)
            
            # Step 4: Update benchmark_mapping.jsonl
            print(f"[4/5] Updating benchmark mapping...")
            self._update_benchmark_mapping(
                target_benchmark,
                dataset_paths or self._get_default_dataset_paths(target_benchmark)
            )
            
            # Step 5: Save configuration
            print(f"[5/5] Saving configuration...")
            self._save_benchmark_config(target_dir, operator_group, source_benchmark)
            
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS: Benchmark '{target_benchmark}' created!")
            print(f"{'='*60}")
            print(f"\nDetails:")
            print(f"  • Location: {target_dir}")
            print(f"  • Operator Group: {operator_group}")
            print(f"  • Source: {source_benchmark}")
            
            # Show operator list
            group = self.group_manager.get_group(operator_group)
            if group:
                print(f"  • Operators ({len(group['operators'])}):")
                for op in group['operators']:
                    print(f"    - {op}")
            
            print(f"\nNext Steps:")
            print(f"  1. Review generated conditions.py")
            print(f"  2. Adjust TASK_PROMPT if needed")
            print(f"  3. Prepare dataset files")
            print(f"  4. Run: bash run_workflow_system.sh --benchmark {target_benchmark}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during cloning: {e}")
            print(f"\n✗ ERROR: {e}")
            # Clean up partial clone
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            return False
    
    def _validate_inputs(self, source_benchmark: str, operator_group: str) -> bool:
        """Validate that source benchmark and operator group exist"""
        # Check source benchmark exists
        source_dir = os.path.join(self.scripts_dir, source_benchmark)
        if not os.path.exists(source_dir):
            print(f"✗ Error: Source benchmark '{source_benchmark}' not found at {source_dir}")
            return False
        
        # Check operator group exists
        if not self.group_manager.get_group(operator_group):
            print(f"✗ Error: Operator group '{operator_group}' not found")
            print(f"Available groups: {', '.join(self.group_manager.list_groups())}")
            return False
        
        # Validate operator group
        is_valid, missing = self.group_manager.validate_group(operator_group)
        if not is_valid:
            print(f"✗ Error: Operator group '{operator_group}' has missing operators: {missing}")
            return False
        
        return True
    
    def _update_handler_class(self, target_dir: str, source_name: str, target_name: str):
        """Update handler.py with new class name"""
        handler_path = os.path.join(target_dir, 'handler.py')
        
        if not os.path.exists(handler_path):
            print(f"  ⚠ handler.py not found, skipping class update")
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
                print(f"  ✓ Updated: {old} -> {new}")
        
        with open(handler_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_conditions(self, target_dir: str, source_name: str, target_name: str, operator_group: str):
        """Generate new conditions.py file"""
        # Extract TASK_PROMPT from source
        source_conditions = os.path.join(target_dir, 'conditions.py')
        task_prompt = self._extract_task_prompt(source_conditions)
        
        # Create prompt builder
        builder = DynamicPromptBuilder(target_name, operator_group)
        
        # Generate new conditions
        new_conditions = builder.build_complete_conditions(task_prompt)
        
        # Add source information
        new_conditions = new_conditions.replace(
            '"""',
            f'"""\nSource benchmark: {source_name}\n',
            1  # Only replace first occurrence
        )
        
        # Write new conditions
        with open(source_conditions, 'w', encoding='utf-8') as f:
            f.write(new_conditions)
        
        print(f"  ✓ Generated conditions.py with {operator_group} operators")
    
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
                        return content[start_idx:end_idx].strip()
            
            return f"# TODO: Add task prompt for this benchmark"
            
        except Exception as e:
            logger.warning(f"Could not extract TASK_PROMPT: {e}")
            return f"# TODO: Add task prompt for this benchmark"
    
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
            print(f"  ✓ Updated existing entry in benchmark_mapping.jsonl")
        else:
            mappings.append(new_mapping)
            print(f"  ✓ Added new entry to benchmark_mapping.jsonl")
        
        # Write back
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            for mapping in mappings:
                f.write(json.dumps(mapping, ensure_ascii=False) + '\n')
    
    def _save_benchmark_config(self, target_dir: str, operator_group: str, source_benchmark: str):
        """Save benchmark configuration metadata"""
        config = {
            'operator_group': operator_group,
            'source_benchmark': source_benchmark,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'tool': 'BenchmarkCloner'
        }
        
        config_path = os.path.join(target_dir, 'benchmark_config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"  ✓ Saved configuration to benchmark_config.yaml")
    
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
                if os.path.isdir(item_path) and item not in ['common', '__pycache__']:
                    benchmarks.append(item)
        return sorted(benchmarks)
    
    def get_benchmark_info(self, benchmark_name: str) -> Dict[str, Any]:
        """Get information about a benchmark"""
        benchmark_dir = os.path.join(self.scripts_dir, benchmark_name)
        info = {
            'name': benchmark_name,
            'exists': os.path.exists(benchmark_dir),
            'has_handler': False,
            'has_conditions': False,
            'has_config': False,
            'operator_group': None,
            'source_benchmark': None
        }
        
        if info['exists']:
            info['has_handler'] = os.path.exists(os.path.join(benchmark_dir, 'handler.py'))
            info['has_conditions'] = os.path.exists(os.path.join(benchmark_dir, 'conditions.py'))
            
            config_path = os.path.join(benchmark_dir, 'benchmark_config.yaml')
            if os.path.exists(config_path):
                info['has_config'] = True
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        info['operator_group'] = config.get('operator_group')
                        info['source_benchmark'] = config.get('source_benchmark')
                except:
                    pass
        
        return info


# Add missing import
from typing import List