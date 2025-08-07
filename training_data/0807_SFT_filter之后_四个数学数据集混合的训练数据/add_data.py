#!/usr/bin/env python3
"""
Merge multiple JSONL files and format them for different chat templates.
Supports Qwen-2.5-7B-Instruct and LLaMA-3.1-8B-Instruct formats.

CORRECTED VERSION: Outputs proper SFT training format, not formatted_text
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of records."""
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON at line {line_num} in {filepath}: {e}")
                        continue
        print(f"Loaded {len(records)} records from {filepath}")
    except FileNotFoundError:
        print(f"Warning: File not found - {filepath}")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return records


def validate_messages(messages: List[Dict[str, str]]) -> bool:
    """
    Validate message format and structure.
    Returns True if valid, False otherwise.
    """
    if not messages:
        return False
    
    valid_roles = {"system", "user", "assistant"}
    
    for msg in messages:
        if not isinstance(msg, dict):
            return False
        if "role" not in msg or "content" not in msg:
            return False
        if msg["role"] not in valid_roles:
            print(f"Warning: Invalid role '{msg['role']}' found")
            return False
        if not isinstance(msg["content"], str):
            return False
    
    # Check for proper conversation flow (optional but recommended)
    # Should have at least one user and one assistant message
    roles = [msg["role"] for msg in messages]
    if "user" not in roles or "assistant" not in roles:
        print("Warning: Conversation should have both user and assistant messages")
        return False
    
    return True


