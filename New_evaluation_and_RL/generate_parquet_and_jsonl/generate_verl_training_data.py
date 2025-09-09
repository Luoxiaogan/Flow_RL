"""
VERL Training Data Generator - Generate training datasets in parquet format
This script generates training data for VERL from various benchmarks.
"""

import os
import sys
import json
import logging
import argparse
import random
import pandas as pd
import numpy as np
import yaml
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
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the generator
        
        Args:
            output_dir: Directory to save generated parquet files
        """
        self.output_dir = Path(output_dir) if output_dir else CURRENT_DIR / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load benchmark mapping
        self.benchmark_mapping = self._load_benchmark_mapping()
        
        logging.info(f"VerlTrainingDataGenerator initialized with output dir: {self.output_dir}")
        logging.info(f"Available benchmarks: {list(self.benchmark_mapping.keys())}")
    
    def _load_benchmark_mapping(self) -> Dict[str, Dict]:
        """Load benchmark mapping from jsonl file"""
        # Try to get mapping file path from config, fallback to default
        mapping_file_path = None
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            # Get project_root from config
            project_root = config.get('project_root', str(PROJECT_ROOT))
            project_root_path = Path(project_root)
            
            # Get benchmark_mapping relative path and build full path
            benchmark_mapping_rel = config.get('paths', {}).get('benchmark_mapping', 'ScoreFlow/benchmark_mapping.jsonl')
            mapping_file_path = str(project_root_path / benchmark_mapping_rel)
        
        if not mapping_file_path:
            # Fallback to default path
            mapping_file_path = PROJECT_ROOT / "ScoreFlow" / "benchmark_mapping.jsonl"
        else:
            mapping_file_path = Path(mapping_file_path)
    
        
        mapping = {}
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    benchmark = data['benchmark']
                    mapping[benchmark] = data
        
        return mapping
    
    def _get_benchmark_handler(self, benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
        """Get handler for a specific benchmark"""
        try:
            # Check benchmark mapping first
            benchmark_info = self.benchmark_mapping.get(benchmark_name)
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
            # Check benchmark mapping first
            benchmark_info = self.benchmark_mapping.get(benchmark_name)
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
            available_operators = ['ScGenerate', 'ScRevise', 'ScEnsemble', 'ScSummarize', 'ScProgrammer', 'ScDecompose']
            
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
                'ScDecompose': 'decompose'
            }
            
            for op_class in available_operators:
                if op_class in operator_key_map:
                    key = operator_key_map[op_class]
                    # Get description from common conditions (directly using the key name)
                    # Note: in conditions.py, 'programmer' description is stored as 'programm'
                    desc_key = key if key != 'programmer' else 'programm'
                    operator_descriptions[key] = getattr(common_conditions, desc_key, "")
                    
                    # Get init code from common conditions
                    init_key = f"{key}_init" if key != 'programmer' else "programm_init"  # Special case
                    operator_inits[key] = getattr(common_conditions, init_key, "")
            
            # Load all required prompt components
            return {
                'system_prompt': getattr(conditions_module, "SYSTEM_PROMPT", "You are a helpful AI assistant."),
                'task_prompt': getattr(conditions_module, "TASK_PROMPT", ""),
                'operator_prompt_part_1': getattr(conditions_module, "OPERATOR_PROMPT_PART_1", ""),
                'operator_prompt_part_2': getattr(conditions_module, "OPERATOR_PROMPT_PART_2", ""),
                'user_prompt_long': getattr(conditions_module, "USER_PROMPT_LONG", ""),
                'user_prompt_short': getattr(common_conditions, "USER_PROMPT_SHORT", ""),
                'operator_prompt_simple_start': getattr(common_conditions, "OPERATOR_PROMPT_SIMPLE_START", ""),
                'available_operators': available_operators,
                'operator_descriptions': operator_descriptions,
                'operator_inits': operator_inits
            }
        except Exception as e:
            logging.error(f"Failed to load prompt templates for {benchmark_name}: {e}")
            raise
    
    def _construct_prompt(self, handler: BenchmarkHandler, data_indices: List[int], 
                         benchmark_name: str) -> Tuple[List[Dict], str]:
        """Construct prompt messages in HuggingFace chat format (simplified version)
        
        Args:
            handler: Benchmark handler instance
            data_indices: Indices of problems to include
            benchmark_name: Name of the benchmark
        """
        # Load all prompt components
        templates = self._load_prompt_templates(benchmark_name)
        
        # 1. 使用 handler 获取问题文本
        problem_text = handler.get_prompt_text(data_indices)
        
        # 2. 根据benchmark配置选择operators组
        import random
        benchmark_info = self.benchmark_mapping.get(benchmark_name, {})
        operators_groups = benchmark_info.get('operators_groups', [])
        
        if operators_groups:
            # 根据比例随机选择一个operators组
            rand_value = random.random()
            cumulative_prop = 0
            selected_operators = None
            
            for group in operators_groups:
                cumulative_prop += group['proportion']
                if rand_value < cumulative_prop:
                    selected_operators = group['operators']
                    break
            
            # 如果没选中（不应该发生），使用第一组
            if selected_operators is None:
                selected_operators = operators_groups[0]['operators']
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
        
        # 3. 动态构建operator文档
        dynamic_operator_prompt = templates.get('operator_prompt_simple_start', '')
        for op in selected_operators:
            if op in templates['operator_descriptions']:
                dynamic_operator_prompt += "\n\n" + templates['operator_descriptions'][op]
        
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
        
        # 5. 使用简化版 USER_PROMPT_SHORT
        user_prompt = templates.get('user_prompt_short', '')
        user_prompt_with_operators = user_prompt.replace('{operators_init}', dynamic_init_code)
        
        # 6. 构建简化版的SFT instruction（不包含OPERATOR_PROMPT_PART_2）
        sft_instruction = (
            templates['task_prompt'] + 
            "\n Problem Examples:\n" + problem_text + "\n\n" + 
            dynamic_operator_prompt + "\n\n" +  # 使用动态构建的operator文档，不包含PART_2
            user_prompt_with_operators +  # 使用简化版模板
            "\n\n### 6. Your Response\nNow, provide the complete and optimized Python workflow code and thinking based on all the specifications above:"
        )
        
        # Build messages in chat format
        messages = [
            {'role': 'system', 'content': templates['system_prompt']},
            {'role': 'user', 'content': sft_instruction}
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
                              dataset_type: str = 'both',
                              num_train_entries: Optional[int] = None,
                              num_test_entries: Optional[int] = None,
                              train_proportion: Optional[float] = None,
                              test_proportion: Optional[float] = None,
                              test_cases_per_entry: int = 5,
                              save_files: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Generate VERL training data for a specific benchmark
        
        Args:
            benchmark_name: Name of the benchmark
            dataset_type: 'train', 'test', or 'both'
            num_train_entries: Specific number of train entries to generate
            num_test_entries: Specific number of test entries to generate
            train_proportion: Proportion of train dataset to use (0.0 to 1.0)
            test_proportion: Proportion of test dataset to use (0.0 to 1.0)
            test_cases_per_entry: Number of test cases to include for each entry
            save_files: Whether to save generated data to files (both parquet and jsonl)
            
        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        if benchmark_name not in self.benchmark_mapping:
            raise ValueError(f"Benchmark {benchmark_name} not found in mapping")
        
        benchmark_info = self.benchmark_mapping[benchmark_name]
        logging.info(f"Generating data for benchmark: {benchmark_name}")
        
        results = {}
        
        # Process train and/or test datasets
        datasets_to_process = []
        if dataset_type in ['train', 'both'] and 'data_train_dir' in benchmark_info:
            datasets_to_process.append(('train', benchmark_info['data_train_dir'], 
                                       num_train_entries, train_proportion))
        if dataset_type in ['test', 'both'] and 'data_test_dir' in benchmark_info:
            datasets_to_process.append(('test', benchmark_info['data_test_dir'],
                                       num_test_entries, test_proportion))
        
        for dtype, data_path, num_entries, proportion in datasets_to_process:
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
            
            # Determine number of entries to generate for this specific dataset type
            if num_entries is not None:
                entries_to_generate = min(num_entries, total_size)
            elif proportion is not None:
                entries_to_generate = int(total_size * proportion)
            else:
                entries_to_generate = total_size
            
            logging.info(f"Generating {entries_to_generate}/{total_size} entries for {benchmark_name} {dtype}")
            
            # Get handler for this benchmark
            handler = self._get_benchmark_handler(benchmark_name, str(full_path))
            
            # Generate entries
            verl_data = []
            indices_used = random.sample(range(total_size), entries_to_generate)
            
            for idx in indices_used:
                try:
                    # Use single index for prompt generation (can be extended to multiple)
                    data_indices = [idx]
                    # 从数据集中随机选择一个问题作为主问题
                    # Construct prompt (using simplified version)
                    messages, problem_text = self._construct_prompt(handler, data_indices, benchmark_name)
                    
                    # Get answer from original data
                    original_answer = data[idx].get('answer', '')
                    
                    # Select random test cases (excluding current index)
                    available_indices = [i for i in range(total_size) if i != idx]
                    test_case_indices = random.sample(
                        available_indices, 
                        min(test_cases_per_entry, len(available_indices))
                    )
                    
                    # Build VERL record
                    record = {
                        'data_source': f"workflow_{benchmark_name}",
                        'prompt': messages,  # HuggingFace chat format
                        'ability': 'workflow',
                        'reward_model': {
                            'ground_truth': 'default'  # Fixed as specified
                        },
                        'extra_info': {
                            # 'answer': original_answer,  # Removed as requested
                            'raw_data': idx,  # Original row number
                            'test_cases': list(test_case_indices) if hasattr(test_case_indices, '__iter__') else [test_case_indices],  # Ensure list format (not numpy array)
                            'data_path': data_path,  # Original dataset location
                        }
                    }
                    
                    verl_data.append(record)
                    
                except Exception as e:
                    logging.error(f"Error generating entry {idx} for {benchmark_name}: {e}")
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
                              total_train_entries: Optional[int] = None,
                              total_test_entries: Optional[int] = None,
                              train_entries_per_benchmark: Optional[int] = None,
                              test_entries_per_benchmark: Optional[int] = None,
                              train_proportion: Optional[float] = None,
                              test_proportion: Optional[float] = None,
                              test_cases_per_entry: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Generate mixed dataset from multiple benchmarks
        
        Args:
            benchmarks: List of benchmark names
            dataset_type: 'train', 'test', or 'both'
            total_train_entries: Total number of train entries across all benchmarks
            total_test_entries: Total number of test entries across all benchmarks
            train_entries_per_benchmark: Number of train entries per benchmark
            test_entries_per_benchmark: Number of test entries per benchmark
            train_proportion: Proportion of each benchmark's train data to use
            test_proportion: Proportion of each benchmark's test data to use
            test_cases_per_entry: Number of test cases to include for each entry
            
        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        all_results = {'train': [], 'test': []}
        
        # Calculate entries per benchmark if total is specified
        if total_train_entries is not None:
            train_entries_per_benchmark = total_train_entries // len(benchmarks)
        if total_test_entries is not None:
            test_entries_per_benchmark = total_test_entries // len(benchmarks)
        
        for benchmark in benchmarks:
            if benchmark not in self.benchmark_mapping:
                logging.warning(f"Skipping unknown benchmark: {benchmark}")
                continue
            
            results = self.generate_for_benchmark(
                benchmark, 
                dataset_type=dataset_type,
                num_train_entries=train_entries_per_benchmark,
                num_test_entries=test_entries_per_benchmark,
                train_proportion=train_proportion,
                test_proportion=test_proportion,
                test_cases_per_entry=test_cases_per_entry,
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
        
        # Count by data source
        if 'data_source' in df.columns:
            source_counts = df['data_source'].value_counts()
            logging.info(f"Entries by benchmark:")
            for benchmark, count in source_counts.items():
                logging.info(f"  {benchmark}: {count}")



def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate VERL training data in parquet format')
    
    # Benchmark selection
    parser.add_argument('--benchmarks', type=str, nargs='+', 
                       help='Benchmark names (space-separated). Use "all" for all benchmarks')
    parser.add_argument('--dataset-type', type=str, default='both',
                       choices=['train', 'test', 'both'],
                       help='Which dataset type to generate')
    
    # Entry count/proportion options
    parser.add_argument('--num-train-entries', type=int,
                       help='Number of train entries to generate per benchmark')
    parser.add_argument('--num-test-entries', type=int,
                       help='Number of test entries to generate per benchmark')
    parser.add_argument('--total-train-entries', type=int,
                       help='Total number of train entries for mixed dataset (divided among benchmarks)')
    parser.add_argument('--total-test-entries', type=int,
                       help='Total number of test entries for mixed dataset (divided among benchmarks)')
    parser.add_argument('--train-proportion', type=float,
                       help='Proportion of train dataset to use (0.0 to 1.0)')
    parser.add_argument('--test-proportion', type=float,
                       help='Proportion of test dataset to use (0.0 to 1.0)')
    
    # Other options
    parser.add_argument('--test-cases-per-entry', type=int, default=5,
                       help='Number of test cases per entry (default: 5)')
    parser.add_argument('--output-dir', type=str, default='data',
                       help='Output directory for parquet and jsonl files')
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
    
    # Initialize generator
    generator = VerlTrainingDataGenerator(output_dir=args.output_dir)
    
    # Get benchmarks to process
    if args.benchmarks:
        if args.benchmarks == ['all']:
            benchmarks = list(generator.benchmark_mapping.keys())
        else:
            benchmarks = args.benchmarks
    else:
        logging.error("No benchmarks specified. Use --benchmarks option.")
        return
    
    logging.info(f"Processing benchmarks: {benchmarks}")
    
    try:
        # Generate individual benchmark files if requested
        if args.save_individual:
            logging.info("🔄 生成单个基准测试文件...")
            for benchmark in benchmarks:
                if benchmark not in generator.benchmark_mapping:
                    logging.warning(f"跳过未知基准测试: {benchmark}")
                    continue
                
                individual_results = generator.generate_for_benchmark(
                    benchmark,
                    dataset_type=args.dataset_type,
                    num_train_entries=args.num_train_entries,
                    num_test_entries=args.num_test_entries,
                    train_proportion=args.train_proportion,
                    test_proportion=args.test_proportion,
                    test_cases_per_entry=args.test_cases_per_entry,
                    save_files=True  # Save individual files
                )
                
                for dtype, df in individual_results.items():
                    generator.print_statistics(df, f"{benchmark} {dtype} dataset")
        
        # Always generate mixed dataset (default behavior)
        logging.info("🔄 生成混合数据集...")
        results = generator.generate_mixed_dataset(
            benchmarks=benchmarks,
            dataset_type=args.dataset_type,
            total_train_entries=args.total_train_entries,
            total_test_entries=args.total_test_entries,
            train_entries_per_benchmark=args.num_train_entries,
            test_entries_per_benchmark=args.num_test_entries,
            train_proportion=args.train_proportion,
            test_proportion=args.test_proportion,
            test_cases_per_entry=args.test_cases_per_entry
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

    # python generate_verl_training_data.py --num-train-entries 3 --num-test-entries 0 --output-dir test_scoreflow_data --benchmarks all --test-cases-per-entry 3