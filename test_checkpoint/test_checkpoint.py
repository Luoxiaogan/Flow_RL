#!/usr/bin/env python3
"""
Main Orchestration Script for Checkpoint Testing
Coordinates workflow generation using vLLM server and testing using API
"""

import asyncio
import json
import os
import sys
import random
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse
from pathlib import Path

# Add parent directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CURRENT_DIR))

from prompt_generator import PromptGenerator
from workflow_tester import WorkflowTester


class CheckpointTester:
    """
    Orchestrates the complete checkpoint testing pipeline
    """
    
    def __init__(
        self,
        checkpoint_path: str,
        benchmark: str,
        dataset_path: str,
        server_url: str,
        exec_llm_config: Dict[str, str],
        num_batches: int = 10,
        workflows_per_batch: int = 15,
        problems_per_workflow: int = 3,
        parallelism: int = 2,
        output_base_dir: str = "checkpoint_test_results"
    ):
        self.checkpoint_path = checkpoint_path
        self.benchmark = benchmark
        self.dataset_path = dataset_path
        self.server_url = server_url
        self.exec_llm_config = exec_llm_config
        self.num_batches = num_batches
        self.workflows_per_batch = workflows_per_batch
        self.problems_per_workflow = problems_per_workflow
        self.parallelism = parallelism
        
        # Create unique output directory for this test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(output_base_dir) / f"{benchmark}_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories
        self.generation_dir = self.output_dir / "generated_workflows"
        self.test_results_dir = self.output_dir / "test_results"
        self.generation_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.generator = PromptGenerator(
            server_url=server_url,
            output_dir=str(self.generation_dir),
            batch_size=8
        )
        
        self.tester = WorkflowTester(
            exec_llm_config=exec_llm_config,
            output_dir=str(self.test_results_dir),
            max_concurrent_executions=5
        )
    
    def get_dataset_size(self) -> int:
        """Get the size of the dataset"""
        # Read dataset to count problems
        with open(self.dataset_path, 'r') as f:
            lines = f.readlines()
        return len(lines)
    
    def create_random_batches(self) -> List[List[List[int]]]:
        """
        Create random batches of problem indices
        Returns list of batches, each containing lists of problem indices
        """
        dataset_size = self.get_dataset_size()
        all_indices = list(range(dataset_size))
        
        batches = []
        for batch_idx in range(self.num_batches):
            batch_workflows = []
            
            for workflow_idx in range(self.workflows_per_batch):
                # Randomly select problems for this workflow
                num_problems = random.randint(2, min(4, self.problems_per_workflow + 1))
                problem_indices = random.sample(all_indices, num_problems)
                batch_workflows.append(problem_indices)
            
            batches.append(batch_workflows)
        
        return batches
    
    async def generate_batch(
        self,
        batch_workflows: List[List[int]],
        batch_idx: int
    ) -> List[Dict[str, Any]]:
        """
        Generate workflows for a single batch
        """
        print(f"\n=== Generating Batch {batch_idx + 1}/{self.num_batches} ===")
        
        tasks = []
        
        for workflow_indices in batch_workflows:
            # Generate multiple versions for diversity
            for version in range(self.parallelism):
                task = {
                    "benchmark": self.benchmark,
                    "data_indices": workflow_indices,
                    "dataset_path": self.dataset_path
                }
                
                # For diversity, reference the first version if this is not the first
                if version > 0 and len(tasks) > 0:
                    # TODO: Load previously generated workflow for diversity
                    # For now, just generate independently
                    pass
                
                tasks.append(task)
        
        # Generate workflows
        results = await self.generator.generate_workflow_batch(tasks)
        
        # Print generation summary
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"Batch {batch_idx + 1} generation complete: {success_count}/{len(results)} successful")
        
        return results
    
    async def test_batch(
        self,
        generation_results: List[Dict[str, Any]],
        batch_idx: int
    ) -> List[Dict[str, Any]]:
        """
        Test workflows from a batch
        """
        print(f"\n=== Testing Batch {batch_idx + 1}/{self.num_batches} ===")
        
        # Get successful workflow paths
        workflow_paths = []
        for result in generation_results:
            if result["status"] == "success":
                workflow_paths.append(Path(result["workflow_path"]))
        
        if not workflow_paths:
            print(f"No successful workflows to test in batch {batch_idx + 1}")
            return []
        
        # Test workflows
        test_results = await self.tester.test_workflows(workflow_paths)
        
        # Print test summary
        correct = sum(1 for r in test_results if r['status'] == 'verified_correct')
        print(f"Batch {batch_idx + 1} testing complete: {correct}/{len(test_results)} correct")
        
        return test_results
    
    async def run_full_test(self):
        """
        Run the complete checkpoint testing pipeline
        """
        print(f"\n{'='*60}")
        print(f"Starting Checkpoint Test")
        print(f"{'='*60}")
        print(f"Checkpoint: {self.checkpoint_path}")
        print(f"Benchmark: {self.benchmark}")
        print(f"Dataset: {self.dataset_path}")
        print(f"Server URL: {self.server_url}")
        print(f"Output Directory: {self.output_dir}")
        print(f"{'='*60}\n")
        
        # Create batches
        print("Creating random problem batches...")
        batches = self.create_random_batches()
        
        # Track overall statistics
        total_generated = 0
        total_successful = 0
        total_tested = 0
        total_correct = 0
        
        start_time = time.time()
        
        # Process each batch
        for batch_idx, batch_workflows in enumerate(batches):
            # Generate workflows
            generation_results = await self.generate_batch(batch_workflows, batch_idx)
            total_generated += len(generation_results)
            total_successful += sum(1 for r in generation_results if r["status"] == "success")
            
            # Test workflows
            test_results = await self.test_batch(generation_results, batch_idx)
            total_tested += len(test_results)
            total_correct += sum(1 for r in test_results if r['status'] == 'verified_correct')
            
            # Progress update
            elapsed = time.time() - start_time
            print(f"\nProgress: {batch_idx + 1}/{self.num_batches} batches completed")
            print(f"Elapsed time: {elapsed:.1f}s")
        
        # Final summary
        elapsed_total = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"Checkpoint Test Complete")
        print(f"{'='*60}")
        print(f"Total workflows generated: {total_generated}")
        print(f"Successfully generated: {total_successful} ({total_successful/total_generated*100:.1f}%)")
        print(f"Total workflows tested: {total_tested}")
        print(f"Verified correct: {total_correct} ({total_correct/total_tested*100:.1f}% of tested)")
        print(f"Overall success rate: {total_correct/total_generated*100:.1f}%")
        print(f"Total time: {elapsed_total:.1f}s")
        print(f"Results saved to: {self.output_dir}")
        
        # Save final summary
        summary = {
            "checkpoint_path": self.checkpoint_path,
            "benchmark": self.benchmark,
            "dataset_path": self.dataset_path,
            "server_url": self.server_url,
            "num_batches": self.num_batches,
            "workflows_per_batch": self.workflows_per_batch,
            "parallelism": self.parallelism,
            "total_generated": total_generated,
            "total_successful": total_successful,
            "total_tested": total_tested,
            "total_correct": total_correct,
            "success_rate": total_correct / total_generated if total_generated > 0 else 0,
            "elapsed_time": elapsed_total,
            "timestamp": datetime.now().isoformat()
        }
        
        summary_path = self.output_dir / "test_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


