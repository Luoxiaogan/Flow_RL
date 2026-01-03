"""
InternBootcamp VERL数据生成器
生成符合VERL格式的训练数据，支持HuggingFace chat格式
"""
import os
import sys
import json
import asyncio
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import random

from internbootcamp_utils import InternBootcampManager, classify_ability, get_task_type

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_examples_for_prompt(examples: List[Dict[str, Any]]) -> str:
    """格式化示例用于prompt"""
    formatted = []
    for i, example in enumerate(examples, 1):
        formatted.append(f"Example {i}:\n{example['prompt']}")
    return "\n\n".join(formatted)


def create_hf_chat_prompt(task_name: str, task_examples: List[Dict[str, Any]], 
                         task_description: str) -> List[Dict[str, str]]:
    """创建HuggingFace chat格式的prompt"""
    
    # System message
    system_message = {
        "role": "system",
        "content": """You are an expert at designing problem-solving workflows. Your task is to create a general workflow that can solve various instances of a specific problem type. The workflow should:
1. Understand the problem structure and constraints
2. Apply appropriate solving strategies
3. Ensure the solution meets all requirements
4. Be adaptable to different problem instances"""
    }
    
    # User message with task information
    user_content = f"""Task Type: {task_name}

Task Description:
{task_description}

Here are some example problems of this type:

{format_examples_for_prompt(task_examples)}

Please create a comprehensive workflow that can solve any problem of this type. The workflow should include:
1. Problem analysis strategy
2. Solution approach
3. Verification steps
4. Output formatting guidelines

Make the workflow general enough to handle various instances while being specific about the solving methodology."""
    
    user_message = {
        "role": "user",
        "content": user_content
    }
    
    return [system_message, user_message]


