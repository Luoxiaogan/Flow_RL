"""
VERL数据生成器 - 简化版
直接生成HuggingFace chat格式，无需API调用
"""
import os
import sys
import json
import asyncio
import argparse
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import random
import time

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from internbootcamp_utils import InternBootcampManager, classify_ability, get_task_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VERLDataGenerator:
    """VERL数据生成器 - 简化版，只生成chat格式"""
    
    def __init__(self, config_path: str = None):
        """初始化生成器"""
        # 简化配置，不依赖外部配置文件
        self.config = {
            'generation_config': {
                'examples_per_task': 3
            }
        }
        
        # 初始化管理器
        self.manager = InternBootcampManager()
        
        # 任务显示名称映射 (task_name -> display_name)
        self.task_display_names = {}
        
        # 生成统计
        self.generation_stats = {
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "by_task": {}
        }
    
    def set_task_display_names(self, display_names: Dict[str, str]):
        """设置任务显示名称映射"""
        self.task_display_names = display_names
        logger.info(f"Set display names for {len(display_names)} tasks")
    
    def get_task_display_name(self, task_name: str) -> str:
        """获取任务的显示名称，如果没有设置则返回原始名称"""
        return self.task_display_names.get(task_name, task_name)
    
    def load_prompt_templates(self) -> Tuple[str, str, str, List[str]]:
        """加载prompt模板，类似workflow_generator的方法"""
        try:
            # 导入conditions模块
            from ScoreFlow.scripts.internbootcamp.conditions import (
                META_PROMPTS, SYSTEM_PROMPT, START_PROMPT_PREDEFINED, 
                START_PROMPT_FLEXIBLE, END_PROMPT
            )
            return START_PROMPT_PREDEFINED, END_PROMPT, SYSTEM_PROMPT, META_PROMPTS
        except ImportError as e:
            logger.warning(f"Failed to load prompt templates from conditions: {e}")
            # 使用默认值
            return "", "", "You are a helpful AI assistant.", []

    def create_chat_messages(self, task_name: str, task_description: str, 
                           examples: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """创建HuggingFace chat格式的对话消息"""
        # 加载prompt模板
        start_prompt, end_prompt, system_prompt, meta_prompts = self.load_prompt_templates()
        
        # 构建prompt内容，包含task_description和一个example
        prompt_content = f"Task: {task_name}\n\n{task_description}"
        
        # 添加一个example（如果有的话）
        if examples and len(examples) > 0:
            example = examples[0]  # 只取第一个example
            example_content = example.get('prompt', json.dumps(example, indent=2, ensure_ascii=False))
            prompt_content += f"\n\nExample:\n{example_content}"
        
        # 使用start_prompt模板
        user_prompt_str = start_prompt.format(prompt_text=prompt_content)
        user_prompt_str += end_prompt
        
        # 创建消息格式（只包含user消息，不包含system消息）
        messages = [
            {"role": "user", "content": user_prompt_str}
        ]
        
        return messages
    
    async def generate_single_entry(self, task_name: str, entry_id: int,
                                  workflow_type: str = "predefined", timeout: float = 3.0) -> Optional[Dict[str, Any]]:
        """生成单个VERL数据条目 - 简化版，带超时功能"""
        try:
            # 使用asyncio.wait_for添加超时
            return await asyncio.wait_for(
                self._generate_single_entry_impl(task_name, entry_id, workflow_type),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Task {task_name} timed out after {timeout} seconds, skipping...")
            return None
        except Exception as e:
            logger.error(f"Failed to generate entry for {task_name}: {e}")
            return None

    async def _generate_single_entry_impl(self, task_name: str, entry_id: int,
                                    workflow_type: str = "predefined") -> Dict[str, Any]:
        """实际的生成逻辑，不包含超时处理"""
        start_time = time.time()
        
        # 尝试生成任务示例
        examples = []
        try:
            # 生成示例数量，确保至少生成1个用于prompt
            n_examples = max(1, self.config['generation_config']['examples_per_task'])
            examples = self.manager.generate_task_examples(task_name, n_examples=n_examples)
        except Exception as e:
            logger.warning(f"Failed to generate examples for {task_name}: {e}")
            examples = []  # 即使没有示例也继续
        
        # 获取任务描述
        try:
            description = self.manager.get_task_description(task_name)
        except Exception as e:
            logger.warning(f"Failed to get description for {task_name}: {e}")
            description = f"Task: {task_name}"
        
        # 使用显示名称作为描述（如果设置了的话）
        display_name = self.get_task_display_name(task_name)
        if display_name != task_name:
            description = display_name
        
        # 创建chat格式的消息，传递examples
        messages = self.create_chat_messages(task_name, description, examples)
        
        # 构建VERL条目
        verl_entry = {
            "data_source": f"internbootcamp_{task_name}",
            "prompt": messages,  # HuggingFace chat格式
            "ability": classify_ability(task_name),
            "reward_model": {
                "ground_truth": "default"
            },
            "extra_info": {
                "score": 1.0,  # 默认分数
                "task_name": task_name,
                "test_cases": [str(ex.get("identity", f"example_{i}")) for i, ex in enumerate(examples)] if examples else [],
                "entry_id": entry_id,
                "task_type": get_task_type(task_name),
                "workflow_type": workflow_type,
                "num_examples": len(examples),
                "timestamp": datetime.now().isoformat(),
                "generation_time": time.time() - start_time
            }
        }
        
        return verl_entry
    
    async def generate_dataset(self, tasks: List[str], entries_per_task: int,
                             workflow_types: Optional[List[str]] = None, 
                             timeout_per_task: float = 3.0) -> List[Dict[str, Any]]:
        """生成完整的数据集，带超时功能"""
        if workflow_types is None:
            workflow_types = ["predefined"]
        
        all_entries = []
        entry_id = 0
        timeout_count = 0  # 记录超时次数
        
        total_tasks = len(tasks) * len(workflow_types) * entries_per_task
        logger.info(f"Generating {total_tasks} VERL entries with {timeout_per_task}s timeout per task...")
        
        for task_name in tasks:
            self.generation_stats["by_task"][task_name] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "timeout": 0  # 新增超时统计
            }
            
            for workflow_type in workflow_types:
                for i in range(entries_per_task):
                    entry = await self.generate_single_entry(task_name, entry_id, workflow_type, timeout_per_task)
                    
                    if entry:
                        all_entries.append(entry)
                        self.generation_stats["successful"] += 1
                        self.generation_stats["by_task"][task_name]["successful"] += 1
                        logger.info(f"✓ Generated entry {entry_id} for {task_name}")
                    else:
                        # 检查是否是超时（通过查看最近的日志或其他方式）
                        # 简单的处理：假设None返回可能是超时或其他错误
                        self.generation_stats["failed"] += 1
                        self.generation_stats["by_task"][task_name]["failed"] += 1
                        logger.warning(f"✗ Failed to generate entry {entry_id} for {task_name}")
                    
                    self.generation_stats["total_generated"] += 1
                    self.generation_stats["by_task"][task_name]["total"] += 1
                    entry_id += 1
        
        logger.info(f"Generation completed. Total timeouts: {timeout_count}")
        return all_entries
    
    def save_to_parquet(self, entries: List[Dict[str, Any]], output_path: str):
        """保存数据为Parquet格式"""
        # 将嵌套的字典转换为JSON字符串以便存储
        processed_entries = []
        for entry in entries:
            processed_entry = entry.copy()
            # 将prompt（消息列表）转换为JSON字符串
            processed_entry['prompt'] = json.dumps(entry['prompt'], ensure_ascii=False)
            # 将其他嵌套字段也转换
            processed_entry['reward_model'] = json.dumps(entry['reward_model'], ensure_ascii=False)
            processed_entry['extra_info'] = json.dumps(entry['extra_info'], ensure_ascii=False)
            processed_entries.append(processed_entry)
        
        # 创建DataFrame
        df = pd.DataFrame(processed_entries)
        
        # 保存为Parquet
        df.to_parquet(output_path, index=False)
        logger.info(f"Saved {len(entries)} entries to {output_path}")
    
    def save_to_json(self, entries: List[Dict[str, Any]], output_path: str):
        """保存数据为JSON格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(entries)} entries to {output_path}")
    
    def split_and_save_dataset(self, entries: List[Dict[str, Any]], output_dir: str,
                              train_ratio: float = 0.8):
        """分割并保存数据集"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 随机打乱数据
        random.shuffle(entries)
        
        # 分割数据
        split_idx = int(len(entries) * train_ratio)
        train_entries = entries[:split_idx]
        test_entries = entries[split_idx:]
        
        # 保存为Parquet格式
        train_parquet = output_path / "train.parquet"
        test_parquet = output_path / "test.parquet"
        self.save_to_parquet(train_entries, str(train_parquet))
        self.save_to_parquet(test_entries, str(test_parquet))
        
        # 同时保存为JSON格式（方便查看）
        train_json = output_path / "train.json"
        test_json = output_path / "test.json"
        self.save_to_json(train_entries, str(train_json))
        self.save_to_json(test_entries, str(test_json))
        
        # 保存统计信息
        stats = {
            "generation_stats": self.generation_stats,
            "dataset_info": {
                "total_entries": len(entries),
                "train_entries": len(train_entries),
                "test_entries": len(test_entries),
                "train_ratio": train_ratio
            },
            "timestamp": datetime.now().isoformat()
        }
        
        stats_path = output_path / "generation_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset saved to {output_dir}")
        logger.info(f"Training set: {len(train_entries)} entries")
        logger.info(f"Test set: {len(test_entries)} entries")
        
        return stats


