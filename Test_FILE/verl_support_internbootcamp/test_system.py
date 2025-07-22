"""
InternBootcamp VERL系统测试脚本
测试各个组件是否正常工作
"""
import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 禁用internbootcamp_utils的冗长日志输出
logging.getLogger('internbootcamp_utils').setLevel(logging.WARNING)


def test_imports():
    """测试所有模块是否可以正常导入"""
    logger.info("Testing imports...")
    
    try:
        from internbootcamp_utils import InternBootcampManager
        logger.info("✓ internbootcamp_utils imported successfully")
        
        from generate_verl_data import generate_verl_entry, create_hf_chat_prompt
        logger.info("✓ generate_verl_data imported successfully")
        
        from workflow_reward import WorkflowRewardCalculator, compute_score
        logger.info("✓ workflow_reward imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_bootcamp_discovery():
    """测试bootcamp发现功能"""
    logger.info("\nTesting bootcamp discovery...")
    
    try:
        from internbootcamp_utils import InternBootcampManager
        
        manager = InternBootcampManager()
        stats = manager.get_task_stats()
        
        logger.info(f"✓ Total discovered: {stats['total_discovered']}")
        logger.info(f"✓ Successfully loaded: {stats['successfully_loaded']}")
        logger.info(f"✓ Failed to load: {stats['failed_to_load']}")
        
        # 显示前10个可用任务
        available = stats['available_tasks']
        if available:
            logger.info(f"✓ Sample tasks: {available[:10]}")
        else:
            logger.warning("✗ No available tasks found")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ Bootcamp discovery failed: {e}")
        return False


def test_example_generation(task_name: str = None):
    """测试示例生成功能"""
    logger.info("\nTesting example generation...")
    
    try:
        from internbootcamp_utils import InternBootcampManager
        
        manager = InternBootcampManager()
        
        # 选择测试任务
        if not task_name:
            available = manager.get_available_tasks()
            if not available:
                logger.error("✗ No available tasks for testing")
                return False
            task_name = available[0]
        
        logger.info(f"Testing with task: {task_name}")
        
        # 生成示例
        examples = manager.generate_task_examples(task_name, n_examples=2)
        
        if examples:
            logger.info(f"✓ Generated {len(examples)} examples")
            
            # 检查示例结构
            for i, example in enumerate(examples):
                if 'identity' in example and 'prompt' in example:
                    logger.info(f"✓ Example {i+1} has correct structure")
                    logger.info(f"  - Prompt length: {len(example['prompt'])} chars")
                else:
                    logger.error(f"✗ Example {i+1} has incorrect structure")
                    return False
        else:
            logger.error("✗ No examples generated")
            return False
        
        # 测试描述提取
        description = manager.get_task_description(task_name)
        logger.info(f"✓ Description extracted ({len(description)} chars)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Example generation failed: {e}")
        return False


def test_verl_data_generation(task_name: str = None):
    """测试VERL数据生成"""
    logger.info("\nTesting VERL data generation...")
    
    try:
        from internbootcamp_utils import InternBootcampManager
        from generate_verl_data import generate_verl_entry, create_hf_chat_prompt, load_config
        
        manager = InternBootcampManager()
        config = load_config()
        
        # 选择测试任务
        if not task_name:
            available = manager.get_available_tasks()
            if not available:
                logger.error("✗ No available tasks")
                return False
            task_name = available[0]
        
        # 生成VERL条目
        entry = generate_verl_entry(task_name, manager, config, entry_id=0)
        
        if entry:
            logger.info("✓ VERL entry generated successfully")
            
            # 检查必要字段
            required_fields = ['data_source', 'prompt', 'ability', 'reward_model', 'extra_info']
            for field in required_fields:
                if field in entry:
                    logger.info(f"✓ Field '{field}' present")
                else:
                    logger.error(f"✗ Field '{field}' missing")
                    return False
            
            # 检查prompt格式
            if isinstance(entry['prompt'], list) and len(entry['prompt']) == 2:
                if all('role' in msg and 'content' in msg for msg in entry['prompt']):
                    logger.info("✓ Prompt in correct HF chat format")
                else:
                    logger.error("✗ Prompt messages missing required fields")
                    return False
            else:
                logger.error("✗ Prompt not in correct format")
                return False
            
            # 显示生成的数据示例
            logger.info("\nGenerated VERL entry sample:")
            print(json.dumps({
                'data_source': entry['data_source'],
                'ability': entry['ability'],
                'prompt_length': len(str(entry['prompt'])),
                'num_test_cases': len(entry['reward_model']['test_cases'])
            }, indent=2))
            
        else:
            logger.error("✗ Failed to generate VERL entry")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ VERL data generation failed: {e}")
        return False


async def test_reward_calculation(task_name: str = None):
    """测试奖励计算功能"""
    logger.info("\nTesting reward calculation...")
    
    try:
        from internbootcamp_utils import InternBootcampManager
        from workflow_reward import compute_score
        
        manager = InternBootcampManager()
        
        # 选择测试任务
        if not task_name:
            available = manager.get_available_tasks()
            if not available:
                logger.error("✗ No available tasks")
                return False
            task_name = available[0]
        
        logger.info(f"Testing reward calculation for: {task_name}")
        
        # 测试工作流
        test_workflow = f"""
class InternBootcampWorkflow:
    def __init__(self):
        self.system_prompt = '''You are an expert at solving {task_name} problems. 
        Analyze the problem carefully and provide the correct solution in the required format.'''
    
    async def solve(self, problem):
        response = await llm_call(self.system_prompt, problem)
        return response
"""
        
        # 计算奖励
        logger.info("Computing reward score...")
        score = await compute_score(test_workflow, task_name)
        
        logger.info(f"✓ Reward score computed: {score:.3f}")
        
        if score > 0:
            logger.info("✓ Workflow produced non-zero reward")
        else:
            logger.warning("⚠ Workflow produced zero reward (might be normal for difficult tasks)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Reward calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests(task_name: str = None):
    """运行所有测试"""
    logger.info("=== InternBootcamp VERL System Test ===\n")
    
    results = {
        "imports": test_imports(),
        "discovery": test_bootcamp_discovery(),
        "example_generation": test_example_generation(task_name),
        "verl_generation": test_verl_data_generation(task_name),
        "reward_calculation": await test_reward_calculation(task_name)
    }
    
    # 总结
    logger.info("\n=== Test Summary ===")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


def main():
    parser = argparse.ArgumentParser(description='Test InternBootcamp VERL System')
    parser.add_argument('--task', help='Specific task to test with')
    parser.add_argument('--test', choices=['imports', 'discovery', 'example', 'verl', 'reward', 'all'],
                       default='all', help='Specific test to run')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        success = asyncio.run(run_all_tests(args.task))
    elif args.test == 'imports':
        success = test_imports()
    elif args.test == 'discovery':
        success = test_bootcamp_discovery()
    elif args.test == 'example':
        success = test_example_generation(args.task)
    elif args.test == 'verl':
        success = test_verl_data_generation(args.task)
    elif args.test == 'reward':
        success = asyncio.run(test_reward_calculation(args.task))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()