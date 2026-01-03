"""
InternBootcamp VERL Training Data Generator
基于原始脚本，最小化修改，生成VERL格式的训练数据

Usage Examples:
===============

1. Use default configuration from config.yaml:
   python internbootcamp_generate_verl_training_data.py

2. Override specific parameters:
   python internbootcamp_generate_verl_training_data.py --entries-per-task 10 --max-tasks 5

3. Specify custom output directory:
   python internbootcamp_generate_verl_training_data.py --output-dir custom_output

4. Use analysis file for filtering tasks:
   python internbootcamp_generate_verl_training_data.py --analysis-file analysis.jsonl

5. Specify specific tasks to generate:
   python internbootcamp_generate_verl_training_data.py --tasks task1 task2 task3

6. Custom train/test split ratio:
   python internbootcamp_generate_verl_training_data.py --train-ratio 0.9

7. Use custom config file:
   python internbootcamp_generate_verl_training_data.py --config /path/to/custom_config.yaml

8. Override timeout settings:
   python internbootcamp_generate_verl_training_data.py --timeout-per-task 5.0

9. Full example with multiple overrides:
   python internbootcamp_generate_verl_training_data.py \
       --config ../config.yaml \
       --entries-per-task 20 \
       --max-tasks 10 \
       --output-dir production_data \
       --train-ratio 0.85 \
       --timeout-per-task 10.0

Default Configuration:
=====================
The script loads default values from New_evaluation_and_RL/config.yaml
Command-line arguments override config file values.

Key Configuration Options (from config.yaml):
- data_generation.output_dir: Default output directory
- data_generation.default_test_cases_per_entry: Number of test cases per entry
- data_generation.default_train_proportion: Train/test split ratio
- project_root: Base directory for all relative paths
"""

import os
import sys
import json
import asyncio
import argparse
import pandas as pd
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time
import yaml

# Add project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# 添加InternBootcamp路径
INTERNBOOTCAMP_ROOT = PROJECT_ROOT / "InternBootcamp"
if INTERNBOOTCAMP_ROOT.exists():
    sys.path.insert(0, str(INTERNBOOTCAMP_ROOT))

