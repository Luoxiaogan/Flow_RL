import argparse
import subprocess
import random
import math
import os
import json
import time

def create_generation_tasks(total_problems: int, min_sample: int, max_sample: int) -> list[list[int]]:
    """
    从总问题数中创建随机抽样任务列表。
    - 随机打乱所有问题的索引。
    - 将索引分组成大小在 [min_sample, max_sample] 之间的随机块。
    - 确保所有索引都被使用一次。
    """
    print(f"正在从 {total_problems} 个问题中创建随机抽样任务...")
    indices = list(range(total_problems))
    random.shuffle(indices)
    
    tasks = []
    i = 0
    while i < len(indices):
        chunk_size = random.randint(min_sample, max_sample)
        chunk = indices[i:i + chunk_size]
        if not chunk:
            continue
        tasks.append(chunk)
        i += chunk_size
        
    print(f"成功创建 {len(tasks)} 个生成任务。")
    return tasks

def main():
    parser = argparse.ArgumentParser(description="大规模工作流生成调度器")
    
    # 调度器配置
    parser.add_argument('--benchmark', type=str, required=True, help='要处理的基准测试名称，例如: GSM8K')
    parser.add_argument('--total-problems', type=int, required=True, help='数据集中问题的总数')
    parser.add_argument('--min-sample-size', type=int, default=2, help='每个工作流最少使用的问题样本数')
    parser.add_argument('--max-sample-size', type=int, default=4, help='每个工作流最多使用的问题样本数')
    parser.add_argument('--batch-size', type=int, default=15, help='每批次并行处理的工作流数量')

    # --- 以下参数将直接传递给 workflow_orchestrator_v5.py ---
    parser.add_argument('--api-pool', type=str, required=True, help='API配置池 (JSON string)')
    parser.add_argument('--exec-llm', type=str, required=True, help='执行LLM配置 (JSON string)')
    parser.add_argument('--workspace-path', type=str, required=True, help='工作空间路径')
    parser.add_argument('--dataset-base-path', type=str, required=True, help='数据集基础路径')
    parser.add_argument('--gsm8k-dataset-path', type=str, help='特定数据集路径')
    parser.add_argument('--training-data-output', type=str, required=True, help='训练数据输出文件路径 (JSONL)')
    parser.add_argument('--log-level', type=str, default='INFO', help='日志级别')
    parser.add_argument('--max-concurrent-tasks', type=int, default=10, help='最大并发任务数')
    parser.add_argument('--workflow-timeout', type=int, default=120, help='工作流超时时间(秒)')
    
    args = parser.parse_args()

    # 1. 生成所有任务
    all_tasks = create_generation_tasks(args.total_problems, args.min_sample_size, args.max_sample_size)
    
    # 2. 分批处理
    num_batches = math.ceil(len(all_tasks) / args.batch_size)
    print(f"任务将被分为 {num_batches} 个批次进行处理，每批次最多 {args.batch_size} 个任务。")
    
    for i in range(num_batches):
        start_time = time.time()
        print("\n" + "="*80)
        print(f"正在处理批次 {i+1}/{num_batches}...")
        
        batch_tasks = all_tasks[i * args.batch_size : (i + 1) * args.batch_size]
        
        # 将任务块格式化为 orchestrator 可接受的字符串
        # e.g., [[1,2], [5,8,9]] -> "1_2,5_8_9"
        task_strings = [ "_".join(map(str, task)) for task in batch_tasks ]
        generation_tasks_arg = f"{args.benchmark}:{','.join(task_strings)}"
        
        # 3. 构建并执行子进程命令
        command = [
            'python3', 'workflow_orchestrator_v5.py',
            '--api-pool', args.api_pool,
            '--exec-llm', args.exec_llm,
            '--generation-tasks', generation_tasks_arg,
            '--workspace-path', args.workspace_path,
            '--dataset-base-path', args.dataset_base_path,
            '--training-data-output', args.training_data_output,
            '--log-level', args.log_level,
            '--max-concurrent-tasks', str(args.max_concurrent_tasks),
            '--workflow-timeout', str(args.workflow_timeout),
            '--no-save-workflows' # <--- 关键：禁用单个py文件保存
        ]
        if args.gsm8k_dataset_path:
            command.extend(['--gsm8k-dataset-path', args.gsm8k_dataset_path])
            
        try:
            print(f"执行命令: {' '.join(command)}")
            subprocess.run(command, check=True, text=True)
            end_time = time.time()
            print(f"批次 {i+1} 处理完成，耗时: {end_time - start_time:.2f} 秒。")
        except subprocess.CalledProcessError as e:
            print(f"批次 {i+1} 执行失败! 错误: {e}")
            print("将继续处理下一个批次...")
        except FileNotFoundError:
            print("错误: 'python3' 命令未找到。请确保Python3已安装并在您的PATH中。")
            break

    print("\n" + "="*80)
    print("所有批次处理完毕！")

if __name__ == "__main__":
    main()