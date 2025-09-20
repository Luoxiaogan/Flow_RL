"""
VERL Training Data Generator - Generate training datasets in parquet format
This script generates training data for VERL from various benchmarks.
"""

import sys
import json
import logging
import argparse
import random
import pandas as pd
import yaml
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import importlib

# Add project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# Load config to get ScoreFlow path
CONFIG_FILE = CURRENT_DIR.parent / "config.yaml"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # Get project_root from config
    project_root = config.get('project_root', str(PROJECT_ROOT))
    project_root_path = Path(project_root)
    
    # Get scoreflow_handlers relative path and build full path
    scoreflow_handlers = config.get('paths', {}).get('scoreflow_handlers', '.')
    if scoreflow_handlers == '.':
        scoreflow_path = project_root_path
    else:
        scoreflow_path = project_root_path / scoreflow_handlers
    sys.path.append(str(scoreflow_path))
else:
    # Fallback to default path
    sys.path.append(str(PROJECT_ROOT))

from ScoreFlow.scripts.base_handler import BenchmarkHandler


class VerlTrainingDataGenerator:
    """Generate VERL training data from benchmarks"""
    
    def __init__(self, output_dir: str = None, benchmark_mapping_file: str = None):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save generated parquet files
            benchmark_mapping_file: Path to benchmark mapping JSONL file
        """
        self.output_dir = Path(output_dir) if output_dir else CURRENT_DIR / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load benchmark mapping (now a list to support multiple configs per benchmark)
        self.benchmark_mapping_list = self._load_benchmark_mapping(benchmark_mapping_file)

        # Create quick lookup dictionary for handlers (use first occurrence for each benchmark)
        self.benchmark_handler_info = {}
        for config in self.benchmark_mapping_list:
            benchmark = config['benchmark']
            if benchmark not in self.benchmark_handler_info:
                self.benchmark_handler_info[benchmark] = config

        # List unique benchmark names
        self.available_benchmarks = list(set(config['benchmark'] for config in self.benchmark_mapping_list))

        logging.info(f"VerlTrainingDataGenerator initialized with output dir: {self.output_dir}")
        logging.info(f"Available benchmarks: {self.available_benchmarks}")
        logging.info(f"Total configurations: {len(self.benchmark_mapping_list)}")
    
    def _load_benchmark_mapping(self, benchmark_mapping_file: str = None) -> List[Dict]:
        """Load benchmark mapping from jsonl file

        Args:
            benchmark_mapping_file: Path to benchmark mapping file (optional)

        Returns:
            List of all benchmark configurations (supports multiple configs per benchmark)
        """
        # Priority: command line arg > config file > default
        if benchmark_mapping_file:
            # Use command line provided path
            mapping_file_path = Path(benchmark_mapping_file)
            logging.info(f"Using benchmark mapping from command line: {mapping_file_path}")
        elif CONFIG_FILE.exists():
            # Try to get from config file
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            # Get project_root from config
            project_root = config.get('project_root', str(PROJECT_ROOT))
            project_root_path = Path(project_root)

            # Get benchmark_mapping relative path and build full path
            benchmark_mapping_rel = config.get('paths', {}).get('benchmark_mapping', 'ScoreFlow/benchmark_mapping.jsonl')
            mapping_file_path = project_root_path / benchmark_mapping_rel
            logging.info(f"Using benchmark mapping from config: {mapping_file_path}")
        else:
            # Fallback to default path
            mapping_file_path = PROJECT_ROOT / "ScoreFlow" / "benchmark_mapping.jsonl"
            logging.info(f"Using default benchmark mapping: {mapping_file_path}")


        # Return list to support multiple configs per benchmark
        mapping_list = []
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    mapping_list.append(data)

        return mapping_list
    
    def _get_benchmark_handler(self, benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
        """Get handler for a specific benchmark"""
        try:
            # Check benchmark mapping first (use handler info which has first occurrence)
            benchmark_info = self.benchmark_handler_info.get(benchmark_name)
            if benchmark_info:
                # Use mapping info for handler class name and path
                handler_class_name = benchmark_info['handler_class']
                handler_dir = benchmark_info['handler_dir']
                
                # Convert handler_dir to Python module path
                # Need to extract relative path from scoreflow_handlers root
                scoreflow_root = None
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    # Get project_root from config
                    project_root = config.get('project_root', str(PROJECT_ROOT))
                    project_root_path = Path(project_root)
                    
                    # Get scoreflow_handlers relative path and build full path
                    scoreflow_handlers = config.get('paths', {}).get('scoreflow_handlers', '.')
                    if scoreflow_handlers == '.':
                        scoreflow_root = str(project_root_path)
                    else:
                        scoreflow_root = str(project_root_path / scoreflow_handlers)
                else:
                    scoreflow_root = str(PROJECT_ROOT)
                
                # Extract relative path from handler_dir
                if handler_dir.startswith(scoreflow_root):
                    # Remove scoreflow_root prefix and leading slash
                    relative_path = handler_dir[len(scoreflow_root):].lstrip('/')
                    handler_module_path = relative_path.replace('/', '.') + '.handler'
                else:
                    # Fallback: assume it's already a relative path from ScoreFlow
                    if handler_dir.startswith('/'):
                        # Extract ScoreFlow part from absolute path
                        scoreflow_index = handler_dir.find('ScoreFlow')
                        if scoreflow_index != -1:
                            relative_path = handler_dir[scoreflow_index:]
                            handler_module_path = relative_path.replace('/', '.') + '.handler'
                        else:
                            raise ValueError(f"Cannot find ScoreFlow in handler_dir: {handler_dir}")
                    else:
                        handler_module_path = handler_dir.replace('/', '.') + '.handler'
            else:
                # Fallback to default naming rules
                if benchmark_name.startswith("high_level_math"):
                    handler_module_path = "ScoreFlow.scripts.high_level_math.handler"
                    handler_class_name = "HighLevelMathHandler"
                else:
                    handler_module_path = f"ScoreFlow.scripts.{benchmark_name}.handler"
                    handler_class_name = f"{benchmark_name.capitalize()}Handler"
            
            # Import handler module
            handler_module = importlib.import_module(handler_module_path)
            handler_class = getattr(handler_module, handler_class_name)
            
            return handler_class(dataset_path=dataset_path)
        except Exception as e:
            logging.error(f"Failed to load handler for {benchmark_name}: {e}")
            raise
    
    def _load_prompt_templates(self, benchmark_name: str) -> Dict[str, Any]:
        """Load prompt templates from conditions.py and related modules"""
        try:
            # Check benchmark mapping first (use handler info which has first occurrence)
            benchmark_info = self.benchmark_handler_info.get(benchmark_name)
            if benchmark_info:
                handler_dir = benchmark_info['handler_dir']
                
                # Convert handler_dir to Python module path (same logic as in _get_benchmark_handler)
                scoreflow_root = None
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    # Get project_root from config
                    project_root = config.get('project_root', str(PROJECT_ROOT))
                    project_root_path = Path(project_root)
                    
                    # Get scoreflow_handlers relative path and build full path
                    scoreflow_handlers = config.get('paths', {}).get('scoreflow_handlers', '.')
                    if scoreflow_handlers == '.':
                        scoreflow_root = str(project_root_path)
                    else:
                        scoreflow_root = str(project_root_path / scoreflow_handlers)
                else:
                    scoreflow_root = str(PROJECT_ROOT)
                
                # Extract relative path from handler_dir
                if handler_dir.startswith(scoreflow_root):
                    # Remove scoreflow_root prefix and leading slash
                    relative_path = handler_dir[len(scoreflow_root):].lstrip('/')
                    conditions_path = relative_path.replace('/', '.') + '.conditions'
                else:
                    # Fallback: extract ScoreFlow part from absolute path
                    if handler_dir.startswith('/'):
                        scoreflow_index = handler_dir.find('ScoreFlow')
                        if scoreflow_index != -1:
                            relative_path = handler_dir[scoreflow_index:]
                            conditions_path = relative_path.replace('/', '.') + '.conditions'
                        else:
                            raise ValueError(f"Cannot find ScoreFlow in handler_dir: {handler_dir}")
                    else:
                        conditions_path = handler_dir.replace('/', '.') + '.conditions'
            else:
                # Fallback to default naming rules
                if benchmark_name.startswith("high_level_math"):
                    conditions_path = "ScoreFlow.scripts.high_level_math.conditions"
                else:
                    conditions_path = f"ScoreFlow.scripts.{benchmark_name}.conditions"
            
            # Import conditions module
            conditions_module = importlib.import_module(conditions_path)
            
            # Also load common conditions for shared components
            common_conditions = importlib.import_module("ScoreFlow.scripts.common.conditions")
            
            # Since we can't always load the operator module (due to metagpt dependency),
            # we'll use a predefined list that matches what's in common.operator
            # This list corresponds to the operators defined in ScoreFlow
            available_operators = [
                'ScGenerate', 
                'ScRevise', 
                'ScEnsemble', 
                'ScSummarize', 
                'ScProgrammer', 
                'ScDecompose',
                'ScVerifyAndRefine',
                ]
            
            # Load operator descriptions and init codes
            operator_descriptions = {}
            operator_inits = {}
            
            # Map operator class names to keys used in conditions
            operator_key_map = {
                'ScGenerate': 'generate',
                'ScRevise': 'revise',
                'ScSummarize': 'summarize',
                'ScEnsemble': 'ensemble',
                'ScProgrammer': 'programmer',
                'ScDecompose': 'decompose',
                'ScVerifyAndRefine': 'verifyandrefine',
            }
            
            for op_class in available_operators:
                if op_class in operator_key_map:
                    key = operator_key_map[op_class]
                    # Get description from common conditions (directly using the key name)
                    # Get description from common conditions (directly using the key name)
                    operator_descriptions[key] = getattr(common_conditions, key, "")

                    # Get init code from common conditions
                    init_key = f"{key}_init" if key != 'programmer' else "programmer_init"
                    operator_inits[key] = getattr(common_conditions, init_key, "")
            
            # Load all required prompt components
            # First try to load from benchmark-specific conditions
            task_prompt = getattr(conditions_module, "TASK_PROMPT", "")

            # Then load RL_RIGHT components from common conditions
            return {
                'task_prompt': task_prompt,
                'system_prompt_rl_right': getattr(common_conditions, "SYSTEM_PROMPT_RL_RIGHT", "You are a helpful AI assistant."),
                'user_prompt_part_1_rl_right': getattr(common_conditions, "USER_PROMPT_PART_1_RL_RIGHT", ""),
                'user_prompt_part_2_rl_right': getattr(common_conditions, "USER_PROMPT_PART_2_RL_RIGHT", ""),
                'user_prompt_part_3_rl_right': getattr(common_conditions, "USER_PROMPT_PART_3_RL_RIGHT", ""),
                'user_prompt_part_4_rl_right': getattr(common_conditions, "USER_PROMPT_PART_4_RL_RIGHT", ""),
                'available_operators': available_operators,
                'operator_descriptions': operator_descriptions,
                'operator_inits': operator_inits
            }
        except Exception as e:
            logging.error(f"Failed to load prompt templates for {benchmark_name}: {e}")
            raise
    
    def _construct_prompt(self, handler: BenchmarkHandler, data_indices: List[int],
                         benchmark_name: str) -> Tuple[List[Dict], str]:
        """Construct prompt messages in HuggingFace chat format (RL_RIGHT version)

        Args:
            handler: Benchmark handler instance
            data_indices: List of indices of problems to include as examples
            benchmark_name: Name of the benchmark
        """
        # Load all prompt components
        templates = self._load_prompt_templates(benchmark_name)

        # 1. 使用 handler 获取问题文本（传入多个索引）
        problem_text = handler.get_prompt_text(data_indices)

        # 2. 根据benchmark配置获取operators组
        import random
        benchmark_info = self.benchmark_handler_info.get(benchmark_name, {})
        operators_group = benchmark_info.get('operators_group', [])  # 注意：单数形式，直接是算子列表

        if operators_group:
            # 直接使用配置的operators
            selected_operators = operators_group
        else:
            # 如果没有配置，使用默认的随机选择逻辑
            available_ops = ['generate', 'revise', 'summarize', 'ensemble', 'programmer', 'decompose']
            # Filter to only operators that have descriptions
            available_ops = [op for op in available_ops if op in templates['operator_descriptions']]

            # 随机选择3到5个operators
            num_operators = random.randint(3, min(5, len(available_ops)))
            selected_operators = random.sample(available_ops, num_operators)

        # 确保选中的operators都有对应的描述
        selected_operators = [op for op in selected_operators if op in templates['operator_descriptions']]

        # 3. 动态构建operator描述文档
        dynamic_operator_descriptions = ""
        for op in selected_operators:
            if op in templates['operator_descriptions']:
                dynamic_operator_descriptions += templates['operator_descriptions'][op]
                if op != selected_operators[-1]:  # 不是最后一个就加换行
                    dynamic_operator_descriptions += "\n\n"

        # 4. 构建动态初始化代码
        init_lines = []
        for op in selected_operators:
            if op in templates['operator_inits']:
                init_lines.append(templates['operator_inits'][op])

        # 如果没有初始化代码，添加默认的空缩进
        if init_lines:
            dynamic_init_code = "\n        ".join(init_lines)  # 8 spaces indent
        else:
            # 如果没有任何init代码，保留适当的缩进
            dynamic_init_code = "# Operators initialization"
            logging.warning(f"No operator init codes found for {selected_operators}. Available: {list(templates.get('operator_inits', {}).keys())}")
        
        dynamic_init_code = " "*8 + dynamic_init_code

        # 5. 构建system prompt (填充operators_init)
        system_content = templates['system_prompt_rl_right'].replace('{operators_init}', dynamic_init_code)

        # 6. 构建user prompt（按照新的组装逻辑）
        user_content = (
            templates['task_prompt'] +  # TASK_PROMPT from benchmark's conditions.py
            templates['user_prompt_part_1_rl_right'] +  # USER_PROMPT_PART_1_RL_RIGHT
            dynamic_operator_descriptions +  # 动态构建的operator描述
            templates['user_prompt_part_2_rl_right'].replace('{operators_init}', dynamic_init_code) +  # USER_PROMPT_PART_2_RL_RIGHT
            templates['user_prompt_part_3_rl_right'] +  # USER_PROMPT_PART_3_RL_RIGHT
            problem_text +  # 问题文本
            templates['user_prompt_part_4_rl_right']  # USER_PROMPT_PART_4_RL_RIGHT
        )

        # Build messages in chat format
        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ]

        return messages, problem_text
    
    def _load_jsonl_data(self, filepath: str) -> List[Dict]:
        """Load data from JSONL file"""
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    

    
    def generate_for_benchmark(self, benchmark_name: str,
                              operators_group: List[str] = None,
                              dataset_type: str = 'both',
                              num_train_entries: Optional[int] = None,
                              num_test_entries: Optional[int] = None,
                              num_examples: int = 1,
                              num_train_test_cases: int = 5,
                              num_test_test_cases: int = 5,
                              save_files: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Generate VERL training data for a specific benchmark

        Args:
            benchmark_name: Name of the benchmark
            operators_group: List of operators for this configuration (optional)
            dataset_type: 'train', 'test', or 'both'
            num_train_entries: Number of train entries to generate
            num_test_entries: Number of test entries to generate
            num_examples: Number of problem examples to include in each prompt
            num_train_test_cases: Number of test cases for train entries
            num_test_test_cases: Number of test cases for test entries
            save_files: Whether to save generated data to files (both parquet and jsonl)

        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        # Find matching configuration
        benchmark_info = None
        for config in self.benchmark_mapping_list:
            if config['benchmark'] == benchmark_name:
                # If operators_group is specified, must match exactly
                if operators_group is not None:
                    if config.get('operators_group', []) == operators_group:
                        benchmark_info = config
                        break
                else:
                    # If no operators_group specified, take the first matching benchmark
                    benchmark_info = config
                    break

        if benchmark_info is None:
            raise ValueError(f"Benchmark {benchmark_name} with operators {operators_group} not found in mapping")

        # If operators_group wasn't specified, get it from the matched config
        if operators_group is None:
            operators_group = benchmark_info.get('operators_group', [])

        logging.info(f"Generating data for benchmark: {benchmark_name} with operators: {operators_group}")

        results = {}

        # Process train and/or test datasets
        datasets_to_process = []
        if dataset_type in ['train', 'both'] and 'data_train_dir' in benchmark_info:
            datasets_to_process.append(('train', benchmark_info['data_train_dir'],
                                       num_train_entries, num_train_test_cases))
        if dataset_type in ['test', 'both'] and 'data_test_dir' in benchmark_info:
            datasets_to_process.append(('test', benchmark_info['data_test_dir'],
                                       num_test_entries, num_test_test_cases))

        for dtype, data_path, num_entries, test_cases_per_entry in datasets_to_process:
            full_path = PROJECT_ROOT / data_path
            if not full_path.exists():
                logging.warning(f"Dataset file not found: {full_path}")
                continue
            
            # Load data
            data = self._load_jsonl_data(str(full_path))
            total_size = len(data)
            
            # Always shuffle data for better randomization
            random.shuffle(data)
            logging.info(f"Applied shuffle to {benchmark_name} {dtype} dataset")
            
            # Determine number of entries to generate
            if num_entries is not None:
                entries_to_generate = min(num_entries, total_size)
            else:
                # If not specified, use the max number from benchmark_mapping if available
                max_key = f'data_{dtype}_max_num'
                if max_key in benchmark_info:
                    entries_to_generate = min(benchmark_info[max_key], total_size)
                else:
                    entries_to_generate = total_size
            
            logging.info(f"Generating {entries_to_generate}/{total_size} entries for {benchmark_name} {dtype}")
            
            # Get handler for this benchmark
            handler = self._get_benchmark_handler(benchmark_name, str(full_path))
            
            # Generate entries
            verl_data = []

            for idx in range(entries_to_generate):
                try:
                    # 随机选择num_examples个不同的问题索引作为prompt示例
                    example_indices = random.sample(range(total_size), min(num_examples, total_size))

                    # 第一个索引作为主问题（用于记录raw_data）
                    main_idx = example_indices[0]

                    # Construct prompt using multiple examples
                    messages, _ = self._construct_prompt(
                        handler, example_indices, benchmark_name
                    )
                    
                    # Select random test cases (excluding the example indices)
                    available_indices = [i for i in range(total_size) if i not in example_indices]
                    test_case_indices = random.sample(
                        available_indices,
                        min(test_cases_per_entry, len(available_indices))
                    )

                    # Build VERL record with new fields
                    record = {
                        'data_source': f"workflow_{benchmark_name}",
                        'prompt': messages,  # HuggingFace chat format
                        'ability': 'workflow',
                        'reward_model': {
                            'ground_truth': 'default'  # Fixed as specified
                        },
                        'benchmark': benchmark_name,  # Add benchmark field
                        'operators_group': operators_group,  # Add operators_group field
                        'extra_info': {
                            'raw_data': main_idx,  # First example index as main
                            'example_indices': example_indices,  # All example indices used in prompt
                            'test_cases': list(test_case_indices) if hasattr(test_case_indices, '__iter__') else [test_case_indices],  # Ensure list format
                            'data_path': data_path,  # Original dataset location
                        }
                    }
                    
                    verl_data.append(record)
                    
                except Exception as e:
                    logging.error(f"Error generating entry {idx+1}/{entries_to_generate} for {benchmark_name}: {e}")
                    continue
            
            # Create DataFrame and optionally save
            if verl_data:
                df = pd.DataFrame(verl_data)
                results[dtype] = df
                logging.info(f"Generated {len(df)} entries for {benchmark_name} {dtype}")
                
                # Save files if requested
                if save_files:
                    self.save_dataset(df, dtype, benchmark_name)
        
        return results
    
    def save_dataset(self, df: pd.DataFrame, dtype: str, benchmark_name: str = "mixed") -> None:
        """
        Save dataset in both parquet and jsonl formats
        
        Args:
            df: DataFrame to save
            dtype: Dataset type ('train' or 'test')
            benchmark_name: Benchmark name for file naming
        """
        if benchmark_name == "mixed":
            # For mixed datasets, use simple names
            parquet_file = self.output_dir / f"{dtype}.parquet"
            jsonl_file = self.output_dir / f"{dtype}.jsonl"
        else:
            # For single benchmark, include benchmark name
            parquet_file = self.output_dir / f"{benchmark_name}_{dtype}.parquet"
            jsonl_file = self.output_dir / f"{benchmark_name}_{dtype}.jsonl"
        
        parquet_file.parent.mkdir(parents=True, exist_ok=True)
        jsonl_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as parquet
        df.to_parquet(parquet_file, index=False)
        logging.info(f"✅ 已保存 {benchmark_name}_{dtype} parquet格式: {parquet_file} (共{len(df)}条记录)")
        
        # Save as jsonl
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                json.dump(row.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        logging.info(f"✅ 已保存 {benchmark_name}_{dtype} jsonl格式: {jsonl_file} (共{len(df)}条记录)")
    
    def generate_mixed_dataset(self, benchmarks: List[str],
                              dataset_type: str = 'both',
                              train_num: Optional[int] = None,
                              test_num: Optional[int] = None,
                              num_examples: int = 1,
                              num_train_test_cases: int = 5,
                              num_test_test_cases: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Generate mixed dataset from multiple benchmarks

        Args:
            benchmarks: List of benchmark names
            dataset_type: 'train', 'test', or 'both'
            train_num: Number of train entries per benchmark
            test_num: Number of test entries per benchmark
            num_examples: Number of problem examples in each prompt
            num_train_test_cases: Number of test cases for train entries
            num_test_test_cases: Number of test cases for test entries

        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        all_results = {'train': [], 'test': []}

        # If no benchmarks specified, use all configs from mapping
        if benchmarks is None:
            configs_to_process = self.benchmark_mapping_list
        else:
            # Filter configs for specified benchmarks
            configs_to_process = [c for c in self.benchmark_mapping_list
                                  if c['benchmark'] in benchmarks]

        for config in configs_to_process:
            benchmark_name = config['benchmark']
            operators_group = config.get('operators_group', [])

            logging.info(f"Processing config: {benchmark_name} with operators {operators_group}")

            results = self.generate_for_benchmark(
                benchmark_name,
                operators_group=operators_group,  # Pass the specific operators_group
                dataset_type=dataset_type,
                num_train_entries=train_num,
                num_test_entries=test_num,
                num_examples=num_examples,
                num_train_test_cases=num_train_test_cases,
                num_test_test_cases=num_test_test_cases,
                save_files=False  # Individual saving controlled by save_individual flag
            )

            for dtype, df in results.items():
                all_results[dtype].append(df)
        
        # Combine and shuffle
        final_results = {}
        for dtype in ['train', 'test']:
            if all_results[dtype]:
                combined_df = pd.concat(all_results[dtype], ignore_index=True)
                combined_df = combined_df.sample(frac=1).reset_index(drop=True)  # Shuffle

                # Save both parquet and jsonl formats using unified method
                self.save_dataset(combined_df, dtype, "mixed")
                final_results[dtype] = combined_df
        
        return final_results
    
    def print_statistics(self, df: pd.DataFrame, name: str = "Dataset"):
        """Print statistics for a dataset"""
        logging.info(f"\\n=== {name} Statistics ===")
        logging.info(f"Total entries: {len(df)}")

        # Count by benchmark and operators_group combination
        if 'benchmark' in df.columns and 'operators_group' in df.columns:
            # Create a combined key for grouping
            df['config_key'] = df.apply(
                lambda row: f"{row['benchmark']} with operators: {row.get('operators_group', [])}",
                axis=1
            )
            config_counts = df['config_key'].value_counts()
            logging.info(f"Entries by configuration:")
            for config, count in config_counts.items():
                logging.info(f"  {config}: {count}")
        elif 'data_source' in df.columns:
            # Fallback to data_source if new fields not present
            source_counts = df['data_source'].value_counts()
            logging.info(f"Entries by benchmark:")
            for benchmark, count in source_counts.items():
                logging.info(f"  {benchmark}: {count}")



def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate VERL training data in parquet format')

    # Required parameters
    parser.add_argument('--benchmark-mapping', type=str, required=True,
                       help='Absolute path to benchmark mapping JSONL file')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Absolute path to output directory for parquet and jsonl files')
    parser.add_argument('--train-num', type=int, required=True,
                       help='Number of train entries to generate per benchmark')
    parser.add_argument('--test-num', type=int, required=True,
                       help='Number of test entries to generate per benchmark')

    # Example and test cases parameters
    parser.add_argument('--num-examples', type=int, default=1,
                       help='Number of problem examples to include in each prompt (default: 1)')
    parser.add_argument('--num-train-test-cases', type=int, default=5,
                       help='Number of test cases for each train entry (default: 5)')
    parser.add_argument('--num-test-test-cases', type=int, default=5,
                       help='Number of test cases for each test entry (default: 5)')

    # Optional parameters
    parser.add_argument('--dataset-type', type=str, default='both',
                       choices=['train', 'test', 'both'],
                       help='Which dataset type to generate (default: both)')
    parser.add_argument('--save-individual', action='store_true',
                       help='Also save individual benchmark files (not just mixed)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # First, update benchmark mapping file with actual line counts
    update_script_path = Path(__file__).parent / "update_benchmark_counts.py"
    if update_script_path.exists():
        logging.info(f"📊 更新benchmark映射文件中的数据行数...")
        print("="*80)  # 分隔线
        try:
            # 直接输出到终端，不捕获输出
            result = subprocess.run(
                [sys.executable, str(update_script_path), args.benchmark_mapping],
                check=True
            )
            print("="*80)  # 分隔线
            logging.info("✅ Benchmark映射文件已更新")
        except subprocess.CalledProcessError as e:
            print("="*80)  # 分隔线
            logging.warning(f"⚠️ 更新benchmark映射文件失败: {e}")
            logging.warning("继续使用原有的映射文件...")
        except FileNotFoundError:
            logging.error(f"❌ Python解释器未找到: {sys.executable}")
            logging.warning("跳过更新步骤...")
    else:
        logging.info(f"未找到update_benchmark_counts.py，跳过更新步骤")

    # Initialize generator with benchmark mapping file
    generator = VerlTrainingDataGenerator(
        output_dir=args.output_dir,
        benchmark_mapping_file=args.benchmark_mapping
    )

    # Get all benchmarks from the mapping file (use available_benchmarks from init)
    benchmarks = generator.available_benchmarks
    logging.info(f"Processing benchmarks: {benchmarks}")

    try:
        # Generate individual benchmark files if requested
        if args.save_individual:
            logging.info("🔄 生成单个基准测试文件...")
            # Iterate through all configurations, not just benchmarks
            for config in generator.benchmark_mapping_list:
                benchmark = config['benchmark']
                operators_group = config.get('operators_group', [])

                individual_results = generator.generate_for_benchmark(
                    benchmark,
                    operators_group=operators_group,
                    dataset_type=args.dataset_type,
                    num_train_entries=args.train_num,
                    num_test_entries=args.test_num,
                    num_examples=args.num_examples,
                    num_train_test_cases=args.num_train_test_cases,
                    num_test_test_cases=args.num_test_test_cases,
                    save_files=True  # Save individual files
                )

                operators_str = '_'.join(operators_group) if operators_group else 'default'
                for dtype, df in individual_results.items():
                    generator.print_statistics(df, f"{benchmark}_{operators_str} {dtype} dataset")

        # Always generate mixed dataset (default behavior)
        logging.info("🔄 生成混合数据集...")
        results = generator.generate_mixed_dataset(
            benchmarks=benchmarks,
            dataset_type=args.dataset_type,
            train_num=args.train_num,
            test_num=args.test_num,
            num_examples=args.num_examples,
            num_train_test_cases=args.num_train_test_cases,
            num_test_test_cases=args.num_test_test_cases
        )

        for dtype, df in results.items():
            generator.print_statistics(df, f"Mixed {dtype} dataset")

        logging.info("✅ Data generation completed successfully!")

    except Exception as e:
        logging.error(f"Error during data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

    # Example commands:
    # python generate_verl_training_data.py --benchmark-mapping /Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/ScoreFlow/benchmark_mapping_all.jsonl --output-dir /Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/parquet_and_jsonl_data/0921_RL_001 --train-num 100 --test-num 50 --num-train-test-cases 10 --num-test-test-cases 10
    # python generate_verl_training_data.py --benchmark-mapping /path/to/mapping.jsonl --output-dir /path/to/output --train-num 200 --test-num 100