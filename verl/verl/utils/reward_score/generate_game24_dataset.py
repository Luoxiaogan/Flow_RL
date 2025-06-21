import os
import json
import argparse
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time
import random

# No QwenAPI or evaluator needed in this script anymore as per new requirements.
# from game24_evaluator import QwenAPI 

TRAIN_CASES_FILE_PATH = "game24/dataset/train_cases.json" # Relative to workspace root

def load_train_cases(workspace_root: str):
    """Loads all 24-game training cases."""
    full_path = os.path.join(workspace_root, TRAIN_CASES_FILE_PATH)
    try:
        with open(full_path, "r") as f:
            train_cases = json.load(f)
            if not isinstance(train_cases, list) or not all(isinstance(tc, list) and len(tc) == 4 for tc in train_cases):
                raise ValueError("Train cases must be a list of lists, each containing 4 numbers.")
            if not train_cases:
                raise ValueError("Train cases file is empty.")
            print(f"Successfully loaded {len(train_cases)} training cases from {full_path}")
            return train_cases
    except FileNotFoundError:
        print(f"Error: {full_path} not found. This file is required to select random examples for ground_truth.")
        raise
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {full_path}.")
        raise
    except ValueError as ve:
        print(f"Error in train cases format or content: {ve}")
        raise

# This is the fixed META-PROMPT that will be in every record of the dataset.
# This prompt is intended to instruct an LLM (in a LATER stage) to generate a system prompt for the 24-game.
META_PROMPT_CONTENT = \
"""You are an AI assistant specialized in designing effective prompts for other AI models.
Your current task is to generate a concise and clear SYSTEM PROMPT that will instruct a large language model (LLM) on how to solve the 24 game.

The 24 game rules are:
1. Given four integers.
2. Use each integer exactly once.
3. Combine the integers using basic arithmetic operations: addition (+), subtraction (-), multiplication (*), and division (/).
4. The goal is to reach the number 24.
5. Parentheses can be used to control the order of operations.

The system prompt you generate should:
- Clearly explain these rules to the LLM.
- Instruct the LLM to show its reasoning steps, one step per line.
- Instruct the LLM to output the final mathematical expression on the last line, prefixed with "expression: ". For example, "expression: ((10 + 1) + (12 - 3))".
- Advise the LLM on what to output if no solution is found (e.g., "No solution found.").

Please output ONLY the system prompt text itself, without any of your own commentary, preamble, or follow-up. The output should be ready to be used directly as a system message for another LLM.
"""

def main():  # Removed async since it's not needed
    parser = argparse.ArgumentParser(
        description="Generate a dataset where each record contains the same meta-prompt for 24-game system prompt generation, paired with 5 unique random game inputs from train_cases.json."
    )
    parser.add_argument('--output_dir', type=str, default='./data/game24_meta_prompt_records', 
                        help='Directory to save the output parquet file.')
    parser.add_argument('--num_records_to_create', type=int, default=100, 
                        help='Number of records to create in the dataset (each with the same meta-prompt but different random game inputs).')
    parser.add_argument('--workspace_root', type=str, default=os.getcwd(), 
                        help='The absolute path to the workspace root, used to locate train_cases.json.')
    
    args = parser.parse_args()

    try:
        all_train_cases = load_train_cases(args.workspace_root)
    except Exception as e:
        print(f"Failed to load {TRAIN_CASES_FILE_PATH}: {e}. Exiting.")
        return
    
    if len(all_train_cases) < 5:
        print(f"Error: Not enough training cases in {TRAIN_CASES_FILE_PATH} (found {len(all_train_cases)}, need at least 5) to randomly sample 5 unique cases. Exiting.")
        return
    
    dataset_records = []
    print(f"Starting generation of {args.num_records_to_create} dataset records...")
    generation_start_time = time.time()

    for i in range(args.num_records_to_create):
        # 1. Select 5 unique random game inputs from train_cases.json
        try:
            selected_game_inputs = random.sample(all_train_cases, 5)
        except ValueError:
            # Should not happen due to the check above, but as a safeguard if all_train_cases somehow becomes smaller than 5
            print("Error: Could not sample 5 unique cases. Check train_cases.json. Skipping record.")
            continue

        # 2. Create the dataset record
        # The 'prompt' field contains the fixed META_PROMPT_CONTENT.
        # The 'ground_truth' contains the 5 randomly selected game inputs.
        record = {
            "data_source": "game24_meta_prompt_evaluation_data", # New data source name
            "prompt": [{  # Hugging Face chat template format for the META_PROMPT
                "role": "user", 
                "content": META_PROMPT_CONTENT 
            }],
            "ability": "meta_prompting_for_game24_solver_design", # Ability being assessed (indirectly)
            "reward_model": {
                "style": "random_game_inputs_for_downstream_evaluation",
                "ground_truth": json.dumps(selected_game_inputs) # The 5 inputs for later evaluation
            },
            "extra_info": {
                'split': 'train', # Or your desired split name
                'index': i
            }
        }
        dataset_records.append(record)
    # Convert to Pandas DataFrame
    df = pd.DataFrame(dataset_records)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    output_filename = f'game24_meta_prompt_records_{len(df)}.parquet' # Adjusted filename
    output_file_path = os.path.join(args.output_dir, output_filename)

    if not df.empty:
        try:
            table = pa.Table.from_pandas(df)
            pq.write_table(table, output_file_path)
            print(f"Dataset successfully generated and saved to {output_file_path}")
            print(f"Number of records: {len(df)}")
            if not df.empty:
                 print("Sample record from the dataset (first record shown):")
                 sample_record = df.iloc[0].to_dict()
                 print(f"  data_source: {sample_record.get('data_source')}")
                 # Displaying a snippet of the meta-prompt for brevity
                 meta_prompt_snippet = sample_record.get('prompt')[0]['content'][:150] + "..."
                 print(f"  prompt (meta-prompt snippet): {meta_prompt_snippet}")
                 print(f"  ability: {sample_record.get('ability')}")
                 reward_model_sample = sample_record.get('reward_model', {})
                 print(f"  reward_model_style: {reward_model_sample.get('style')}")
                 print(f"  reward_model_ground_truth (5 random game inputs): {reward_model_sample.get('ground_truth')}")
                 print(f"  extra_info: {sample_record.get('extra_info')}")
        except Exception as e:
            print(f"Error saving dataset to Parquet: {e}")
    else:
        print("No data was generated, Parquet file not saved.")

if __name__ == '__main__':
    # Example: 
    # python verl/verl/utils/reward_score/generate_game24_dataset.py --num_records_to_create 100 --output_dir ./game24_meta_prompt_records --workspace_root .
    main()  # Direct call without asyncio.run() 