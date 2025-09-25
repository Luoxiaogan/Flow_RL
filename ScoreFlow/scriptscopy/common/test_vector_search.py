#!/usr/bin/env python3
"""
Test script for VectorSearch operator
Tests the integration of RAG system with ScoreFlow workflow
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import operators - use explicit module name to avoid conflict with built-in operator
import operator as workflow_operator
from operator import VectorSearch, Generate, Ensemble


async def test_vector_search_basic():
    """Test basic VectorSearch functionality"""
    print("\n" + "="*60)
    print("Test 1: Basic VectorSearch")
    print("="*60)

    # Initialize LLM (using a simple mock for testing)
    class MockLLM:
        async def aask(self, prompt):
            return "Mock response"

    llm = MockLLM()

    # Test problem
    problem = "What role did Julianne Moore play in the 2002 Oscar winning movie?"

    # Initialize VectorSearch operator
    try:
        vector_search = VectorSearch(llm, problem)
        print("✅ VectorSearch operator initialized successfully")

        # Test retrieval
        result = await vector_search(
            instruction="Find information about Julianne Moore and 2002 Oscar movies",
            context="",
            top_k=2
        )

        print("\nRetrieved Information:")
        print("-" * 40)
        print(result)

        if "Error" not in result:
            print("\n✅ VectorSearch retrieval successful")
        else:
            print(f"\n⚠️ VectorSearch encountered an error: {result}")

    except Exception as e:
        print(f"❌ Error initializing VectorSearch: {e}")
        import traceback
        traceback.print_exc()


async def test_vector_search_with_context():
    """Test VectorSearch with context"""
    print("\n" + "="*60)
    print("Test 2: VectorSearch with Context")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            return "Mock response"

    llm = MockLLM()
    problem = "Are both Days of the New and TV on the Radio from New York?"

    try:
        vector_search = VectorSearch(llm, problem)

        # Test with context
        result = await vector_search(
            instruction="Find information about the bands' origins",
            context="We need to compare where these two bands are from",
            top_k=3
        )

        print("\nRetrieved Information:")
        print("-" * 40)
        print(result)

        if "Error" not in result:
            print("\n✅ VectorSearch with context successful")
        else:
            print(f"\n⚠️ VectorSearch encountered an error: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def test_workflow_integration():
    """Test VectorSearch integration with other operators"""
    print("\n" + "="*60)
    print("Test 3: Workflow Integration")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            # Return a simple XML response for testing
            if "Generate" in prompt:
                return "Based on the retrieved information, the answer is..."
            return "<think>Processing multiple options</think><result>Best option selected</result>"

        async def __call__(self, *args, **kwargs):
            return await self.aask(args[0] if args else "")

    llm = MockLLM()
    problem = "Which fruits/crops from Stephanandra and Coffea are valued more across the world?"

    try:
        # Step 1: Use VectorSearch to retrieve information
        vector_search = VectorSearch(llm, problem)
        retrieved_info = await vector_search(
            instruction="Find information about Stephanandra and Coffea crops",
            context="",
            top_k=2
        )

        print("Step 1 - Vector Search Result:")
        print("-" * 40)
        print(retrieved_info[:500] + "..." if len(retrieved_info) > 500 else retrieved_info)

        # Step 2: Use Generate to process the retrieved information
        generate = Generate(llm, problem)
        analysis = await generate(
            instruction="Analyze which crop is more valuable",
            context=retrieved_info
        )

        print("\nStep 2 - Generate Analysis:")
        print("-" * 40)
        print(analysis)

        print("\n✅ Workflow integration test successful")

    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()


async def test_error_handling():
    """Test error handling when database is not available"""
    print("\n" + "="*60)
    print("Test 4: Error Handling")
    print("="*60)

    class MockLLM:
        async def aask(self, prompt):
            return "Mock response"

    llm = MockLLM()

    # Test with invalid database path
    invalid_config = {
        'db_path': '/invalid/path/to/database'
    }

    try:
        vector_search = VectorSearch(llm, "test problem", db_config=invalid_config)
        result = await vector_search(
            instruction="Test query",
            context="",
            top_k=1
        )

        if "Error" in result:
            print(f"✅ Error handling works correctly: {result}")
        else:
            print("⚠️ Expected error message but got successful result")

    except Exception as e:
        print(f"✅ Exception handled: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("VectorSearch Operator Test Suite")
    print("="*60)

    # Check if database exists
    base_dir = Path(__file__).parent.parent.parent.parent
    db_path = base_dir / "Processed_dataset" / "hotpotqa" / "vector" / "db" / "chroma_db"

    if not db_path.exists():
        print(f"⚠️ Warning: Database not found at {db_path}")
        print("Please ensure the HotpotQA RAG system is set up first.")
        print("Run the scripts in Processed_dataset/hotpotqa/vector/scripts/")
    else:
        print(f"✅ Database found at {db_path}")

    # Run tests
    await test_vector_search_basic()
    await test_vector_search_with_context()
    await test_workflow_integration()
    await test_error_handling()

    print("\n" + "="*60)
    print("Test Suite Complete")
    print("="*60)


if __name__ == "__main__":
    # Set silent mode for cleaner test output
    os.environ['SCOREFLOW_SILENT'] = 'false'

    # Run tests
    asyncio.run(main())