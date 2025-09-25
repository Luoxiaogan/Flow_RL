#!/usr/bin/env python3
"""
02_build_vector_db.py
Build ChromaDB vector database from extracted documents
"""

import json
import os
from typing import Dict, List
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm
import hashlib
from sentence_transformers import SentenceTransformer

class VectorDBBuilder:
    def __init__(self, db_path: str, model_path: str = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector database builder

        Args:
            db_path: Path to store ChromaDB
            model_path: Local path to save/load embedding model
            embedding_model: Name of sentence-transformer model
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.model_path = model_path

        # Initialize ChromaDB client
        print(f"初始化ChromaDB，存储路径: {db_path}")
        self.client = chromadb.PersistentClient(path=db_path)

        # Initialize embedding function with local model path
        if model_path:
            print(f"使用本地Embedding模型路径: {model_path}")
            # Check if model exists locally, if not download and save
            if not os.path.exists(model_path):
                print(f"下载并保存模型到本地: {model_path}")
                model = SentenceTransformer(embedding_model)
                model.save(model_path)
                print(f"模型已保存到: {model_path}")

            # Use local model path for ChromaDB
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_path
            )
        else:
            print(f"使用Embedding模型: {embedding_model}")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )

        # Create collections for different granularities
        self._create_collections()

    def _create_collections(self):
        """Create collections for document and sentence level indexing"""
        # Delete existing collections if they exist
        try:
            self.client.delete_collection("documents")
        except:
            pass
        try:
            self.client.delete_collection("sentences")
        except:
            pass

        # Create document-level collection
        self.doc_collection = self.client.create_collection(
            name="documents",
            embedding_function=self.embedding_function,
            metadata={"description": "Document-level embeddings"}
        )
        print("创建文档级Collection: documents")

        # Create sentence-level collection
        self.sent_collection = self.client.create_collection(
            name="sentences",
            embedding_function=self.embedding_function,
            metadata={"description": "Sentence-level embeddings"}
        )
        print("创建句子级Collection: sentences")

    def load_documents(self, documents_file: str) -> List[Dict]:
        """Load documents from JSONL file"""
        documents = []
        print(f"加载文档: {documents_file}")
        with open(documents_file, 'r', encoding='utf-8') as f:
            for line in f:
                documents.append(json.loads(line.strip()))
        print(f"加载了 {len(documents)} 个文档")
        return documents

    def index_documents(self, documents: List[Dict], batch_size: int = 50):
        """Index documents at document level"""
        print("\n索引文档级数据...")

        doc_texts = []
        doc_metadatas = []
        doc_ids = []

        for doc in tqdm(documents, desc="准备文档数据"):
            # Use full text for document-level embedding
            doc_texts.append(doc['full_text'])

            # Prepare metadata
            metadata = {
                'title': doc['title'],
                'doc_id': doc['doc_id'],
                'num_sentences': doc['num_sentences'],
                'text_length': doc['text_length']
            }
            doc_metadatas.append(metadata)

            # Use doc_id as unique ID
            doc_ids.append(doc['doc_id'])

        # Add to collection in batches (smaller batch size for stability)
        for i in tqdm(range(0, len(doc_texts), batch_size), desc="索引文档"):
            batch_end = min(i + batch_size, len(doc_texts))
            self.doc_collection.add(
                documents=doc_texts[i:batch_end],
                metadatas=doc_metadatas[i:batch_end],
                ids=doc_ids[i:batch_end]
            )

        print(f"成功索引 {len(documents)} 个文档")

    def index_sentences(self, documents: List[Dict], batch_size: int = 50):
        """Index documents at sentence level"""
        print("\n索引句子级数据...")

        sent_texts = []
        sent_metadatas = []
        sent_ids = []

        total_sentences = 0

        for doc in tqdm(documents, desc="准备句子数据"):
            for sent_idx, sentence in enumerate(doc['sentences']):
                # Skip empty sentences
                if not sentence.strip():
                    continue

                sent_texts.append(sentence)

                # Prepare metadata
                metadata = {
                    'title': doc['title'],
                    'doc_id': doc['doc_id'],
                    'sentence_id': sent_idx,
                    'sentence_length': len(sentence)
                }
                sent_metadatas.append(metadata)

                # Create unique ID for sentence
                sent_id = f"{doc['doc_id']}_sent_{sent_idx:03d}"
                sent_ids.append(sent_id)

                total_sentences += 1

        # Add to collection in batches (smaller batch size for stability)
        for i in tqdm(range(0, len(sent_texts), batch_size), desc="索引句子"):
            batch_end = min(i + batch_size, len(sent_texts))
            self.sent_collection.add(
                documents=sent_texts[i:batch_end],
                metadatas=sent_metadatas[i:batch_end],
                ids=sent_ids[i:batch_end]
            )

        print(f"成功索引 {total_sentences} 个句子")

    def create_indices(self):
        """Create indices for better retrieval performance"""
        print("\n创建索引...")
        # ChromaDB now automatically persists data
        print("索引创建完成")

    def get_statistics(self) -> Dict:
        """Get statistics about the vector database"""
        stats = {
            'document_collection': {
                'name': 'documents',
                'count': self.doc_collection.count(),
            },
            'sentence_collection': {
                'name': 'sentences',
                'count': self.sent_collection.count(),
            },
            'embedding_model': self.embedding_model,
            'model_path': self.model_path,
            'db_path': self.db_path
        }
        return stats