async def main():
    parser = argparse.ArgumentParser(description='Generate VERL training data - Simplified Version')
    
    # 任务选择参数
    parser.add_argument('--tasks', nargs='+', 
                       default=['sudoku_4x4_easy', 'minesweeper_5x5'],
                       help='Tasks to generate data for')
    parser.add_argument('--entries-per-task', type=int, default=5,
                       help='Number of entries per task')
    
    # 新增：随机任务数量参数
    parser.add_argument('--random-task-count', type=int, default=None,
                       help='Number of random tasks to generate (overrides --tasks if specified)')
    
    # 输出参数
    parser.add_argument('--output-dir', default='verl_data_simple',
                       help='Output directory for data files')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='Train/test split ratio')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = VERLDataGenerator()
    
    # 获取可用任务
    available_tasks = generator.manager.get_available_tasks()
    
    # 确定要使用的任务列表
    if args.random_task_count is not None:
        # 如果指定了随机任务数量，从可用任务中随机选择
        if args.random_task_count > len(available_tasks):
            logger.warning(f"Requested {args.random_task_count} tasks, but only {len(available_tasks)} available. Using all available tasks.")
            valid_tasks = available_tasks.copy()
        else:
            # 随机选择指定数量的任务
            valid_tasks = random.sample(available_tasks, args.random_task_count)
            logger.info(f"Randomly selected {len(valid_tasks)} tasks from {len(available_tasks)} available tasks")
    else:
        # 使用指定的任务列表
        valid_tasks = []
        for task in args.tasks:
            if task in available_tasks:
                valid_tasks.append(task)
            else:
                logger.warning(f"Task '{task}' not found in available tasks")
    
    if not valid_tasks:
        logger.error("No valid tasks specified")
        return
    
    logger.info(f"Using {len(valid_tasks)} tasks: {valid_tasks}")
    
    # 生成数据集
    entries = await generator.generate_dataset(
        valid_tasks, 
        args.entries_per_task,
        ["simple"]  # 简化的workflow类型
    )
    
    if not entries:
        logger.error("No entries generated")
        return
    
    # 保存数据集
    stats = generator.split_and_save_dataset(
        entries, 
        args.output_dir,
        args.train_ratio
    )
    
    # 打印统计信息
    logger.info("\n" + "="*50)
    logger.info("GENERATION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total entries generated: {stats['generation_stats']['total_generated']}")
    logger.info(f"Successful: {stats['generation_stats']['successful']}")
    logger.info(f"Failed: {stats['generation_stats']['failed']}")
    logger.info(f"Success rate: {stats['generation_stats']['successful'] / stats['generation_stats']['total_generated'] * 100:.1f}%")
    
    logger.info(f"\nOutput saved to: {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())