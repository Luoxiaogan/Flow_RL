#!/usr/bin/env python3
"""
综合测试脚本：测试VectorSearch operator与其他operator的集成
Tests the integrated VectorSearch operator with workflow scenarios
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all operators - avoid conflict with built-in operator module
import operator as workflow_operator
VectorSearch = workflow_operator.VectorSearch
Generate = workflow_operator.Generate
Revise = workflow_operator.Revise
Ensemble = workflow_operator.Ensemble
Summarize = workflow_operator.Summarize
Decompose = workflow_operator.Decompose


async def test_basic_vector_search():
    """测试基础的VectorSearch功能"""
    print("\n" + "="*60)
    print("测试1: 基础向量检索")
    print("="*60)

    # Mock LLM for testing
    class MockLLM:
        async def aask(self, prompt):
            return "Mock LLM response"

    llm = MockLLM()
    problem = "What role did Julianne Moore play in the 2002 Oscar winning movie?"

    # Initialize and test VectorSearch
    try:
        vector_search = VectorSearch(llm, problem)

        # Test retrieval
        result = await vector_search(
            instruction="Find information about Julianne Moore's Oscar movies",
            context="Focus on 2002 films",
            top_k=2
        )

        print("\n检索结果:")
        print("-" * 40)
        print(result[:800] + "..." if len(result) > 800 else result)

        if "Error" not in result:
            print("\n✅ 基础向量检索测试成功")
            return True
        else:
            print(f"\n⚠️ 检索遇到错误: {result}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_query_enhancement():
    """测试查询增强功能"""
    print("\n" + "="*60)
    print("测试2: 查询增强处理")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            # Simulate query enhancement
            if "optimized search query" in prompt.lower():
                return "Julianne Moore 2002 Oscar winning movie role character"
            return "Mock response"

    llm = MockLLM()
    problem = "Compare the origins of two bands"

    try:
        vector_search = VectorSearch(llm, problem)

        # Test with both instruction and context to trigger query enhancement
        result = await vector_search(
            instruction="Find information about band origins",
            context="Days of the New and TV on the Radio",
            top_k=3
        )

        print("\n增强后的检索结果:")
        print("-" * 40)
        print(result[:600] + "..." if len(result) > 600 else result)

        if "Error" not in result:
            print("\n✅ 查询增强测试成功")
            return True
        else:
            print(f"\n⚠️ 查询增强遇到错误")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_workflow_integration():
    """测试VectorSearch与其他operator的工作流集成"""
    print("\n" + "="*60)
    print("测试3: 工作流集成 (VectorSearch -> Generate -> Revise)")
    print("="*60)

    class WorkflowLLM:
        async def aask(self, prompt):
            # Simulate different responses for different operators
            if "generate" in prompt.lower() or "response" in prompt.lower():
                return "Based on the retrieved information, Coffea (coffee) is more valued globally than Stephanandra."
            elif "revise" in prompt.lower():
                return "<think>Improving clarity and adding evidence</think><revised_context>Coffee (from Coffea plants) is significantly more valued worldwide than Stephanandra, as coffee is one of the most traded commodities globally.</revised_context>"
            return "Mock LLM response"

    llm = WorkflowLLM()
    problem = "Which fruits/crops from Stephanandra and Coffea are valued more across the world?"

    try:
        print("步骤1: 使用VectorSearch检索信息")
        vector_search = VectorSearch(llm, problem)
        retrieved_info = await vector_search(
            instruction="Find information about Stephanandra and Coffea crops and their global value",
            context="",
            top_k=2
        )
        print(f"  ✓ 检索到 {len(retrieved_info)} 字符的信息")

        print("\n步骤2: 使用Generate处理检索结果")
        generate = Generate(llm, problem)
        initial_answer = await generate(
            instruction="Based on the retrieved information, determine which crop is more valued",
            context=retrieved_info[:500]  # Use partial context for testing
        )
        print(f"  ✓ 生成初始答案: {initial_answer[:100]}...")

        print("\n步骤3: 使用Revise改进答案")
        revise = Revise(llm, problem)
        final_answer = await revise(
            instruction="Make the answer more precise and add supporting evidence",
            context=initial_answer
        )
        print(f"  ✓ 改进后答案: {final_answer[:150]}...")

        print("\n✅ 工作流集成测试成功")
        return True

    except Exception as e:
        print(f"\n❌ 工作流集成错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_structured_results():
    """测试结构化结果获取"""
    print("\n" + "="*60)
    print("测试4: 结构化结果获取")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            return "Mock response"

    llm = MockLLM()
    problem = "Test problem for structured results"

    try:
        vector_search = VectorSearch(llm, problem)

        # Test structured results method
        structured = await vector_search.get_structured_results(
            instruction="Test query",
            context="",
            top_k=1
        )

        print("\n结构化结果包含以下字段:")
        print("-" * 40)
        for key in structured.keys():
            print(f"  • {key}")
            if key == "metadata":
                for meta_key in structured[key].keys():
                    print(f"    - {meta_key}")

        # Validate structure
        required_fields = ["processed_query", "retrieved_documents", "relevance_scores", "formatted_context", "metadata"]
        missing_fields = [f for f in required_fields if f not in structured]

        if not missing_fields:
            print("\n✅ 结构化结果测试成功")
            return True
        else:
            print(f"\n⚠️ 缺少字段: {missing_fields}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_error_handling():
    """测试错误处理机制"""
    print("\n" + "="*60)
    print("测试5: 错误处理")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            return "Mock response"

    llm = MockLLM()

    # Test with invalid database configuration
    invalid_config = {
        'db_path': '/invalid/nonexistent/path/to/database'
    }

    try:
        vector_search = VectorSearch(llm, "test problem", db_config=invalid_config)
        result = await vector_search(
            instruction="Test query",
            context="",
            top_k=1
        )

        if "Error" in result:
            print(f"✅ 错误处理正常: {result}")
            return True
        else:
            print("⚠️ 应该返回错误信息但返回了成功结果")
            return False

    except Exception as e:
        print(f"✅ 捕获异常: {e}")
        return True


async def test_ensemble_with_vector_search():
    """测试VectorSearch与Ensemble的组合使用"""
    print("\n" + "="*60)
    print("测试6: VectorSearch + Ensemble组合")
    print("="*60)

    class EnsembleLLM:
        async def aask(self, prompt):
            if "ensemble" in prompt.lower() or "select" in prompt.lower():
                return "<think>Analyzing multiple search results</think><result>The most relevant information is from the first search about Julianne Moore.</result>"
            return "Mock response"

    llm = EnsembleLLM()
    problem = "Find the best information about a specific topic"

    try:
        vector_search = VectorSearch(llm, problem)

        # Perform multiple searches
        print("执行多个检索查询...")
        search_results = []

        queries = [
            ("Julianne Moore movies", "Oscar 2002"),
            ("actress awards", "dramatic roles"),
            ("film history", "2000s cinema")
        ]

        for instruction, context in queries[:2]:  # Limit to 2 for testing
            result = await vector_search(instruction, context, top_k=1)
            search_results.append(result[:200] if result else "No results")
            print(f"  ✓ 查询 '{instruction}' 完成")

        # Use Ensemble to select best result
        print("\n使用Ensemble选择最佳结果...")
        ensemble = Ensemble(llm, problem)
        best_result = await ensemble(
            instruction="Select the most relevant and informative search result",
            contexts_list=search_results
        )

        print(f"  ✓ Ensemble选择结果: {best_result[:150]}...")
        print("\n✅ VectorSearch + Ensemble测试成功")
        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "🚀 " + "="*58)
    print("   VectorSearch Operator 综合测试套件")
    print("="*60)

    # Check if database exists
    base_dir = Path(__file__).parent.parent.parent.parent
    db_path = base_dir / "Processed_dataset" / "hotpotqa" / "vector" / "db" / "chroma_db"

    if not db_path.exists():
        print(f"\n⚠️ 警告: 向量数据库未找到")
        print(f"   预期路径: {db_path}")
        print("   请先运行HotpotQA RAG系统设置脚本")
        print("   位置: Processed_dataset/hotpotqa/vector/scripts/")
        print("\n将运行有限的测试...")
    else:
        print(f"✅ 向量数据库已找到: {db_path}")

    # Run all tests
    test_results = {}

    tests = [
        ("基础向量检索", test_basic_vector_search),
        ("查询增强", test_query_enhancement),
        ("工作流集成", test_workflow_integration),
        ("结构化结果", test_structured_results),
        ("错误处理", test_error_handling),
        ("Ensemble组合", test_ensemble_with_vector_search)
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results[test_name] = "✅ 成功" if result else "❌ 失败"
        except Exception as e:
            test_results[test_name] = f"❌ 异常: {str(e)[:50]}"

    # Print summary
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    for test_name, result in test_results.items():
        print(f"  {test_name}: {result}")

    success_count = sum(1 for r in test_results.values() if "✅" in r)
    total_count = len(test_results)

    print("\n" + "="*60)
    if success_count == total_count:
        print(f"🎉 所有测试通过! ({success_count}/{total_count})")
    else:
        print(f"⚠️ 部分测试失败 ({success_count}/{total_count} 通过)")
    print("="*60)


if __name__ == "__main__":
    # Set environment for testing
    os.environ['SCOREFLOW_SILENT'] = 'false'

    # Run all tests
    asyncio.run(main())