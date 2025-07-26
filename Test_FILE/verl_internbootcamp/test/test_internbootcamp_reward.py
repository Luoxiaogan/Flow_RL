"""
测试InternBootcamp Reward Function
使用真实的LLM调用，不使用mock
"""
import os
import sys
import json
import asyncio
import pandas as pd
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from internbootcamp_reward import compute_score, batch_compute_score
from openai import AsyncOpenAI

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestInternBootcampReward:
    """测试InternBootcamp reward计算"""
    
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
        self.df = pd.read_parquet(self.data_path)
        logger.info(f"Loaded {len(self.df)} records from {self.data_path}")
    
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
    
    async def test_single_workflow(self, index: int = 0):
        """测试单个workflow的reward计算"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing single workflow reward calculation")
        logger.info(f"{'='*60}")
        
        # 获取数据
        data = self.df.iloc[index].to_dict()
        prompt = json.loads(data['prompt'])[0]['content']
        
        # 打印任务信息
        reward_model = json.loads(data['reward_model'])
        task_name = reward_model['task_name']
        test_cases = reward_model['test_cases']
        
        logger.info(f"Task: {task_name}")
        logger.info(f"Number of test cases: {len(test_cases)}")
        logger.info(f"Prompt preview: {prompt[:200]}...")
        
        # 生成response
        logger.info("\nGenerating workflow with LLM...")
        response = await self.generate_response(prompt)
        
        if not response:
            logger.error("Failed to generate response")
            return
        
        logger.info(f"Generated response length: {len(response)} chars")
        
        # 提取workflow代码预览
        if '<graph>' in response:
            start = response.find('<graph>')
            end = response.find('</graph>')
            if start != -1 and end != -1:
                workflow_preview = response[start:start+200] + "..."
                logger.info(f"Workflow preview: {workflow_preview}")
        
        # 计算reward
        logger.info("\nComputing reward...")
        score = compute_score(response, data)
        
        logger.info(f"\nFinal reward score: {score:.3f}")
        
        return score
    
    async def test_batch_workflow(self, num_samples: int = 3):
        """测试批量workflow的reward计算"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing batch workflow reward calculation")
        logger.info(f"{'='*60}")
        
        # 选择样本
        sample_indices = list(range(min(num_samples, len(self.df))))
        samples = [self.df.iloc[i].to_dict() for i in sample_indices]
        
        # 生成responses
        logger.info(f"\nGenerating {num_samples} workflows...")
        responses = []
        for i, data in enumerate(samples):
            prompt = json.loads(data['prompt'])[0]['content']
            reward_model = json.loads(data['reward_model'])
            task_name = reward_model['task_name']
            
            logger.info(f"\nGenerating workflow {i+1}/{num_samples} for task: {task_name}")
            response = await self.generate_response(prompt)
            responses.append(response)
            
            if response:
                logger.info(f"Generated response {i+1}: {len(response)} chars")
            else:
                logger.error(f"Failed to generate response {i+1}")
        
        # 批量计算rewards
        logger.info("\nComputing batch rewards...")
        scores = await batch_compute_score(responses, samples)
        
        # 输出结果
        logger.info("\nBatch Results:")
        logger.info(f"{'Index':<10} {'Task Name':<30} {'Score':<10}")
        logger.info("-" * 50)
        
        for i, (data, score) in enumerate(zip(samples, scores)):
            reward_model = json.loads(data['reward_model'])
            task_name = reward_model['task_name']
            logger.info(f"{i:<10} {task_name:<30} {score:<10.3f}")
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        logger.info(f"\nAverage score: {avg_score:.3f}")
        
        return scores
    
    async def test_specific_task(self, task_name: str):
        """测试特定任务类型"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing specific task: {task_name}")
        logger.info(f"{'='*60}")
        
        # 查找该任务的数据
        found = False
        for i in range(len(self.df)):
            data = self.df.iloc[i].to_dict()
            reward_model = json.loads(data['reward_model'])
            if reward_model['task_name'] == task_name:
                found = True
                logger.info(f"Found {task_name} at index {i}")
                await self.test_single_workflow(i)
                break
        
        if not found:
            logger.error(f"Task {task_name} not found in dataset")
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info(f"\n{'='*60}")
        logger.info("Testing error handling")
        logger.info(f"{'='*60}")
        
        # 测试空response
        logger.info("\nTest 1: Empty response")
        test_data = self.df.iloc[0].to_dict()
        score = compute_score("", test_data)
        logger.info(f"Score for empty response: {score}")
        
        # 测试无效的workflow代码
        logger.info("\nTest 2: Invalid workflow code")
        invalid_response = "This is not a valid workflow"
        score = compute_score(invalid_response, test_data)
        logger.info(f"Score for invalid response: {score}")
        
        # 测试有语法错误的workflow
        logger.info("\nTest 3: Workflow with syntax error")
        syntax_error_response = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        # Missing closing parenthesis
        self.custom = operator.Custom(self.config, self.problem
    
    async def run_workflow(self):
        return "test"
</graph>
"""
        score = compute_score(syntax_error_response, test_data)
        logger.info(f"Score for syntax error response: {score}")


async def main():
    """主测试函数"""
    tester = TestInternBootcampReward()
    
    # 1. 测试单个workflow
    logger.info("\n\n=== TEST 1: Single Workflow ===")
    await tester.test_single_workflow(0)
    
    # 2. 测试批量workflow
    logger.info("\n\n=== TEST 2: Batch Workflows ===")
    await tester.test_batch_workflow(3)
    
    # 3. 测试特定任务（如果存在）
    logger.info("\n\n=== TEST 3: Specific Task ===")
    await tester.test_specific_task("adidyoumean")
    
    # 4. 测试错误处理
    logger.info("\n\n=== TEST 4: Error Handling ===")
    await tester.test_error_handling()
    
    logger.info("\n\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())