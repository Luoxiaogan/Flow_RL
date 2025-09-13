#!/usr/bin/env python3
"""
分析JSONL文件中data_path字段的唯一值及分布

功能：
- 读取JSONL文件
- 统计extra_info.data_path字段的所有唯一值
- 显示每个数据路径的数量和占比
- 分析路径模式（train/test分布等）
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Tuple


def analyze_data_paths(jsonl_path: str) -> Tuple[Counter, int, int, int]:
    """
    分析JSONL文件中的data_path字段
    
    Args:
        jsonl_path: JSONL文件路径
        
    Returns:
        Tuple[Counter, int, int, int]: data_path计数器，总行数，错误数，缺失数
    """
    
    if not Path(jsonl_path).exists():
        print(f"❌ 错误: 文件 '{jsonl_path}' 不存在")
        sys.exit(1)
    
    data_paths = []
    line_count = 0
    error_count = 0
    missing_field_count = 0
    
    print(f"正在分析文件: {jsonl_path}")
    print("-" * 60)
    
    # 读取文件并收集data_path
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            try:
                data = json.loads(line.strip())
                
                # data_path在extra_info字段内
                if 'extra_info' in data:
                    if 'data_path' in data['extra_info']:
                        data_paths.append(data['extra_info']['data_path'])
                    else:
                        missing_field_count += 1
                        print(f"⚠️  第{line_num}行extra_info中缺少data_path字段")
                else:
                    missing_field_count += 1
                    print(f"⚠️  第{line_num}行缺少extra_info字段")
                    
            except json.JSONDecodeError as e:
                error_count += 1
                print(f"❌ 第{line_num}行JSON解析错误: {e}")
            except Exception as e:
                error_count += 1
                print(f"❌ 第{line_num}行处理错误: {e}")
    
    # 统计data_path分布
    path_counter = Counter(data_paths)
    
    return path_counter, line_count, error_count, missing_field_count


def analyze_path_patterns(path_counter: Counter) -> Dict:
    """
    分析路径模式
    
    Args:
        path_counter: data_path计数器
        
    Returns:
        Dict: 模式分析结果
    """
    patterns = {
        'datasets': defaultdict(int),
        'splits': defaultdict(int),
        'file_types': defaultdict(int),
        'base_paths': set()
    }
    
    for path, count in path_counter.items():
        path_obj = Path(path)
        
        # 提取数据集名称（倒数第二个目录）
        if len(path_obj.parts) >= 2:
            dataset_name = path_obj.parts[-2]
            patterns['datasets'][dataset_name] += count
        
        # 提取文件名中的split信息
        filename = path_obj.stem  # 不带扩展名的文件名
        if 'train' in filename:
            patterns['splits']['train'] += count
        elif 'test' in filename:
            patterns['splits']['test'] += count
        elif 'val' in filename or 'valid' in filename:
            patterns['splits']['validation'] += count
        else:
            patterns['splits']['other'] += count
        
        # 提取文件类型
        file_ext = path_obj.suffix
        patterns['file_types'][file_ext] += count
        
        # 提取基础路径
        if len(path_obj.parts) >= 3:
            base_path = '/'.join(path_obj.parts[:-2])
            patterns['base_paths'].add(base_path)
    
    return patterns


def display_results(path_counter: Counter, total_lines: int, error_count: int, missing_count: int):
    """
    显示分析结果
    
    Args:
        path_counter: data_path计数器
        total_lines: 总行数
        error_count: 错误行数
        missing_count: 缺少字段的行数
    """
    
    print("\n" + "=" * 60)
    print("📊 分析结果")
    print("=" * 60)
    
    # 基本统计
    print(f"\n📈 文件统计:")
    print(f"  总行数: {total_lines}")
    print(f"  有效记录: {sum(path_counter.values())}")
    print(f"  解析错误: {error_count}")
    print(f"  缺少data_path字段: {missing_count}")
    
    # data_path分布
    print(f"\n🏷️  data_path唯一值: {len(path_counter)} 个")
    print("-" * 40)
    
    if path_counter:
        # 按数量排序
        sorted_paths = sorted(path_counter.items(), key=lambda x: x[1], reverse=True)
        
        # 计算显示格式
        max_path_display_len = 50  # 限制路径显示长度
        
        print(f"\n{'数据路径':<{max_path_display_len}}  {'数量':>6}  {'占比':>7}")
        print("-" * (max_path_display_len + 20))
        
        total_valid = sum(path_counter.values())
        
        for path, count in sorted_paths:
            percentage = (count / total_valid) * 100 if total_valid > 0 else 0
            
            # 缩短路径显示
            if len(path) > max_path_display_len:
                # 提取关键部分：数据集名和文件名
                path_obj = Path(path)
                if len(path_obj.parts) >= 2:
                    display_path = f".../{path_obj.parts[-2]}/{path_obj.name}"
                else:
                    display_path = f".../{path_obj.name}"
            else:
                display_path = path
            
            print(f"{display_path:<{max_path_display_len}}  {count:6d}  {percentage:6.1f}%")
        
        print("-" * (max_path_display_len + 20))
        print(f"{'总计':<{max_path_display_len}}  {total_valid:6d}  100.0%")
        
        # 模式分析
        patterns = analyze_path_patterns(path_counter)
        
        print(f"\n🔍 路径模式分析:")
        
        # 数据集分布
        if patterns['datasets']:
            print(f"\n  📁 数据集分布:")
            sorted_datasets = sorted(patterns['datasets'].items(), key=lambda x: x[1], reverse=True)
            for dataset, count in sorted_datasets:
                print(f"    {dataset}: {count} 条")
        
        # Train/Test分布
        if patterns['splits']:
            print(f"\n  📊 数据集划分:")
            for split, count in sorted(patterns['splits'].items()):
                percentage = (count / total_valid) * 100
                print(f"    {split}: {count} 条 ({percentage:.1f}%)")
        
        # 文件类型
        if patterns['file_types']:
            print(f"\n  📄 文件类型:")
            for ext, count in sorted(patterns['file_types'].items()):
                print(f"    {ext}: {count} 条")
        
        # 基础路径
        if patterns['base_paths']:
            print(f"\n  🗂️  基础路径:")
            for base_path in sorted(patterns['base_paths']):
                print(f"    {base_path}")
        
        # 额外统计
        print(f"\n📝 详细信息:")
        print(f"  最常见路径: {sorted_paths[0][0]}")
        print(f"    出现次数: {sorted_paths[0][1]} 次")
        if len(sorted_paths) > 1:
            print(f"  最少见路径: {sorted_paths[-1][0]}")
            print(f"    出现次数: {sorted_paths[-1][1]} 次")
    
    else:
        print("  未找到任何有效的data_path")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    
    # 获取命令行参数或使用默认路径
    if len(sys.argv) > 1:
        jsonl_path = sys.argv[1]
    else:
        # 默认路径
        jsonl_path = "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all/train_sampled_10_to_5.jsonl"
    
    print("=" * 60)
    print("🔎 JSONL Data Path 分析工具")
    print("=" * 60)
    
    # 执行分析
    path_counter, total_lines, error_count, missing_count = analyze_data_paths(jsonl_path)
    
    # 显示结果
    display_results(path_counter, total_lines, error_count, missing_count)
    
    # 导出唯一值列表
    if path_counter:
        unique_paths = sorted(path_counter.keys())
        print("\n💾 唯一data_path值列表:")
        for i, path in enumerate(unique_paths, 1):
            print(f"  {i}. {path} ({path_counter[path]} 条)")
        
        # 保存到文件
        output_file = Path(jsonl_path).parent / "data_paths_unique.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Unique data_path values\n")
            f.write(f"# From file: {jsonl_path}\n")
            f.write(f"# Total unique paths: {len(unique_paths)}\n\n")
            
            # 按路径字母顺序排序输出
            for path in unique_paths:
                f.write(f"{path}\t{path_counter[path]}\n")
        
        print(f"\n  详细列表已保存到: {output_file}")
    
    print("=" * 60)
    print("✅ 分析完成！")


if __name__ == "__main__":
    main()