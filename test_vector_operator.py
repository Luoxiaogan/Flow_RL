#!/usr/bin/env python3
"""
Standalone test script for VectorSearch operator
Run from Flow_RL directory to avoid module conflicts
"""

import os
import sys
import asyncio
from pathlib import Path

# Add ScoreFlow to path
sys.path.insert(0, str(Path(__file__).parent / "ScoreFlow" / "scripts"))

# Now import from common module
from common.operator import VectorSearch
from common.operator_an import VectorSearchOp


async def test_vector_search():
    """Test VectorSearch operator functionality"""
    print("\n" + "="*60)
    print("VectorSearch Operator Test")
    print("="*60)

    # Mock LLM for testing
    class MockLLM:
        async def aask(self, prompt):
            return "Mock LLM response"

    llm = MockLLM()

    # Test problem
    problem = "What role did Julianne Moore play in the 2002 Oscar winning movie?"

    try:
        # Initialize operator
        print("\n1. Initializing VectorSearch operator...")
        vector_search = VectorSearch(llm, problem)

        # Check configuration
        print("   ✅ Operator initialized")
        print(f"   - Config loaded: {vector_search.config is not None}")
        print(f"   - DB Path: {vector_search.config.get('db_path', 'Not set')}")

        # Check database connection
        if vector_search.doc_collection and vector_search.sent_collection:
            print("   ✅ Database connected successfully")
            print(f"   - Documents: {vector_search.doc_collection.count()}")
            print(f"   - Sentences: {vector_search.sent_collection.count()}")
        else:
            print("   ⚠️ Database not connected")

        # Test retrieval
        print("\n2. Testing retrieval...")
        result = await vector_search(
            instruction="Find information about Julianne Moore and Oscar-winning movies from 2002",
            context="",
            top_k=2
        )

        print("\n3. Results:")
        print("-" * 40)
        if "Error" in result:
            print(f"   ⚠️ {result}")
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print("\n   ✅ Retrieval successful")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)


def test_imports():
    """Test that imports work correctly"""
    print("\n" + "="*60)
    print("Import Test")
    print("="*60)

    try:
        print("1. Testing VectorSearchOp import...")
        fields = list(VectorSearchOp.__fields__.keys())
        print(f"   ✅ VectorSearchOp imported successfully")
        print(f"   - Fields: {fields}")

        # Test creating instance
        print("\n2. Testing VectorSearchOp instance...")
        test_data = {
            "processed_query": "test query",
            "retrieved_documents": [{"title": "Test", "text": "Content"}],
            "relevance_scores": [0.95],
            "formatted_context": "Test context"
        }
        instance = VectorSearchOp(**test_data)
        print(f"   ✅ Instance created successfully")
        print(f"   - Query: {instance.processed_query}")
        print(f"   - Docs: {len(instance.retrieved_documents)}")

    except Exception as e:
        print(f"   ❌ Import test failed: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VectorSearch Operator Test Suite")
    print("Running from:", os.getcwd())
    print("="*60)

    # Test imports first
    test_imports()

    # Then test operator
    asyncio.run(test_vector_search())

    print("\nTest suite complete!")
    print("="*60)