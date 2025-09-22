"""
测试Verifier-Refiner循环的简单Workflow
用于验证执行器的基本功能
"""

import asyncio
import json
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from simple_executor import SimpleWorkflowExecutor

# 简单的Verifier-Refiner循环workflow
VERIFIER_REFINER_WORKFLOW = '''
import asyncio
from typing import List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

class Workflow:
    def __init__(self, config, problem) -> None:
        """初始化Workflow"""
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        # 初始化必需的算子
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.verifier = operator.Verifier(self.llm, self.problem_text)
        self.refiner = operator.Refiner(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)

        print("✅ Workflow初始化完成")

    async def run_workflow(self):
        """
        简单的Verifier-Refiner循环示例
        最多迭代3次，确保解答的数学严谨性
        """
        print("\\n" + "="*60)
        print("🚀 开始执行Verifier-Refiner循环Workflow")
        print("="*60)

        # Step 1: 生成初始解答
        print("\\n📝 Step 1: 生成初始解答...")
        initial_solution = await self.generate(
            instruction="""
            Solve this mathematical problem step by step.
            Provide a clear and detailed solution with all necessary steps.
            Show your reasoning at each step.
            """,
            context=""
        )

        print(f"✅ 初始解答生成完成 (长度: {len(initial_solution)} 字符)")

        # 迭代改进循环
        current_solution = initial_solution
        max_iterations = 3

        for iteration in range(max_iterations):
            print(f"\\n{'='*40}")
            print(f"🔄 迭代 {iteration + 1}/{max_iterations}")
            print(f"{'='*40}")

            # Step 2: 验证当前解答
            print(f"\\n🔍 验证解答的严谨性...")
            verification = await self.verifier(
                instruction="""
                Carefully verify this mathematical solution.
                Check for:
                1. Logical correctness of each step
                2. Mathematical rigor and completeness
                3. Any gaps in reasoning or unjustified claims
                4. Calculation errors

                Be strict but fair in your assessment.
                """,
                context=current_solution
            )

            # 提取验证结果
            verdict = str(verification.get('verdict', '')).lower()
            findings = verification.get('findings', [])

            print(f"📊 验证结果: {verdict}")
            if findings:
                print(f"📌 发现 {len(findings)} 个问题点")
                for i, finding in enumerate(findings[:3], 1):  # 只显示前3个
                    print(f"   {i}. {finding.get('issue', 'N/A')[:100]}...")

            # 检查是否通过验证
            if "correct" in verdict and not any(
                word in verdict for word in ["invalid", "incorrect", "error", "gap"]
            ):
                print(f"\\n✅ 解答通过验证！在第 {iteration + 1} 次迭代后完成")
                break

            # Step 3: 改进解答
            print(f"\\n🔧 基于验证反馈改进解答...")
            refined = await self.refiner(
                instruction="""
                Improve this solution based on the verification feedback.
                Address all identified issues:
                1. Fix any logical errors
                2. Fill in reasoning gaps
                3. Correct calculations
                4. Enhance clarity and rigor

                Provide a complete, corrected solution.
                """,
                context=current_solution,
                verification_feedback=json.dumps(verification, ensure_ascii=False)
            )

            # 更新当前解答
            current_solution = refined.get('refined_solution', current_solution)
            print(f"✅ 解答改进完成 (新长度: {len(current_solution)} 字符)")

            # 最后一次迭代的特殊处理
            if iteration == max_iterations - 1:
                print(f"\\n⚠️ 达到最大迭代次数 ({max_iterations})")

        # Step 4: 总结最终答案
        print(f"\\n📋 Step 4: 总结最终答案...")
        final_answer = await self.summarize(
            instruction="""
            Summarize the final solution clearly and concisely.
            Include:
            1. The problem statement (brief)
            2. The key steps of the solution
            3. The final answer clearly stated

            Format it professionally.
            """,
            context=current_solution
        )

        print(f"✅ 最终答案总结完成")

        # 返回结果
        result = f"""
{'='*60}
📊 Workflow执行完成
{'='*60}

🎯 最终答案：
{final_answer}

📈 执行统计：
- 初始解答长度: {len(initial_solution)} 字符
- 最终解答长度: {len(current_solution)} 字符
- 总结长度: {len(final_answer)} 字符
{'='*60}
"""

        return result

    async def __call__(self):
        """主入口点"""
        TIMEOUT = 180

        try:
            result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return result
        except asyncio.TimeoutError:
            return "Error: Workflow execution timed out (180s)"
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return f"Error: {str(e)}\\n\\nTraceback:\\n{error_trace}"
'''

