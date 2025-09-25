import json

def filter_jsonl_by_data_source(input_file_path, output_file_path, keyword):
    """
    Reads a JSONL file, filters lines based on a keyword in the 'data_source' field,
    and saves the result to a new JSONL file.

    Args:
        input_file_path (str): The path to the input JSONL file.
        output_file_path (str): The path to the output JSONL file.
        keyword (str): The keyword to search for in the 'data_source' field.
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                try:
                    # Parse the JSON object from the line
                    data = json.loads(line)
                    
                    # Check if 'data_source' field exists and contains the keyword
                    if 'data_source' in data and keyword in data.get('data_source', '') and 'plus' not in data.get('data_source', ''):
                        # Write the original line to the output file
                        outfile.write(line)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Specify the input and output file paths
input_file = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/proportion_data_0923/test_with_responses_rollout=1.jsonl'
output_file = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/proportion_data_0923/test_with_responses_rollout=1_MBPP.jsonl'
filter_keyword = 'mbpp'

# Run the filtering function
filter_jsonl_by_data_source(input_file, output_file, filter_keyword)

print(f"Filtering complete. Filtered data saved to {output_file}")