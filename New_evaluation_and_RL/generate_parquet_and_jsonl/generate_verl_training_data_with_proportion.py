# python generate_verl_training_data_with_proportion.py --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test.jsonl --output-dir ./proportion_data_0923 --train-num 1 --test-num 20 

# python generate_verl_training_data_with_proportion.py --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test_code.jsonl --output-dir ./proportion_data_code_0924 --train-num 1 --test-num 20 

# python generate_verl_training_data_with_proportion.py --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test_code_self_consistency.jsonl --output-dir ./proportion_data_code_0924_consistency --train-num 1 --test-num 20 


"""
VERL Training Data Generator with Proportion Support
支持operators_groups和proportion比例分配的VERL训练数据生成器

This script extends the original generate_verl_training_data.py to support:
1. New format with operators_groups and proportion fields
2. Strict proportion-based data allocation
3. Backward compatibility with the old format

Usage Examples:
==============
1. Use benchmark_mapping_test.jsonl with proportion support:
   python generate_verl_training_data_with_proportion.py \
       --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test.jsonl \
       --output-dir ./proportion_data \
       --train-num 1000 \
       --test-num 200

2. Generate with specific benchmarks:
   python generate_verl_training_data_with_proportion.py \
       --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test.jsonl \
       --output-dir ./proportion_data \
       --benchmarks gsm8k mbpp \
       --train-num 500 \
       --test-num 100

3. Save individual benchmark files:
   python generate_verl_training_data_with_proportion.py \
       --benchmark-mapping ../../ScoreFlow/benchmark_mapping_test.jsonl \
       --output-dir ./proportion_data \
       --train-num 1000 \
       --test-num 200 \
       --save-individual
"""

import sys
import json
import logging
import argparse
import random
import pandas as pd
import yaml
import subprocess
import math
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import importlib
from collections import defaultdict

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


