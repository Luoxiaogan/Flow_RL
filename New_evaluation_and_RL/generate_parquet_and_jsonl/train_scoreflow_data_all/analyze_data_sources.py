#!/usr/bin/env python3
"""
分析JSONL文件中data_source字段的唯一值及分布

功能：
- 读取JSONL文件
- 统计data_source字段的所有唯一值
- 显示每个数据源的数量和占比
"""

import json
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List


def analyze_data_sources(jsonl_path: str) -> Dict[str, int]:
    """
    分析JSONL文件中的data_source字段
    
    Args:
        jsonl_path: JSONL文件路径
        
    Returns:
        Dict[str, int]: 每个data_source的计数
    """
    
    if not Path(jsonl_path).exists():
        print(f"❌ 错误: 文件 '{jsonl_path}' 不存在")
        sys.exit(1)
    
    data_sources = []
    line_count = 0
    error_count = 0
    missing_field_count = 0
    
    print(f"正在分析文件: {jsonl_path}")
    print("-" * 60)
    
    # 读取文件并收集data_source
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            try:
                data = json.loads(line.strip())
                
                if 'data_source' in data:
                    data_sources.append(data['data_source'])
                else:
                    missing_field_count += 1
                    print(f"⚠️  第{line_num}行缺少data_source字段")
                    
            except json.JSONDecodeError as e:
                error_count += 1
                print(f"❌ 第{line_num}行JSON解析错误: {e}")
            except Exception as e:
                error_count += 1
                print(f"❌ 第{line_num}行处理错误: {e}")
    
    # 统计data_source分布
    source_counter = Counter(data_sources)
    
    return source_counter, line_count, error_count, missing_field_count


def display_results(source_counter: Counter, total_lines: int, error_count: int, missing_count: int):
    """
    显示分析结果
    
    Args:
        source_counter: data_source计数器
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
    print(f"  有效记录: {sum(source_counter.values())}")
    print(f"  解析错误: {error_count}")
    print(f"  缺少data_source字段: {missing_count}")
    
    # data_source分布
    print(f"\n🏷️  data_source唯一值: {len(source_counter)} 种")
    print("-" * 40)
    
    if source_counter:
        # 按数量排序
        sorted_sources = sorted(source_counter.items(), key=lambda x: x[1], reverse=True)
        
        # 计算最长的source名称用于对齐
        max_source_len = max(len(source) for source, _ in sorted_sources)
        
        print(f"\n{'数据源'.ljust(max_source_len)}  {'数量':>6}  {'占比':>7}  分布图")
        print("-" * (max_source_len + 40))
        
        total_valid = sum(source_counter.values())
        
        for source, count in sorted_sources:
            percentage = (count / total_valid) * 100 if total_valid > 0 else 0
            # 创建简单的条形图
            bar_length = int(percentage / 2)  # 每2%一个字符
            bar = "█" * bar_length
            
            print(f"{source.ljust(max_source_len)}  {count:6d}  {percentage:6.1f}%  {bar}")
        
        print("-" * (max_source_len + 40))
        print(f"{'总计'.ljust(max_source_len)}  {total_valid:6d}  100.0%")
        
        # 额外的统计信息
        print(f"\n📝 详细信息:")
        print(f"  最常见数据源: {sorted_sources[0][0]} ({sorted_sources[0][1]} 条)")
        if len(sorted_sources) > 1:
            print(f"  最少见数据源: {sorted_sources[-1][0]} ({sorted_sources[-1][1]} 条)")
        
        # 如果data_source包含特定模式，进行分组统计
        print(f"\n🔍 模式分析:")
        
        # 检查是否有workflow_前缀的数据源
        workflow_sources = [s for s, _ in sorted_sources if s.startswith('workflow_')]
        if workflow_sources:
            workflow_count = sum(source_counter[s] for s in workflow_sources)
            print(f"  workflow_* 类型: {len(workflow_sources)} 种, 共 {workflow_count} 条")
            for ws in workflow_sources:
                print(f"    - {ws}: {source_counter[ws]} 条")
        
        # 检查其他常见模式
        non_workflow_sources = [s for s, _ in sorted_sources if not s.startswith('workflow_')]
        if non_workflow_sources:
            print(f"  其他类型: {len(non_workflow_sources)} 种")
            for nws in non_workflow_sources:
                print(f"    - {nws}: {source_counter[nws]} 条")
    
    else:
        print("  未找到任何有效的data_source")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    
    # 获取命令行参数或使用默认路径
    if len(sys.argv) > 1:
        jsonl_path = sys.argv[1]
    else:
        # 默认路径
        jsonl_path = "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all/test_cleared.jsonl"
    
    print("=" * 60)
    print("🔎 JSONL Data Source 分析工具")
    print("=" * 60)
    
    # 执行分析
    source_counter, total_lines, error_count, missing_count = analyze_data_sources(jsonl_path)
    
    # 显示结果
    display_results(source_counter, total_lines, error_count, missing_count)
    
    # 导出唯一值列表
    if source_counter:
        unique_sources = sorted(source_counter.keys())
        print("\n💾 唯一data_source值列表:")
        print(f"  {unique_sources}")
        
        # 可选：保存到文件
        output_file = Path(jsonl_path).parent / "data_sources_unique.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Unique data_source values\n")
            f.write(f"# From file: {jsonl_path}\n")
            f.write(f"# Total unique values: {len(unique_sources)}\n\n")
            for source in unique_sources:
                f.write(f"{source}\t{source_counter[source]}\n")
        print(f"\n  已保存到: {output_file}")
    
    print("=" * 60)
    print("✅ 分析完成！")


if __name__ == "__main__":
    main()