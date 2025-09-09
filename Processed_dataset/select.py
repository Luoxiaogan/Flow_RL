import json
import random

def select_random_data(input_file, output_file, num_samples=400):
    """
    从输入文件中随机选择指定数量的数据行，保存到输出文件
    """
    # 读取所有数据
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 随机选择指定数量的行
    if len(lines) < num_samples:
        print(f"警告: 文件只有 {len(lines)} 行数据，少于请求的 {num_samples} 行")
        selected_lines = lines
    else:
        selected_lines = random.sample(lines, num_samples)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(selected_lines)
    
    print(f"已从 {input_file} 中随机选择 {len(selected_lines)} 行数据保存到 {output_file}")

if __name__ == "__main__":
    input_file = "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/hotpotqa/train.jsonl"
    output_file = "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/hotpotqa/random_400.jsonl"

    select_random_data(input_file, output_file, 400)