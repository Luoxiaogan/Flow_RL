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
    test_solution = r'''
<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        import asyncio
        
        # Step 1: Parallel extraction and deep question analysis
        extraction_task = self.generate(
            instruction="Extract ALL numbers, dates, entities, facts, and relationships from the passage. List every occurrence separately, even if values repeat. Include context for each number."
        )
        
        question_interpretation_task = self.generate(
            instruction="Analyze the question carefully: 1) Is it asking for a sum/total or a single value? 2) Look for keywords like 'total', 'combined', 'each', 'per', 'altogether'. 3) Could the question be ambiguous? List multiple possible interpretations if unclear."
        )
        
        # Execute in parallel
        information_extraction, question_interpretation = await asyncio.gather(
            extraction_task,
            question_interpretation_task
        )
        
        # Step 2: Create comprehensive context
        combined_context = f"EXTRACTED DATA:\n{information_extraction}\n\nQUESTION ANALYSIS:\n{question_interpretation}"
        
        # Step 3: Generate multiple interpretations in parallel
        # Each strategy considers different possible meanings
        
        # Strategy 1: Conservative interpretation (single value)
        solution_conservative = self.generate(
            instruction="Answer assuming the question asks for a SINGLE value, not a sum. If multiple instances exist with the same value, return that common value. If different values exist, return the first or most relevant one.",
            context=combined_context
        )
        
        # Strategy 2: Summation interpretation
        solution_sum = self.generate(
            instruction="Answer by summing ALL relevant values found in the passage. Add up every instance that matches what the question asks for.",
            context=combined_context
        )
        
        # Strategy 3: Counting interpretation
        solution_count = self.generate(
            instruction="Answer by counting the NUMBER of occurrences or instances, not their values. Count how many times something happens.",
            context=combined_context
        )
        
        # Strategy 4: Contextual interpretation
        solution_contextual = self.generate(
            instruction="Consider the grammatical structure and context of the question. Does it refer to a specific event or all events? Is there implicit context suggesting which answer makes most sense?",
            context=combined_context
        )
        
        # Strategy 5: Literal interpretation
        solution_literal = self.generate(
            instruction="Take the question at face value without overthinking. What's the most straightforward answer based on direct text matching?",
            context=combined_context
        )
        
        # Execute all interpretations in parallel
        candidates = await asyncio.gather(
            solution_conservative,
            solution_sum,
            solution_count,
            solution_contextual,
            solution_literal
        )
        
        # Step 4: Smart ensemble considering question ambiguity
        preliminary_answer = await self.ensemble(
            instruction="Review all interpretations. If the question is unambiguous, select the consensus answer. If ambiguous, prefer the simplest interpretation (single value over sum, specific over general). Extract just the numeric answer or text span.",
            contexts_to_ensemble=candidates
        )
        
        # Step 5: Validation against common patterns
        validated_answer = await self.revise(
            instruction="Check if this answer makes logical sense: Is it within reasonable bounds? For 'how many yards' questions, is the answer a plausible yardage? If the answer seems like a sum but all components are identical, consider returning the single value instead.",
            context_to_revise=preliminary_answer
        )
        
        # Step 6: Final formatting
        final_answer = await self.generate(
            instruction="Return ONLY the answer with no explanation: just the number, date, or exact text span from the passage.",
            context=validated_answer
        )
        
        return final_answer
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
'''
    
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
    
    async def run_workflow(self):
        solution = await self.custom(
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