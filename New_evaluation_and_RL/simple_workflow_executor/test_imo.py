"""
测试IMO Workflow执行
使用真实的IMO问题和workflow代码
"""

import asyncio
import json
from pathlib import Path
from simple_executor import SimpleWorkflowExecutor

# IMO示例workflow代码
IMO_WORKFLOW_CODE = '''
import asyncio
from typing import List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        # 初始化5个必需的算子
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.verifier = operator.Verifier(self.llm, self.problem_text)
        self.refiner = operator.Refiner(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        IMO问题求解workflow
        使用Verifier-Refiner循环确保数学严谨性
        """
        import asyncio

        # Step 1: 并行探索多种解法
        print("🔍 Step 1: 探索多种解法...")
        approaches = await asyncio.gather(
            self.generate(
                instruction="Solve this IMO problem using algebraic methods. Provide detailed step-by-step reasoning.",
                context=""
            ),
            self.generate(
                instruction="Solve this IMO problem using geometric or visual insights if applicable. Otherwise use number theory approach.",
                context=""
            ),
            self.generate(
                instruction="Solve this IMO problem using proof by contradiction or induction if suitable.",
                context=""
            )
        )

        # Step 2: 选择最佳方法
        print("🎯 Step 2: 选择最佳解法...")
        best_solution = await self.ensemble(
            instruction="Select the most promising and rigorous solution approach. Explain your choice.",
            contexts=approaches
        )

        # Step 3: 验证解答
        print("✅ Step 3: 验证解答的严谨性...")
        verification = await self.verifier(
            instruction="Verify this IMO solution with the highest standards of mathematical rigor",
            context=best_solution
        )

        # Step 4: 如果需要，改进解答
        if "invalid" in str(verification.get('verdict', '')).lower() or "gap" in str(verification.get('verdict', '')).lower():
            print("🔧 Step 4: 改进解答...")
            refined = await self.refiner(
                instruction="Fix all identified issues and provide a complete, rigorous proof",
                context=best_solution,
                verification_feedback=str(verification)
            )
            final_solution = refined['refined_solution']
        else:
            print("✨ Step 4: 解答已通过验证")
            final_solution = best_solution

        # Step 5: 生成最终答案
        print("📝 Step 5: 整理最终答案...")
        final_answer = await self.summarize(
            instruction="Extract and format the final answer clearly. Include the complete proof.",
            context=final_solution
        )

        return f"Final Answer:\\n{final_answer}"

    async def __call__(self):
        """
        主入口点，执行workflow
        """
        TIMEOUT = 180

        try:
            # 执行workflow
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Final Answer: Error - {str(e)}\\nDetails: {error_details}"
'''

def load_imo_problems():
    """加载IMO测试问题"""
    imo_file = Path("D:/temp/Flow_RL/Processed_dataset/imo_test.jsonl")

    problems = []
    if imo_file.exists():
        with open(imo_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
        print(f"✅ 加载了 {len(problems)} 道IMO问题")
    else:
        # 使用默认问题
        problems = [{
            "task_id": "imo_test",
            "question": "Prove that for any positive integer n, the sum 1 + 2 + ... + n equals n(n+1)/2.",
            "answer": "This can be proved by mathematical induction."
        }]
        print("⚠️ 使用默认测试问题")

    return problems

async def test_single_problem(executor, problem, workflow_code):
    """测试单个IMO问题"""
    print(f"\n{'='*60}")
    print(f"📚 问题ID: {problem.get('task_id', 'unknown')}")
    print(f"📝 问题内容: {problem['question'][:100]}...")
    print(f"{'='*60}")

    # 执行workflow
    result = await executor.execute_workflow(
        workflow_code=workflow_code,
        problem_text=problem['question'],
        benchmark_name="imo",
        test_case=problem.get('task_id', 0)
    )

    # 显示结果
    if result['success']:
        print(f"✅ 执行成功！")
        print(f"📊 结果预览:")
        result_text = str(result.get('result', ''))
        if len(result_text) > 500:
            print(result_text[:500] + "...")
        else:
            print(result_text)
    else:
        print(f"❌ 执行失败: {result.get('error', 'Unknown error')}")

    return result

async def main():
    """主测试函数"""
    print("🚀 IMO Workflow执行器测试")
    print("=" * 60)

    # 创建执行器
    executor = SimpleWorkflowExecutor()

    # 加载IMO问题
    problems = load_imo_problems()

    # 选择要测试的问题
    test_problems = problems[:2]  # 测试前2个问题

    print(f"\n准备测试 {len(test_problems)} 道IMO问题")

    # 测试每个问题
    results = []
    for i, problem in enumerate(test_problems, 1):
        print(f"\n{'='*60}")
        print(f"测试问题 {i}/{len(test_problems)}")

        result = await test_single_problem(
            executor=executor,
            problem=problem,
            workflow_code=IMO_WORKFLOW_CODE
        )
        results.append(result)

        # 短暂延迟，避免API限流
        if i < len(test_problems):
            print("\n⏳ 等待3秒后继续...")
            await asyncio.sleep(3)

    # 汇总结果
    print(f"\n{'='*60}")
    print("📊 测试汇总")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r['success'])
    print(f"✅ 成功: {success_count}/{len(results)}")
    print(f"❌ 失败: {len(results) - success_count}/{len(results)}")

    # 保存结果
    output_file = Path("test_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 结果已保存到: {output_file}")

    print("\n✨ 测试完成！")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())