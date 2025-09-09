#!/usr/bin/env python
"""
Temporary script to set all test_cases fields to empty lists in both JSONL and Parquet files.
"""

import json
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from pathlib import Path


def clear_test_cases_jsonl(input_path, output_path):
    """Clear test_cases field in JSONL file."""
    print(f"处理JSONL文件: {input_path}")
    
    modified_lines = []
    line_count = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Set test_cases to empty list
                if 'extra_info' in data and 'test_cases' in data['extra_info']:
                    original_test_cases = data['extra_info']['test_cases']
                    data['extra_info']['test_cases'] = []
                    print(f"  行 {line_num}: 清空test_cases (原有 {len(original_test_cases)} 个测试用例)")
                    line_count += 1
                
                modified_lines.append(json.dumps(data, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"  警告: 行 {line_num} JSON解析失败: {e}")
                modified_lines.append(line.strip())
    
    # Write modified data
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in modified_lines:
            f.write(line + '\n')
    
    print(f"  完成！修改了 {line_count} 行，保存到: {output_path}")
    return line_count


def clear_test_cases_parquet(input_path, output_path):
    """Clear test_cases field in Parquet file."""
    print(f"处理Parquet文件: {input_path}")
    
    # Read parquet file
    df = pd.read_parquet(input_path)
    print(f"  原始数据行数: {len(df)}")
    
    # Check if extra_info column exists
    if 'extra_info' not in df.columns:
        print("  警告: 文件中没有 'extra_info' 列")
        df.to_parquet(output_path)
        return 0
    
    modified_count = 0
    
    # Process each row
    for idx in df.index:
        extra_info = df.at[idx, 'extra_info']
        
        # Handle different data types
        if isinstance(extra_info, str):
            try:
                extra_info_dict = json.loads(extra_info)
            except json.JSONDecodeError:
                print(f"  警告: 行 {idx} 的 extra_info 不是有效的JSON")
                continue
        elif isinstance(extra_info, dict):
            extra_info_dict = extra_info
        else:
            print(f"  警告: 行 {idx} 的 extra_info 类型未知: {type(extra_info)}")
            continue
        
        # Clear test_cases
        if 'test_cases' in extra_info_dict:
            original_test_cases = extra_info_dict['test_cases']
            extra_info_dict['test_cases'] = []
            
            # Save back to dataframe
            if isinstance(df.at[idx, 'extra_info'], str):
                df.at[idx, 'extra_info'] = json.dumps(extra_info_dict, ensure_ascii=False)
            else:
                df.at[idx, 'extra_info'] = extra_info_dict
            
            print(f"  行 {idx}: 清空test_cases (原有 {len(original_test_cases)} 个测试用例)")
            modified_count += 1
    
    # Save modified dataframe
    df.to_parquet(output_path, engine='pyarrow')
    print(f"  完成！修改了 {modified_count} 行，保存到: {output_path}")
    return modified_count


def main():
    """Main function to process both files."""
    base_dir = Path("D:/temp/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all")
    
    # File paths
    jsonl_input = base_dir / "test.jsonl"
    jsonl_output = base_dir / "test_cleared.jsonl"
    
    parquet_input = base_dir / "test.parquet"
    parquet_output = base_dir / "test_cleared.parquet"
    
    print("=" * 60)
    print("开始清空test_cases字段")
    print("=" * 60)
    
    # Process JSONL file
    if jsonl_input.exists():
        jsonl_count = clear_test_cases_jsonl(jsonl_input, jsonl_output)
    else:
        print(f"JSONL文件不存在: {jsonl_input}")
        jsonl_count = 0
    
    print()
    
    # Process Parquet file
    if parquet_input.exists():
        parquet_count = clear_test_cases_parquet(parquet_input, parquet_output)
    else:
        print(f"Parquet文件不存在: {parquet_input}")
        parquet_count = 0
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"- JSONL文件: 修改了 {jsonl_count} 行")
    print(f"- Parquet文件: 修改了 {parquet_count} 行")
    print("\n输出文件:")
    print(f"- {jsonl_output}")
    print(f"- {parquet_output}")
    print("\n如需覆盖原文件，请手动重命名:")
    print(f"  mv {jsonl_output} {jsonl_input}")
    print(f"  mv {parquet_output} {parquet_input}")
    print("=" * 60)


if __name__ == "__main__":
    main()