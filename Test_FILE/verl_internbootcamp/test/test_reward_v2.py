"""
测试InternBootcamp Reward Function V2
完整测试并输出结果到JSON
"""
import os
import sys
import json
import asyncio
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import re
import nest_asyncio

# 允许嵌套的事件循环
nest_asyncio.apply()

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from internbootcamp_reward import compute_score
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
        
        # 直接加载真实数据
        self.data_path = Path(__file__).parent.parent / "verl_data_filtered" / "train.parquet"
        self.df = pd.read_parquet(self.data_path)
        logger.info(f"Loaded {len(self.df)} records from {self.data_path}")
    
    async def generate_response(self, prompt: str) -> str:
        """使用真实LLM生成response"""
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
    
    def extract_workflow(self, response: str) -> str:
        """从响应中提取workflow代码"""
        # 尝试提取<graph>标签中的内容
        graph_match = re.search(r'<graph>(.*?)</graph>', response, re.DOTALL)
        if graph_match:
            return graph_match.group(1).strip()
        
        # 如果没有<graph>标签，尝试提取代码块
        code_match = re.search(r'```python(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # 如果都没有，返回整个响应
        return response
    
    async def run_complete_test(self):
        """运行完整测试并输出结果到JSON"""
        logger.info(f"\n{'='*60}")
        logger.info("Running Complete Test with Real Data")
        logger.info(f"{'='*60}")
        
        # 使用第一条真实数据
        data = self.df.iloc[0].to_dict()
        
        # 解析数据
        if 'extra_info' in data and isinstance(data['extra_info'], str):
            extra_info = json.loads(data['extra_info'])
        else:
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
        logger.info("\nGenerating workflow with real LLM...")
        
        start_time = datetime.now()
        full_response = await self.generate_response(prompt)
        generation_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Generated response in {generation_time:.2f} seconds")
        
        # 提取workflow
        extracted_workflow = self.extract_workflow(full_response)
        
        # 计算reward
        logger.info("\nComputing reward...")
        reward_model = data.get('reward_model', {})
        if isinstance(reward_model, str):
            reward_model = json.loads(reward_model)
        ground_truth = reward_model.get('ground_truth', 'default')
        
        # 这里会触发实际的workflow执行
        reward_score = compute_score(full_response, ground_truth, extra_info)
        
        logger.info(f"\nFinal reward score: {reward_score:.3f}")
        
        # 构建完整的测试结果
        test_result = {
            "test_timestamp": datetime.now().isoformat(),
            "data_source": data.get('data_source', ''),
            "task_name": task_name,
            "test_cases": test_cases,
            "prompt": prompt,
            "model_response": {
                "full_response": full_response,
                "extracted_workflow": extracted_workflow,
                "generation_time_seconds": generation_time,
                "response_length": len(full_response)
            },
            "execution": {
                "ground_truth": ground_truth,
                "reward_score": reward_score,
                "execution_status": "success" if reward_score > 0 else "failed"
            },
            "metadata": {
                "model": self.model,
                "temperature": 0.7,
                "max_tokens": 2000,
                "data_index": 0,
                "extra_info": extra_info
            }
        }
        
        # 保存结果到JSON文件
        output_path = Path(__file__).parent / "test_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\nTest results saved to: {output_path}")
        
        # 打印摘要
        logger.info(f"\n{'='*60}")
        logger.info("Test Summary:")
        logger.info(f"- Task: {task_name}")
        logger.info(f"- Model Response Length: {len(full_response)} chars")
        logger.info(f"- Extracted Workflow Length: {len(extracted_workflow)} chars")
        logger.info(f"- Generation Time: {generation_time:.2f} seconds")
        logger.info(f"- Reward Score: {reward_score:.3f}")
        logger.info(f"- Execution Status: {'Success' if reward_score > 0 else 'Failed'}")
        logger.info(f"{'='*60}")
        
        return test_result


async def main():
    """主测试函数"""
    tester = TestInternBootcampRewardV2()
    
    # 运行完整测试
    await tester.run_complete_test()
    
    logger.info("\nTest completed!")


if __name__ == "__main__":
    # 创建并运行事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        # 不要立即关闭事件循环，让pending的任务完成
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()