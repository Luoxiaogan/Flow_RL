"""
Generate IMO training data in VERL format
Specialized script for International Mathematical Olympiad problems
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

class IMOTrainingDataGenerator:
    """Generate training data for IMO problems"""

    def __init__(self, data_file: str = None, output_dir: str = None):
        """
        Initialize the IMO data generator

        Args:
            data_file: Path to IMO jsonl data file
            output_dir: Directory to save generated parquet files
        """
        self.data_file = Path(data_file) if data_file else PROJECT_ROOT / "Processed_dataset" / "imo_test.jsonl"
        self.output_dir = Path(output_dir) if output_dir else CURRENT_DIR / "imo_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load IMO data
        self.imo_data = self._load_imo_data()
        logging.info(f"Loaded {len(self.imo_data)} IMO problems")

    def _load_imo_data(self) -> List[Dict]:
        """Load IMO problems from jsonl file"""
        data = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data

    def _create_prompt(self, problem_indices: List[int]) -> str:
        """
        Create a workflow generation prompt for selected IMO problems

        Args:
            problem_indices: Indices of problems to include (0-based)
        """
        # Get selected problems
        selected_problems = [self.imo_data[i] for i in problem_indices]

        # Format problems for prompt
        problem_texts = []
        for problem in selected_problems:
            problem_text = f"""---
**QUESTION:**
{problem['question']}
---"""
            problem_texts.append(problem_text)

        # Combine into full prompt
        problems_section = "\n\n".join(problem_texts)

        # Create the system message and user message
        system_message = """You are an expert System Architect specializing in designing universal workflow solutions for International Mathematical Olympiad (IMO) problems. Your task is to create a generalizable Python workflow that can solve ALL IMO-level problems, not just individual examples.

You will receive:
1. IMO problem characteristics and requirements
2. 1-3 concrete IMO problem examples
3. Available operators including Verifier and Refiner for rigorous mathematical validation
4. Output requirements for complete mathematical solutions with proofs

Your goal: Design a robust workflow that handles the entire IMO problem class with mathematical rigor."""

        user_message = f"""### Problem Domain: International Mathematical Olympiad (IMO)

IMO tests the highest level of mathematical problem-solving capabilities, requiring creative insights and rigorous proofs.

### Example Problems:
{problems_section}

### Available Operators:
- Generate: Create new mathematical analysis or solutions
- Summarize: Compress information while preserving key mathematical insights
- Ensemble: Evaluate and synthesize multiple solution approaches
- Verifier: Rigorously verify solutions using IMO-level standards
- Refiner: Improve solutions based on verification feedback

### Requirements:
Create a workflow that:
1. Explores multiple solution strategies in parallel
2. Uses Verifier to ensure mathematical rigor
3. Employs Refiner to address any identified issues
4. Produces complete solutions with full proofs and justifications

Design your workflow to handle ANY IMO problem with the same level of rigor and creativity."""

        return system_message, user_message

    def generate_training_data(self, num_samples: int = 100, problems_per_sample: int = 2):
        """
        Generate training data samples

        Args:
            num_samples: Number of training samples to generate
            problems_per_sample: Number of problems to include in each sample
        """
        training_data = []

        for sample_id in range(num_samples):
            # Randomly select problems for this sample
            problem_indices = random.sample(range(len(self.imo_data)),
                                          min(problems_per_sample, len(self.imo_data)))

            # Create prompt
            system_msg, user_msg = self._create_prompt(problem_indices)

            # Create VERL format entry
            entry = {
                "data_source": "imo",
                "prompt": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                "ability": "mathematical_reasoning",
                "reward_model": {
                    "ground_truth": problem_indices
                },
                "extra_info": {
                    "sample_id": sample_id,
                    "num_problems": len(problem_indices),
                    "problem_indices": problem_indices,
                    "problem_ids": [self.imo_data[i]["task_id"] for i in problem_indices]
                }
            }

            training_data.append(entry)

        # Convert to DataFrame and save as parquet
        df = pd.DataFrame(training_data)
        output_file = self.output_dir / f"imo_training_data_{num_samples}samples.parquet"
        df.to_parquet(output_file, engine='pyarrow')

        logging.info(f"Generated {num_samples} training samples")
        logging.info(f"Saved to {output_file}")

        return df

    def generate_test_data(self, num_samples: int = 20, problems_per_sample: int = 1):
        """
        Generate test data samples (smaller set for validation)

        Args:
            num_samples: Number of test samples to generate
            problems_per_sample: Number of problems to include in each sample
        """
        test_data = []

        # Use different random seed for test data
        random.seed(42)

        for sample_id in range(num_samples):
            # Select problems for test
            problem_indices = random.sample(range(len(self.imo_data)),
                                          min(problems_per_sample, len(self.imo_data)))

            # Create prompt
            system_msg, user_msg = self._create_prompt(problem_indices)

            # Create VERL format entry
            entry = {
                "data_source": "imo",
                "prompt": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                "ability": "mathematical_reasoning",
                "reward_model": {
                    "ground_truth": problem_indices
                },
                "extra_info": {
                    "sample_id": sample_id,
                    "num_problems": len(problem_indices),
                    "problem_indices": problem_indices,
                    "problem_ids": [self.imo_data[i]["task_id"] for i in problem_indices],
                    "split": "test"
                }
            }

            test_data.append(entry)

        # Convert to DataFrame and save as parquet
        df = pd.DataFrame(test_data)
        output_file = self.output_dir / f"imo_test_data_{num_samples}samples.parquet"
        df.to_parquet(output_file, engine='pyarrow')

        logging.info(f"Generated {num_samples} test samples")
        logging.info(f"Saved to {output_file}")

        return df

    def create_combined_dataset(self):
        """Create a combined train/test dataset with proper split"""
        # Generate training data
        train_df = self.generate_training_data(num_samples=50, problems_per_sample=2)

        # Generate test data
        test_df = self.generate_test_data(num_samples=10, problems_per_sample=1)

        # Add split column
        train_df['split'] = 'train'
        test_df['split'] = 'test'

        # Combine
        combined_df = pd.concat([train_df, test_df], ignore_index=True)

        # Save combined dataset
        output_file = self.output_dir / "imo_combined_dataset.parquet"
        combined_df.to_parquet(output_file, engine='pyarrow')

        logging.info(f"Created combined dataset with {len(train_df)} train and {len(test_df)} test samples")
        logging.info(f"Saved to {output_file}")

        # Also save as JSONL for readability
        jsonl_file = self.output_dir / "imo_combined_dataset.jsonl"
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for _, row in combined_df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')

        logging.info(f"Also saved as JSONL: {jsonl_file}")

        return combined_df

def main():
    """Main function to generate IMO training data"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate IMO training data in VERL format')
    parser.add_argument('--data_file', type=str, help='Path to IMO jsonl data file')
    parser.add_argument('--output_dir', type=str, help='Output directory for parquet files')
    parser.add_argument('--num_train', type=int, default=50, help='Number of training samples')
    parser.add_argument('--num_test', type=int, default=10, help='Number of test samples')
    parser.add_argument('--combined', action='store_true', help='Create combined dataset')

    args = parser.parse_args()

    # Initialize generator
    generator = IMOTrainingDataGenerator(
        data_file=args.data_file,
        output_dir=args.output_dir
    )

    if args.combined:
        # Create combined dataset
        generator.create_combined_dataset()
    else:
        # Generate training and test data separately
        generator.generate_training_data(num_samples=args.num_train)
        generator.generate_test_data(num_samples=args.num_test)

    logging.info("IMO training data generation completed!")

if __name__ == "__main__":
    main()