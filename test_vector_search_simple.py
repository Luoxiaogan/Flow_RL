#!/usr/bin/env python3
"""
Simple test for VectorSearch operator
Avoids module naming conflicts
"""

import sys
import os
import asyncio

# Add ScoreFlow path and import directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "workflow_operators",
    "/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/ScoreFlow/scripts/common/operator.py"
)
workflow_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow_ops)

VectorSearch = workflow_ops.VectorSearch
Generate = workflow_ops.Generate
Ensemble = workflow_ops.Ensemble

async def simple_test():
    """Run a simple test of VectorSearch"""
    print("\n" + "="*60)
    print("VectorSearch Operator 简单测试")
    print("="*60)

    # Mock LLM
    class MockLLM:
        async def aask(self, prompt):
            return "Mock LLM response"

    llm = MockLLM()

    # Test 1: Basic initialization and call
    print("\n测试1: 基础初始化")
    problem = "What role did Julianne Moore play in the 2002 Oscar winning movie?"

    try:
        vector_search = VectorSearch(llm, problem)
        print("✅ VectorSearch初始化成功")

        # Test basic search
        result = await vector_search(
            instruction="Find information about Julianne Moore and 2002 Oscar",
            context="",
            top_k=2
        )

        if isinstance(result, str):
            if "Error" in result:
                print(f"⚠️ 检索返回错误: {result[:200]}")
            else:
                print(f"✅ 检索成功，返回 {len(result)} 字符")
                print(f"   结果预览: {result[:150]}...")

    except Exception as e:
        print(f"❌ 初始化或调用失败: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Workflow integration
    print("\n测试2: 工作流集成 (VectorSearch + Generate)")
    try:
        # Use VectorSearch
        vector_search = VectorSearch(llm, problem)
        retrieved = await vector_search(
            instruction="Search for relevant information",
            context="",
            top_k=1
        )

        if retrieved and "Error" not in retrieved:
            # Use Generate with retrieved context
            generate = Generate(llm, problem)
            answer = await generate(
                instruction="Answer based on the retrieved information",
                context=retrieved[:200]  # Use first 200 chars
            )
            print(f"✅ 工作流集成成功")
            print(f"   Generate输出: {answer[:100]}...")
        else:
            print("⚠️ VectorSearch未返回有效结果")

    except Exception as e:
        print(f"❌ 工作流集成失败: {e}")

    # Test 3: Structured results
    print("\n测试3: 结构化结果")
    try:
        vector_search = VectorSearch(llm, "test problem")
        structured = await vector_search.get_structured_results(
            instruction="test query",
            context="",
            top_k=1
        )

        required_fields = ["processed_query", "retrieved_documents", "relevance_scores", "formatted_context", "metadata"]
        missing = [f for f in required_fields if f not in structured]

        if not missing:
            print("✅ 结构化结果包含所有必要字段")
            print(f"   字段: {list(structured.keys())}")
        else:
            print(f"⚠️ 缺少字段: {missing}")

    except Exception as e:
        print(f"❌ 结构化结果测试失败: {e}")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    # Set environment
    os.environ['SCOREFLOW_SILENT'] = 'false'

    # Run test
    asyncio.run(simple_test())