async def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description="Test model checkpoint with workflow generation and execution")
    parser.add_argument("--checkpoint-path", type=str, required=True,
                        help="Path to model checkpoint")
    parser.add_argument("--benchmark", type=str, required=True,
                        help="Benchmark name (e.g., gsm8k, mbpp)")
    parser.add_argument("--dataset-path", type=str, required=True,
                        help="Path to dataset file")
    parser.add_argument("--server-url", type=str, default="http://localhost:8000",
                        help="vLLM server URL")
    parser.add_argument("--exec-llm", type=str, required=True,
                        help="Execution LLM config (JSON string)")
    parser.add_argument("--num-batches", type=int, default=10,
                        help="Number of batches to process")
    parser.add_argument("--workflows-per-batch", type=int, default=15,
                        help="Number of workflows per batch")
    parser.add_argument("--problems-per-workflow", type=int, default=3,
                        help="Average number of problems per workflow")
    parser.add_argument("--parallelism", type=int, default=2,
                        help="Number of parallel versions per workflow")
    parser.add_argument("--output-base-dir", type=str, default="checkpoint_test_results",
                        help="Base directory for output")
    
    args = parser.parse_args()
    
    # Parse exec LLM config
    try:
        exec_llm_config = json.loads(args.exec_llm)
    except json.JSONDecodeError as e:
        print(f"Failed to parse exec-llm config: {e}")
        sys.exit(1)
    
    # Create tester
    tester = CheckpointTester(
        checkpoint_path=args.checkpoint_path,
        benchmark=args.benchmark,
        dataset_path=args.dataset_path,
        server_url=args.server_url,
        exec_llm_config=exec_llm_config,
        num_batches=args.num_batches,
        workflows_per_batch=args.workflows_per_batch,
        problems_per_workflow=args.problems_per_workflow,
        parallelism=args.parallelism,
        output_base_dir=args.output_base_dir
    )
    
    # Run test
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())