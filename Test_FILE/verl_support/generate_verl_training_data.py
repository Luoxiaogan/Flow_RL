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
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import importlib

# Add project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
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
        mapping_file = PROJECT_ROOT / "ScoreFlow" / "benchmark_mapping.jsonl"
        if not mapping_file.exists():
            raise FileNotFoundError(f"Benchmark mapping file not found: {mapping_file}")
        
        mapping = {}
        with open(mapping_file, 'r', encoding='utf-8') as f:
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
                # Convert handler_dir to Python module path (e.g., "ScoreFlow/scripts/gsm8k" -> "ScoreFlow.scripts.gsm8k")
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
    
    def _load_prompt_templates(self, benchmark_name: str) -> Tuple[str, str, str, List[str]]:
        """Load prompt templates from conditions.py"""
        try:
            # Check benchmark mapping first
            benchmark_info = self.benchmark_mapping.get(benchmark_name)
            if benchmark_info:
                handler_dir = benchmark_info['handler_dir']
                # Convert handler_dir to Python module path
                conditions_path = handler_dir.replace('/', '.') + '.conditions'
            else:
                # Fallback to default naming rules
                if benchmark_name.startswith("high_level_math"):
                    conditions_path = "ScoreFlow.scripts.high_level_math.conditions"
                else:
                    conditions_path = f"ScoreFlow.scripts.{benchmark_name}.conditions"
            
            # Import conditions module
            conditions_module = importlib.import_module(conditions_path)
            
            return (
                getattr(conditions_module, "START_PROMPT", ""), 
                getattr(conditions_module, "SYSTEM_PROMPT", "You are a helpful AI assistant."),
                getattr(conditions_module, "TASK_PROMPT", [])
            )
        except Exception as e:
            logging.error(f"Failed to load prompt templates for {benchmark_name}: {e}")
            raise
    
    def _construct_prompt(self, handler: BenchmarkHandler, data_indices: List[int], 
                         benchmark_name: str) -> Tuple[List[Dict], str]:
        """Construct prompt messages in HuggingFace chat format"""
        start_prompt, system_prompt, task_prompt = self._load_prompt_templates(benchmark_name)
        
        # 1. 使用 handler 获取问题文本
        problem_text = handler.get_prompt_text(data_indices)
        
        # Build instruction (clean version for SFT)
        instruction = task_prompt + start_prompt + problem_text + "\n\n### 6. Your Response\nNow, provide the complete and optimized Python workflow graph and thinking based on all the specifications above:"
        
        # Build messages in chat format
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': instruction}
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
                              test_cases_per_entry: int = 5) -> Dict[str, pd.DataFrame]:
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
            
        Returns:
            Dictionary with 'train' and/or 'test' DataFrames (not saved to files)
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
                    
                    # Construct prompt
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
                            'answer': original_answer,
                            'raw_data': idx,  # Original row number
                            'test_cases': test_case_indices,  # Random test case indices
                            'data_path': data_path,  # Original dataset location
                        }
                    }
                    
                    verl_data.append(record)
                    
                except Exception as e:
                    logging.error(f"Error generating entry {idx} for {benchmark_name}: {e}")
                    continue
            
            # Return DataFrame without saving
            if verl_data:
                df = pd.DataFrame(verl_data)
                results[dtype] = df
                logging.info(f"Generated {len(df)} entries for {benchmark_name} {dtype}")
        
        return results
    
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
                test_cases_per_entry=test_cases_per_entry
            )
            
            for dtype, df in results.items():
                all_results[dtype].append(df)
        
        # Combine and shuffle
        final_results = {}
        for dtype in ['train', 'test']:
            if all_results[dtype]:
                combined_df = pd.concat(all_results[dtype], ignore_index=True)
                combined_df = combined_df.sample(frac=1).reset_index(drop=True)  # Shuffle
                
                output_file = self.output_dir / f"{dtype}.parquet"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                combined_df.to_parquet(output_file, index=False)
                logging.info(f"Saved {dtype} dataset with {len(combined_df)} entries to {output_file}")
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
                       help='Output directory for parquet files')
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
        # Always generate mixed dataset (default behavior)
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

    # python generate_verl_training_data.py --num-train-entries 0 --num-test-entries 10 --output-dir data/test_new --benchmarks all --test-cases-per-entry 10