# 导入原始的InternBootcampManager（从Test_FILE照搬）
sys.path.append(str(PROJECT_ROOT / "Test_FILE" / "verl_internbootcamp"))
from internbootcamp_utils import InternBootcampManager, classify_ability, get_task_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        配置字典
    """
    if config_path is None:
        # 默认配置文件路径
        config_path = PROJECT_ROOT / "New_evaluation_and_RL" / "config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using built-in defaults")
        # 返回内置默认配置
        return {
            'data_generation': {
                'output_dir': 'New_evaluation_and_RL/parquet_and_jsonl_data',
                'default_test_cases_per_entry': 5,
                'default_train_proportion': 0.8
            },
            'project_root': PROJECT_ROOT
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 处理project_root - 转换为Path对象
    if 'project_root' in config:
        config['project_root'] = Path(config['project_root'])
    else:
        config['project_root'] = PROJECT_ROOT
    
    # 确保data_generation部分存在
    if 'data_generation' not in config:
        config['data_generation'] = {
            'output_dir': 'New_evaluation_and_RL/parquet_and_jsonl_data',
            'default_test_cases_per_entry': 5,
            'default_train_proportion': 0.8
        }
    
    logger.info(f"Loaded config from {config_path}")
    return config


class InternBootcampVERLDataGenerator:
    """InternBootcamp VERL数据生成器 - 基于原始generate_verl_data.py"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            config: 配置字典，通常从config.yaml加载
        """
        # 使用传入的配置或默认配置
        if config:
            self.full_config = config
            self.config = {
                'generation_config': {
                    'examples_per_task': config.get('data_generation', {}).get('default_test_cases_per_entry', 3)
                }
            }
            # 设置输出目录
            project_root = config.get('project_root', PROJECT_ROOT)
            output_dir = config.get('data_generation', {}).get('output_dir', 'internbootcamp_data')
            if Path(output_dir).is_absolute():
                self.output_dir = Path(output_dir)
            else:
                self.output_dir = project_root / output_dir / "internbootcamp"
        else:
            # 使用默认配置
            self.full_config = {}
            self.config = {
                'generation_config': {
                    'examples_per_task': 3
                }
            }
            self.output_dir = CURRENT_DIR / "internbootcamp_data"
        
        # 初始化管理器（照搬原始）
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
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def set_task_display_names(self, display_names: Dict[str, str]):
        """设置任务显示名称映射（照搬原始）"""
        self.task_display_names = display_names
        logger.info(f"Set display names for {len(display_names)} tasks")
    
    def get_task_display_name(self, task_name: str) -> str:
        """获取任务的显示名称（照搬原始）"""
        return self.task_display_names.get(task_name, task_name)
    
    def load_prompt_templates(self) -> Tuple[str, str, str, List[str]]:
        """加载prompt模板（照搬原始）"""
        try:
            # 尝试导入internbootcamp的conditions模块
            from ScoreFlow.scripts.internbootcamp.conditions import (
                META_PROMPTS, SYSTEM_PROMPT, START_PROMPT, END_PROMPT
            )
            return START_PROMPT, END_PROMPT, SYSTEM_PROMPT, META_PROMPTS
        except ImportError as e:
            logger.warning(f"Failed to load prompt templates from conditions: {e}")
            # 使用默认值
            return "", "", "You are a helpful AI assistant.", []
    
    def create_chat_messages(self, task_name: str, task_description: str, 
                           examples: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """创建HuggingFace chat格式的对话消息（照搬原始）"""
        # 加载prompt模板
        start_prompt, end_prompt, system_prompt, meta_prompts = self.load_prompt_templates()
        
        # 构建prompt内容，包含task_description和一个example
        prompt_content = f"Task: {task_name}\n\n{task_description}"
        
        # 使用start_prompt模板
        user_prompt_str = start_prompt.format(prompt_text=prompt_content) if start_prompt else prompt_content
        
        # 添加一个example（如果有的话）
        if examples and len(examples) > 0:
            example = examples[0]  # 只取第一个example
            example_content = example.get('prompt', json.dumps(example, indent=2, ensure_ascii=False))
            user_prompt_str += f"\n\nExample:\n{example_content}"
        
        user_prompt_str += end_prompt if end_prompt else ""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_str}
        ]
        
        return messages
    
    async def generate_single_entry(self, task_name: str, entry_id: int,
                                  timeout: float = 3.0) -> Optional[Dict[str, Any]]:
        """生成单个VERL数据条目（照搬原始，带超时功能）"""
        try:
            # 使用asyncio.wait_for添加超时
            return await asyncio.wait_for(
                self._generate_single_entry_impl(task_name, entry_id),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Task {task_name} timed out after {timeout} seconds, skipping...")
            return None
        except Exception as e:
            import traceback
            logger.error(f"Failed to generate entry for {task_name}: {e}\n{traceback.format_exc()}")
            return None

    async def _generate_single_entry_impl(self, task_name: str, entry_id: int) -> Dict[str, Any]:
        """实际的生成逻辑（照搬原始）"""
        start_time = time.time()
        
        # 尝试生成任务示例
        examples = []
        try:
            # 生成示例数量，确保至少生成1个用于prompt
            n_examples = max(1, self.config['generation_config']['examples_per_task'])
            examples = self.manager.generate_task_examples(task_name, n_examples=n_examples)
        except Exception as e:
            logger.warning(f"Failed to generate examples for {task_name}: {e}")
            import traceback
            traceback.print_exc()
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
        
        # 构建VERL条目（照搬原始格式）
        verl_entry = {
            "data_source": f"internbootcamp",
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
                "num_examples": len(examples),
                "timestamp": datetime.now().isoformat(),
                "generation_time": time.time() - start_time
            }
        }
        
        return verl_entry
    
    async def generate_dataset(self, tasks: List[str], entries_per_task: int,
                             timeout_per_task: float = 3.0) -> List[Dict[str, Any]]:
        """生成完整的数据集（照搬原始）"""
        all_entries = []
        entry_id = 0
        timeout_count = 0  # 记录超时次数
        
        total_tasks = len(tasks) * entries_per_task
        logger.info(f"Generating {total_tasks} VERL entries with {timeout_per_task}s timeout per task...")
        
        for task_name in tasks:
            self.generation_stats["by_task"][task_name] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "timeout": 0  # 新增超时统计
            }
            
            for i in range(entries_per_task):
                entry = await self.generate_single_entry(task_name, entry_id, timeout_per_task)
                
                if entry:
                    all_entries.append(entry)
                    self.generation_stats["successful"] += 1
                    self.generation_stats["by_task"][task_name]["successful"] += 1
                    logger.info(f"✓ Generated entry {entry_id} for {task_name}")
                else:
                    self.generation_stats["failed"] += 1
                    self.generation_stats["by_task"][task_name]["failed"] += 1
                    logger.warning(f"✗ Failed to generate entry {entry_id} for {task_name}")
                
                self.generation_stats["total_generated"] += 1
                self.generation_stats["by_task"][task_name]["total"] += 1
                entry_id += 1
        
        logger.info(f"Generation completed. Total timeouts: {timeout_count}")
        return all_entries
    
    def save_to_parquet(self, entries: List[Dict[str, Any]], output_path: str):
        """保存数据为Parquet格式（照搬原始）"""
        # 创建DataFrame
        df = pd.DataFrame(entries)
        
        # 保存为Parquet
        df.to_parquet(output_path, index=False)
        logger.info(f"Saved {len(entries)} entries to {output_path}")
    
    def save_to_jsonl(self, entries: List[Dict[str, Any]], output_path: str):
        """保存数据为JSONL格式（新增，方便查看）"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        logger.info(f"Saved {len(entries)} entries to {output_path}")
    
    def split_and_save_dataset(self, entries: List[Dict[str, Any]], output_dir: str = None,
                              train_ratio: float = 0.8):
        """分割并保存数据集（照搬原始）"""
        if output_dir is None:
            output_dir = self.output_dir
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 随机打乱数据
        random.shuffle(entries)
        
        # 分割数据
        split_idx = int(len(entries) * train_ratio)
        train_entries = entries[:split_idx]
        test_entries = entries[split_idx:]
        
        # 保存为Parquet格式
        if train_entries:
            train_parquet = output_dir / "train.parquet"
            self.save_to_parquet(train_entries, str(train_parquet))
        
        if test_entries:
            test_parquet = output_dir / "test.parquet"
            self.save_to_parquet(test_entries, str(test_parquet))
        
        # 同时保存为JSONL格式（方便查看）
        if train_entries:
            train_jsonl = output_dir / "train.jsonl"
            self.save_to_jsonl(train_entries, str(train_jsonl))
        
        if test_entries:
            test_jsonl = output_dir / "test.jsonl"
            self.save_to_jsonl(test_entries, str(test_jsonl))
        
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
        
        stats_path = output_dir / "generation_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset saved to {output_dir}")
        logger.info(f"Training set: {len(train_entries)} entries")
        logger.info(f"Test set: {len(test_entries)} entries")
        
        return stats