# 测试问题集合
TEST_PROBLEMS = [
    {
        "id": "simple_proof",
        "problem": "Prove that the sum of the first n positive integers is n(n+1)/2.",
        "type": "proof"
    },
    {
        "id": "inequality",
        "problem": "For positive real numbers a, b, c, prove that (a+b+c)(1/a + 1/b + 1/c) ≥ 9.",
        "type": "inequality"
    },
    {
        "id": "number_theory",
        "problem": "Prove that if p is a prime number greater than 3, then p^2 - 1 is divisible by 24.",
        "type": "number_theory"
    }
]

async def test_workflow():
    """测试Verifier-Refiner循环workflow"""
    print("🎯 Verifier-Refiner循环Workflow测试")
    print("=" * 80)

    # 创建执行器
    executor = SimpleWorkflowExecutor()

    # 选择测试问题
    test_problem = TEST_PROBLEMS[0]  # 使用第一个简单的证明题

    print(f"\n📚 测试问题: {test_problem['id']}")
    print(f"📝 问题类型: {test_problem['type']}")
    print(f"❓ 问题内容: {test_problem['problem']}")
    print("=" * 80)

    # 执行workflow
    print("\n⚡ 开始执行Workflow...")
    result = await executor.execute_workflow(
        workflow_code=VERIFIER_REFINER_WORKFLOW,
        problem_text=test_problem['problem'],
        benchmark_name="test",
        test_case=test_problem['id']
    )

    # 显示结果
    print("\n" + "=" * 80)
    print("📊 执行结果")
    print("=" * 80)

    if result['success']:
        print("✅ Workflow执行成功！")
        print(f"⏱️ 执行时间: {result.get('execution_time', 0):.2f}秒")
        print(f"\n📄 Workflow输出:")
        print("-" * 40)
        print(result['result'])
        print("-" * 40)
    else:
        print(f"❌ Workflow执行失败!")
        print(f"错误: {result.get('error', 'Unknown error')}")
        if 'error_trace' in result:
            print(f"\n错误追踪:")
            print(result['error_trace'])

    # 保存结果
    output_file = Path("verifier_refiner_test_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 完整结果已保存到: {output_file}")

    return result

async def test_all_problems():
    """测试所有问题"""
    print("🎯 批量测试Verifier-Refiner循环")
    print("=" * 80)

    executor = SimpleWorkflowExecutor()
    results = []

    for i, problem in enumerate(TEST_PROBLEMS, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(TEST_PROBLEMS)}: {problem['id']}")
        print(f"{'='*60}")

        result = await executor.execute_workflow(
            workflow_code=VERIFIER_REFINER_WORKFLOW,
            problem_text=problem['problem'],
            benchmark_name="test",
            test_case=problem['id']
        )

        results.append({
            'problem': problem,
            'result': result
        })

        # 短暂延迟
        if i < len(TEST_PROBLEMS):
            print("\n⏳ 等待2秒后继续...")
            await asyncio.sleep(2)

    # 汇总
    print("\n" + "=" * 80)
    print("📊 测试汇总")
    print("=" * 80)

    success = sum(1 for r in results if r['result']['success'])
    print(f"✅ 成功: {success}/{len(results)}")
    print(f"❌ 失败: {len(results) - success}/{len(results)}")

    # 保存所有结果
    output_file = Path("all_test_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 所有结果已保存到: {output_file}")

if __name__ == "__main__":
    # 直接运行单个测试（避免输入问题）
    print("\n🚀 运行单个测试...")
    asyncio.run(test_workflow())