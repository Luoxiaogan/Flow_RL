#!/usr/bin/env python
"""
将 JSONL 生成样本文件转换为独立的 Python 文件
"""

import json
import os
import re
import argparse
from pathlib import Path


def extract_think_and_code(output_text):
    """
    从output中提取 <think></think> 部分和 ```python 代码块
    
    Args:
        output_text: 生成的输出文本
        
    Returns:
        tuple: (思考部分, 代码部分)
    """
    
    # 提取 <think></think> 部分
    think_pattern = r'<think>(.*?)</think>'
    think_match = re.search(think_pattern, output_text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""
    
    # 提取 ```python 代码块
    code_pattern = r'```python\n(.*?)```'
    code_match = re.search(code_pattern, output_text, re.DOTALL)
    code_content = code_match.group(1).strip() if code_match else ""
    
    # 如果没找到 ```python，尝试查找 ```后面直接是代码的情况
    if not code_content:
        code_pattern = r'```\n(.*?)```'
        code_match = re.search(code_pattern, output_text, re.DOTALL)
        code_content = code_match.group(1).strip() if code_match else ""
    
    return think_content, code_content


def process_jsonl_to_python_files(jsonl_file, output_dir):
    """
    处理 JSONL 文件，将每个样本转换为 Python 文件
    
    Args:
        jsonl_file: 输入的 JSONL 文件路径
        output_dir: 输出目录路径
    """
    
    if not os.path.exists(jsonl_file):
        print(f"❌ 错误: JSONL 文件不存在 {jsonl_file}")
        return
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_path}")
    
    processed_count = 0
    error_count = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析 JSON
                    data = json.loads(line)
                    
                    step = data.get('step', 'unknown')
                    sample_idx = data.get('sample_idx', 0)
                    output = data.get('output', '')
                    
                    if not output:
                        print(f"⚠️  第 {line_num} 行: 空的 output，跳过")
                        continue
                    
                    # 提取思考和代码部分
                    think_content, code_content = extract_think_and_code(output)
                    
                    # 生成文件名
                    filename = f"step_{step}_{sample_idx}.py"
                    filepath = output_path / filename
                    
                    # 生成 Python 文件内容
                    python_content = generate_python_file_content(
                        think_content, code_content, step, sample_idx, data
                    )
                    
                    # 写入文件
                    with open(filepath, 'w', encoding='utf-8') as py_file:
                        py_file.write(python_content)
                    
                    processed_count += 1
                    print(f"✅ 已生成: {filename}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ 第 {line_num} 行 JSON 解析错误: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"❌ 第 {line_num} 行处理错误: {e}")
                    error_count += 1
    
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return
    
    # 统计信息
    print(f"\n📊 处理完成:")
    print(f"  ✅ 成功生成: {processed_count} 个 Python 文件")
    if error_count > 0:
        print(f"  ❌ 错误记录: {error_count} 条")
    print(f"  📂 文件保存在: {output_path}")


def generate_python_file_content(think_content, code_content, step, sample_idx, data):
    """
    生成 Python 文件内容
    
    Args:
        think_content: 思考部分内容
        code_content: 代码部分内容
        step: 训练步数
        sample_idx: 样本索引
        data: 完整的 JSON 数据
        
    Returns:
        str: 生成的 Python 文件内容
    """
    
    # 文件头部注释
    header = f'''#!/usr/bin/env python
"""
Generated from training step {step}, sample {sample_idx}
Timestamp: {data.get('timestamp', 'N/A')}
"""

'''
    
    # 思考部分（作为多行文档字符串）
    thinking_section = ''
    if think_content:
        # 处理转义字符，将 \\n 转换为真正的换行
        processed_think = think_content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
        thinking_section = f'''"""
THINKING PROCESS:
{processed_think}
"""

'''
    
    # 代码部分
    code_section = ''
    if code_content:
        # 处理代码中的转义字符
        processed_code = code_content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
        code_section = f'''{processed_code}

'''
    else:
        # 如果没有找到代码块，可能整个output就是代码
        # 尝试提取类似代码的内容
        output = data.get('output', '')
        if 'def ' in output or 'class ' in output or 'import ' in output:
            # 去掉 <think></think> 部分后的内容可能是代码
            remaining_content = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL).strip()
            if remaining_content:
                processed_remaining = remaining_content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                code_section = f'''{processed_remaining}

'''
    
    # 如果既没有思考也没有代码，至少保留原始输出作为注释
    if not thinking_section and not code_section:
        raw_output = data.get('output', '').replace('\\n', '\n')
        code_section = f'''"""
Raw output (no think/code blocks found):
{raw_output}
"""

'''
    
    return header + thinking_section + code_section


def preview_sample(jsonl_file, num_samples=3):
    """
    预览 JSONL 文件中的样本，帮助了解数据结构
    
    Args:
        jsonl_file: JSONL 文件路径
        num_samples: 预览的样本数量
    """
    
    print(f"🔍 预览文件: {jsonl_file}")
    print("=" * 60)
    
    if not os.path.exists(jsonl_file):
        print(f"❌ 文件不存在: {jsonl_file}")
        return
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= num_samples:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    output = data.get('output', '')
                    
                    print(f"\n📝 样本 {i+1}:")
                    print(f"  Step: {data.get('step')}, Sample: {data.get('sample_idx')}")
                    
                    # 检查是否包含 <think> 标签
                    has_think = '<think>' in output and '</think>' in output
                    print(f"  包含 <think> 部分: {'✅' if has_think else '❌'}")
                    
                    # 检查是否包含代码块
                    has_code = '```python' in output or '```' in output
                    print(f"  包含代码块: {'✅' if has_code else '❌'}")
                    
                    # 显示内容预览
                    preview = output[:200].replace('\n', '\\n')
                    print(f"  内容预览: {preview}{'...' if len(output) > 200 else ''}")
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON 解析错误: {e}")
    
    except Exception as e:
        print(f"❌ 预览时出错: {e}")


def main():
    parser = argparse.ArgumentParser(description="将JSONL生成样本转换为Python文件")
    parser.add_argument("jsonl_file", help="输入的JSONL文件路径")
    parser.add_argument("output_dir", help="输出目录路径")
    parser.add_argument("-p", "--preview", action="store_true", help="只预览文件结构")
    parser.add_argument("--samples", type=int, default=3, help="预览时显示的样本数（默认3）")
    
    args = parser.parse_args()
    
    if args.preview:
        preview_sample(args.jsonl_file, args.samples)
    else:
        process_jsonl_to_python_files(args.jsonl_file, args.output_dir)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("📋 用法示例:")
        print("  python jsonl_to_python_files.py input.jsonl output_dir/")
        print("  python jsonl_to_python_files.py input.jsonl output_dir/ -p  # 预览")
        print()
        
        # 自动查找当前目录下的 generation_samples 文件
        current_dir = Path(__file__).parent
        jsonl_files = list(current_dir.glob("*generation_samples*.jsonl"))
        
        if jsonl_files:
            print("🔍 发现以下生成样本文件:")
            for i, file in enumerate(jsonl_files):
                print(f"  {i+1}. {file.name}")
            print()
            print("请使用以下命令处理:")
            for file in jsonl_files:
                dir_name = file.stem.replace('generation_samples_', 'extracted_')
                print(f"  python jsonl_to_python_files.py {file.name} {dir_name}/")
    else:
        main()