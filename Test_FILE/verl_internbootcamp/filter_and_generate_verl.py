"""
过滤InternBootcamp分析文件并生成VERL数据
根据quality_evaluation.correctness和english_detailed字段过滤任务
"""
import json
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generate_verl_data import VERLDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FilteredVERLGenerator:
    """过滤后的VERL数据生成器"""
    
    def __init__(self, analysis_file: str, config_path: str = "config.json"):
        """初始化"""
        self.analysis_file = analysis_file
        self.config_path = config_path
        self.filtered_tasks = self._load_and_filter_tasks()
        self.generator = VERLDataGenerator(config_path)
    
    def _load_and_filter_tasks(self) -> List[Dict[str, Any]]:
        """从分析文件加载并过滤任务"""
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
        """获取过滤后的任务名称列表（原始task_name）"""
        return [task['original_task_name'] for task in self.filtered_tasks]
    
    def get_task_display_names(self) -> Dict[str, str]:
        """获取任务名称到显示名称的映射"""
        return {task['original_task_name']: task['display_name'] for task in self.filtered_tasks}
    
    def print_task_summary(self):
        """打印任务摘要"""
        logger.info("="*60)
        logger.info("FILTERED TASKS SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Total filtered tasks: {len(self.filtered_tasks)}")
        
        # 按质量评分分组
        quality_groups = {}
        correctness_groups = {}
        
        for task in self.filtered_tasks:
            quality = task['quality_score']
            correctness = task['correctness']
            
            quality_groups[quality] = quality_groups.get(quality, 0) + 1
            correctness_groups[correctness] = correctness_groups.get(correctness, 0) + 1
        
        logger.info("\nBy Quality Score:")
        for score in sorted(quality_groups.keys()):
            logger.info(f"  Score {score}: {quality_groups[score]} tasks")
        
        logger.info("\nBy Correctness:")
        for correctness in sorted(correctness_groups.keys()):
            logger.info(f"  {correctness}: {correctness_groups[correctness]} tasks")
        
        logger.info("\nFirst 10 tasks:")
        for i, task in enumerate(self.filtered_tasks[:10]):
            logger.info(f"  {i+1}. {task['original_task_name']} (quality: {task['quality_score']}, correctness: {task['correctness']})")
        
        if len(self.filtered_tasks) > 10:
            logger.info(f"  ... and {len(self.filtered_tasks) - 10} more tasks")
    
    async def generate_verl_dataset(self, entries_per_task: int = 5, 
                                  workflow_types: List[str] = None,
                                  output_dir: str = "verl_data_filtered",
                                  max_tasks: int = None,
                                  timeout_per_task: float = 3.0) -> Dict[str, Any]:
        """生成过滤后的VERL数据集，带超时功能"""
        if workflow_types is None:
            workflow_types = ["predefined"]
        
        task_names = self.get_task_names()
        
        # 限制任务数量（用于测试）
        if max_tasks and max_tasks < len(task_names):
            task_names = task_names[:max_tasks]
            logger.info(f"Limited to first {max_tasks} tasks for testing")
        
        logger.info(f"Generating VERL data for {len(task_names)} filtered tasks with {timeout_per_task}s timeout")
        
        # 设置任务显示名称到生成器
        display_names = self.get_task_display_names()
        self.generator.set_task_display_names(display_names)
        
        # 使用基础生成器生成数据，传递超时参数
        entries = await self.generator.generate_dataset(
            task_names, 
            entries_per_task,
            workflow_types,
            timeout_per_task  # 添加超时参数
        )
        
        if entries:
            # 保存数据集
            stats = self.generator.split_and_save_dataset(
                entries, 
                output_dir,
                train_ratio=0.8
            )
            
            # 保存过滤任务的映射信息
            task_mapping = {
                'filtered_tasks': self.filtered_tasks,
                'task_display_names': self.get_task_display_names(),
                'generation_config': {
                    'entries_per_task': entries_per_task,
                    'workflow_types': workflow_types,
                    'source_file': self.analysis_file
                }
            }
            
            mapping_file = Path(output_dir) / "task_mapping.json"
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(task_mapping, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Task mapping saved to {mapping_file}")
            
            return stats
        else:
            logger.error("No entries were generated")
            return {}


async def main():
    parser = argparse.ArgumentParser(description='Generate VERL data from filtered bootcamp analysis')
    
    # 输入文件参数
    parser.add_argument('--analysis-file', 
                       default='bootcamp_analysis_20250723_190329.jsonl',
                       help='InternBootcamp analysis JSONL file')
    
    # 生成参数
    parser.add_argument('--entries-per-task', type=int, default=3,
                       help='Number of VERL entries per task')
    parser.add_argument('--workflow-types', nargs='+', 
                       default=['predefined'],
                       choices=['predefined', 'flexible'],
                       help='Workflow types to generate')
    parser.add_argument('--max-tasks', type=int, default=None,
                       help='Maximum number of tasks to process (for testing)')
    parser.add_argument('--timeout', type=float, default=3.0,
                       help='Timeout per task in seconds (default: 3.0)')
    
    # 输出参数
    parser.add_argument('--output-dir', default='verl_data_filtered',
                       help='Output directory for VERL data')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path')
    
    # 控制参数
    parser.add_argument('--dry-run', action='store_true',
                       help='Only show filtered tasks, do not generate data')
    
    args = parser.parse_args()
    
    # 检查分析文件是否存在
    if not os.path.exists(args.analysis_file):
        logger.error(f"Analysis file not found: {args.analysis_file}")
        return
    
    # 创建过滤生成器
    filtered_generator = FilteredVERLGenerator(args.analysis_file, args.config)
    
    # 打印任务摘要
    filtered_generator.print_task_summary()
    
    if args.dry_run:
        logger.info("Dry run mode - not generating VERL data")
        return
    
    # 生成VERL数据集，传递超时参数
    stats = await filtered_generator.generate_verl_dataset(
        entries_per_task=args.entries_per_task,
        workflow_types=args.workflow_types,
        output_dir=args.output_dir,
        max_tasks=args.max_tasks,
        timeout_per_task=args.timeout  # 添加超时参数
    )
    
    if stats:
        logger.info("\n" + "="*60)
        logger.info("FILTERED VERL GENERATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Generated entries: {stats['generation_stats']['successful']}")
        logger.info(f"Failed entries: {stats['generation_stats']['failed']}")
        logger.info(f"Success rate: {stats['generation_stats']['successful'] / stats['generation_stats']['total_generated'] * 100:.1f}%")
        logger.info(f"Output directory: {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main()) 