# ===== 过滤功能（从filter_and_generate_verl.py照搬） =====
class FilteredVERLGenerator:
    """过滤后的VERL数据生成器"""
    
    def __init__(self, analysis_file: str = None, config: Dict[str, Any] = None):
        """初始化
        
        Args:
            analysis_file: 分析文件路径
            config: 配置字典
        """
        self.analysis_file = analysis_file
        self.filtered_tasks = []
        if analysis_file and Path(analysis_file).exists():
            self.filtered_tasks = self._load_and_filter_tasks()
        self.generator = InternBootcampVERLDataGenerator(config)
    
    def _load_and_filter_tasks(self) -> List[Dict[str, Any]]:
        """从分析文件加载并过滤任务（照搬原始）"""
        filtered_tasks = []
        
        logger.info(f"Loading tasks from {self.analysis_file}")
        
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    task_data = json.loads(line)
                    
                    # 检查必要字段
                    if not all(key in task_data for key in ['task_name', 'english_detailed', 'quality_evaluation']):
                        logger.warning(f"Line {line_num}: Missing required fields, skipping")
                        continue
                    
                    english_detailed = task_data['english_detailed']
                    quality_eval = task_data['quality_evaluation']
                    
                    # 过滤条件1: english_detailed不能以"Error"开头
                    if english_detailed.startswith('Error'):
                        logger.debug(f"Line {line_num}: Filtered out due to Error in english_detailed")
                        continue
                    
                    # 过滤条件2: quality_evaluation.correctness不能是"incorrect"
                    if quality_eval.get('correctness') == 'incorrect':
                        logger.debug(f"Line {line_num}: Filtered out due to incorrect quality evaluation")
                        continue
                    
                    # 通过过滤，添加到结果
                    filtered_task = {
                        'original_task_name': task_data['task_name'],
                        'display_name': english_detailed,  # 使用english_detailed作为显示名称
                        'chinese_brief': task_data.get('chinese_brief', ''),
                        'quality_score': quality_eval.get('quality_score', 0),
                        'correctness': quality_eval.get('correctness', 'unknown')
                    }
                    
                    filtered_tasks.append(filtered_task)
                    logger.debug(f"Line {line_num}: Added task {task_data['task_name']}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Line {line_num}: JSON decode error: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Line {line_num}: Unexpected error: {e}")
                    continue
        
        logger.info(f"Filtered {len(filtered_tasks)} valid tasks from {self.analysis_file}")
        return filtered_tasks
    
    def get_task_names(self) -> List[str]:
        """获取过滤后的任务名称列表"""
        return [task['original_task_name'] for task in self.filtered_tasks]
    
    def get_task_display_names(self) -> Dict[str, str]:
        """获取任务名称到显示名称的映射"""
        return {task['original_task_name']: task['display_name'] for task in self.filtered_tasks}


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Generate InternBootcamp VERL training data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default configuration
  python %(prog)s
  
  # Override specific parameters
  python %(prog)s --entries-per-task 10 --max-tasks 5
  
  # Use custom config file
  python %(prog)s --config /path/to/config.yaml
  
  # Full example with overrides
  python %(prog)s --config ../config.yaml --entries-per-task 20 --output-dir production_data
        """
    )
    
    # 配置文件参数
    parser.add_argument('--config', type=str, default=None,
                       help='Path to config.yaml file (default: New_evaluation_and_RL/config.yaml)')
    
    # 任务选择参数
    parser.add_argument('--tasks', nargs='+', 
                       help='Tasks to generate data for (default: use available tasks up to max-tasks)')
    parser.add_argument('--entries-per-task', type=int, default=None,
                       help='Number of entries per task (default: from config or 5)')
    parser.add_argument('--max-tasks', type=int, default=2,
                       help='Maximum number of tasks to process (default: 2)')
    
    # 过滤参数
    parser.add_argument('--analysis-file', type=str,
                       help='Optional: InternBootcamp analysis JSONL file for filtering')
    
    # 输出参数
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for data files (default: from config)')
    parser.add_argument('--train-ratio', type=float, default=None,
                       help='Train/test split ratio (default: from config or 0.8)')
    
    # 超时参数
    parser.add_argument('--timeout-per-task', type=float, default=3.0,
                       help='Timeout in seconds per task (default: 3.0)')
    
    args = parser.parse_args()
    
    # 加载配置文件
    config = load_config(args.config)
    
    # 从配置文件获取默认值，命令行参数优先
    if args.entries_per_task is None:
        args.entries_per_task = config.get('data_generation', {}).get('default_test_cases_per_entry', 5)
    
    if args.train_ratio is None:
        args.train_ratio = config.get('data_generation', {}).get('default_train_proportion', 0.8)
    
    if args.output_dir is None:
        # 使用配置文件中的输出目录
        base_output = config.get('data_generation', {}).get('output_dir', 'internbootcamp_data')
        project_root = config.get('project_root', PROJECT_ROOT)
        if Path(base_output).is_absolute():
            args.output_dir = Path(base_output) / "internbootcamp"
        else:
            args.output_dir = project_root / base_output / "internbootcamp"
    else:
        # 如果用户指定了输出目录，处理相对路径
        if not Path(args.output_dir).is_absolute():
            args.output_dir = Path.cwd() / args.output_dir
    
    # 打印配置信息
    logger.info("="*50)
    logger.info("Configuration Summary")
    logger.info("="*50)
    logger.info(f"Config file: {args.config or 'default (New_evaluation_and_RL/config.yaml)'}")
    logger.info(f"Entries per task: {args.entries_per_task}")
    logger.info(f"Max tasks: {args.max_tasks}")
    logger.info(f"Train ratio: {args.train_ratio}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Timeout per task: {args.timeout_per_task}s")
    if args.analysis_file:
        logger.info(f"Analysis file: {args.analysis_file}")
    logger.info("="*50)
    
    # 创建生成器
    if args.analysis_file and Path(args.analysis_file).exists():
        # 使用过滤模式
        filtered_generator = FilteredVERLGenerator(args.analysis_file, config)
        generator = filtered_generator.generator
        
        # 设置显示名称
        display_names = filtered_generator.get_task_display_names()
        generator.set_task_display_names(display_names)
        
        # 获取过滤后的任务
        valid_tasks = filtered_generator.get_task_names()[:args.max_tasks]
        
        logger.info(f"Using {len(valid_tasks)} filtered tasks")
    else:
        # 直接使用所有可用任务
        generator = InternBootcampVERLDataGenerator(config)
        
        # 获取可用任务
        available_tasks = generator.manager.get_available_tasks()
        
        if args.tasks:
            # 使用指定的任务
            valid_tasks = []
            for task in args.tasks:
                if task in available_tasks:
                    valid_tasks.append(task)
                else:
                    logger.warning(f"Task '{task}' not found in available tasks")
        else:
            # 使用前N个可用任务
            valid_tasks = available_tasks[:args.max_tasks]
    
    if not valid_tasks:
        logger.error("No valid tasks to process")
        return
    
    logger.info(f"Processing tasks: {valid_tasks}")
    
    # 生成数据集
    entries = await generator.generate_dataset(
        valid_tasks, 
        args.entries_per_task,
        timeout_per_task=args.timeout_per_task  # 使用命令行参数的超时设置
    )
    
    if not entries:
        logger.error("No entries generated")
        return
    
    # 使用已经处理好的输出目录（args.output_dir已经是绝对路径）
    output_dir = Path(args.output_dir)
    
    # 保存数据集
    stats = generator.split_and_save_dataset(
        entries, 
        str(output_dir),
        args.train_ratio
    )
    
    # 打印统计信息
    logger.info("\n" + "="*50)
    logger.info("GENERATION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total entries generated: {stats['generation_stats']['total_generated']}")
    logger.info(f"Successful: {stats['generation_stats']['successful']}")
    logger.info(f"Failed: {stats['generation_stats']['failed']}")
    if stats['generation_stats']['total_generated'] > 0:
        success_rate = stats['generation_stats']['successful'] / stats['generation_stats']['total_generated'] * 100
        logger.info(f"Success rate: {success_rate:.1f}%")
    
    logger.info(f"\nOutput saved to: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())