def convert_to_qwen_format(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert to Qwen-2.5-7B-Instruct SFT format.
    
    Qwen expects:
    {
        "type": "chatml",
        "messages": [...],
        "source": "custom"
    }
    """
    messages = record.get("messages", [])
    
    # Clean and validate messages
    cleaned_messages = []
    for msg in messages:
        cleaned_msg = {
            "role": msg.get("role", "").strip(),
            "content": msg.get("content", "").strip()
        }
        if cleaned_msg["content"]:  # Skip empty messages
            cleaned_messages.append(cleaned_msg)
    
    return {
        "type": "chatml",
        "messages": cleaned_messages,
        "source": record.get("benchmark", "custom"),
        # Optional: preserve metadata for tracking
        "metadata": {
            "workflow_id": record.get("workflow_id", ""),
            "benchmark": record.get("benchmark", ""),
            "data_indices": record.get("data_indices", [])
        }
    }


def convert_to_llama_format(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert to LLaMA-3.1-8B-Instruct SFT format.
    
    LLaMA expects:
    {
        "messages": [...]
    }
    
    That's it! LLaMA format is simpler.
    """
    messages = record.get("messages", [])
    
    # Clean and validate messages
    cleaned_messages = []
    for msg in messages:
        cleaned_msg = {
            "role": msg.get("role", "").strip(),
            "content": msg.get("content", "").strip()
        }
        if cleaned_msg["content"]:  # Skip empty messages
            cleaned_messages.append(cleaned_msg)
    
    return {
        "messages": cleaned_messages,
        # Optional: preserve metadata as separate field (won't affect training)
        "metadata": {
            "workflow_id": record.get("workflow_id", ""),
            "benchmark": record.get("benchmark", ""),
            "data_indices": record.get("data_indices", [])
        }
    }


def merge_and_format_jsonl(
    input_files: List[str],
    output_qwen_path: str,
    output_llama_path: str,
    validate: bool = True
) -> None:
    """
    Merge multiple JSONL files and format for different model training.
    
    Args:
        input_files: List of input JSONL file paths
        output_qwen_path: Output path for Qwen-formatted JSONL
        output_llama_path: Output path for LLaMA-formatted JSONL
        validate: Whether to validate message format
    """
    all_records = []
    
    # Load all records from input files
    for filepath in input_files:
        records = load_jsonl(filepath)
        all_records.extend(records)
    
    print(f"\nTotal records loaded: {len(all_records)}")
    
    # Process records
    qwen_records = []
    llama_records = []
    skipped_count = 0
    
    for idx, record in enumerate(all_records):
        # Extract and validate messages
        messages = record.get("messages", [])
        
        if validate and not validate_messages(messages):
            print(f"Skipping record {idx} (workflow_id: {record.get('workflow_id', 'unknown')}) due to invalid messages")
            skipped_count += 1
            continue
        
        # Convert to respective formats
        try:
            qwen_record = convert_to_qwen_format(record)
            qwen_records.append(qwen_record)
            
            llama_record = convert_to_llama_format(record)
            llama_records.append(llama_record)
            
        except Exception as e:
            print(f"Error processing record {idx}: {e}")
            skipped_count += 1
            continue
    
    print(f"\nProcessed {len(qwen_records)} valid records, skipped {skipped_count} invalid records")
    
    # Save Qwen-formatted records
    print(f"\nSaving {len(qwen_records)} Qwen-formatted records to {output_qwen_path}")
    Path(output_qwen_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_qwen_path, 'w', encoding='utf-8') as f:
        for record in qwen_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Save LLaMA-formatted records
    print(f"Saving {len(llama_records)} LLaMA-formatted records to {output_llama_path}")
    Path(output_llama_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_llama_path, 'w', encoding='utf-8') as f:
        for record in llama_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Print statistics
    print("\n" + "="*50)
    print("Conversion Complete!")
    print("="*50)
    print(f"Qwen output: {output_qwen_path}")
    print(f"LLaMA output: {output_llama_path}")
    print(f"Total records processed: {len(qwen_records)}")
    print(f"Records skipped: {skipped_count}")
    
    # Sample output for verification
    if qwen_records:
        print("\nSample Qwen record (first entry):")
        print(json.dumps(qwen_records[0], indent=2, ensure_ascii=False)[:500] + "...")
    if llama_records:
        print("\nSample LLaMA record (first entry):")
        print(json.dumps(llama_records[0], indent=2, ensure_ascii=False)[:500] + "...")


def main():
    """Main function with hardcoded file paths."""
    
    # Hardcoded input JSONL file paths
    base_dir = "/Users/luogan/Code/workflow_generation/Flow_RL/training_data"
    
    input_files = [
        f"{base_dir}/0807_workspace_aime_limr/filtered_training_data.jsonl",
        f"{base_dir}/0807_workspace_aime_test/filtered_training_data.jsonl",
        f"{base_dir}/0807_workspace_drop_new/filtered_training_data.jsonl",
        f"{base_dir}/0807_workspace_gsm8k_new/filtered_training_data.jsonl",
    ]
    
    # Output paths
    output_dir = f"{base_dir}/0807_SFT_filter之后_四个数学数据集混合的训练数据"
    output_qwen_path = f"{output_dir}/merged_training_data_qwen.jsonl"
    output_llama_path = f"{output_dir}/merged_training_data_llama.jsonl"
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Filter out non-existent files
    existing_files = []
    missing_files = []
    
    for filepath in input_files:
        if Path(filepath).exists():
            existing_files.append(filepath)
        else:
            missing_files.append(filepath)
    
    # Report status
    print("="*50)
    print("SFT Data Preparation for Qwen & LLaMA")
    print("="*50)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} files:")
        for f in missing_files:
            print(f"  - {f}")
    
    if not existing_files:
        print("\n❌ Error: No input files found!")
        return
    
    print(f"\n✅ Found {len(existing_files)} input files:")
    for f in existing_files:
        file_size = Path(f).stat().st_size / (1024 * 1024)  # Size in MB
        print(f"  - {Path(f).name} ({file_size:.2f} MB)")
    
    # Merge and format
    merge_and_format_jsonl(
        existing_files,
        output_qwen_path,
        output_llama_path,
        validate=True  # Enable validation
    )


if __name__ == '__main__':
    main()