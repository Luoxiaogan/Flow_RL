#!/usr/bin/env python3
"""
Filter JSONL records based on CSV status criteria.
Matches records between JSONL and CSV files and filters based on status.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of records."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_csv_filter(filepath: str, csv_key: str, csv_target_key: str, want_info: str) -> set:
    """Load CSV and return set of IDs that match the filter criteria."""
    matching_ids = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get(csv_target_key) == want_info:
                matching_ids.add(row[csv_key])
    return matching_ids


def filter_jsonl_records(
    jsonl_records: List[Dict[str, Any]], 
    matching_ids: set, 
    jsonl_key: str
) -> List[Dict[str, Any]]:
    """Filter JSONL records based on matching IDs."""
    filtered = []
    for record in jsonl_records:
        if str(record.get(jsonl_key)) in matching_ids:
            filtered.append(record)
    return filtered


def save_jsonl(records: List[Dict[str, Any]], filepath: str):
    """Save records to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    # Configuration (hardcoded)
    jsonl_path = '/Users/luogan/Code/workflow_generation/Flow_RL/training_data/workspace_mbpp_COT_qwen_max/training_data_mbpp.jsonl'
    csv_path = '/Users/luogan/Code/workflow_generation/Flow_RL/training_data/workspace_mbpp_COT_qwen_max/execution_results.csv'
    csv_key = 'ID'
    jsonl_key = 'workflow_id'
    csv_target_key = 'Status'
    want_info = 'verified_correct'
    output_dir = '/Users/luogan/Code/workflow_generation/Flow_RL/training_data/workspace_mbpp_COT_qwen_max'
    output_filename = 'filtered_training_data.jsonl'
    
    # Load JSONL records
    print(f"Loading JSONL from: {jsonl_path}")
    jsonl_records = load_jsonl(jsonl_path)
    print(f"Loaded {len(jsonl_records)} records from JSONL")
    
    # Load CSV and get matching IDs
    print(f"Loading CSV from: {csv_path}")
    print(f"Filtering for {csv_target_key} = {want_info}")
    matching_ids = load_csv_filter(csv_path, csv_key, csv_target_key, want_info)
    print(f"Found {len(matching_ids)} records with {csv_target_key} = {want_info}")
    
    # Filter JSONL records
    filtered_records = filter_jsonl_records(jsonl_records, matching_ids, jsonl_key)
    print(f"Filtered to {len(filtered_records)} JSONL records")
    
    # Save filtered records
    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(filtered_records, str(output_path))
    print(f"Saved filtered records to: {output_path}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Input JSONL records: {len(jsonl_records)}")
    print(f"  CSV records with {csv_target_key}={want_info}: {len(matching_ids)}")
    print(f"  Filtered JSONL records: {len(filtered_records)}")
    print(f"  Filter rate: {len(filtered_records)/len(jsonl_records)*100:.1f}%")


if __name__ == '__main__':
    main()