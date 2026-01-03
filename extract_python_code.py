import json
import re

def extract_python_code_blocks(user_content):
    """
    Extract all Python code blocks from user content that are wrapped in ```python ... ``` markers
    """
    # Pattern to match Python code blocks - non-greedy matching
    pattern = r'```python\n(.*?)```'

    # Find all matches with DOTALL flag to handle multi-line code
    matches = re.findall(pattern, user_content, re.DOTALL)

    return matches

def process_jsonl_file(input_file, output_file):
    """
    Process JSONL file and extract Python code blocks from user content
    """
    extracted_data = []
    line_count = 0

    print(f"开始处理文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(infile, 1):
            try:
                # Parse each line as JSON
                data = json.loads(line.strip())
                line_count += 1

                # Extract messages field
                if 'messages' in data:
                    # Find user messages
                    for message in data['messages']:
                        if message.get('role') == 'assistant':
                            user_content = message.get('content', '')

                            # Extract Python code blocks
                            code_blocks = extract_python_code_blocks(user_content)

                            if code_blocks:
                                # Create new entry with extracted code
                                extracted_entry = {
                                    'workflow_id': data.get('workflow_id', ''),
                                    'benchmark': data.get('benchmark', ''),
                                    'data_indices': data.get('data_indices', []),
                                    'python_code_blocks': code_blocks,
                                    'num_code_blocks': len(code_blocks)
                                }
                                extracted_data.append(extracted_entry)
                                print(f"  行 {line_num}: 找到 {len(code_blocks)} 个代码块")

            except json.JSONDecodeError as e:
                print(f"  警告: 行 {line_num} JSON解析失败: {e}")
                continue
            except Exception as e:
                print(f"  警告: 行 {line_num} 处理失败: {e}")
                continue

    # Write extracted data to new JSONL file
    print(f"\n写入提取的数据到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for entry in extracted_data:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')

    print(f"\n处理完成!")
    print(f"  总共处理行数: {line_count}")
    print(f"  成功提取代码的条目: {len(extracted_data)}")

    # Calculate total code blocks
    total_blocks = sum(entry['num_code_blocks'] for entry in extracted_data)
    print(f"  提取的总代码块数: {total_blocks}")

    return extracted_data

if __name__ == "__main__":
    input_file = "D:\\temp\\Flow_RL\\ONLY_QWEN3_0910.jsonl"
    output_file = "D:\\temp\\Flow_RL\\extracted_python_code.jsonl"

    # Process the file
    result = process_jsonl_file(input_file, output_file)

    # Show sample of first extracted entry if exists
    if result:
        print("\n第一个提取条目的示例:")
        first_entry = result[0]
        print(f"  Workflow ID: {first_entry['workflow_id']}")
        print(f"  Benchmark: {first_entry['benchmark']}")
        print(f"  代码块数量: {first_entry['num_code_blocks']}")
        if first_entry['python_code_blocks']:
            print(f"  第一个代码块前100字符:")
            print(f"    {first_entry['python_code_blocks'][0][:100]}...")