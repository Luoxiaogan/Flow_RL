"""
测试ScoreFlow Reward函数
"""
import asyncio
import pandas as pd
from scoreflow_reward import compute_score, _compute_score_async

def test_with_parquet_data():
    """使用实际的parquet数据测试"""
    print("=== Testing with actual parquet data ===")
    
    # 读取测试数据
    df = pd.read_parquet('data/test_gen/test.parquet')
    
    # 测试第一行数据
    row = df.iloc[0]
    
    # 构造一个简单的测试solution（包含workflow）
    test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
    
    async def run_workflow(self):
        # Generate initial solution
        initial_solution = await self.custom(
            instruction="Solve this mathematical problem step by step. Show all your work and reasoning."
        )
        
        # Review and improve the solution
        final_solution = await self.review(pre_solution=initial_solution)
        
        return final_solution
</graph>
"""
    
    print(f"Data source: {row['data_source']}")
    print(f"Test cases: {row['extra_info']['test_cases']}")
    print(f"Data path: {row['extra_info']['data_path']}")
    
    # 调用compute_score函数
    score = compute_score(
        data_source=row['data_source'],
        solution_str=test_solution,
        ground_truth=row['reward_model']['ground_truth'],
        extra_info=row['extra_info']
    )
    
    print(f"Computed score: {score}")
    return score

def test_with_gsm8k():
    """测试GSM8K benchmark"""
    print("\n=== Testing with GSM8K benchmark ===")
    
    test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.answer_generate(
            instruction="Solve this grade school math problem step by step."
        )
        return solution
</graph>
"""
    
    test_extra_info = {
        'data_path': 'Processed_dataset/gsm8k/test.jsonl',
        'test_cases': [0, 1, 2],  # 使用前3个测试用例
        'raw_data': 0,
        'answer': 'test_answer'
    }
    
    score = compute_score(
        data_source='gsm8k',
        solution_str=test_solution,
        ground_truth='default',
        extra_info=test_extra_info
    )
    
    print(f"GSM8K score: {score}")
    return score

async def test_async_execution():
    """测试异步执行"""
    print("\n=== Testing async execution ===")
    
    test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.flexible_custom(
            custom_instruction="Analyze and solve this problem systematically"
        )
        return solution
</graph>
"""
    
    test_extra_info = {
        'data_path': 'Processed_dataset/gsm8k/test.jsonl',
        'test_cases': [0],  # 只用一个测试用例进行快速测试
        'raw_data': 0,
        'answer': 'test_answer'
    }
    
    score = await _compute_score_async(
        'gsm8k',
        test_solution,
        'default',
        test_extra_info
    )
    
    print(f"Async test score: {score}")
    return score

def test_invalid_workflow():
    """测试无效的workflow"""
    print("\n=== Testing invalid workflow ===")
    
    # 没有workflow的solution
    invalid_solution = "This is not a valid workflow"
    
    test_extra_info = {
        'data_path': 'Processed_dataset/gsm8k/test.jsonl',
        'test_cases': [0],
        'raw_data': 0,
        'answer': 'test_answer'
    }
    
    score = compute_score(
        data_source='gsm8k',
        solution_str=invalid_solution,
        ground_truth='default',
        extra_info=test_extra_info
    )
    
    print(f"Invalid workflow score (should be 0.0): {score}")
    assert score == 0.0, "Invalid workflow should return 0.0"
    print("✓ Invalid workflow test passed")

def main():
    """运行所有测试"""
    print("Starting ScoreFlow Reward Function Tests")
    print("=" * 50)
    
    try:
        # 测试无效workflow
        test_invalid_workflow()
        
        # 测试GSM8K
        # 注意：这需要有效的API配置和数据集
        test_with_gsm8k()
        
        # 测试异步执行
        asyncio.run(test_async_execution())
        
        # 测试实际的parquet数据
        # 注意：这需要有test.parquet文件
        test_with_parquet_data()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()