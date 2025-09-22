#!/usr/bin/env python
"""
极简测试脚本 - 只测试单个样例
用于快速验证系统是否能够运行
"""

import json
import asyncio
import aiohttp
from pathlib import Path

# 简单的CoT workflow模板
# 必须用```python和```包裹
SIMPLE_COT_WORKFLOW = '''```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        self.generate = operator.Generate(self.llm, self.problem_text)

    async def run_workflow(self):
        """简化的CoT workflow - 只用一个Generate步骤"""
        # 只使用一个简单的Generate步骤
        instruction = "Please solve this problem step by step. Show your work clearly."
        solution = await self.generate(instruction, "")
        return solution
```'''

async def test_single_sample():
    """测试单个样例"""

    print("="*60)
    print("    极简测试 - 单样例")
    print("="*60)

    # 1. 加载一个GSM8K样例
    print("\n1. 加载测试样例...")
    data_path = Path("../ScoreFlow/benchmark_mapping.jsonl")

    # 从benchmark_mapping获取GSM8K数据路径
    gsm8k_data_path = None
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry['benchmark'] == 'gsm8k':
                    gsm8k_data_path = entry['data_test_dir']
                    break

    if not gsm8k_data_path:
        print("错误: 无法找到GSM8K数据路径")
        return

    print(f"   数据路径: {gsm8k_data_path}")

    # 加载第一个样例
    with open(gsm8k_data_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        sample = json.loads(first_line)

    print(f"   样例索引: {sample.get('index', 0)}")
    print(f"   问题预览: {sample['question'][:100]}...")

    # 2. 准备请求数据
    print("\n2. 准备请求数据...")
    request_data = {
        "data_source": "gsm8k",
        "solution_str": SIMPLE_COT_WORKFLOW,
        "ground_truth": "default",
        "extra_info": {
            "test_cases": [0],  # 只测试第一个样例
            "data_path": gsm8k_data_path
        }
    }

    print("   请求数据准备完成")

    # 3. 发送到Reward Server
    print("\n3. 发送请求到Reward Server...")
    reward_server_url = "http://localhost:7788"

    try:
        timeout = aiohttp.ClientTimeout(total=60)  # 60秒超时
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{reward_server_url}/compute_score",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                result = await response.json()

                print("\n4. 收到响应:")
                print(f"   成功: {result.get('success', False)}")
                print(f"   分数: {result.get('score', 0.0)}")

                if result.get('error'):
                    print(f"   错误: {result['error']}")

                if result.get('message'):
                    print(f"   消息: {result['message']}")

                return result

    except asyncio.TimeoutError:
        print("   ❌ 请求超时")
        return None
    except aiohttp.ClientConnectorError:
        print("   ❌ 无法连接到Reward Server")
        print("   请确保Reward Server运行在 http://localhost:7788")
        return None
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

async def main():
    """主函数"""
    print("极简测试脚本 - 测试单个GSM8K样例")
    print("-"*60)
    print("注意事项:")
    print("1. 确保Reward Server运行在 http://localhost:7788")
    print("2. 此脚本只测试一个样例，用于验证系统是否能运行")
    print("-"*60)

    result = await test_single_sample()

    print("\n" + "="*60)
    if result and result.get('success'):
        print("✅ 测试成功! 系统可以正常运行")
    else:
        print("❌ 测试失败，请检查错误信息")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())