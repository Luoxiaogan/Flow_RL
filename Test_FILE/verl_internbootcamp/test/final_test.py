"""
最终测试脚本 - 验证InternBootcamp Reward Function V2
"""
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from internbootcamp_reward_v2 import compute_score

# 测试数据（新格式）
test_data = {
    "data_source": "internbootcamp_adidyoumean",
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
        "task_name": "adidyoumean",
        "test_cases": [
            "{'input': 'hello'}",      # 没有typo
            "{'input': 'hellno'}",     # 有typo
            "{'input': 'abacaba'}"     # 没有typo
        ],
        "entry_id": 1,
        "task_type": "string_manipulation",
        "workflow_type": "predefined",
        "num_examples": 3
    }
}

# 测试workflow（简单版本）
test_solution = """
Based on the problem, I'll create a workflow to solve the Adidyoumean typo detection task.

<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        # Solve the typo detection problem
        solution = await self.custom(
            instruction="Analyze the input string for typos (3+ consecutive consonants with at least 2 different characters). If no typos exist, return the original string. If typos exist, insert minimum spaces to eliminate them. Return the answer in [answer] tags."
        )
        return solution
</graph>
"""

print("=" * 60)
print("Final Test - InternBootcamp Reward Function V2")
print("=" * 60)

# 提取必要信息
ground_truth = test_data['reward_model']['ground_truth']
extra_info = test_data['extra_info']

print(f"\nTask: {extra_info['task_name']}")
print(f"Test cases: {len(extra_info['test_cases'])}")
print(f"Solution length: {len(test_solution)} chars")

print("\nComputing reward score...")

try:
    # 计算分数
    score = compute_score(test_solution, ground_truth, extra_info)
    
    print(f"\nResult: {score:.3f}")
    
    if score > 0:
        print("[SUCCESS] Reward function is working correctly!")
    else:
        print("[WARNING] Score is 0, check logs for details")
        
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")