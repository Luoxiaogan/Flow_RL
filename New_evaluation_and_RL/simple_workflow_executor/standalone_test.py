"""
独立测试脚本 - 使用真实的Gemini API
不依赖MetaGPT，直接调用API
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Gemini API配置
API_URL = "http://39.96.211.155:8000/proxy/api/openai/v1/chat/completions"
API_KEY = "8cf060f9e1f444858609730176542253"
MODEL = "gemini-2.5-pro"

class GeminiLLM:
    """Gemini LLM wrapper"""

    async def aask(self, prompt: str, system_prompt: str = "You are a helpful AI assistant"):
        """调用Gemini API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            try:
                async with session.post(API_URL, headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        print(f"API Error {response.status}: {error_text}")
                        return f"API Error: {response.status}"
            except Exception as e:
                print(f"Request failed: {str(e)}")
                return f"Error: {str(e)}"

# 模拟算子
class MockOperator:
    """基础算子类"""
    def __init__(self, llm, problem_text):
        self.llm = llm
        self.problem_text = problem_text

class Generate(MockOperator):
    """生成算子"""
    async def __call__(self, instruction: str, context: str = ""):
        prompt = f"""
Problem: {self.problem_text}

Instruction: {instruction}

Context: {context}

Please provide a detailed solution.
"""
        return await self.llm.aask(prompt)

class Verifier(MockOperator):
    """验证算子"""
    async def __call__(self, instruction: str, context: str):
        prompt = f"""
Problem: {self.problem_text}

Solution to verify:
{context}

Instruction: {instruction}

Provide verification result with:
1. Verdict: correct/incorrect/has_gaps
2. Findings: List of issues found
"""
        result = await self.llm.aask(prompt)
        # 简单解析返回字典格式
        return {
            "verdict": "correct" if "correct" in result.lower() else "has_gaps",
            "findings": [],
            "raw_response": result
        }

class Refiner(MockOperator):
    """改进算子"""
    async def __call__(self, instruction: str, context: str, verification_feedback: str):
        prompt = f"""
Problem: {self.problem_text}

Original solution:
{context}

Verification feedback:
{verification_feedback}

Instruction: {instruction}

Provide an improved solution.
"""
        result = await self.llm.aask(prompt)
        return {
            "refined_solution": result
        }

class Summarize(MockOperator):
    """总结算子"""
    async def __call__(self, instruction: str, context: str):
        prompt = f"""
Problem: {self.problem_text}

Content to summarize:
{context}

Instruction: {instruction}
"""
        return await self.llm.aask(prompt)

async def test_verifier_refiner_loop():
    """测试Verifier-Refiner循环"""
    print("=" * 60)
    print("Testing Verifier-Refiner Loop with Gemini API")
    print("=" * 60)

    # 创建LLM实例
    llm = GeminiLLM()

    # 测试问题
    problem = "Prove that for any positive integer n, the sum 1 + 2 + ... + n equals n(n+1)/2."

    # 初始化算子
    generate = Generate(llm, problem)
    verifier = Verifier(llm, problem)
    refiner = Refiner(llm, problem)
    summarize = Summarize(llm, problem)

    print(f"\nProblem: {problem}")
    print("=" * 60)

    try:
        # Step 1: 生成初始解答
        print("\n[Step 1] Generating initial solution...")
        start_time = datetime.now()

        solution = await generate(
            instruction="Provide a mathematical proof using induction",
            context=""
        )

        print(f"Initial solution generated ({len(solution)} chars)")
        print(f"Preview: {solution[:200]}...")

        # Step 2: 验证解答
        print("\n[Step 2] Verifying solution...")
        verification = await verifier(
            instruction="Check if this proof is mathematically rigorous",
            context=solution
        )

        verdict = verification.get('verdict', 'unknown')
        print(f"Verification verdict: {verdict}")

        # Step 3: 如果需要，改进解答
        if verdict != "correct":
            print("\n[Step 3] Refining solution...")
            refined = await refiner(
                instruction="Fix any issues and make the proof more rigorous",
                context=solution,
                verification_feedback=str(verification)
            )
            solution = refined['refined_solution']
            print(f"Solution refined ({len(solution)} chars)")
        else:
            print("\n[Step 3] Solution passed verification!")

        # Step 4: 总结
        print("\n[Step 4] Summarizing final answer...")
        final = await summarize(
            instruction="Provide a concise summary of the proof",
            context=solution
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 60)
        print("Test Results")
        print("=" * 60)
        print(f"Execution time: {duration:.2f} seconds")
        print(f"\nFinal Answer:")
        print("-" * 40)
        print(final[:500] + "..." if len(final) > 500 else final)
        print("-" * 40)

        return {
            "success": True,
            "duration": duration,
            "final_answer": final
        }

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """主函数"""
    print("Starting standalone test with real Gemini API")
    print("API URL:", API_URL)
    print("Model:", MODEL)

    result = await test_verifier_refiner_loop()

    # 保存结果
    with open("standalone_test_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\nResult saved to standalone_test_result.json")
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(main())