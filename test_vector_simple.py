#!/usr/bin/env python3
"""
Simple test for VectorSearch operator without MetaGPT dependencies
"""

import sys
from pathlib import Path

# Test imports only
sys.path.insert(0, str(Path(__file__).parent / "ScoreFlow" / "scripts"))

print("\n" + "="*60)
print("VectorSearch Import Test")
print("="*60)

try:
    # Test VectorSearchOp import
    from common.operator_an import VectorSearchOp
    print("✅ VectorSearchOp imported successfully")

    # Check fields
    fields = list(VectorSearchOp.__fields__.keys())
    print(f"   Fields: {fields}")

    # Test instance creation
    test_instance = VectorSearchOp(
        processed_query="test query",
        retrieved_documents=[{"title": "Doc1", "text": "Content"}],
        relevance_scores=[0.95],
        formatted_context="Formatted content"
    )
    print("✅ VectorSearchOp instance created successfully")

except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Testing db.config loading")
print("="*60)

config_file = Path(__file__).parent / "ScoreFlow" / "scripts" / "common" / "db.config"
if config_file.exists():
    print(f"✅ db.config found at: {config_file}")

    # Read and display config
    with open(config_file, 'r') as f:
        print("\nConfiguration:")
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                print(f"   {line}")
else:
    print(f"❌ db.config not found at: {config_file}")

print("\n" + "="*60)
print("Testing ChromaDB connection")
print("="*60)

try:
    import chromadb
    from chromadb.utils import embedding_functions

    # Read db path from config
    db_path = None
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if line.strip().startswith('DB_PATH='):
                    db_path = line.split('=', 1)[1].strip()
                    break

    if db_path:
        print(f"Attempting to connect to: {db_path}")

        # Try to connect
        client = chromadb.PersistentClient(path=db_path)
        print("✅ ChromaDB client initialized")

        # Try to get collections
        try:
            doc_collection = client.get_collection("documents")
            sent_collection = client.get_collection("sentences")

            print(f"✅ Collections loaded successfully")
            print(f"   - Documents: {doc_collection.count()}")
            print(f"   - Sentences: {sent_collection.count()}")

        except Exception as e:
            print(f"⚠️ Collections not found: {e}")
            print("   Please ensure the RAG database is built first")
    else:
        print("⚠️ DB_PATH not found in config")

except ImportError:
    print("⚠️ ChromaDB not installed. Run: pip install chromadb")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)