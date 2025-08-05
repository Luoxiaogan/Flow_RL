"""
测试异步并行执行性能
"""
import asyncio
import time
from internbootcamp_reward import compute_score, _compute_score_async

async def test_performance():
    # 测试数据
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
    
    # 创建多个测试用例
    test_cases = ["{'input': 'hello'}", "{'input': 'world'}", "{'input': 'test'}", 
                  "{'input': 'async'}", "{'input': 'parallel'}"]
    
    test_extra_info = {
        'task_name': 'adidyoumean',
        'test_cases': test_cases
    }
    
    print(f"Testing with {len(test_cases)} test cases...")
    
    # 测试异步版本
    start_time = time.time()
    score = await _compute_score_async(test_solution, "default", test_extra_info)
    async_duration = time.time() - start_time
    
    print(f"Async version completed in {async_duration:.2f} seconds")
    print(f"Average time per test case: {async_duration/len(test_cases):.2f} seconds")
    print(f"Score: {score:.3f}")
    
    # 估算串行执行时间（基于平均时间）
    estimated_serial_time = (async_duration / len(test_cases)) * len(test_cases) * 0.8  # 假设有20%的并行开销
    print(f"Estimated serial execution time: {estimated_serial_time:.2f} seconds")
    print(f"Speed improvement: {estimated_serial_time/async_duration:.2f}x")

if __name__ == "__main__":
    asyncio.run(test_performance())