#!/usr/bin/env python3
"""
测试简化后的GSM8K Handler和LLM Judge
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append('/Users/luogan/Code/workflow_generation/Flow_RL')
os.chdir('/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE')

from metagpt.configs.llm_config import LLMConfig, LLMType
from ScoreFlow.scripts.gsm8k.handler import Gsm8kHandler

async def test_gsm8k_judge():
    """测试GSM8K的LLM-based Judge"""
    
    # 配置LLM
    llm_config = LLMConfig(
        api_type=LLMType.OPENAI,
        model='qwen-turbo',
        api_key='956c41bd0f31beaf68b871d4987af4bb',
        base_url='https://idealab.alibaba-inc.com/api/openai/v1'
    )
    
    # 创建handler
    dataset_path = '/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k/1000_train.jsonl'
    handler = Gsm8kHandler(dataset_path=dataset_path, config=llm_config)
    
    # 测试用例
    test_cases = [
        {
            "name": "完全正确的答案",
            "model_output": "The total cost is $150 and James pays half, so he pays $75",
            "ground_truth_data": {
                "question": "James gets a cable program. The first 100 channels cost $100 and the next 100 channels cost half that much. He splits it evenly with his roommate. How much did he pay?",
                "answer": "The next 100 channels cost 100/2=$<<100/2=50>>50\nSo the total cost is 100+50=$<<100+50=150>>150\nSo he pays 150/2=$<<150/2=75>>75\n#### 75"
            },
            "expected": True
        },
        {
            "name": "正确答案但格式不同",
            "model_output": "James needs to pay 75 dollars",
            "ground_truth_data": {
                "question": "James gets a cable program. The first 100 channels cost $100 and the next 100 channels cost half that much. He splits it evenly with his roommate. How much did he pay?",
                "answer": "#### 75"
            },
            "expected": True
        },
        {
            "name": "错误的答案",
            "model_output": "James pays $150 in total",
            "ground_truth_data": {
                "question": "James gets a cable program. The first 100 channels cost $100 and the next 100 channels cost half that much. He splits it evenly with his roommate. How much did he pay?",
                "answer": "#### 75"
            },
            "expected": False
        },
        {
            "name": "包含正确数字但上下文错误",
            "model_output": "The cable costs 75 channels",
            "ground_truth_data": {
                "question": "James gets a cable program. The first 100 channels cost $100 and the next 100 channels cost half that much. He splits it evenly with his roommate. How much did he pay?",
                "answer": "#### 75"
            },
            "expected": False  # 75是对的但单位错误（channels vs dollars）
        }
    ]
    
    print("============================================================")
    print("测试GSM8K的简化Handler和LLM Judge")
    print("============================================================\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print("-" * 40)
        print(f"模型输出: {test_case['model_output'][:100]}...")
        print(f"标准答案: {test_case['ground_truth_data']['answer'][:50]}...")
        print(f"期望结果: {'正确' if test_case['expected'] else '错误'}")
        
        # 调用judge
        result = await handler.judge(
            test_case['model_output'],
            test_case['ground_truth_data']
        )
        
        # 验证结果
        if result == test_case['expected']:
            print(f"✅ 测试通过")
        else:
            print(f"❌ 测试失败 (判断为{'正确' if result else '错误'})")
        print()
    
    print("============================================================")
    print("测试完成")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(test_gsm8k_judge())