"""
IMO Training Data Generator - Generate training datasets in parquet format with RL_RIGHT prompt format
This script generates training data for IMO problems using the same prompt format as generate_verl_training_data.py
"""

import sys
import json
import logging
import argparse
import random
import pandas as pd
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import importlib

# Add project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# Add necessary paths to sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ScoreFlow"))
sys.path.insert(0, str(PROJECT_ROOT / "ScoreFlow" / "scripts"))

# Import base handler
from ScoreFlow.scripts.base_handler import BenchmarkHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration file path
CONFIG_FILE = PROJECT_ROOT / "New_evaluation_and_RL" / "config.yaml"


class IMOTrainingDataGenerator:
    """Generate IMO training data with RL_RIGHT prompt format"""

    def __init__(self, output_dir: str = None):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save generated parquet files
        """
        self.output_dir = Path(output_dir) if output_dir else CURRENT_DIR / "imo_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Define IMO benchmark configuration
        self.benchmark_info = {
            'benchmark': 'imo',
            'handler_class': 'ImoHandler',
            'handler_dir': 'ScoreFlow/scripts/imo',
            'data_train_dir': 'Processed_dataset/imo_test.jsonl',
            'data_test_dir': 'Processed_dataset/imo_test.jsonl',
            'operators_group': ['generate', 'ensemble', 'verifier', 'refiner']  # IMO-specific operators
        }

        self.benchmark_name = 'imo'

        logging.info(f"IMOTrainingDataGenerator initialized with output dir: {self.output_dir}")
        logging.info(f"Using operators: {self.benchmark_info['operators_group']}")

    def _get_benchmark_handler(self, dataset_path: str) -> BenchmarkHandler:
        """Get handler for IMO benchmark"""
        try:
            handler_class_name = self.benchmark_info['handler_class']
            handler_dir = self.benchmark_info['handler_dir']

            # Import the handler module
            handler_module_path = f"ScoreFlow.scripts.imo.handler"
            handler_module = importlib.import_module(handler_module_path)

            # Get the handler class
            handler_class = getattr(handler_module, handler_class_name)

            # Create and return handler instance
            return handler_class(dataset_path=dataset_path)
        except Exception as e:
            logging.error(f"Failed to load IMO handler: {e}")
            raise

    def _load_prompt_templates(self) -> Dict[str, Any]:
        """Load prompt templates from conditions.py and related modules"""
        try:
            # Load IMO-specific conditions
            imo_conditions = importlib.import_module("ScoreFlow.scripts.imo.conditions")

            # Load common conditions for RL_RIGHT components
            common_conditions = importlib.import_module("ScoreFlow.scripts.common.conditions")

            # IMO uses specific operators
            imo_operators = ['generate', 'ensemble', 'verifier', 'refiner']

            # Load operator descriptions and init codes
            operator_descriptions = {}
            operator_inits = {}

            # Map operator names to their descriptions and inits
            for op in imo_operators:
                if op == 'generate':
                    operator_descriptions[op] = getattr(common_conditions, "generate", "")
                    operator_inits[op] = getattr(common_conditions, "generate_init", "")
                elif op == 'ensemble':
                    operator_descriptions[op] = getattr(common_conditions, "ensemble", "")
                    operator_inits[op] = getattr(common_conditions, "ensemble_init", "")
                elif op == 'verifier':
                    # Verifier is IMO-specific, get from IMO conditions if available
                    operator_descriptions[op] = """**Verifier: VALIDATE mathematical rigor**
- **Signature:** `await self.verifier(instruction: str = "", context: str = "") -> Dict[str, Any]`
- **Purpose:** Performs rigorous mathematical verification of solutions, checking logical correctness, proof validity, and completeness
- **Returns:** Dictionary with 'verdict' (valid/invalid/partial) and 'findings' (detailed analysis)
- **Use Cases:** Validating proof steps, checking mathematical rigor, identifying logical gaps"""
                    operator_inits[op] = "self.verifier = operator.Verifier(self.llm, self.problem_text)"
                elif op == 'refiner':
                    # Refiner is IMO-specific
                    operator_descriptions[op] = """**Refiner: IMPROVE based on feedback**
