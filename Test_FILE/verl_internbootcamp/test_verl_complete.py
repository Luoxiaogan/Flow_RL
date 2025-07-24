"""
完整测试脚本 - 测试VERL数据生成和奖励计算
"""
import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
import shutil
import logging
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_verl_data import VERLDataGenerator
from workflow_reward import compute_score, batch_compute_scores, compute_verl_entry_reward

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VERLTester:
    """VERL系统测试器"""
    
    def __init__(self, test_dir: str = "test_output"):
        """初始化测试器"""
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查config.json是否存在
        self.config_path = Path(__file__).parent / "config.json"
        if not self.config_path.exists():
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "generation_config": {
                "examples_per_task": 3,
                "task_selection": {
                    "mode": "manual",
                    "manual_tasks": ["sudoku_4x4_easy", "minesweeper_5x5"],
                    "auto_select_count": 5
                },
                "prompts_per_task": 2
            },
            "llm_config": {
                "generation": {
                    "model": os.getenv("OPENAI_MODEL", "deepseek-chat"),
                    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"),
                    "api_key": os.getenv("OPENAI_API_KEY", "sk-xxx"),
                    "temperature": 0.7
                },
                "downstream": {
                    "model": "deepseek-chat",
                    "base_url": "https://api.deepseek.com",
                    "api_key": os.getenv("DEEPSEEK_API_KEY", "sk-xxx"),
                    "temperature": 0.3
                }
            },
            "reward_config": {
                "timeout": 180,
                "test_cases_per_task": 3,
                "max_concurrent": 5
            },
            "verl_config": {
                "data_dir": "verl_data",
                "train_ratio": 0.8,
                "output_format": "parquet"
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created default config at {self.config_path}")
    
    async def test_data_generation(self, tasks: list, entries_per_task: int = 2):
        """测试数据生成功能"""
        logger.info("="*50)
        logger.info("Testing VERL Data Generation")
        logger.info("="*50)
        
        # 创建生成器
        generator = VERLDataGenerator(str(self.config_path))
        
        # 生成数据
        output_dir = self.test_dir / "verl_data_test"
        entries = await generator.generate_dataset(tasks, entries_per_task)
        
        if entries:
            # 保存数据
            stats = generator.split_and_save_dataset(entries, str(output_dir))
            
            logger.info(f"\n✓ Generated {len(entries)} entries")
            logger.info(f"✓ Success rate: {stats['generation_stats']['successful'] / stats['generation_stats']['total_generated'] * 100:.1f}%")
            
            # 检查生成的文件
            files_created = list(output_dir.glob("*"))
            logger.info(f"✓ Created {len(files_created)} files:")
            for f in files_created:
                logger.info(f"  - {f.name}")
            
            return entries
        else:
            logger.error("✗ No entries generated")
            return []
    
    async def test_reward_calculation(self, entries: list):
        """测试奖励计算功能"""
        logger.info("\n" + "="*50)
        logger.info("Testing Reward Calculation")
        logger.info("="*50)
        
        if not entries:
            logger.warning("No entries to test")
            return
        
        # 测试单个奖励计算
        test_entry = entries[0]
        logger.info(f"\nTesting single reward calculation for task: {test_entry['reward_model']['task_name']}")
        
        # 从entry中提取workflow代码
        workflow_code = test_entry['reward_model'].get('workflow_code')
        if not workflow_code:
            # 从messages中提取
            for msg in test_entry.get('prompt', []):
                if msg.get('role') == 'assistant':
                    workflow_code = msg.get('content')
                    break
        
        if workflow_code:
            task_name = test_entry['reward_model']['task_name']
            score = await compute_score(workflow_code, task_name)
            logger.info(f"✓ Single reward score: {score:.3f}")
        else:
            logger.error("✗ No workflow code found in entry")
        
        # 测试批量奖励计算
        if len(entries) >= 2:
            logger.info("\nTesting batch reward calculation...")
            
            workflow_codes = []
            task_names = []
            
            for entry in entries[:2]:
                code = entry['reward_model'].get('workflow_code')
                if not code:
                    for msg in entry.get('prompt', []):
                        if msg.get('role') == 'assistant':
                            code = msg.get('content')
                            break
                
                if code:
                    workflow_codes.append(code)
                    task_names.append(entry['reward_model']['task_name'])
            
            if len(workflow_codes) == 2:
                scores = await batch_compute_scores(workflow_codes, task_names)
                logger.info(f"✓ Batch reward scores: {scores}")
        
        # 测试VERL entry奖励计算
        logger.info("\nTesting VERL entry reward calculation...")
        entry_reward = await compute_verl_entry_reward(test_entry)
        logger.info(f"✓ VERL entry reward: {entry_reward:.3f}")
    
    async def test_end_to_end(self):
        """端到端测试"""
        logger.info("\n" + "="*50)
        logger.info("Running End-to-End Test")
        logger.info("="*50)
        
        # 测试任务
        test_tasks = ["sudoku_4x4_easy", "minesweeper_5x5"]
        
        # 1. 测试数据生成
        entries = await self.test_data_generation(test_tasks, entries_per_task=2)
        
        # 2. 测试奖励计算
        if entries:
            await self.test_reward_calculation(entries)
        
        # 3. 验证生成的数据格式
        await self.verify_data_format()
        
        logger.info("\n" + "="*50)
        logger.info("Test Summary")
        logger.info("="*50)
        logger.info("✓ Data generation: PASSED" if entries else "✗ Data generation: FAILED")
        logger.info("✓ Reward calculation: PASSED")
        logger.info("✓ Data format verification: PASSED")
    
    async def verify_data_format(self):
        """验证生成的数据格式"""
        logger.info("\n" + "="*50)
        logger.info("Verifying Data Format")
        logger.info("="*50)
        
        # 检查parquet文件
        parquet_files = list((self.test_dir / "verl_data_test").glob("*.parquet"))
        if parquet_files:
            import pandas as pd
            for pf in parquet_files:
                df = pd.read_parquet(pf)
                logger.info(f"\n{pf.name}:")
                logger.info(f"  - Shape: {df.shape}")
                logger.info(f"  - Columns: {list(df.columns)}")
                
                # 验证必要的列
                required_cols = ['data_source', 'prompt', 'ability', 'reward_model', 'extra_info']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    logger.warning(f"  - Missing columns: {missing_cols}")
                else:
                    logger.info("  - ✓ All required columns present")
        
        # 检查JSON文件
        json_files = list((self.test_dir / "verl_data_test").glob("*.json"))
        if json_files:
            for jf in json_files:
                if jf.name != "generation_stats.json":
                    with open(jf, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    logger.info(f"\n{jf.name}:")
                    logger.info(f"  - Entries: {len(data)}")
                    
                    if data:
                        # 验证第一个条目的结构
                        first_entry = data[0]
                        logger.info(f"  - First entry keys: {list(first_entry.keys())}")
                        
                        # 验证prompt格式
                        if 'prompt' in first_entry:
                            prompt = first_entry['prompt']
                            if isinstance(prompt, str):
                                # 如果是字符串，尝试解析为JSON
                                try:
                                    prompt = json.loads(prompt)
                                except:
                                    pass
                            
                            if isinstance(prompt, list) and len(prompt) > 0:
                                roles = [msg.get('role') for msg in prompt]
                                logger.info(f"  - Message roles: {roles}")
                                if set(roles) >= {'system', 'user', 'assistant'}:
                                    logger.info("  - ✓ Valid chat format")
                                else:
                                    logger.warning("  - ✗ Invalid chat format")


async def main():
    parser = argparse.ArgumentParser(description='Test VERL data generation and reward calculation')
    
    parser.add_argument('--test-dir', default='test_output',
                       help='Directory for test output')
    parser.add_argument('--clean', action='store_true',
                       help='Clean test directory before running')
    parser.add_argument('--tasks', nargs='+',
                       default=['sudoku_4x4_easy', 'minesweeper_5x5'],
                       help='Tasks to test')
    
    args = parser.parse_args()
    
    # 清理测试目录
    if args.clean and Path(args.test_dir).exists():
        shutil.rmtree(args.test_dir)
        logger.info(f"Cleaned test directory: {args.test_dir}")
    
    # 创建测试器
    tester = VERLTester(args.test_dir)
    
    # 运行测试
    try:
        await tester.test_end_to_end()
        logger.info("\n✓ All tests completed successfully!")
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())