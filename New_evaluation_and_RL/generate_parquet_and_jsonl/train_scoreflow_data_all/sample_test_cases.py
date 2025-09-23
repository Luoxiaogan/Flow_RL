#!/usr/bin/env python3
"""
从JSONL文件中随机采样test_cases子集

功能：
- 读取train.jsonl文件
- 对每条记录的extra_info.test_cases进行随机子采样（从10个采样5个）
- 输出到train_sampled_10_to_5.jsonl文件
"""

import json
import random
from pathlib import Path
from tqdm import tqdm


def main():
    """主函数 - 硬编码所有参数"""
    
    # 硬编码路径和参数
    base_dir = Path("/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/train_scoreflow_data_all")
    input_file = base_dir / "train.jsonl"
    output_file = base_dir / "train_sampled_10_to_5.jsonl"
    
    # 硬编码采样参数
    original_len = 10  # 原始test_cases长度
    target_len = 5     # 目标采样长度
    seed = 42          # 固定随机种子
    
    # 设置随机种子
    random.seed(seed)
    print(f"使用随机种子: {seed}")
    
    # 统计信息
    total_lines = 0
    successful_samples = 0
    skipped_lines = 0
    original_test_cases_counts = []
    sampled_test_cases_counts = []
    
    # 计算总行数（用于进度条）
    print("正在计算文件行数...")
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"总记录数: {total_lines}")
    print(f"采样策略: {original_len} -> {target_len}")
    print("-" * 50)
    
    # 处理文件
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        # 使用进度条
        for line_num, line in enumerate(tqdm(infile, total=total_lines, desc="处理中"), 1):
            try:
                # 解析JSON
                data = json.loads(line.strip())
                
                # 检查是否有extra_info和test_cases
                if 'extra_info' not in data:
                    print(f"\n警告: 第{line_num}行缺少extra_info字段，跳过")
                    skipped_lines += 1
                    # 保持原样写入，使用真正的换行符
                    json.dump(data, outfile, ensure_ascii=False)
                    outfile.write('\n')
                    continue
                
                if 'test_cases' not in data['extra_info']:
                    print(f"\n警告: 第{line_num}行缺少test_cases字段，跳过")
                    skipped_lines += 1
                    # 保持原样写入，使用真正的换行符
                    json.dump(data, outfile, ensure_ascii=False)
                    outfile.write('\n')
                    continue
                
                # 获取原始test_cases
                original_test_cases = data['extra_info']['test_cases']
                original_count = len(original_test_cases)
                original_test_cases_counts.append(original_count)
                
                # 检查是否有足够的test_cases
                if original_count < target_len:
                    print(f"\n警告: 第{line_num}行只有{original_count}个test_cases，小于目标的{target_len}个")
                    # 使用所有可用的test_cases
                    sampled_cases = original_test_cases.copy()
                else:
                    # 随机采样
                    sampled_cases = random.sample(original_test_cases, target_len)
                
                # 更新test_cases
                data['extra_info']['test_cases'] = sampled_cases
                sampled_test_cases_counts.append(len(sampled_cases))
                
                # 写入新文件 - 使用json.dump而不是json.dumps
                json.dump(data, outfile, ensure_ascii=False)
                outfile.write('\n')  # 添加真正的换行符
                successful_samples += 1
                
            except json.JSONDecodeError as e:
                print(f"\n错误: 第{line_num}行JSON解析失败: {e}")
                skipped_lines += 1
                continue
            except Exception as e:
                print(f"\n错误: 第{line_num}行处理失败: {e}")
                skipped_lines += 1
                continue
    
    # 输出统计信息
    print("\n" + "=" * 50)
    print("📊 处理统计:")
    print(f"  总记录数: {total_lines}")
    print(f"  成功处理: {successful_samples}")
    print(f"  跳过记录: {skipped_lines}")
    
    if original_test_cases_counts:
        avg_original = sum(original_test_cases_counts) / len(original_test_cases_counts)
        avg_sampled = sum(sampled_test_cases_counts) / len(sampled_test_cases_counts)
        print(f"\n📈 test_cases统计:")
        print(f"  原始平均长度: {avg_original:.1f}")
        print(f"  采样后平均长度: {avg_sampled:.1f}")
        print(f"  最小原始长度: {min(original_test_cases_counts)}")
        print(f"  最大原始长度: {max(original_test_cases_counts)}")
    
    print("=" * 50)
    print(f"✅ 处理完成！")
    print(f"输出文件: {output_file}")
    print(f"文件命名规则: train_sampled_{original_len}_to_{target_len}.jsonl")


if __name__ == "__main__":
    main()