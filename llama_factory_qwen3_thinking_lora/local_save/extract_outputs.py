#!/usr/bin/env python
"""
从生成样本JSONL文件中提取output内容，保留关键元数据
"""

import json
import os
import argparse
from pathlib import Path


def extract_outputs(input_file, output_file=None):
    """
    从JSONL文件中提取output，保留step和sample_idx
    
    Args:
        input_file: 输入JSONL文件路径
        output_file: 输出JSONL文件路径（可选，默认自动生成）
    """
    
    if not os.path.exists(input_file):
        print(f"❌ 错误: 文件不存在 {input_file}")
        return
    
    # 如果没有指定输出文件，自动生成
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"extracted_{input_path.name}"
    
    print(f"📁 输入文件: {input_file}")
    print(f"📁 输出文件: {output_file}")
    
    extracted_count = 0
    error_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                try:
                    # 解析JSON
                    data = json.loads(line)
                    
                    # 提取需要的字段
                    extracted_data = {
                        "step": data.get("step"),
                        "sample_idx": data.get("sample_idx"), 
                        "output": data.get("output", "")
                    }
                    
                    # 如果有timestamp也保留（可选）
                    if "timestamp" in data:
                        extracted_data["timestamp"] = data["timestamp"]
                    
                    # 写入输出文件
                    outfile.write(json.dumps(extracted_data, ensure_ascii=False) + '\n')
                    extracted_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  第 {line_num} 行JSON解析错误: {e}")
                    error_count += 1
                except KeyError as e:
                    print(f"⚠️  第 {line_num} 行缺少字段: {e}")
                    error_count += 1
    
    except Exception as e:
        print(f"❌ 处理文件时出错: {e}")
        return
    
    # 统计信息
    print(f"\n📊 处理完成:")
    print(f"  ✅ 成功提取: {extracted_count} 条记录")
    if error_count > 0:
        print(f"  ❌ 错误记录: {error_count} 条")
    print(f"  📄 输出保存至: {output_file}")


def analyze_file_structure(input_file, show_samples=3):
    """
    分析JSONL文件结构，显示样本
    
    Args:
        input_file: 输入文件路径
        show_samples: 显示的样本数量
    """
    
    print(f"🔍 分析文件结构: {input_file}")
    print("=" * 60)
    
    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            total_lines = 0
            sample_count = 0
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                total_lines += 1
                
                # 显示前几个样本
                if sample_count < show_samples:
                    try:
                        data = json.loads(line)
                        print(f"\n📝 样本 {sample_count + 1} (第{line_num}行):")
                        print(f"  - step: {data.get('step', 'N/A')}")
                        print(f"  - sample_idx: {data.get('sample_idx', 'N/A')}")
                        print(f"  - 包含字段: {list(data.keys())}")
                        
                        # 显示output的前100个字符
                        output = data.get('output', '')
                        if output:
                            preview = output[:100].replace('\n', '\\n')
                            print(f"  - output预览: {preview}{'...' if len(output) > 100 else ''}")
                        
                        sample_count += 1
                        
                    except json.JSONDecodeError:
                        print(f"  ⚠️ 第{line_num}行JSON格式错误")
            
            print(f"\n📊 文件统计:")
            print(f"  - 总行数: {total_lines}")
            print(f"  - 有效JSON行: 至少 {sample_count}")
            
    except Exception as e:
        print(f"❌ 分析文件时出错: {e}")


def main():
    parser = argparse.ArgumentParser(description="从生成样本JSONL中提取output")
    parser.add_argument("input_file", help="输入JSONL文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（可选）")
    parser.add_argument("-a", "--analyze", action="store_true", help="只分析文件结构")
    parser.add_argument("--samples", type=int, default=3, help="分析时显示的样本数（默认3）")
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_file_structure(args.input_file, args.samples)
    else:
        extract_outputs(args.input_file, args.output)


if __name__ == "__main__":
    # 如果直接运行（没有命令行参数），处理当前目录的默认文件
    import sys
    
    if len(sys.argv) == 1:
        # 自动查找当前目录下的generation_samples文件
        current_dir = Path(__file__).parent
        jsonl_files = list(current_dir.glob("*generation_samples*.jsonl"))
        
        if jsonl_files:
            print("🔍 发现以下生成样本文件:")
            for i, file in enumerate(jsonl_files):
                print(f"  {i+1}. {file.name}")
            
            if len(jsonl_files) == 1:
                print(f"\n📁 自动处理: {jsonl_files[0].name}")
                extract_outputs(str(jsonl_files[0]))
            else:
                print("\n请指定要处理的文件:")
                print("python extract_outputs.py <文件名>")
        else:
            print("❌ 当前目录下没有找到 generation_samples 文件")
            print("\n使用方法:")
            print("  python extract_outputs.py <输入文件> [-o 输出文件]")
            print("  python extract_outputs.py <输入文件> -a  # 只分析文件结构")
    else:
        main()