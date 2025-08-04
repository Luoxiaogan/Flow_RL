import json
import pandas as pd

# Read the CSV file
csv_file = "/Users/luogan/Code/workflow_generation/Flow_RL/workspace_drop/execution_results.csv"
df = pd.read_csv(csv_file)

# Filter rows where Status is 'verified_correct'
correct_ids = set(df[df['Status'] == 'verified_correct']['ID'].tolist())

# Read JSONL file and filter
jsonl_file = "/Users/luogan/Code/workflow_generation/Flow_RL/workspace_drop/training_data_drop.jsonl"
output_file = "/Users/luogan/Code/workflow_generation/Flow_RL/workspace_drop/correct.jsonl"

with open(jsonl_file, 'r', encoding='utf-8') as infile, \
    open(output_file, 'w', encoding='utf-8') as outfile:
    
    for line in infile:
       data = json.loads(line.strip())
       workflow_id = data.get('workflow_id', '')
       
       # Check if workflow_id is in the correct_ids set
       if workflow_id in correct_ids:
          outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

print(f"Filtered data saved to {output_file}")