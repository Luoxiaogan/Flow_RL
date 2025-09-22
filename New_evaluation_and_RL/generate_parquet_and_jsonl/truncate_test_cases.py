#!/usr/bin/env python3
"""
Script to truncate test_cases in JSONL files to keep only the first N entries.

Usage:
    python truncate_test_cases.py <input_file> <n>
    python truncate_test_cases.py test.jsonl 10  # Keep first 10 test cases

This will create a new file: test_10.jsonl
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import argparse


def truncate_test_cases(record: Dict[str, Any], n: int) -> Dict[str, Any]:
    """
    Truncate test_cases field in a record to keep only first n entries.

    Args:
        record: The JSON record containing test_cases
        n: Number of test cases to keep

    Returns:
        Modified record with truncated test_cases
    """
    # Create a deep copy to avoid modifying the original
    import copy
    new_record = copy.deepcopy(record)

    # Check if extra_info and test_cases exist
    if 'extra_info' in new_record and 'test_cases' in new_record['extra_info']:
        original_count = len(new_record['extra_info']['test_cases'])
        # Truncate the test_cases list
        new_record['extra_info']['test_cases'] = new_record['extra_info']['test_cases'][:n]
        truncated_count = len(new_record['extra_info']['test_cases'])

        # Add metadata about truncation
        new_record['extra_info']['original_test_cases_count'] = original_count
        new_record['extra_info']['truncated_test_cases_count'] = truncated_count

        print(f"  Truncated test_cases from {original_count} to {truncated_count}")
    else:
        print(f"  Warning: No test_cases field found in extra_info")

    return new_record


def process_jsonl_file(input_file: str, n: int, output_file: str = None) -> str:
    """
    Process a JSONL file and truncate test_cases in each record.

    Args:
        input_file: Path to input JSONL file
        n: Number of test cases to keep
        output_file: Optional output file path (default: input_file_n.jsonl)

    Returns:
        Path to the created output file
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_{n}{input_path.suffix}"
    else:
        output_file = Path(output_file)

    print(f"Processing: {input_file}")
    print(f"Output will be saved to: {output_file}")
    print(f"Keeping first {n} test cases in each record")
    print("-" * 50)

    records_processed = 0
    total_original_test_cases = 0
    total_truncated_test_cases = 0

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # Parse JSON record
                record = json.loads(line)
                print(f"Processing record {line_num}:")

                # Count original test cases
                if 'extra_info' in record and 'test_cases' in record['extra_info']:
                    total_original_test_cases += len(record['extra_info']['test_cases'])

                # Truncate test_cases
                truncated_record = truncate_test_cases(record, n)

                # Count truncated test cases
                if 'extra_info' in truncated_record and 'test_cases' in truncated_record['extra_info']:
                    total_truncated_test_cases += len(truncated_record['extra_info']['test_cases'])

                # Write to output file
                json.dump(truncated_record, outfile, ensure_ascii=False)
                outfile.write('\n')

                records_processed += 1

            except json.JSONDecodeError as e:
                print(f"  Error: Failed to parse JSON at line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"  Error processing line {line_num}: {e}")
                continue

    print("-" * 50)
    print(f"Processing complete!")
    print(f"Records processed: {records_processed}")
    print(f"Total original test cases: {total_original_test_cases}")
    print(f"Total truncated test cases: {total_truncated_test_cases}")
    print(f"Test cases removed: {total_original_test_cases - total_truncated_test_cases}")
    print(f"Output saved to: {output_file}")

    return str(output_file)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Truncate test_cases in JSONL files to keep only the first N entries.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python truncate_test_cases.py test.jsonl 10
    Creates test_10.jsonl with first 10 test cases per record

  python truncate_test_cases.py data.jsonl 5 -o output.jsonl
    Creates output.jsonl with first 5 test cases per record

  python truncate_test_cases.py --batch "*.jsonl" 20
    Process all .jsonl files in current directory
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to the input JSONL file'
    )

    parser.add_argument(
        'n',
        type=int,
        help='Number of test cases to keep (from the beginning)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: input_file_n.jsonl)',
        default=None
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process multiple files matching the input pattern'
    )

    args = parser.parse_args()

    # Validate n
    if args.n <= 0:
        print(f"Error: n must be a positive integer, got {args.n}")
        sys.exit(1)

    # Batch processing mode
    if args.batch:
        from glob import glob
        files = glob(args.input_file)
        if not files:
            print(f"No files found matching pattern: {args.input_file}")
            sys.exit(1)

        print(f"Found {len(files)} files to process")
        print("=" * 50)

        for file in files:
            try:
                process_jsonl_file(file, args.n)
                print("=" * 50)
            except Exception as e:
                print(f"Error processing {file}: {e}")
                print("=" * 50)
    else:
        # Single file processing
        try:
            process_jsonl_file(args.input_file, args.n, args.output)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()