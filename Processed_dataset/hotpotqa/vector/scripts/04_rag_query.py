#!/usr/bin/env python3
"""
04_rag_query.py
RAG query system for HotpotQA with evaluation metrics
"""

import json
import os
from typing import Dict, List, Tuple, Optional
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm
import numpy as np
from collections import defaultdict
import argparse

class RAGQuerySystem:
    def __init__(self, db_path: str, model_path: str = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG query system

        Args:
            db_path: Path to ChromaDB
            model_path: Local path to embedding model
            embedding_model: Name of sentence-transformer model
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.model_path = model_path

        # Initialize ChromaDB client
        print(f"连接到ChromaDB: {db_path}")
        self.client = chromadb.PersistentClient(path=db_path)

        # Initialize embedding function with local model if available
        if model_path and os.path.exists(model_path):
            print(f"使用本地模型: {model_path}")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_path
            )
        else:
            print(f"使用模型: {embedding_model}")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )

        # Get collections
        self.doc_collection = self.client.get_collection("documents")
        self.sent_collection = self.client.get_collection("sentences")

        print(f"文档Collection: {self.doc_collection.count()} 个文档")
        print(f"句子Collection: {self.sent_collection.count()} 个句子")

    def query_documents(self, query: str, n_results: int = 10) -> Dict:
        """
        Query document-level collection

        Args:
            query: Query text
            n_results: Number of results to return

        Returns:
            Query results with documents, metadata, and distances
        """
        results = self.doc_collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return {
            'ids': results['ids'][0],
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0]
        }

    def query_sentences(self, query: str, n_results: int = 20) -> Dict:
        """
        Query sentence-level collection

        Args:
            query: Query text
            n_results: Number of results to return

        Returns:
            Query results with sentences, metadata, and distances
        """
        results = self.sent_collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return {
            'ids': results['ids'][0],
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0]
        }

    def hybrid_retrieval(self, query: str, doc_k: int = 5, sent_k: int = 10) -> Dict:
        """
        Perform hybrid retrieval using both document and sentence level

        Args:
            query: Query text
            doc_k: Number of documents to retrieve
            sent_k: Number of sentences to retrieve per document

        Returns:
            Combined retrieval results
        """
        # Get top documents
        doc_results = self.query_documents(query, n_results=doc_k)

        # Get top sentences
        sent_results = self.query_sentences(query, n_results=sent_k * 2)

        # Combine and deduplicate
        retrieved_docs = {}

        # Add document-level results
        for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
            doc_results['ids'],
            doc_results['documents'],
            doc_results['metadatas'],
            doc_results['distances']
        )):
            title = metadata['title']
            if title not in retrieved_docs:
                retrieved_docs[title] = {
                    'doc_id': doc_id,
                    'title': title,
                    'full_text': doc_text,
                    'doc_distance': distance,
                    'sentences': [],
                    'retrieval_method': 'document'
                }

        # Add sentence-level results
        for i, (sent_id, sent_text, metadata, distance) in enumerate(zip(
            sent_results['ids'],
            sent_results['documents'],
            sent_results['metadatas'],
            sent_results['distances']
        )):
            title = metadata['title']

            # If document not already retrieved, add it
            if title not in retrieved_docs:
                retrieved_docs[title] = {
                    'doc_id': metadata['doc_id'],
                    'title': title,
                    'full_text': None,  # Will be filled from document collection
                    'doc_distance': None,
                    'sentences': [],
                    'retrieval_method': 'sentence'
                }

            # Add sentence
            retrieved_docs[title]['sentences'].append({
                'sentence_id': metadata['sentence_id'],
                'text': sent_text,
                'distance': distance
            })

        # Sort sentences within each document by distance
        for doc in retrieved_docs.values():
            doc['sentences'] = sorted(doc['sentences'], key=lambda x: x['distance'])[:sent_k]

        return retrieved_docs

    def evaluate_retrieval(self, query_result: Dict, supporting_facts: Dict) -> Dict:
        """
        Evaluate retrieval quality against ground truth supporting facts

        Args:
            query_result: Retrieved documents
            supporting_facts: Ground truth supporting facts

        Returns:
            Evaluation metrics
        """
        # Extract ground truth titles
        gt_titles = set(supporting_facts.get('title', []))
        gt_sent_indices = supporting_facts.get('sent_id', [])

        # Extract retrieved titles
        retrieved_titles = set(query_result.keys())

        # Calculate title-level metrics
        title_intersection = gt_titles & retrieved_titles
        title_recall = len(title_intersection) / len(gt_titles) if gt_titles else 0
        title_precision = len(title_intersection) / len(retrieved_titles) if retrieved_titles else 0

        # Calculate sentence-level metrics (approximate)
        sentence_hits = 0
        total_gt_sentences = len(gt_sent_indices)

        for title in title_intersection:
            doc = query_result[title]
            # Check if we retrieved sentences close to ground truth indices
            retrieved_sent_ids = [s['sentence_id'] for s in doc['sentences']]
            # Find matching sentences (within ±1 of ground truth)
            for i, gt_title in enumerate(supporting_facts['title']):
                if gt_title == title:
                    gt_idx = gt_sent_indices[i]
                    for ret_idx in retrieved_sent_ids:
                        if abs(ret_idx - gt_idx) <= 1:  # Allow small margin
                            sentence_hits += 1
                            break

        sentence_recall = sentence_hits / total_gt_sentences if total_gt_sentences > 0 else 0

        # Calculate F1 scores
        title_f1 = 2 * (title_precision * title_recall) / (title_precision + title_recall) \
                   if (title_precision + title_recall) > 0 else 0

        return {
            'title_recall': title_recall,
            'title_precision': title_precision,
            'title_f1': title_f1,
            'sentence_recall': sentence_recall,
            'retrieved_titles': list(retrieved_titles),
            'ground_truth_titles': list(gt_titles),
            'matched_titles': list(title_intersection)
        }

