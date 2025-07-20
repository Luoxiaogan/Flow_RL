import argparse
import subprocess
import random
import math
import os
import json
import time
import glob
import asyncio
from typing import List

async def execute_workflow_async(exec_command: List[str], py_file: str) -> None:
    """异步执行单个工作流"""
    try:
        print(f"\n执行验证命令: {' '.join(exec_command)}")
        # 使用 asyncio.create_subprocess_exec 执行命令
        process = await asyncio.create_subprocess_exec(
            *exec_command,
            stdout=None,  # 不捕获stdout，让其直接输出到终端
            stderr=None   # 不捕获stderr，让其直接输出到终端
        )
        # 等待进程完成
        returncode = await process.wait()
        
        if returncode != 0:
            print(f"工作流 {os.path.basename(py_file)} 执行失败或验证未通过。详情请查看日志和CSV结果。")
    except Exception as e:
        print(f"调用执行器时发生未知错误: {e}")

async def execute_workflows_parallel(exec_commands_and_files: List[tuple], max_concurrent: int = 5) -> None:
    """并行执行多个工作流，限制最大并发数"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_with_semaphore(exec_command, py_file):
        async with semaphore:
            await execute_workflow_async(exec_command, py_file)
    
    tasks = []
    for exec_command, py_file in exec_commands_and_files:
        task = asyncio.create_task(execute_with_semaphore(exec_command, py_file))
        tasks.append(task)
    
    await asyncio.gather(*tasks)

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
    parser = argparse.ArgumentParser(description="大规模工作流生成与执行调度器 V2")
    
    # === 调度器配置 ===
    parser.add_argument('--benchmark', type=str, required=True, help='要处理的基准测试名称，例如: gsm8k')
    parser.add_argument('--total-problems', type=int, required=True, help='数据集中问题的总数')
    parser.add_argument('--min-sample-size', type=int, default=2, help='每个工作流最少使用的问题样本数')
    parser.add_argument('--max-sample-size', type=int, default=4, help='每个工作流最多使用的问题样本数')
    parser.add_argument('--batch-size', type=int, default=15, help='每批次并行生成的工作流数量')

    # === 传递给子脚本的通用参数 ===
    parser.add_argument('--api-pool', type=str, required=True, help='API配置池 (JSON string)')
    parser.add_argument('--exec-llm', type=str, required=True, help='执行LLM配置 (JSON string)')
    parser.add_argument('--workspace-path', type=str, required=True, help='工作空间路径')
    
    # --- 参数修改：使用统一的数据集路径 ---
    parser.add_argument('--dataset-path', type=str, required=True, help='数据集文件的完整路径，例如 /path/to/data.jsonl')
    
    parser.add_argument('--training-data-output', type=str, help='训练数据输出文件路径 (JSONL)')
    parser.add_argument('--log-level', type=str, default='INFO', help='日志级别')
    parser.add_argument('--max-concurrent-tasks', type=int, default=10, help='生成器内部的最大并发任务数')
    parser.add_argument('--workflow-timeout', type=int, default=120, help='执行器的工作流超时时间(秒)')
    parser.add_argument('--max-concurrent-executions', type=int, default=5, help='并行执行工作流的最大并发数')
    parser.add_argument('--parallelism', type=int, default=2, help='每个数据组合生成的工作流并行度')
    
    args = parser.parse_args()

    # 1. 生成所有任务
    all_tasks = create_generation_tasks(args.total_problems, args.min_sample_size, args.max_sample_size)
    
    # 2. 分批处理
    num_batches = math.ceil(len(all_tasks) / args.batch_size)
    print(f"任务将被分为 {num_batches} 个批次进行处理，每批次最多 {args.batch_size} 个任务。")
    
    total_processed_workflows = 0
    for i in range(num_batches):
        batch_start_time = time.time()
        print("\n" + "="*80)
        print(f"正在处理批次 {i+1}/{num_batches}...")
        
        batch_tasks = all_tasks[i * args.batch_size : (i + 1) * args.batch_size]
        if not batch_tasks:
            continue

        # 将任务块格式化为 generator 可接受的字符串
        # e.g., [[1,2], [5,8,9]] -> "1_2,5_8_9"
        task_strings = [ "_".join(map(str, task)) for task in batch_tasks ]
        generation_tasks_arg = ','.join(task_strings)

        # =================================================================
        # 阶段一：调用 workflow_generator.py
        # =================================================================
        print(f"--- 阶段 1: 为批次 {i+1} 生成 {len(batch_tasks)} 个工作流 ---")
        
        ### 修改点: 计算当前批次的起始索引，并将其传递给生成器 ###
        start_index = i * args.batch_size
        
        gen_command = [
            'python3', 'workflow_generator.py',
            '--api-pool', args.api_pool,
            '--benchmark', args.benchmark,
            '--dataset-path', args.dataset_path,
            '--generation-tasks', generation_tasks_arg,
            '--workspace-path', args.workspace_path,
            '--log-level', args.log_level,
            '--max-concurrent-tasks', str(args.max_concurrent_tasks),
            # 新增参数传递
            '--id-start-index', str(start_index),
            '--parallelism', str(args.parallelism)
        ]
        
        if args.training_data_output:
            gen_command.extend(['--training-data-output', args.training_data_output])
            
        try:
            print(f"执行生成命令: {' '.join(gen_command)}")
            subprocess.run(gen_command, check=True, text=True)
            print("生成阶段成功。")
        except subprocess.CalledProcessError as e:
            print(f"批次 {i+1} 的生成阶段失败! 错误: {e}\n跳过此批次。")
            continue
        except FileNotFoundError:
            print("错误: 'python3' 命令未找到。请确保Python3已安装并在您的PATH中。")
            break

        # =================================================================
        # 阶段二：调用 workflow_executor.py
        # =================================================================
        print(f"--- 阶段 2: 逐个执行并验证新生成的工作流 ---")

        # 构造此次批次生成的工作流ID，并找到对应的 .py 文件
        # 注意：这里的逻辑现在与 generator 的新逻辑完全匹配了。
        
        generated_files_to_execute = []
        for j in range(len(batch_tasks)):
            # ID 从0开始，但我们是从总任务数中分批的，所以ID需要全局唯一
            workflow_index = i * args.batch_size + j
            
            # 对于每个数据组合，现在有多个版本的工作流
            for k in range(args.parallelism):
                workflow_id = f"{args.benchmark.lower()}_{workflow_index}_{k}"
                
                # 构造 .py 文件路径
                py_file_path = os.path.join(args.workspace_path, "generated_workflows", args.benchmark, f"{workflow_id}.py")
                
                if os.path.exists(py_file_path):
                    generated_files_to_execute.append(py_file_path)
                else:
                    print(f"警告: 未找到预期生成的文件 {py_file_path}，可能该工作流生成失败，将跳过。")

        # 准备所有执行命令
        exec_commands_and_files = []
        for py_file in generated_files_to_execute:
            exec_command = [
                'python3', 'workflow_executor.py',
                '--workflow-path', py_file,
                '--exec-llm', args.exec_llm,
                '--workspace-path', args.workspace_path,
                '--workflow-timeout', str(args.workflow_timeout),
                '--log-level', args.log_level
            ]
            exec_commands_and_files.append((exec_command, py_file))
        
        # 并行执行所有工作流验证
        print(f"并行执行 {len(exec_commands_and_files)} 个工作流验证（最多 {args.max_concurrent_executions} 个并发）...")
        asyncio.run(execute_workflows_parallel(exec_commands_and_files, max_concurrent=args.max_concurrent_executions))
        
        total_processed_workflows += len(generated_files_to_execute)
        batch_end_time = time.time()
        print(f"批次 {i+1} 处理完成，耗时: {batch_end_time - batch_start_time:.2f} 秒。")

    print("\n" + "="*80)
    print(f"所有批次处理完毕！总共处理了 {total_processed_workflows} 个工作流。")
    print(f"所有结果保存在: {os.path.join(args.workspace_path, 'execution_results.csv')}")
    if args.training_data_output:
        print(f"训练数据保存在: {args.training_data_output}")

if __name__ == "__main__":
    main()