def test_retrieval(db_builder: VectorDBBuilder):
    """Test retrieval functionality"""
    print("\n" + "="*50)
    print("测试检索功能")
    print("="*50)

    test_queries = [
        "What role did Julianne Moore play in the Oscar winning movie?",
        "Who is an American actress born in 1960?",
        "What movie won Oscar in 2002?"
    ]

    for query in test_queries:
        print(f"\n查询: {query}")

        # Test document-level retrieval
        print("  文档级检索 (Top 3):")
        doc_results = db_builder.doc_collection.query(
            query_texts=[query],
            n_results=3
        )

        for i, (doc_id, metadata, distance) in enumerate(zip(
            doc_results['ids'][0],
            doc_results['metadatas'][0],
            doc_results['distances'][0]
        )):
            print(f"    {i+1}. {metadata['title'][:50]} (距离: {distance:.4f})")

        # Test sentence-level retrieval
        print("  句子级检索 (Top 3):")
        sent_results = db_builder.sent_collection.query(
            query_texts=[query],
            n_results=3
        )

        for i, (sent_id, metadata, distance, text) in enumerate(zip(
            sent_results['ids'][0],
            sent_results['metadatas'][0],
            sent_results['distances'][0],
            sent_results['documents'][0]
        )):
            print(f"    {i+1}. [{metadata['title']}] {text[:80]}... (距离: {distance:.4f})")

def main():
    # Paths
    base_dir = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/Processed_dataset/hotpotqa/vector'
    documents_file = os.path.join(base_dir, 'data/documents.jsonl')
    db_path = os.path.join(base_dir, 'db/chroma_db')
    model_path = os.path.join(base_dir, 'models/all-MiniLM-L6-v2')  # Local model path

    # Create directories
    os.makedirs(db_path, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Initialize builder with local model path
    builder = VectorDBBuilder(
        db_path=db_path,
        model_path=model_path,  # Use local model
        embedding_model="all-MiniLM-L6-v2"
    )

    # Load documents
    documents = builder.load_documents(documents_file)

    # Index at both levels with smaller batch size
    builder.index_documents(documents, batch_size=50)
    builder.index_sentences(documents, batch_size=50)

    # Create indices
    builder.create_indices()

    # Get statistics
    stats = builder.get_statistics()

    print("\n" + "="*50)
    print("向量数据库统计:")
    print("="*50)
    print(f"文档Collection: {stats['document_collection']['count']} 个文档")
    print(f"句子Collection: {stats['sentence_collection']['count']} 个句子")
    print(f"Embedding模型: {stats['embedding_model']}")
    print(f"模型路径: {stats['model_path']}")
    print(f"数据库路径: {stats['db_path']}")

    # Save statistics
    stats_file = os.path.join(base_dir, 'data/vectordb_statistics.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n保存统计信息到: {stats_file}")

    # Test retrieval
    test_retrieval(builder)

    print("\n向量数据库构建完成! ✓")

if __name__ == "__main__":
    main()