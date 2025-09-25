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

# Import operators - use explicit import to avoid conflict
import operator as workflow_operator
from common.operator import VectorSearch, Generate


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
        print(f"   Config loaded from db.config:")
        print(f"   - DB Path: {vector_search.config.get('db_path', 'Not set')}")
        print(f"   - Model Path: {vector_search.config.get('model_path', 'Not set')}")

        # Test retrieval
        result = await vector_search(
            instruction="Find information about Julianne Moore and 2002 Oscar movies",
            context="",
            top_k=2
        )

        print("\nRetrieved Information:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)

        if "Error" not in result:
            print("\n✅ VectorSearch retrieval successful")
        else:
            print(f"\n⚠️ VectorSearch encountered an error: {result}")

    except Exception as e:
        print(f"❌ Error initializing VectorSearch: {e}")
        import traceback
        traceback.print_exc()


async def test_import_and_structure():
    """Test that all imports work correctly"""
    print("\n" + "="*60)
    print("Test 0: Import and Structure Test")
    print("="*60)

    try:
        # Test importing VectorSearchOp from operator_an
        from common.operator_an import VectorSearchOp
        print("✅ VectorSearchOp imported successfully from operator_an.py")
        print(f"   Fields: {list(VectorSearchOp.__fields__.keys())}")

        # Test creating an instance
        test_instance = VectorSearchOp(
            processed_query="test query",
            retrieved_documents=[{"title": "Test", "text": "Test content"}],
            relevance_scores=[0.95],
            formatted_context="Test context"
        )
        print("✅ VectorSearchOp instance created successfully")

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("VectorSearch Operator Test Suite")
    print("="*60)

    # Check if database exists
    from pathlib import Path

    # Read db.config to get path
    config_file = Path(__file__).parent / "db.config"
    db_path = None

    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if line.strip().startswith('DB_PATH='):
                    db_path = line.split('=', 1)[1].strip()
                    break

    if db_path:
        db_path = Path(db_path)
        if db_path.exists():
            print(f"✅ Database found at {db_path}")
        else:
            print(f"⚠️ Warning: Database not found at {db_path}")
            print("Please ensure the HotpotQA RAG system is set up first.")
    else:
        print("⚠️ db.config not found or DB_PATH not set")

    # Run tests
    await test_import_and_structure()
    await test_vector_search_basic()

    print("\n" + "="*60)
    print("Test Suite Complete")
    print("="*60)


if __name__ == "__main__":
    # Set silent mode for cleaner test output
    os.environ['SCOREFLOW_SILENT'] = 'false'

    # Run tests
    asyncio.run(main())