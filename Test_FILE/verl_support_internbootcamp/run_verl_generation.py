"""
运行VERL数据生成的示例脚本
展示如何使用完整的系统
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from verl_complete_generator import VERLCompleteGenerator
from internbootcamp_utils import InternBootcampManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_generation_example():
    """运行VERL数据生成示例"""
    
    # 配置
    config = {
        "examples_per_entry": 3,  # 每个条目包含3个示例
        "save_parquet": False     # 暂时关闭parquet格式（数据结构复杂）
    }
    
    # LLM配置（使用模拟生成）
    llm_config = {
        "model": "mock",  # 使用模拟模式
        "temperature": 0.7
    }
    
    # 输出目录
    output_dir = "verl_generation_output"
    
    # 创建生成器
    logger.info("Initializing VERL generator...")
    generator = VERLCompleteGenerator(config, output_dir)
    
    # 获取可用任务
    manager = InternBootcampManager()
    available_tasks = manager.get_available_tasks()
    logger.info(f"Found {len(available_tasks)} available tasks")
    
    # 选择要生成的任务
    # 示例1：选择特定任务
    selected_tasks = []
    for task in available_tasks:
        if any(keyword in task.lower() for keyword in ['sudoku', 'minesweeper', 'kakuro']):
            selected_tasks.append(task)
    
    # 如果没有找到特定任务，选择前5个
    if not selected_tasks:
        selected_tasks = available_tasks[:5]
    
    logger.info(f"Selected {len(selected_tasks)} tasks: {selected_tasks}")
    
    # 选择workflow类型
    workflow_types = ["predefined", "flexible"]
    
    # 每种配置生成的条目数
    entries_per_config = 3
    
    # 生成数据集
    logger.info("\nStarting VERL data generation...")
    logger.info(f"Tasks: {len(selected_tasks)}")
    logger.info(f"Workflow types: {workflow_types}")
    logger.info(f"Entries per configuration: {entries_per_config}")
    logger.info(f"Total entries to generate: {len(selected_tasks) * len(workflow_types) * entries_per_config}")
    
    dataset = await generator.generate_dataset(
        selected_tasks,
        workflow_types,
        entries_per_config,
        llm_config
    )
    
    # 保存数据集
    logger.info("\nSaving dataset...")
    generator.save_dataset(dataset, train_ratio=0.8)
    
    # 打印详细统计
    stats = dataset["stats"]
    logger.info("\n" + "="*60)
    logger.info("GENERATION COMPLETE - DETAILED STATISTICS")
    logger.info("="*60)
    
    logger.info(f"\nOverall Statistics:")
    logger.info(f"  Total entries: {stats['total_entries']}")
    logger.info(f"  Successful entries: {stats['successful_entries']}")
    logger.info(f"  Success rate: {stats['success_rate']*100:.1f}%")
    logger.info(f"  Average reward: {stats['average_reward']:.3f}")
    logger.info(f"  Reward range: [{stats['min_reward']:.3f}, {stats['max_reward']:.3f}]")
    
    logger.info(f"\nBy Task:")
    for task, task_stats in stats['by_task'].items():
        logger.info(f"  {task}:")
        logger.info(f"    - Entries: {task_stats['count']}")
        logger.info(f"    - Avg reward: {task_stats['average_reward']:.3f}")
        logger.info(f"    - Success rate: {task_stats['success_rate']*100:.1f}%")
    
    logger.info(f"\nBy Workflow Type:")
    for wf_type, wf_stats in stats['by_workflow_type'].items():
        logger.info(f"  {wf_type}:")
        logger.info(f"    - Entries: {wf_stats['count']}")
        logger.info(f"    - Avg reward: {wf_stats['average_reward']:.3f}")
        logger.info(f"    - Success rate: {wf_stats['success_rate']*100:.1f}%")
    
    logger.info(f"\nOutput Directory Structure:")
    logger.info(f"  {output_dir}/")
    logger.info(f"    ├── workflows/          # Generated workflow code files")
    logger.info(f"    ├── execution_results/  # Workflow execution results")
    logger.info(f"    ├── verl_data/         # VERL format training data")
    logger.info(f"    │   ├── train.json     # Training set")
    logger.info(f"    │   ├── test.json      # Test set")
    logger.info(f"    │   ├── train.parquet  # Training set (Parquet format)")
    logger.info(f"    │   └── test.parquet   # Test set (Parquet format)")
    logger.info(f"    ├── logs/              # Generation logs")
    logger.info(f"    └── generation_stats.json  # Generation statistics")
    
    # 展示一个生成的条目示例
    if dataset["entries"]:
        logger.info("\n" + "="*60)
        logger.info("EXAMPLE VERL ENTRY")
        logger.info("="*60)
        
        example_entry = dataset["entries"][0]
        logger.info(f"\nTask: {example_entry['reward_model']['task_name']}")
        logger.info(f"Workflow Type: {example_entry['extra_info']['workflow_type']}")
        logger.info(f"Ability: {example_entry['ability']}")
        logger.info(f"Average Reward: {example_entry['reward_model']['average_reward']:.3f}")
        logger.info(f"Success Rate: {example_entry['reward_model']['successful_examples']}/{example_entry['reward_model']['total_examples']}")
        
        logger.info("\nPrompt Messages:")
        for i, msg in enumerate(example_entry['prompt']):
            logger.info(f"  [{msg['role']}]: {msg['content'][:100]}...")
    
    logger.info("\n✓ VERL data generation completed successfully!")
    logger.info(f"✓ Check {output_dir}/ for all generated files")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run VERL data generation')
    parser.add_argument('--quick', action='store_true', 
                       help='Quick mode: generate fewer entries for testing')
    
    args = parser.parse_args()
    
    if args.quick:
        logger.info("Running in quick mode (fewer entries)...")
        # 在快速模式下修改全局配置
        import verl_complete_generator
        # 这里可以修改配置以生成更少的数据
    
    # 运行生成
    asyncio.run(run_generation_example())


if __name__ == "__main__":
    main()