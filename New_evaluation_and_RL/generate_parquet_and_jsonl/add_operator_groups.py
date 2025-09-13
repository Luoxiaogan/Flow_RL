#!/usr/bin/env python
"""
Script to add operator_group field to JSONL files by extracting operator names from prompt
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime
import shutil

def extract_operators_from_prompt(prompt):
    """
    Extract operator names from workflow initialization code in prompt
    
    Args:
        prompt: The prompt field from JSON (can be string or list of messages)
        
    Returns:
        List of operator names found
    """
    operators = []
    
    # Convert prompt to string for searching
    prompt_text = ""
    if isinstance(prompt, list):
        # Handle chat format prompts
        for msg in prompt:
            if isinstance(msg, dict):
                content = msg.get('content', '')
                prompt_text += str(content) + "\n"
    else:
        prompt_text = str(prompt)
    
    # Pattern to match self.xxx = operator.Xxx(
    # This will capture the operator name after self.
    pattern = r'self\.(\w+)\s*=\s*operator\.\w+\('
    
    # Find all matches
    matches = re.findall(pattern, prompt_text)
    
    # Filter out non-operator fields
    exclude_fields = ['llm', 'config', 'problem_text', 'workflow']
    
    for match in matches:
        if match.lower() not in exclude_fields:
            if match not in operators:  # Avoid duplicates
                operators.append(match)
    
    return operators

def process_jsonl_file(input_file, output_file=None, create_backup=True):
    """
    Process JSONL file to add operator_group field
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output file (if None, overwrites input)
        create_backup: Whether to create backup before modifying
        
    Returns:
        Statistics dictionary
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        return None
    
    # Create backup if requested
    if create_backup:
        backup_path = input_path.with_suffix('.jsonl.backup')
        shutil.copy2(input_path, backup_path)
        print(f"[OK] Created backup: {backup_path}")
    
    # Determine output path
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = input_path
    
    # Process file
    print(f"[Processing] File: {input_path}")
    
    processed_lines = []
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'operators_found': {},
        'errors': []
    }
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total'] += 1
            
            if not line.strip():
                continue
            
            try:
                # Parse JSON
                data = json.loads(line)
                
                # Extract operators from prompt
                prompt = data.get('prompt', '')
                operators = extract_operators_from_prompt(prompt)
                
                # Add operator_group to extra_info
                if 'extra_info' not in data:
                    data['extra_info'] = {}
                
                data['extra_info']['operator_group'] = operators
                
                # Track statistics
                operators_key = ','.join(sorted(operators)) if operators else 'none'
                if operators_key not in stats['operators_found']:
                    stats['operators_found'][operators_key] = 0
                stats['operators_found'][operators_key] += 1
                
                # Add to processed lines
                processed_lines.append(json.dumps(data, ensure_ascii=False))
                stats['success'] += 1
                
                # Progress indicator
                if line_num % 100 == 0:
                    print(f"  Processing... {line_num} lines")
                
            except json.JSONDecodeError as e:
                stats['failed'] += 1
                stats['errors'].append(f"Line {line_num}: JSON parse error - {e}")
                processed_lines.append(line.strip())  # Keep original line
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f"Line {line_num}: {e}")
                processed_lines.append(line.strip())  # Keep original line
    
    # Write output
    print(f"[Saving] Output to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in processed_lines:
            f.write(line + '\n')
    
    return stats

def print_statistics(stats):
    """Print processing statistics"""
    if not stats:
        return
    
    print("\n" + "="*60)
    print("[STATISTICS] Processing Results")
    print("="*60)
    
    print(f"Total lines: {stats['total']}")
    print(f"Successfully processed: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    
    print(f"\n[OPERATORS] Found operator combinations:")
    for operators, count in sorted(stats['operators_found'].items(), 
                                  key=lambda x: x[1], reverse=True):
        if operators == 'none':
            print(f"  [no operators]: {count} samples")
        else:
            operator_list = operators.split(',')
            print(f"  [{', '.join(operator_list)}]: {count} samples")
    
    if stats['errors']:
        print(f"\n[ERRORS] Error details (first 10):")
        for error in stats['errors'][:10]:
            print(f"  - {error}")

def main():
    """Main function"""
    print("="*60)
    print("Add operator_group field to JSONL file")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # File paths
    input_file = "test_scoreflow_data_all/test.jsonl"
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not Path(input_file).exists():
        # Try to find the file in parent directories
        possible_paths = [
            current_dir / input_file,
            current_dir.parent / input_file,
            Path("D:/temp/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl") / input_file
        ]
        
        for path in possible_paths:
            if path.exists():
                input_file = str(path)
                break
        else:
            print(f"[ERROR] Cannot find file: {input_file}")
            print(f"Current directory: {current_dir}")
            return 1
    
    # Process file
    stats = process_jsonl_file(
        input_file=input_file,
        output_file=None,  # Overwrite original
        create_backup=True
    )
    
    # Print statistics
    print_statistics(stats)
    
    print(f"\n[SUCCESS] Processing complete!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())