def batch_evaluate(rag_system: RAGQuerySystem, test_data_file: str, n_samples: int = None) -> Dict:
    """
    Batch evaluate RAG system on test data

    Args:
        rag_system: RAG query system
        test_data_file: Path to test data file
        n_samples: Number of samples to evaluate (None for all)

    Returns:
        Aggregated evaluation metrics
    """
    # Load test data
    test_data = []
    with open(test_data_file, 'r', encoding='utf-8') as f:
        for line in f:
            test_data.append(json.loads(line.strip()))

    if n_samples:
        test_data = test_data[:n_samples]

    print(f"\n评估 {len(test_data)} 个样本...")

    # Evaluation metrics
    all_metrics = []
    question_types = defaultdict(list)

    for sample in tqdm(test_data, desc="处理查询"):
        question = sample['question']
        supporting_facts = sample['original_supporting_facts']
        q_type = sample.get('type', 'unknown')

        # Perform hybrid retrieval
        retrieved = rag_system.hybrid_retrieval(question)

        # Evaluate
        metrics = rag_system.evaluate_retrieval(retrieved, supporting_facts)
        metrics['question_type'] = q_type
        metrics['question'] = question

        all_metrics.append(metrics)
        question_types[q_type].append(metrics)

    # Calculate aggregate metrics
    aggregate = {
        'total_samples': len(all_metrics),
        'avg_title_recall': np.mean([m['title_recall'] for m in all_metrics]),
        'avg_title_precision': np.mean([m['title_precision'] for m in all_metrics]),
        'avg_title_f1': np.mean([m['title_f1'] for m in all_metrics]),
        'avg_sentence_recall': np.mean([m['sentence_recall'] for m in all_metrics]),
        'perfect_title_recall': sum(1 for m in all_metrics if m['title_recall'] == 1.0) / len(all_metrics),
        'by_type': {}
    }

    # Metrics by question type
    for q_type, metrics_list in question_types.items():
        aggregate['by_type'][q_type] = {
            'count': len(metrics_list),
            'avg_title_recall': np.mean([m['title_recall'] for m in metrics_list]),
            'avg_title_f1': np.mean([m['title_f1'] for m in metrics_list])
        }

    return aggregate, all_metrics

