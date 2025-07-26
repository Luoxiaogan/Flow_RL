"""
快速测试InternBootcamp reward功能
"""
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from internbootcamp_reward import compute_score

# 测试用的workflow response
test_response = """
Based on the problem, I'll create a workflow to solve the Adidyoumean typo detection task.

<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = create(config)
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

# 测试数据（从train.parquet中的格式）
test_data = {
    'data_source': 'internbootcamp_adidyoumean',
    'prompt': json.dumps([{"role": "user", "content": "Create a workflow..."}]),
    'ability': 'general_reasoning',
    'reward_model': json.dumps({
        "task_name": "adidyoumean",
        "test_cases": [
            "{'input': 'hellno'}",
            "{'input': 'abacaba'}",
            "{'input': 'asdfasdf'}"
        ],
        "score": 1.0
    }),
    'extra_info': '{}'
}

print("Starting quick test...")
print(f"Test response length: {len(test_response)} chars")
print(f"Number of test cases: 3")

try:
    score = compute_score(test_response, test_data)
    print(f"\nComputed reward score: {score:.3f}")
    
    if score > 0:
        print("✓ Test passed! Reward function is working.")
    else:
        print("✗ Test failed! Score is 0.")
        
except Exception as e:
    print(f"✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()

print("\nQuick test completed.")