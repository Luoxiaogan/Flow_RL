"""
测试InternBootcamp Reward Function V2
适配新的数据格式
"""
import os
import sys
import json
import asyncio
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import time

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from internbootcamp_reward_v2 import compute_score, batch_compute_score
from openai import AsyncOpenAI

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestInternBootcampRewardV2:
    """测试InternBootcamp reward计算 V2"""
    
    def __init__(self):
        # 加载配置
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # 初始化LLM客户端
        llm_config = self.config['llm_config']['upstream']
        self.client = AsyncOpenAI(
            api_key=llm_config['api_key'],
            base_url=llm_config['base_url']
        )
        self.model = llm_config['model']
        
        # 加载数据
        self.data_path = Path(__file__).parent.parent / "verl_data_filtered" / "train.parquet"
        if self.data_path.exists():
            self.df = pd.read_parquet(self.data_path)
            logger.info(f"Loaded {len(self.df)} records from {self.data_path}")
        else:
            self.df = None
            logger.warning("No data file found, will use test data")
    
    async def generate_response(self, prompt: str) -> str:
        """使用LLM生成response"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating Python workflow graphs to solve problems using MetaGPT ActionNodes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""
    
    def create_test_data(self, task_name: str = "adidyoumean"):
        """创建测试数据（新格式）"""
        return {
            "data_source": f"internbootcamp_{task_name}",
            "prompt": json.dumps([{
                "role": "user", 
                "content": "Create a workflow to solve the Adidyoumean typo detection task..."
            }]),
            "ability": "general_reasoning",
            "reward_model": {
                "ground_truth": "default"
            },
            "extra_info": {
                "score": 1.0,
                "task_name": task_name,
                "test_cases": ["{'input': 'hello'}", "{'input': 'hellno'}", "{'input': 'abacaba'}"],
                "entry_id": 1,
                "task_type": "string_manipulation",
                "workflow_type": "predefined",
                "num_examples": 3,
                "timestamp": datetime.now().isoformat(),
                "generation_time": 0.0
            }
        }
    
    async def test_single_workflow(self):
        """测试单个workflow的reward计算"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing single workflow reward calculation V2")
        logger.info(f"{'='*60}")
        
        # 创建测试数据
        test_data = self.create_test_data()
        
        # 打印任务信息
        extra_info = test_data['extra_info']
        task_name = extra_info['task_name']
        test_cases = extra_info['test_cases']
        
        logger.info(f"Task: {task_name}")
        logger.info(f"Number of test cases: {len(test_cases)}")
        
        # 创建测试workflow
        test_solution = """
Based on the problem, I'll create a workflow to solve the Adidyoumean typo detection task.

<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
    
    async def run_workflow(self):
        # First attempt to solve the problem
        initial_solution = await self.custom(
            instruction="Analyze the input string and identify typos (3+ consecutive consonants with at least 2 different characters). Insert minimum spaces to split the word and eliminate all typos. Return the result in [answer] tags."
        )
        
        # Review and improve the solution
        final_solution = await self.review(pre_solution=initial_solution)
        
        return final_solution
</graph>
"""
        
        logger.info(f"Test solution length: {len(test_solution)} chars")
        
        # 计算reward
        logger.info("\nComputing reward...")
        ground_truth = test_data['reward_model']['ground_truth']
        score = compute_score(test_solution, ground_truth, extra_info)
        
        logger.info(f"\nFinal reward score: {score:.3f}")
        
        return score
    
    async def test_with_real_data(self):
        """使用真实数据测试"""
        if self.df is None:
            logger.warning("No real data available, skipping test")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info("Testing with real data from parquet file")
        logger.info(f"{'='*60}")
        
        # 选择第一条数据
        data = self.df.iloc[0].to_dict()
        
        # 检查数据格式
        if 'extra_info' in data and isinstance(data['extra_info'], str):
            extra_info = json.loads(data['extra_info'])
        else:
            # 如果是旧格式，需要转换
            logger.info("Converting old format to new format...")
            reward_model = json.loads(data.get('reward_model', '{}'))
            extra_info = {
                'task_name': reward_model.get('task_name', ''),
                'test_cases': reward_model.get('test_cases', []),
                'score': reward_model.get('score', 1.0)
            }
        
        task_name = extra_info.get('task_name', 'unknown')
        test_cases = extra_info.get('test_cases', [])
        
        logger.info(f"Task: {task_name}")
        logger.info(f"Number of test cases: {len(test_cases)}")
        
        # 生成workflow
        prompt = json.loads(data['prompt'])[0]['content']
        logger.info("\nGenerating workflow with LLM...")
        solution = await self.generate_response(prompt)
        
        if not solution:
            logger.error("Failed to generate solution")
            return
        
        logger.info(f"Generated solution length: {len(solution)} chars")
        
        # 计算reward
        reward_model = data.get('reward_model', {})
        if isinstance(reward_model, str):
            reward_model = json.loads(reward_model)
        ground_truth = reward_model.get('ground_truth', 'default')
        score = compute_score(solution, ground_truth, extra_info)
        
        logger.info(f"\nFinal reward score: {score:.3f}")
        
        return score
    
    async def test_batch_processing(self):
        """测试批量处理"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing batch processing")
        logger.info(f"{'='*60}")
        
        # 创建多个测试数据
        test_data_list = [
            self.create_test_data("adidyoumean"),
            self.create_test_data("adidyoumean"),
            self.create_test_data("adidyoumean")
        ]
        
        # 创建测试solutions
        test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
</graph>
"""
        
        solutions = [test_solution] * 3
        ground_truths = ["default"] * 3
        extra_infos = [d['extra_info'] for d in test_data_list]
        
        # 批量计算
        logger.info(f"Processing {len(solutions)} solutions...")
        scores = await batch_compute_score(solutions, ground_truths, extra_infos)
        
        # 输出结果
        logger.info("\nBatch Results:")
        for i, score in enumerate(scores):
            logger.info(f"Solution {i+1}: {score:.3f}")
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        logger.info(f"\nAverage score: {avg_score:.3f}")
        
        return scores
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing error handling")
        logger.info(f"{'='*60}")
        
        test_data = self.create_test_data()
        extra_info = test_data['extra_info']
        
        # 测试1：空solution
        logger.info("\nTest 1: Empty solution")
        score = compute_score("", "default", extra_info)
        logger.info(f"Score for empty solution: {score}")
        assert score == 0.0, "Empty solution should return 0"
        
        # 测试2：无效的workflow代码
        logger.info("\nTest 2: Invalid workflow code")
        score = compute_score("This is not a valid workflow", "default", extra_info)
        logger.info(f"Score for invalid workflow: {score}")
        assert score == 0.0, "Invalid workflow should return 0"
        
        # 测试3：缺少task_name
        logger.info("\nTest 3: Missing task_name")
        bad_extra_info = {k: v for k, v in extra_info.items() if k != 'task_name'}
        score = compute_score(test_data['extra_info']['test_cases'][0], "default", bad_extra_info)
        logger.info(f"Score without task_name: {score}")
        assert score == 0.0, "Missing task_name should return 0"
        
        logger.info("\nAll error handling tests passed!")


async def main():
    """主测试函数"""
    tester = TestInternBootcampRewardV2()
    
    # 1. 测试单个workflow
    logger.info("\n\n=== TEST 1: Single Workflow ===")
    await tester.test_single_workflow()
    
    # 2. 测试真实数据（如果有）
    logger.info("\n\n=== TEST 2: Real Data ===")
    await tester.test_with_real_data()
    
    # 3. 测试批量处理
    logger.info("\n\n=== TEST 3: Batch Processing ===")
    await tester.test_batch_processing()
    
    # 4. 测试错误处理
    logger.info("\n\n=== TEST 4: Error Handling ===")
    await tester.test_error_handling()
    
    logger.info("\n\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())