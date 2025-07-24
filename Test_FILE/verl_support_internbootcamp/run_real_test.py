"""
运行真实的VERL数据生成测试
使用真实的LLM API和MetaGPT执行
"""
import os
import sys
import asyncio
import logging
import json
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置API密钥 - 使用Alibaba Qwen API
os.environ["OPENAI_API_KEY"] = "956c41bd0f31beaf68b871d4987af4bb"
os.environ["OPENAI_BASE_URL"] = "https://idealab.alibaba-inc.com/api/openai/v1"


async def run_real_test():
    """运行真实的VERL数据生成测试"""
    from verl_complete_generator import VERLCompleteGenerator
    from internbootcamp_utils import InternBootcampManager
    
    # 配置
    config = {
        "examples_per_entry": 2,  # 每个条目2个示例
        "save_parquet": False
    }
    
    # 真实的LLM配置 - 使用Alibaba Qwen
    llm_config = {
        "model": "qwen-turbo",
        "base_url": "https://idealab.alibaba-inc.com/api/openai/v1",
        "api_key": "956c41bd0f31beaf68b871d4987af4bb",
        "temperature": 0.7
    }
    
    # 输出目录
    output_dir = f"real_test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 创建生成器
    logger.info("=" * 60)
    logger.info("REAL VERL DATA GENERATION TEST")
    logger.info("=" * 60)
    logger.info(f"API: {llm_config['base_url']}")
    logger.info(f"Model: {llm_config['model']}")
    logger.info(f"Output: {output_dir}")
    
    generator = VERLCompleteGenerator(config, output_dir)
    
    # 获取可用任务
    manager = InternBootcampManager()
    available_tasks = manager.get_available_tasks()
    
    # 选择一个简单的任务进行测试
    test_task = None
    for task in available_tasks:
        if 'sudoku' in task.lower() and '4x4' in task:
            test_task = task
            break
    
    if not test_task:
        # 如果没有找到4x4数独，选择第一个任务
        test_task = available_tasks[0]
    
    logger.info(f"\nSelected test task: {test_task}")
    
    # 测试两种workflow类型
    workflow_types = ["predefined", "flexible"]
    entries_per_config = 1  # 每种类型生成1个条目
    
    # 生成数据集
    logger.info("\nGenerating VERL data with REAL API and execution...")
    
    dataset = await generator.generate_dataset(
        [test_task],
        workflow_types,
        entries_per_config,
        llm_config
    )
    
    # 保存数据集
    generator.save_dataset(dataset, train_ratio=0.8)
    
    # 显示结果
    stats = dataset["stats"]
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Successful entries: {stats['successful_entries']}")
    logger.info(f"Success rate: {stats['success_rate']*100:.1f}%")
    logger.info(f"Average reward: {stats['average_reward']:.3f}")
    
    # 显示一个生成的workflow示例
    if dataset["entries"]:
        example_entry = dataset["entries"][0]
        logger.info("\n" + "-" * 60)
        logger.info("EXAMPLE WORKFLOW")
        logger.info("-" * 60)
        
        workflow_file = example_entry['extra_info']['workflow_file']
        if os.path.exists(workflow_file):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                code = f.read()
                # 显示workflow代码的前1000个字符
                logger.info(code[:1000])
                if len(code) > 1000:
                    logger.info("\n... (truncated)")
        
        # 显示执行结果
        execution_file = example_entry['extra_info']['execution_file']
        if os.path.exists(execution_file):
            with open(execution_file, 'r', encoding='utf-8') as f:
                exec_result = json.load(f)
                logger.info("\n" + "-" * 60)
                logger.info("EXECUTION RESULTS")
                logger.info("-" * 60)
                logger.info(f"Task: {exec_result['task_name']}")
                logger.info(f"Total examples: {exec_result['total_examples']}")
                logger.info(f"Successful: {exec_result['successful_examples']}")
                logger.info(f"Average reward: {exec_result['average_reward']:.3f}")
                
                # 显示第一个结果的详情
                if exec_result['results']:
                    result = exec_result['results'][0]
                    logger.info(f"\nExample result:")
                    logger.info(f"  Input: {result['input'][:100]}...")
                    logger.info(f"  Expected: {result['expected_output'][:100]}...")
                    logger.info(f"  Output: {result['workflow_output'][:100]}...")
                    logger.info(f"  Reward: {result['reward']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST COMPLETED SUCCESSFULLY")
    logger.info(f"All files saved to: {output_dir}")
    logger.info("=" * 60)


def main():
    """主函数"""
    try:
        asyncio.run(run_real_test())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()