class VerlTrainingDataGeneratorWithProportion:
    """Generate VERL training data with proportion-based operator allocation"""

    def __init__(self, output_dir: str = None, benchmark_mapping_file: str = None):
        """
        Initialize the generator with proportion support

        Args:
            output_dir: Directory to save generated parquet files
            benchmark_mapping_file: Path to benchmark mapping JSONL file
        """
        self.output_dir = Path(output_dir) if output_dir else CURRENT_DIR / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load and expand benchmark mapping
        self.benchmark_configs = self._load_and_expand_benchmark_mapping(benchmark_mapping_file)

        # Create lookup structures
        self._create_lookup_structures()

        logging.info(f"VerlTrainingDataGeneratorWithProportion initialized")
        logging.info(f"Output directory: {self.output_dir}")
        logging.info(f"Total expanded configurations: {len(self.benchmark_configs)}")
        self._print_config_summary()

    def _load_and_expand_benchmark_mapping(self, benchmark_mapping_file: str = None) -> List[Dict]:
        """
        Load benchmark mapping and expand operators_groups into individual configs

        Args:
            benchmark_mapping_file: Path to benchmark mapping file

        Returns:
            List of expanded benchmark configurations
        """
        # Determine mapping file path
        if benchmark_mapping_file:
            mapping_file_path = Path(benchmark_mapping_file)
            logging.info(f"Using benchmark mapping from command line: {mapping_file_path}")
        elif CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            project_root = config.get('project_root', str(PROJECT_ROOT))
            project_root_path = Path(project_root)
            benchmark_mapping_rel = config.get('paths', {}).get('benchmark_mapping', 'ScoreFlow/benchmark_mapping.jsonl')
            mapping_file_path = project_root_path / benchmark_mapping_rel
            logging.info(f"Using benchmark mapping from config: {mapping_file_path}")
        else:
            mapping_file_path = PROJECT_ROOT / "ScoreFlow" / "benchmark_mapping.jsonl"
            logging.info(f"Using default benchmark mapping: {mapping_file_path}")

        # Load and expand configurations
        expanded_configs = []

        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)

                    # Check if this is the new format with operators_groups
                    if 'operators_groups' in data:
                        # New format: expand each operator group into a separate config
                        base_config = {k: v for k, v in data.items() if k != 'operators_groups'}

                        for group in data['operators_groups']:
                            config = base_config.copy()
                            config['operators_group'] = group['operators']
                            config['proportion'] = group.get('proportion', 1.0)
                            config['original_benchmark'] = data['benchmark']
                            expanded_configs.append(config)
                    else:
                        # Old format: use as is with default proportion
                        data['proportion'] = 1.0
                        data['original_benchmark'] = data['benchmark']
                        expanded_configs.append(data)

        return expanded_configs

    def _create_lookup_structures(self):
        """Create lookup structures for efficient access"""
        # Group configs by benchmark
        self.configs_by_benchmark = defaultdict(list)
        for config in self.benchmark_configs:
            benchmark = config['original_benchmark']
            self.configs_by_benchmark[benchmark].append(config)

        # Get unique benchmark names
        self.available_benchmarks = list(self.configs_by_benchmark.keys())

        # Validate proportions for each benchmark
        for benchmark, configs in self.configs_by_benchmark.items():
            total_proportion = sum(c.get('proportion', 1.0) for c in configs)
            if abs(total_proportion - 1.0) > 0.001:  # Allow small floating point errors
                logging.warning(f"Benchmark {benchmark} has total proportion {total_proportion:.3f} (expected 1.0)")

    def _print_config_summary(self):
        """Print summary of loaded configurations"""
        logging.info("\n=== Configuration Summary ===")
        for benchmark in self.available_benchmarks:
            configs = self.configs_by_benchmark[benchmark]
            logging.info(f"\nBenchmark: {benchmark}")
            for i, config in enumerate(configs, 1):
                operators = config.get('operators_group', [])
                proportion = config.get('proportion', 1.0)
                logging.info(f"  Config {i}: {len(operators)} operators, proportion={proportion:.2%}")
                logging.info(f"    Operators: {operators}")

    def _get_benchmark_handler(self, benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
        """Get handler for a specific benchmark"""
        try:
            # Get first config for this benchmark (they all share the same handler info)
            configs = self.configs_by_benchmark[benchmark_name]
            if not configs:
                raise ValueError(f"No configuration found for benchmark {benchmark_name}")

            benchmark_info = configs[0]

            # Use mapping info for handler class name and path
            handler_class_name = benchmark_info['handler_class']
            handler_dir = benchmark_info['handler_dir']

            # Convert handler_dir to Python module path
            scoreflow_root = None
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                project_root = config.get('project_root', str(PROJECT_ROOT))
                project_root_path = Path(project_root)
                scoreflow_handlers = config.get('paths', {}).get('scoreflow_handlers', '.')
                if scoreflow_handlers == '.':
                    scoreflow_root = str(project_root_path)
                else:
                    scoreflow_root = str(project_root_path / scoreflow_handlers)
            else:
                scoreflow_root = str(PROJECT_ROOT)

            # Extract relative path from handler_dir
            if handler_dir.startswith(scoreflow_root):
                relative_path = handler_dir[len(scoreflow_root):].lstrip('/')
                handler_module_path = relative_path.replace('/', '.') + '.handler'
            else:
                if handler_dir.startswith('/'):
                    scoreflow_index = handler_dir.find('ScoreFlow')
                    if scoreflow_index != -1:
                        relative_path = handler_dir[scoreflow_index:]
                        handler_module_path = relative_path.replace('/', '.') + '.handler'
                    else:
                        raise ValueError(f"Cannot find ScoreFlow in handler_dir: {handler_dir}")
                else:
                    handler_module_path = handler_dir.replace('/', '.') + '.handler'

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
            # Get first config for handler info
            configs = self.configs_by_benchmark[benchmark_name]
            if not configs:
                raise ValueError(f"No configuration found for benchmark {benchmark_name}")

            benchmark_info = configs[0]
            handler_dir = benchmark_info['handler_dir']

            # Convert handler_dir to Python module path
            scoreflow_root = None
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                project_root = config.get('project_root', str(PROJECT_ROOT))
                project_root_path = Path(project_root)
                scoreflow_handlers = config.get('paths', {}).get('scoreflow_handlers', '.')
                if scoreflow_handlers == '.':
                    scoreflow_root = str(project_root_path)
                else:
                    scoreflow_root = str(project_root_path / scoreflow_handlers)
            else:
                scoreflow_root = str(PROJECT_ROOT)

            # Extract relative path from handler_dir
            if handler_dir.startswith(scoreflow_root):
                relative_path = handler_dir[len(scoreflow_root):].lstrip('/')
                conditions_path = relative_path.replace('/', '.') + '.conditions'
            else:
                if handler_dir.startswith('/'):
                    scoreflow_index = handler_dir.find('ScoreFlow')
                    if scoreflow_index != -1:
                        relative_path = handler_dir[scoreflow_index:]
                        conditions_path = relative_path.replace('/', '.') + '.conditions'
                    else:
                        raise ValueError(f"Cannot find ScoreFlow in handler_dir: {handler_dir}")
                else:
                    conditions_path = handler_dir.replace('/', '.') + '.conditions'

            # Import conditions module
            conditions_module = importlib.import_module(conditions_path)

            # Also load common conditions for shared components
            common_conditions = importlib.import_module("ScoreFlow.scripts.common.conditions")

            # Available operators
            available_operators = [
                'ScGenerate', 'ScRevise', 'ScEnsemble', 'ScSummarize',
                'ScProgrammer', 'ScDecompose', 'ScVerifyAndRefine', 'ScSelfConsistency'
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
                'ScSelfConsistency': 'selfconsistency'
            }

            for op_class in available_operators:
                if op_class in operator_key_map:
                    key = operator_key_map[op_class]
                    operator_descriptions[key] = getattr(common_conditions, key, "")
                    init_key = f"{key}_init" if key != 'programmer' else "programmer_init"
                    operator_inits[key] = getattr(common_conditions, init_key, "")

            # Load all required prompt components
            task_prompt = getattr(conditions_module, "TASK_PROMPT", "")

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
                         operators_group: List[str], benchmark_name: str) -> Tuple[List[Dict], str]:
        """
        Construct prompt messages with specific operators

        Args:
            handler: Benchmark handler instance
            data_indices: List of indices of problems to include as examples
            operators_group: Specific list of operators to use
            benchmark_name: Name of the benchmark
        """
        # Load all prompt components
        templates = self._load_prompt_templates(benchmark_name)

        # Get problem text
        problem_text = handler.get_prompt_text_example(data_indices)

        # Use the specific operators provided
        selected_operators = operators_group

        # Ensure selected operators have descriptions
        selected_operators = [op for op in selected_operators if op in templates['operator_descriptions']]

        # Build operator descriptions
        dynamic_operator_descriptions = ""
        for op in selected_operators:
            if op in templates['operator_descriptions']:
                dynamic_operator_descriptions += templates['operator_descriptions'][op]
                if op != selected_operators[-1]:
                    dynamic_operator_descriptions += "\n\n"

        # Build initialization code
        init_lines = []
        for op in selected_operators:
            if op in templates['operator_inits']:
                init_lines.append(templates['operator_inits'][op])

        if init_lines:
            dynamic_init_code = "\n        ".join(init_lines)  # 8 spaces indent
        else:
            dynamic_init_code = "# Operators initialization"
            logging.warning(f"No operator init codes found for {selected_operators}")

        dynamic_init_code = " "*8 + dynamic_init_code

        # Build system prompt
        system_content = templates['system_prompt_rl_right'].replace('{operators_init}', dynamic_init_code)

        add_fix = "\nThe domain problem instances example above is for helping you to understand to domain. Your generated Python workflow must be robust enough to work for any problem instance within the described domain.\n"

        # Build user prompt
        user_content = (
            templates['task_prompt'] +
            templates['user_prompt_part_1_rl_right'] +
            dynamic_operator_descriptions +
            templates['user_prompt_part_2_rl_right'].replace('{operators_init}', dynamic_init_code) +
            templates['user_prompt_part_3_rl_right'] +
            problem_text +
            add_fix +
            templates['user_prompt_part_4_rl_right']
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

    def generate_for_benchmark_with_proportions(self, benchmark_name: str,
                                               dataset_type: str = 'both',
                                               num_train_entries: Optional[int] = None,
                                               num_test_entries: Optional[int] = None,
                                               num_examples: int = 1,
                                               num_train_test_cases: int = 5,
                                               num_test_test_cases: int = 5,
                                               save_files: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Generate VERL training data with proportion-based allocation

        Args:
            benchmark_name: Name of the benchmark
            dataset_type: 'train', 'test', or 'both'
            num_train_entries: Total number of train entries to generate
            num_test_entries: Total number of test entries to generate
            num_examples: Number of problem examples to include in each prompt
            num_train_test_cases: Number of test cases for train entries
            num_test_test_cases: Number of test cases for test entries
            save_files: Whether to save generated data to files

        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        configs = self.configs_by_benchmark.get(benchmark_name, [])
        if not configs:
            logging.error(f"No configurations found for benchmark {benchmark_name}")
            return {}

        logging.info(f"\n=== Generating data for {benchmark_name} ===")
        logging.info(f"Found {len(configs)} operator configurations")

        results = {'train': [], 'test': []}

        # Process train and/or test datasets
        datasets_to_process = []
        if dataset_type in ['train', 'both'] and 'data_train_dir' in configs[0]:
            datasets_to_process.append(('train', configs[0]['data_train_dir'],
                                       num_train_entries, num_train_test_cases))
        if dataset_type in ['test', 'both'] and 'data_test_dir' in configs[0]:
            datasets_to_process.append(('test', configs[0]['data_test_dir'],
                                       num_test_entries, num_test_test_cases))

        for dtype, data_path, total_entries, test_cases_per_entry in datasets_to_process:
            full_path = PROJECT_ROOT / data_path
            if not full_path.exists():
                logging.warning(f"Dataset file not found: {full_path}")
                continue

            # Load data
            data = self._load_jsonl_data(str(full_path))
            total_data_size = len(data)

            # Shuffle data for randomization
            random.shuffle(data)

            # Determine total entries to generate
            if total_entries is not None:
                entries_to_generate = min(total_entries, total_data_size)
            else:
                max_key = f'data_{dtype}_max_num'
                if max_key in configs[0]:
                    entries_to_generate = min(configs[0][max_key], total_data_size)
                else:
                    entries_to_generate = total_data_size

            logging.info(f"\n{dtype.upper()} dataset: {entries_to_generate} total entries")

            # Get handler
            handler = self._get_benchmark_handler(benchmark_name, str(full_path))

            # Calculate entries per configuration based on proportion
            entries_per_config = []
            remaining_entries = entries_to_generate

            for i, config in enumerate(configs):
                proportion = config.get('proportion', 1.0)

                if i == len(configs) - 1:
                    # Last config gets all remaining entries to handle rounding
                    config_entries = remaining_entries
                else:
                    # Calculate proportional entries
                    config_entries = int(entries_to_generate * proportion)
                    remaining_entries -= config_entries

                entries_per_config.append(config_entries)

                operators = config.get('operators_group', [])
                logging.info(f"  Config {i+1}: {config_entries} entries ({proportion:.1%}), "
                           f"operators={operators}")

            # Generate data for each configuration
            for config_idx, (config, num_entries_for_config) in enumerate(zip(configs, entries_per_config)):
                if num_entries_for_config == 0:
                    continue

                operators_group = config.get('operators_group', [])

                logging.info(f"\nGenerating {num_entries_for_config} entries for config {config_idx+1}")

                config_data = []
                for entry_idx in range(num_entries_for_config):
                    try:
                        # Select random examples for prompt
                        example_indices = random.sample(range(total_data_size),
                                                       min(num_examples, total_data_size))
                        main_idx = example_indices[0]
                        # main_idx = random.sample(range(total_data_size), min(3, total_data_size)) # 2个

                        # Construct prompt with specific operators
                        messages, _ = self._construct_prompt(
                            handler, example_indices, operators_group, benchmark_name
                        )

                        # Select test cases
                        available_indices = [i for i in range(total_data_size) if i not in example_indices]
                        test_case_indices = random.sample(
                            available_indices,
                            min(test_cases_per_entry, len(available_indices))
                        )

                        # Build VERL record
                        record = {
                            'data_source': f"workflow_{benchmark_name}",
                            'prompt': messages,
                            'ability': 'workflow',
                            'reward_model': {
                                'ground_truth': 'default'
                            },
                            'benchmark': benchmark_name,
                            'operators_group': operators_group,
                            'operators_config_idx': config_idx,  # Track which config was used
                            'proportion': config.get('proportion', 1.0),
                            'extra_info': {
                                'raw_data': main_idx,
                                'example_indices': example_indices,
                                'test_cases': list(test_case_indices),
                                'data_path': data_path,
                            }
                        }

                        config_data.append(record)

                    except Exception as e:
                        logging.error(f"Error generating entry: {e}")
                        continue

                if config_data:
                    results[dtype].extend(config_data)
                    logging.info(f"  Generated {len(config_data)} entries successfully")

        # Create final DataFrames
        final_results = {}
        for dtype in ['train', 'test']:
            if results[dtype]:
                df = pd.DataFrame(results[dtype])
                # Shuffle again to mix different configs
                df = df.sample(frac=1).reset_index(drop=True)
                final_results[dtype] = df

                logging.info(f"\n{dtype.upper()} total: {len(df)} entries")

                # Print distribution statistics
                if 'operators_config_idx' in df.columns:
                    config_dist = df['operators_config_idx'].value_counts().sort_index()
                    logging.info(f"{dtype.upper()} distribution by config:")
                    for idx, count in config_dist.items():
                        proportion = count / len(df)
                        expected_proportion = configs[idx].get('proportion', 1.0)
                        logging.info(f"  Config {idx+1}: {count} entries ({proportion:.1%}, "
                                   f"expected {expected_proportion:.1%})")

                if save_files:
                    self.save_dataset(df, dtype, benchmark_name)

        return final_results

    def save_dataset(self, df: pd.DataFrame, dtype: str, benchmark_name: str = "mixed") -> None:
        """Save dataset in both parquet and jsonl formats"""
        if benchmark_name == "mixed":
            parquet_file = self.output_dir / f"{dtype}.parquet"
            jsonl_file = self.output_dir / f"{dtype}.jsonl"
        else:
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

    def generate_mixed_dataset_with_proportions(self, benchmarks: Optional[List[str]] = None,
                                               dataset_type: str = 'both',
                                               train_num: Optional[int] = None,
                                               test_num: Optional[int] = None,
                                               num_examples: int = 1,
                                               num_train_test_cases: int = 5,
                                               num_test_test_cases: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Generate mixed dataset from multiple benchmarks with proportion support

        Args:
            benchmarks: List of benchmark names (None for all)
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

        # If no benchmarks specified, use all available
        if benchmarks is None:
            benchmarks = self.available_benchmarks

        logging.info(f"\n=== Generating mixed dataset ===")
        logging.info(f"Benchmarks: {benchmarks}")

        for benchmark in benchmarks:
            if benchmark not in self.available_benchmarks:
                logging.warning(f"Benchmark {benchmark} not found in mapping, skipping")
                continue

            results = self.generate_for_benchmark_with_proportions(
                benchmark,
                dataset_type=dataset_type,
                num_train_entries=train_num,
                num_test_entries=test_num,
                num_examples=num_examples,
                num_train_test_cases=num_train_test_cases,
                num_test_test_cases=num_test_test_cases,
                save_files=False
            )

            for dtype, df in results.items():
                if not df.empty:
                    all_results[dtype].append(df)

        # Combine and shuffle
        final_results = {}
        for dtype in ['train', 'test']:
            if all_results[dtype]:
                combined_df = pd.concat(all_results[dtype], ignore_index=True)
                combined_df = combined_df.sample(frac=1).reset_index(drop=True)

                # Save both formats
                self.save_dataset(combined_df, dtype, "mixed")
                final_results[dtype] = combined_df

                # Print final statistics
                self.print_statistics(combined_df, f"Mixed {dtype} dataset")

        return final_results

    def print_statistics(self, df: pd.DataFrame, name: str = "Dataset"):
        """Print detailed statistics for a dataset with proportion information"""
        logging.info(f"\n=== {name} Statistics ===")
        logging.info(f"Total entries: {len(df)}")

        if 'benchmark' in df.columns:
            # Statistics by benchmark
            benchmark_counts = df['benchmark'].value_counts()
            logging.info(f"\nEntries by benchmark:")
            for benchmark, count in benchmark_counts.items():
                logging.info(f"  {benchmark}: {count} ({count/len(df):.1%})")

                # Detailed operator group distribution for this benchmark
                benchmark_df = df[df['benchmark'] == benchmark]
                if 'operators_group' in benchmark_df.columns:
                    # Create readable operator group strings
                    operator_strings = benchmark_df['operators_group'].apply(
                        lambda x: ', '.join(x) if isinstance(x, list) else str(x)
                    )
                    operator_dist = operator_strings.value_counts()

                    logging.info(f"\n  Operator group distribution for {benchmark}:")
                    for operators, op_count in operator_dist.items():
                        proportion = op_count / len(benchmark_df)
                        logging.info(f"    [{operators}]: {op_count} ({proportion:.1%})")

        if 'proportion' in df.columns:
            # Verify proportion accuracy
            logging.info(f"\nProportion verification:")
            unique_proportions = df['proportion'].unique()
            for prop in sorted(unique_proportions):
                count = len(df[df['proportion'] == prop])
                actual_prop = count / len(df)
                logging.info(f"  Expected {prop:.1%}: {count} entries (actual {actual_prop:.1%})")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate VERL training data with proportion-based operator allocation'
    )

    # Required parameters
    parser.add_argument('--benchmark-mapping', type=str, required=True,
                       help='Path to benchmark mapping JSONL file (supports new format with operators_groups)')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for parquet and jsonl files')
    parser.add_argument('--train-num', type=int, required=True,
                       help='Total number of train entries per benchmark')
    parser.add_argument('--test-num', type=int, required=True,
                       help='Total number of test entries per benchmark')

    # Optional parameters
    parser.add_argument('--benchmarks', type=str, nargs='+',
                       help='Specific benchmarks to process (default: all)')
    parser.add_argument('--num-examples', type=int, default=1,
                       help='Number of problem examples per prompt (default: 1)')
    parser.add_argument('--num-train-test-cases', type=int, default=5,
                       help='Number of test cases for train entries (default: 5)')
    parser.add_argument('--num-test-test-cases', type=int, default=5,
                       help='Number of test cases for test entries (default: 5)')
    parser.add_argument('--dataset-type', type=str, default='both',
                       choices=['train', 'test', 'both'],
                       help='Which dataset type to generate (default: both)')
    parser.add_argument('--save-individual', action='store_true',
                       help='Also save individual benchmark files')
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

    # Update benchmark counts if update script exists
    update_script_path = Path(__file__).parent / "update_benchmark_counts.py"
    if update_script_path.exists():
        logging.info(f"📊 更新benchmark映射文件中的数据行数...")
        print("="*80)
        try:
            result = subprocess.run(
                [sys.executable, str(update_script_path), args.benchmark_mapping],
                check=True
            )
            print("="*80)
            logging.info("✅ Benchmark映射文件已更新")
        except subprocess.CalledProcessError as e:
            print("="*80)
            logging.warning(f"⚠️ 更新benchmark映射文件失败: {e}")
            logging.warning("继续使用原有的映射文件...")

    # Initialize generator
    generator = VerlTrainingDataGeneratorWithProportion(
        output_dir=args.output_dir,
        benchmark_mapping_file=args.benchmark_mapping
    )

    # Select benchmarks
    benchmarks = args.benchmarks if args.benchmarks else generator.available_benchmarks

    try:
        # Generate individual benchmark files if requested
        if args.save_individual:
            logging.info("🔄 生成单个基准测试文件...")
            for benchmark in benchmarks:
                individual_results = generator.generate_for_benchmark_with_proportions(
                    benchmark,
                    dataset_type=args.dataset_type,
                    num_train_entries=args.train_num,
                    num_test_entries=args.test_num,
                    num_examples=args.num_examples,
                    num_train_test_cases=args.num_train_test_cases,
                    num_test_test_cases=args.num_test_test_cases,
                    save_files=True
                )

                for dtype, df in individual_results.items():
                    if not df.empty:
                        generator.print_statistics(df, f"{benchmark} {dtype} dataset")

        # Always generate mixed dataset
        logging.info("🔄 生成混合数据集...")
        results = generator.generate_mixed_dataset_with_proportions(
            benchmarks=benchmarks,
            dataset_type=args.dataset_type,
            train_num=args.train_num,
            test_num=args.test_num,
            num_examples=args.num_examples,
            num_train_test_cases=args.num_train_test_cases,
            num_test_test_cases=args.num_test_test_cases
        )

        logging.info("\n✅ Data generation completed successfully!")

    except Exception as e:
        logging.error(f"Error during data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()