import json
import re
import os

def extract_and_save_workflow_scripts(jsonl_file_path, output_dir):
    """
    读取JSONL文件，提取每行中的Python代码块，并保存为独立的.py文件。

    Args:
        jsonl_file_path (str): .jsonl文件的路径。
        output_dir (str): 保存.py文件的目录。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            try:
                data = json.loads(line.strip())
                response_content = data.get('response', {}).get('content', '')

                # 使用正则表达式查找 ```python ... ``` 包裹的代码块
                # re.DOTALL 使得 . 匹配包括换行符在内的所有字符
                python_code_match = re.search(r'```python\s*(.*?)\s*```', response_content, re.DOTALL)

                if python_code_match:
                    python_code = python_code_match.group(1).strip()
                    output_filename = os.path.join(output_dir, f'imo_wf_{index}.py')

                    with open(output_filename, 'w', encoding='utf-8') as out_f:
                        out_f.write(python_code)
                    print(f"成功保存 imo_wf_{index}.py 到 {output_dir}")
                else:
                    print(f"第 {index} 行未找到Python代码块。")
            except json.JSONDecodeError as e:
                print(f"解析第 {index} 行JSON时出错: {e}")
            except Exception as e:
                print(f"处理第 {index} 行时发生意外错误: {e}")

# 文件路径和输出目录
jsonl_file = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/imo_data_0923/imo_test_with_responses_rollout=1.jsonl'
output_directory = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/imo_data_0923/'

# 运行函数
extract_and_save_workflow_scripts(jsonl_file, output_directory)