- **Signature:** `await self.refiner(instruction: str = "", context: str = "", verification_feedback: str = "") -> Dict[str, str]`
- **Purpose:** Iteratively improves solutions based on verification feedback, addressing logical gaps and strengthening proofs
- **Parameters:** Takes original solution context and verification feedback
- **Returns:** Dictionary with 'analysis' (improvement strategy) and 'refined_solution' (enhanced solution)
- **Use Cases:** Fixing identified errors, filling proof gaps, enhancing mathematical rigor"""
                    operator_inits[op] = "self.refiner = operator.Refiner(self.llm, self.problem_text)"

            # Get TASK_PROMPT from IMO conditions
            task_prompt = getattr(imo_conditions, "TASK_PROMPT", "")

            # Get RL_RIGHT components from common conditions
            return {
                'task_prompt': task_prompt,
                'system_prompt_rl_right': getattr(common_conditions, "SYSTEM_PROMPT_RL_RIGHT", "You are a helpful AI assistant."),
                'user_prompt_part_1_rl_right': getattr(common_conditions, "USER_PROMPT_PART_1_RL_RIGHT", ""),
                'user_prompt_part_2_rl_right': getattr(common_conditions, "USER_PROMPT_PART_2_RL_RIGHT", ""),
                'user_prompt_part_3_rl_right': getattr(common_conditions, "USER_PROMPT_PART_3_RL_RIGHT", ""),
                'user_prompt_part_4_rl_right': getattr(common_conditions, "USER_PROMPT_PART_4_RL_RIGHT", ""),
                'available_operators': imo_operators,
                'operator_descriptions': operator_descriptions,
                'operator_inits': operator_inits
            }
        except Exception as e:
            logging.error(f"Failed to load prompt templates for IMO: {e}")
            raise

    def _construct_prompt(self, handler: BenchmarkHandler, data_indices: List[int]) -> Tuple[List[Dict], str]:
        """Construct prompt messages in HuggingFace chat format (RL_RIGHT version)

        Args:
            handler: Benchmark handler instance
            data_indices: List of indices of problems to include as examples
        """
        # Load all prompt components
        templates = self._load_prompt_templates()

        # 1. Use handler to get problem text (pass multiple indices)
        problem_text = handler.get_prompt_text_example(data_indices)

        # 2. Use IMO-specific operators
        selected_operators = self.benchmark_info['operators_group']

        # 3. Dynamically build operator descriptions
        dynamic_operator_descriptions = ""
        for op in selected_operators:
            if op in templates['operator_descriptions']:
                dynamic_operator_descriptions += templates['operator_descriptions'][op]
                if op != selected_operators[-1]:  # Not the last one
                    dynamic_operator_descriptions += "\n\n"

        # 4. Build dynamic initialization code
        init_lines = []
        for op in selected_operators:
            if op in templates['operator_inits']:
                init_lines.append(templates['operator_inits'][op])

        if init_lines:
            dynamic_init_code = "\n        ".join(init_lines)  # 8 spaces indent
        else:
            dynamic_init_code = "# Operators initialization"
            logging.warning(f"No operator init codes found for {selected_operators}")

        dynamic_init_code = " " * 8 + dynamic_init_code

        # 5. Build system prompt (fill in operators_init)
        system_content = templates['system_prompt_rl_right'].replace('{operators_init}', dynamic_init_code)

        # 6. Build user prompt (follow the new assembly logic)
        user_content = (
            templates['task_prompt'] +  # TASK_PROMPT from IMO's conditions.py
            templates['user_prompt_part_1_rl_right'] +  # USER_PROMPT_PART_1_RL_RIGHT
            dynamic_operator_descriptions +  # Dynamically built operator descriptions
            templates['user_prompt_part_2_rl_right'].replace('{operators_init}', dynamic_init_code) +  # USER_PROMPT_PART_2_RL_RIGHT
            templates['user_prompt_part_3_rl_right'] +  # USER_PROMPT_PART_3_RL_RIGHT
            problem_text +  # Problem text
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

    def generate_dataset(self, dataset_type: str = 'both',
                        num_train_entries: Optional[int] = None,
                        num_test_entries: Optional[int] = None,
                        num_examples: int = 1,
                        num_train_test_cases: int = 5,
                        num_test_test_cases: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Generate IMO training data in VERL format

        Args:
            dataset_type: 'train', 'test', or 'both'
            num_train_entries: Number of train entries to generate
            num_test_entries: Number of test entries to generate
            num_examples: Number of problem examples to include in each prompt
            num_train_test_cases: Number of test cases for train entries
            num_test_test_cases: Number of test cases for test entries

        Returns:
            Dictionary with 'train' and/or 'test' DataFrames
        """
        results = {}

        # Load IMO data
        data_path = PROJECT_ROOT / self.benchmark_info['data_train_dir']
        if not data_path.exists():
            logging.warning(f"Dataset file not found: {data_path}")
            return results

        data = self._load_jsonl_data(str(data_path))
        total_size = len(data)

        # Get handler for IMO
        handler = self._get_benchmark_handler(str(data_path))

        # Process train and/or test datasets
        datasets_to_process = []
        if dataset_type in ['train', 'both']:
            datasets_to_process.append(('train', num_train_entries or 50, num_train_test_cases))
        if dataset_type in ['test', 'both']:
            datasets_to_process.append(('test', num_test_entries or 10, num_test_test_cases))

        for dtype, num_entries, test_cases_per_entry in datasets_to_process:
            # Shuffle data for better randomization
            random.shuffle(data)
            logging.info(f"Applied shuffle to IMO {dtype} dataset")

            entries_to_generate = min(num_entries, total_size)
            logging.info(f"Generating {entries_to_generate}/{total_size} entries for IMO {dtype}")

            # Generate entries
            verl_data = []

            for idx in range(entries_to_generate):
                try:
                    # Randomly select num_examples different problem indices as prompt examples
                    example_indices = random.sample(range(total_size), min(num_examples, total_size))

                    # First index as main problem (for recording raw_data)
                    main_idx = example_indices[0]

                    # Construct prompt using multiple examples
                    messages, _ = self._construct_prompt(handler, example_indices)

                    # Select random test cases (excluding the example indices)
                    available_indices = [i for i in range(total_size) if i not in example_indices]
                    test_case_indices = random.sample(
                        available_indices,
                        min(test_cases_per_entry, len(available_indices))
                    )

                    # Build VERL record with new fields
                    record = {
                        'data_source': f"workflow_{self.benchmark_name}",
                        'prompt': messages,  # HuggingFace chat format
                        'ability': 'workflow',
                        'reward_model': {
                            'ground_truth': 'default'  # Fixed as specified
                        },
                        'benchmark': self.benchmark_name,  # Add benchmark field
                        'operators_group': self.benchmark_info['operators_group'],  # Add operators_group field
                        'extra_info': {
                            'raw_data': main_idx,  # First example index as main
                            'example_indices': example_indices,  # All example indices used in prompt
                            'test_cases': list(test_case_indices),  # Ensure list format
                            'data_path': self.benchmark_info['data_train_dir'],  # Original dataset location
                        }
                    }

                    verl_data.append(record)

                except Exception as e:
                    logging.error(f"Error generating entry {idx+1}/{entries_to_generate} for IMO: {e}")
                    continue

            # Create DataFrame
            if verl_data:
                df = pd.DataFrame(verl_data)
                results[dtype] = df
                logging.info(f"Generated {len(df)} entries for IMO {dtype}")

                # Save both parquet and jsonl formats
                self.save_dataset(df, dtype)

        return results

    def save_dataset(self, df: pd.DataFrame, dtype: str):
        """Save dataset in both parquet and jsonl formats"""
        # Save parquet format
        parquet_file = self.output_dir / f"imo_{dtype}.parquet"
        df.to_parquet(parquet_file, engine='pyarrow')
        logging.info(f"✅ 已保存 IMO {dtype} parquet格式: {parquet_file} (共{len(df)}条记录)")

        # Save jsonl format
        jsonl_file = self.output_dir / f"imo_{dtype}.jsonl"
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                json.dump(row.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        logging.info(f"✅ 已保存 IMO {dtype} jsonl格式: {jsonl_file} (共{len(df)}条记录)")

    def create_combined_dataset(self):
        """Create a combined train/test dataset"""
        # Generate training data
        train_results = self.generate_dataset(
            dataset_type='train',
            num_train_entries=50,
            num_examples=2,
            num_train_test_cases=5
        )

        # Generate test data
        test_results = self.generate_dataset(
            dataset_type='test',
            num_test_entries=10,
            num_examples=1,
            num_test_test_cases=5
        )

        # Combine if both exist
        if 'train' in train_results and 'test' in test_results:
            train_df = train_results['train']
            test_df = test_results['test']

            # Add split column
            train_df['split'] = 'train'
            test_df['split'] = 'test'

            # Combine
            combined_df = pd.concat([train_df, test_df], ignore_index=True)

            # Save combined dataset
            output_file = self.output_dir / "imo_combined.parquet"
            combined_df.to_parquet(output_file, engine='pyarrow')

            logging.info(f"Created combined dataset with {len(train_df)} train and {len(test_df)} test samples")
            logging.info(f"Saved to {output_file}")

            # Also save as JSONL
            jsonl_file = self.output_dir / "imo_combined.jsonl"
            with open(jsonl_file, 'w', encoding='utf-8') as f:
                for _, row in combined_df.iterrows():
                    f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')

            logging.info(f"Also saved as JSONL: {jsonl_file}")

            return combined_df

        return None

    def print_statistics(self, df: pd.DataFrame, name: str = "Dataset"):
        """Print statistics for a dataset"""
        logging.info(f"\n=== {name} Statistics ===")
        logging.info(f"Total entries: {len(df)}")

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


def main():
    """Main function to generate IMO training data"""
    parser = argparse.ArgumentParser(description='Generate IMO training data in VERL format with RL_RIGHT prompts')
    parser.add_argument('--output_dir', type=str, help='Output directory for parquet files')
    parser.add_argument('--num_train', type=int, default=50, help='Number of training samples')
    parser.add_argument('--num_test', type=int, default=10, help='Number of test samples')
    parser.add_argument('--num_examples', type=int, default=2, help='Number of problem examples in each prompt')
    parser.add_argument('--num_train_test_cases', type=int, default=5, help='Number of test cases for train entries')
    parser.add_argument('--num_test_test_cases', type=int, default=5, help='Number of test cases for test entries')
    parser.add_argument('--combined', action='store_true', help='Create combined dataset')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Initialize generator
    generator = IMOTrainingDataGenerator(output_dir=args.output_dir)

    if args.combined:
        # Create combined dataset
        combined_df = generator.create_combined_dataset()
        if combined_df is not None:
            generator.print_statistics(combined_df, "IMO Combined")
    else:
        # Generate training and test data separately
        results = generator.generate_dataset(
            dataset_type='both',
            num_train_entries=args.num_train,
            num_test_entries=args.num_test,
            num_examples=args.num_examples,
            num_train_test_cases=args.num_train_test_cases,
            num_test_test_cases=args.num_test_test_cases
        )

        for dtype, df in results.items():
            generator.print_statistics(df, f"IMO {dtype}")

    logging.info("✅ IMO training data generation completed!")


if __name__ == "__main__":
    main()