import sys
import json
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from internbootcamp_reward import InternBootcampRewardCalculator

async def single_call(reward_calculator, idx):
    # 你可以根据需要传不同的 prompt
    prompt = f"hello {idx}"
    try:
        result = await reward_calculator.call_llm_api(prompt)
        print(f"Task {idx} result: {result}")
        return result
    except Exception as e:
        print(f"Task {idx} error: {e}")
        return None

async def main():
    reward_calculator = InternBootcampRewardCalculator(
        config_path=r"D:\temp\Flow_RL\Test_FILE\verl_internbootcamp\config.json"
    )
    tasks = []
    num_concurrent = 100  # 并发数量，可根据实际情况调整
    for i in range(num_concurrent):
        tasks.append(single_call(reward_calculator, i))
    results = await asyncio.gather(*tasks)
    print(f"Total finished: {len([r for r in results if r is not None])}")

if __name__ == "__main__":
    asyncio.run(main())

    





