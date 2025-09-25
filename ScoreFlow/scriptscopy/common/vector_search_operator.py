#!/usr/bin/env python3
"""
VectorSearch Operator for HotpotQA RAG System
Integrates ChromaDB vector database with ScoreFlow workflow system
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import chromadb
from chromadb.utils import embedding_functions

# Import base operator and Pydantic model
from operator import Operator
from operator_an import VectorSearchOp


class VectorSearch(Operator):
    """
    核心算子：向量检索 (Vector Search)
    使用RAG系统从HotpotQA向量数据库中检索相关文档。
    为workflow提供基于向量相似度的信息检索能力。
    """

    def __init__(self, llm, problem_text: str = "", db_config: Optional[Dict] = None):
        """
        Initialize VectorSearch operator with RAG system connection.

        Args:
            llm: Language model instance
            problem_text: Original problem text
            db_config: Optional database configuration override
        """
        super().__init__(llm, problem_text)

        # Setup paths relative to ScoreFlow directory
        self.base_dir = Path(__file__).parent.parent.parent.parent  # Go up to Flow_RL_RIGHT
        self.vector_dir = self.base_dir / "Processed_dataset" / "hotpotqa" / "vector"

        # Default configuration
        self.config = {
            'db_path': str(self.vector_dir / "db" / "chroma_db"),
            'model_path': str(self.vector_dir / "models" / "all-MiniLM-L6-v2"),
            'doc_top_k': 3,
            'sent_top_k': 5,
            'hybrid_mode': True
        }

        # Override with custom config if provided
        if db_config:
            self.config.update(db_config)

        # Initialize ChromaDB client and collections
        self._init_chromadb()

    def _init_chromadb(self):
        """Initialize ChromaDB connection and collections"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.config['db_path'])

            # Initialize embedding function with local model
            if os.path.exists(self.config['model_path']):
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.config['model_path']
                )
            else:
                # Fallback to default model name if local model not found
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )

            # Get collections
            self.doc_collection = self.client.get_collection("documents")
            self.sent_collection = self.client.get_collection("sentences")

            # Print initialization info if not in silent mode
            if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
                print(f"✅ 成功连接到向量数据库")
                print(f"   文档数: {self.doc_collection.count()}")
                print(f"   句子数: {self.sent_collection.count()}")

        except Exception as e:
            if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
                print(f"⚠️ 向量数据库初始化失败: {e}")
                print(f"   尝试路径: {self.config['db_path']}")
            # Initialize as None if connection fails
            self.doc_collection = None
            self.sent_collection = None

    async def __call__(self, instruction: str = "", context: str = "", top_k: int = None) -> str:
        """
        Execute vector search based on instruction and context.

        Args:
            instruction: Search instruction or query enhancement guidance
            context: Previous context to consider for search
            top_k: Optional override for number of documents to retrieve

        Returns:
            Formatted string containing retrieved documents and context
        """
        # Check SILENT mode
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: VectorSearch")

        # Check if database is initialized
        if not self.doc_collection or not self.sent_collection:
            return "Error: Vector database not initialized. Please check database path and configuration."

        # Use provided top_k or default from config
        doc_k = top_k or self.config['doc_top_k']
        sent_k = self.config['sent_top_k']

        # Step 1: Process and enhance query
        processed_query = await self._process_query(instruction, context)

        # Step 2: Perform hybrid retrieval
        retrieved_data = self._hybrid_retrieval(processed_query, doc_k, sent_k)

        # Step 3: Format context for output
        formatted_context = self._format_context(retrieved_data)

        # Step 4: Create structured response
        response = {
            "processed_query": processed_query,
            "retrieved_documents": retrieved_data['documents'],
            "relevance_scores": retrieved_data['scores'],
            "formatted_context": formatted_context
        }

        # For operator output, return just the formatted context as string
        # This makes it easy for downstream operators to use
        return formatted_context

    async def _process_query(self, instruction: str, context: str) -> str:
        """
        Process and enhance the query using LLM.

        Args:
            instruction: Original instruction
            context: Previous context

        Returns:
            Enhanced query string
        """
        # If both instruction and context are provided, combine them
        if instruction and context:
            prompt = f"""Based on the following instruction and context, generate an optimized search query for retrieving relevant information.

**Instruction:**
{instruction}

**Context:**
{context}

**Original Problem:**
{self.problem_text}

Generate a concise, focused search query that will help retrieve the most relevant documents.
Your query should be a single sentence or phrase, optimized for semantic search.

**Optimized Query:**"""

            response = await self._fill_node(
                VectorSearchOp,
                prompt,
                mode="single_fill"
            )
            # Extract just the query part
            return instruction  # Fallback to instruction if LLM fails

        elif instruction:
            return instruction
        elif context:
            # Extract key information from context if no instruction
            return context[:200]  # Use first 200 chars of context
        else:
            # Use problem text as fallback
            return self.problem_text[:200] if self.problem_text else "general information"

    def _hybrid_retrieval(self, query: str, doc_k: int, sent_k: int) -> Dict:
        """
        Perform hybrid document and sentence level retrieval.

        Args:
            query: Processed query string
            doc_k: Number of documents to retrieve
            sent_k: Number of sentences to retrieve

        Returns:
            Dictionary with retrieved documents and scores
        """
        retrieved_data = {
            'documents': [],
            'scores': []
        }

        try:
            # Document-level retrieval
            if self.config['hybrid_mode']:
                doc_results = self.doc_collection.query(
                    query_texts=[query],
                    n_results=doc_k
                )

                # Process document results
                for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
                    doc_results['ids'][0],
                    doc_results['documents'][0],
                    doc_results['metadatas'][0],
                    doc_results['distances'][0]
                )):
                    retrieved_data['documents'].append({
                        'doc_id': doc_id,
                        'title': metadata.get('title', 'Unknown'),
                        'text': doc_text[:500],  # Limit text length
                        'type': 'document',
                        'rank': i + 1
                    })
                    retrieved_data['scores'].append(float(distance))

            # Sentence-level retrieval
            sent_results = self.sent_collection.query(
                query_texts=[query],
                n_results=sent_k
            )

            # Process sentence results
            for i, (sent_id, sent_text, metadata, distance) in enumerate(zip(
                sent_results['ids'][0],
                sent_results['documents'][0],
                sent_results['metadatas'][0],
                sent_results['distances'][0]
            )):
                # Add only if not too similar to existing documents
                if i < 3:  # Limit to top 3 sentences
                    retrieved_data['documents'].append({
                        'doc_id': sent_id,
                        'title': metadata.get('title', 'Unknown'),
                        'text': sent_text,
                        'type': 'sentence',
                        'sentence_id': metadata.get('sentence_id', -1),
                        'rank': i + 1
                    })
                    retrieved_data['scores'].append(float(distance))

        except Exception as e:
            if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
                print(f"⚠️ 检索过程出错: {e}")

        return retrieved_data

    def _format_context(self, retrieved_data: Dict) -> str:
        """
        Format retrieved documents into a readable context string.

        Args:
            retrieved_data: Dictionary with documents and scores

        Returns:
            Formatted context string
        """
        if not retrieved_data['documents']:
            return "No relevant documents found."

        formatted_parts = []
        formatted_parts.append("**Retrieved Information:**\n")

        # Group by document vs sentence
        doc_items = [d for d in retrieved_data['documents'] if d.get('type') == 'document']
        sent_items = [d for d in retrieved_data['documents'] if d.get('type') == 'sentence']

        # Format document-level results
        if doc_items:
            formatted_parts.append("📄 **Relevant Documents:**")
            for doc in doc_items:
                formatted_parts.append(f"\n[{doc['rank']}. {doc['title']}]")
                formatted_parts.append(f"{doc['text']}")
                formatted_parts.append("")

        # Format sentence-level results
        if sent_items:
            formatted_parts.append("\n🔍 **Relevant Passages:**")
            for sent in sent_items:
                formatted_parts.append(f"\n[From: {sent['title']}]")
                formatted_parts.append(f"{sent['text']}")
                formatted_parts.append("")

        # Add metadata summary
        formatted_parts.append(f"\n---\n*Retrieved {len(retrieved_data['documents'])} relevant items*")

        return "\n".join(formatted_parts)

    async def get_structured_results(self, instruction: str = "", context: str = "", top_k: int = None) -> Dict:
        """
        Get structured results including all metadata.
        Useful for detailed analysis or debugging.

        Args:
            instruction: Search instruction
            context: Previous context
            top_k: Number of results

        Returns:
            Complete structured dictionary with all retrieval data
        """
        # Similar to __call__ but returns full dictionary
        doc_k = top_k or self.config['doc_top_k']
        sent_k = self.config['sent_top_k']

        processed_query = await self._process_query(instruction, context)
        retrieved_data = self._hybrid_retrieval(processed_query, doc_k, sent_k)
        formatted_context = self._format_context(retrieved_data)

        return {
            "processed_query": processed_query,
            "retrieved_documents": retrieved_data['documents'],
            "relevance_scores": retrieved_data['scores'],
            "formatted_context": formatted_context,
            "metadata": {
                "db_path": self.config['db_path'],
                "doc_count": self.doc_collection.count() if self.doc_collection else 0,
                "sent_count": self.sent_collection.count() if self.sent_collection else 0,
                "retrieval_config": {
                    "doc_k": doc_k,
                    "sent_k": sent_k,
                    "hybrid_mode": self.config['hybrid_mode']
                }
            }
        }


# Test function for standalone execution
async def test_vector_search():
    """Test the VectorSearch operator"""
    from metagpt.llm import LLM

    # Initialize LLM (you may need to configure this)
    llm = LLM()

    # Test problem
    problem = "What role did Julianne Moore play in the 2002 Oscar winning movie?"

    # Initialize operator
    vector_search = VectorSearch(llm, problem)

    # Test search
    result = await vector_search(
        instruction="Find information about Julianne Moore and Oscar-winning movies from 2002",
        context="We need to identify the specific movie and her role in it.",
        top_k=3
    )

    print("\n" + "="*60)
    print("Vector Search Test Results:")
    print("="*60)
    print(result)

    # Also test structured results
    structured = await vector_search.get_structured_results(
        instruction="Find information about Julianne Moore and Oscar-winning movies from 2002",
        context="",
        top_k=2
    )

    print("\n" + "="*60)
    print("Structured Results:")
    print("="*60)
    print(f"Query: {structured['processed_query']}")
    print(f"Documents retrieved: {len(structured['retrieved_documents'])}")
    print(f"Database stats: {structured['metadata']}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_vector_search())