def interactive_query(rag_system: RAGQuerySystem):
    """
    Interactive query mode

    Args:
        rag_system: RAG query system
    """
    print("\n" + "="*50)
    print("交互式查询模式 (输入 'quit' 退出)")
    print("="*50)

    while True:
        query = input("\n请输入查询: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("退出交互模式")
            break

        if not query:
            continue

        # Perform retrieval
        print("\n检索中...")
        results = rag_system.hybrid_retrieval(query, doc_k=3, sent_k=5)

        # Display results
        print(f"\n检索到 {len(results)} 个文档:")
        print("-" * 50)

        for i, (title, doc) in enumerate(results.items(), 1):
            print(f"\n{i}. {title}")
            print(f"   检索方式: {doc['retrieval_method']}")
            if doc['doc_distance'] is not None:
                print(f"   文档距离: {doc['doc_distance']:.4f}")

            if doc['sentences']:
                print(f"   相关句子 (Top {min(3, len(doc['sentences']))}):")
                for j, sent in enumerate(doc['sentences'][:3], 1):
                    print(f"     {j}. {sent['text'][:100]}...")
                    print(f"        (句子{sent['sentence_id']}, 距离: {sent['distance']:.4f})")

def main():
    parser = argparse.ArgumentParser(description='RAG Query System for HotpotQA')
    parser.add_argument('--mode', choices=['interactive', 'evaluate', 'demo'],
                       default='demo', help='Operation mode')
    parser.add_argument('--n_samples', type=int, default=None,
                       help='Number of samples to evaluate (for evaluate mode)')

    args = parser.parse_args()

    # Paths
    base_dir = '/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/Processed_dataset/hotpotqa'
    db_path = os.path.join(base_dir, 'vector/db/chroma_db')
    model_path = os.path.join(base_dir, 'vector/models/all-MiniLM-L6-v2')
    test_data_file = os.path.join(base_dir, 'validation_vector.jsonl')

    # Initialize RAG system with local model
    rag_system = RAGQuerySystem(db_path, model_path=model_path)

    if args.mode == 'interactive':
        interactive_query(rag_system)

    elif args.mode == 'evaluate':
        # Batch evaluation
        aggregate, all_metrics = batch_evaluate(rag_system, test_data_file, args.n_samples)

        print("\n" + "="*50)
        print("评估结果:")
        print("="*50)
        print(f"总样本数: {aggregate['total_samples']}")
        print(f"\n整体性能:")
        print(f"  文档召回率: {aggregate['avg_title_recall']:.3f}")
        print(f"  文档精确率: {aggregate['avg_title_precision']:.3f}")
        print(f"  文档F1分数: {aggregate['avg_title_f1']:.3f}")
        print(f"  句子召回率: {aggregate['avg_sentence_recall']:.3f}")
        print(f"  完美召回比例: {aggregate['perfect_title_recall']:.3f}")

        print(f"\n按问题类型:")
        for q_type, metrics in aggregate['by_type'].items():
            print(f"  {q_type}:")
            print(f"    数量: {metrics['count']}")
            print(f"    文档召回率: {metrics['avg_title_recall']:.3f}")
            print(f"    文档F1: {metrics['avg_title_f1']:.3f}")

        # Save results
        results_file = os.path.join(base_dir, 'vector/data/evaluation_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'aggregate': aggregate,
                'detailed_metrics': all_metrics[:100]  # Save first 100 for analysis
            }, f, ensure_ascii=False, indent=2)
        print(f"\n评估结果已保存到: {results_file}")

    else:  # demo mode
        # Demo with a few queries
        demo_queries = [
            "What role did Julianne Moore play in the 2002 Oscar winning movie?",
            "Are both Days of the New and TV on the Radio from New York?",
            "Which fruits/crops from Stephanandra and Coffea are valued more across the world?"
        ]

        print("\n" + "="*50)
        print("演示模式 - 示例查询")
        print("="*50)

        for query in demo_queries:
            print(f"\n查询: {query}")
            print("-" * 40)

            results = rag_system.hybrid_retrieval(query, doc_k=2, sent_k=3)

            for title, doc in list(results.items())[:2]:
                print(f"\n  文档: {title}")
                if doc['sentences']:
                    print(f"  相关句子:")
                    for sent in doc['sentences'][:2]:
                        print(f"    - {sent['text'][:100]}...")

    print("\nRAG查询系统运行完成! ✓")

if __name__ == "__main__":
    main()