def generate_verl_entry(task_name: str, manager: InternBootcampManager, 
                       config: Dict[str, Any], entry_id: int) -> Optional[Dict[str, Any]]:
    """生成单个VERL数据条目"""
    try:
        # 生成任务示例
        n_examples = config['generation_config']['examples_per_task']
        examples = manager.generate_task_examples(task_name, n_examples=n_examples)
        
        # 获取任务描述
        description = manager.get_task_description(task_name)
        
        # 创建HF chat格式的prompt
        messages = create_hf_chat_prompt(task_name, examples, description)
        
        # 构建VERL格式数据
        verl_entry = {
            "data_source": f"internbootcamp_{task_name}",
            "prompt": messages,  # HF chat格式
            "ability": classify_ability(task_name),
            "reward_model": {
                "task_name": task_name,
                "test_cases": [ex["identity"] for ex in examples]
            },
            "extra_info": {
                "entry_id": entry_id,
                "task_type": get_task_type(task_name),
        logger.error(f"Failed to generate VERL entry for {task_name}: {e}")
        return None


def select_tasks(manager: InternBootcampManager, config: Dict[str, Any], 
                args: argparse.Namespace) -> List[str]:
    """根据配置和参数选择要处理的任务"""
    available_tasks = manager.get_available_tasks()
    
    # 命令行参数优先级最高
    if args.tasks:
        # 指定具体任务
        selected = []
        for task in args.tasks:
            if task in available_tasks:
                selected.append(task)
            else:
                logger.warning(f"Task '{task}' not found in available tasks")
        return selected
    
    elif args.all:
        # 处理所有任务
        logger.info(f"Processing all {len(available_tasks)} available tasks")
        return available_tasks
    
    else:
        # 使用配置文件中的设置
        mode = config['generation_config']['task_selection']['mode']
        
        if mode == 'manual':
            # 手动指定的任务列表
            manual_tasks = config['generation_config']['task_selection']['manual_tasks']
            selected = [task for task in manual_tasks if task in available_tasks]
            
        elif mode == 'random':
            # 随机选择
            count = min(
                config['generation_config']['task_selection']['auto_select_count'],
                len(available_tasks)
            )
            selected = random.sample(available_tasks, count)
            
        else:
            # 默认使用前N个
            count = min(
                config['generation_config']['task_selection'].get('auto_select_count', 10),
                len(available_tasks)
            )
            selected = available_tasks[:count]
    
    logger.info(f"Selected {len(selected)} tasks: {selected[:5]}{'...' if len(selected) > 5 else ''}")
    return selected


def main():
    parser = argparse.ArgumentParser(description='Generate VERL training data for InternBootcamp')
    
    # 任务选择参数
    task_group = parser.add_mutually_exclusive_group()
    task_group.add_argument('--tasks', nargs='+', help='Specific tasks to process')
    task_group.add_argument('--all', action='store_true', help='Process all available tasks')
    
    # 其他参数
    parser.add_argument('--prompts-per-task', type=int, help='Number of prompts per task')
    parser.add_argument('--examples-per-prompt', type=int, help='Number of examples per prompt')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--dry-run', action='store_true', help='Test run without saving data')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 覆盖配置中的参数
    if args.prompts_per_task:
        config['generation_config']['prompts_per_task'] = args.prompts_per_task
    if args.examples_per_prompt:
        config['generation_config']['examples_per_task'] = args.examples_per_prompt
    if args.output_dir:
        config['verl_config']['data_dir'] = args.output_dir
    
    # 创建输出目录
    output_dir = Path(config['verl_config']['data_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化manager
    logger.info("Initializing InternBootcamp manager...")
    manager = InternBootcampManager()
    
    # 显示统计信息
    stats = manager.get_task_stats()
    logger.info(f"Found {stats['successfully_loaded']} bootcamp tasks")
    
    # 选择任务
    selected_tasks = select_tasks(manager, config, args)
    
    if not selected_tasks:
        logger.error("No tasks selected for processing")
        return
    
    # 生成数据
    logger.info("Generating VERL data...")
    all_entries = []
    failed_tasks = []
    
    prompts_per_task = config['generation_config']['prompts_per_task']
    entry_id = 0
    
    for task_name in selected_tasks:
        logger.info(f"Processing task: {task_name}")
        task_success_count = 0
        
        for prompt_idx in range(prompts_per_task):
            # 为每个prompt生成不同的示例
            entry = generate_verl_entry(task_name, manager, config, entry_id)
            
            if entry:
                all_entries.append(entry)
                task_success_count += 1
                entry_id += 1
            else:
                logger.warning(f"Failed to generate prompt {prompt_idx + 1} for {task_name}")
        
        if task_success_count == 0:
            failed_tasks.append(task_name)
        else:
            logger.info(f"Generated {task_success_count}/{prompts_per_task} prompts for {task_name}")
    
    # 统计结果
    logger.info(f"\nGeneration complete:")
    logger.info(f"- Total entries: {len(all_entries)}")
    logger.info(f"- Successful tasks: {len(selected_tasks) - len(failed_tasks)}")
    logger.info(f"- Failed tasks: {len(failed_tasks)}")
    
    if failed_tasks:
        logger.warning(f"Failed tasks: {failed_tasks}")
    
    # 如果是dry run，只显示示例
    if args.dry_run:
        logger.info("\nDry run mode - showing first entry:")
        if all_entries:
            print(json.dumps(all_entries[0], indent=2, ensure_ascii=False))
        return
    
    # 分割训练集和测试集
    train_ratio = config['verl_config']['train_ratio']
    random.shuffle(all_entries)
    
    split_idx = int(len(all_entries) * train_ratio)
    train_entries = all_entries[:split_idx]
    test_entries = all_entries[split_idx:]
    
    # 保存数据
    output_format = config['verl_config']['output_format']
    
    if output_format == 'parquet':
        # 保存为parquet格式
        train_df = pd.DataFrame(train_entries)
        test_df = pd.DataFrame(test_entries)
        
        train_path = output_dir / "internbootcamp_verl_train.parquet"
        test_path = output_dir / "internbootcamp_verl_test.parquet"
        
        train_df.to_parquet(train_path, index=False)
        test_df.to_parquet(test_path, index=False)
        
        logger.info(f"Saved training data to {train_path} ({len(train_entries)} entries)")
        logger.info(f"Saved test data to {test_path} ({len(test_entries)} entries)")
        
    else:
        # 保存为JSON格式
        train_path = output_dir / "internbootcamp_verl_train.json"
        test_path = output_dir / "internbootcamp_verl_test.json"
        
        with open(train_path, 'w', encoding='utf-8') as f:
            json.dump(train_entries, f, indent=2, ensure_ascii=False)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            json.dump(test_entries, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved training data to {train_path} ({len(train_entries)} entries)")
        logger.info(f"Saved test data to {test_path} ({len(test_entries)} entries)")
    
    # 保存元数据
    metadata = {
        "generation_time": datetime.now().isoformat(),
        "config": config,
        "stats": {
            "total_entries": len(all_entries),
            "train_entries": len(train_entries),
            "test_entries": len(test_entries),
            "successful_tasks": len(selected_tasks) - len(failed_tasks),
            "failed_tasks": failed_tasks
        }
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved metadata to {metadata_path}")


if __name__ == "__main__":
    main()