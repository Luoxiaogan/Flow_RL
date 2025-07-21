#!/usr/bin/env python3
"""
Prompt Generator Module for Checkpoint Testing
Generates prompts and sends them to vLLM server for workflow generation
"""

import asyncio
import aiohttp
import json
import os
import random
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import argparse
from pathlib import Path
import importlib

# Add parent directory to path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CURRENT_DIR))
from ScoreFlow.scripts.base_handler import BenchmarkHandler


def get_benchmark_handler(benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
    """Dynamically import and instantiate the handler for specified benchmark."""
    try:
        handler_module_path = f"ScoreFlow.scripts.{benchmark_name.lower()}.handler"
        handler_module = importlib.import_module(handler_module_path)
        
        # Convention: Handler class name is BenchmarkNameHandler (e.g., Gsm8kHandler)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        
        return handler_class(dataset_path=dataset_path)
    except (ModuleNotFoundError, AttributeError, ValueError) as e:
        print(f"Cannot load handler for benchmark '{benchmark_name}': {e}")
        raise


class PromptGenerator:
    """
    Generates prompts and sends them to vLLM server for workflow generation
    """
    
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        model_name: str = "checkpoint-model",
        output_dir: str = "generated_workflows",
        batch_size: int = 8,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        self.server_url = server_url
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.batch_size = batch_size
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API endpoint
        self.completion_url = f"{server_url}/v1/chat/completions"
    
    def construct_prompt(
        self,
        benchmark: str,
        data_indices: List[int],
        dataset_path: str,
        diversity_reference: Optional[str] = None
    ) -> Tuple[List[Dict[str, str]], str]:
        """
        Construct prompt for workflow generation
        
        Args:
            benchmark: Benchmark name (e.g., "gsm8k", "mbpp")
            data_indices: List of problem indices to include
            dataset_path: Path to the dataset
            diversity_reference: Optional reference to previous workflow for diversity
        
        Returns:
            Tuple of (messages, workflow_id)
        """
        # Get handler for the benchmark
        handler = get_benchmark_handler(benchmark, dataset_path)
        
        # Load conditions from benchmark
        conditions_module = __import__(
            f"ScoreFlow.scripts.{benchmark.lower()}.conditions",
            fromlist=["*"]
        )
        
        # Get random meta prompt
        meta_prompt = random.choice(conditions_module.META_PROMPTS)
        system_prompt = conditions_module.SYSTEM_PROMPT
        start_prompt = conditions_module.PYTHON_START
        end_prompt = conditions_module.PYTHON_END
        
        # Construct workflow text
        workflow_data_text_list = []
        
        for idx in data_indices:
            prompt_text = handler.get_prompt_text(idx)
            workflow_data_text_list.append(prompt_text)
        
        # Create unique workflow ID
        workflow_id = f"{benchmark}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add meta prompt with problem examples
        user_content = meta_prompt + "\n\n"
        
        # Add problems
        for i, problem_text in enumerate(workflow_data_text_list):
            user_content += f"Problem {i+1}:\n{problem_text}\n\n"
        
        # Add diversity reference if provided
        if diversity_reference:
            user_content += f"\nFor diversity, here is a reference workflow (please generate a different approach):\n"
            user_content += f"```python\n{diversity_reference}\n```\n\n"
        
        user_content += f"\n{start_prompt}"
        
        messages.append({"role": "user", "content": user_content})
        
        return messages, workflow_id
    
    async def send_to_server(
        self,
        messages: List[Dict[str, str]],
        workflow_id: str
    ) -> Optional[str]:
        """
        Send prompt to vLLM server and get response
        
        Args:
            messages: Chat messages
            workflow_id: Unique workflow ID
        
        Returns:
            Generated workflow code or None if failed
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.completion_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # Extract code between ```python and ```
                        if "```python" in content:
                            start = content.find("```python") + 9
                            end = content.find("```", start)
                            if end > start:
                                return content[start:end].strip()
                        
                        # If no code blocks, return entire content
                        return content.strip()
                    else:
                        error_text = await response.text()
                        print(f"Server error for {workflow_id}: {response.status} - {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            print(f"Timeout for workflow {workflow_id}")
            return None
        except Exception as e:
            print(f"Error generating workflow {workflow_id}: {e}")
            return None
    
    async def generate_workflow_batch(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate workflows for a batch of tasks
        
        Args:
            tasks: List of task dictionaries with keys:
                - benchmark: str
                - data_indices: List[int]
                - dataset_path: str
                - diversity_reference: Optional[str]
        
        Returns:
            List of results with workflow content and metadata
        """
        results = []
        
        # Process in batches
        for i in range(0, len(tasks), self.batch_size):
            batch = tasks[i:i + self.batch_size]
            batch_coroutines = []
            
            for task in batch:
                messages, workflow_id = self.construct_prompt(
                    benchmark=task["benchmark"],
                    data_indices=task["data_indices"],
                    dataset_path=task["dataset_path"],
                    diversity_reference=task.get("diversity_reference")
                )
                
                # Create coroutine for this task
                coro = self.process_single_task(
                    messages, workflow_id, task
                )
                batch_coroutines.append(coro)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*batch_coroutines)
            results.extend(batch_results)
        
        return results
    
    async def process_single_task(
        self,
        messages: List[Dict[str, str]],
        workflow_id: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single task and save results
        """
        # Generate workflow
        workflow_code = await self.send_to_server(messages, workflow_id)
        
        if workflow_code:
            # Save workflow file
            workflow_path = self.output_dir / f"{workflow_id}.py"
            with open(workflow_path, "w") as f:
                f.write(workflow_code)
            
            # Save metadata
            metadata = {
                "id": workflow_id,
                "benchmark": task["benchmark"],
                "data_indices": task["data_indices"],
                "dataset_path": task["dataset_path"],
                "generated_at": datetime.now().isoformat(),
                "status": "generated"
            }
            
            metadata_path = self.output_dir / f"{workflow_id}.meta.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "workflow_id": workflow_id,
                "status": "success",
                "workflow_path": str(workflow_path),
                "metadata_path": str(metadata_path)
            }
        else:
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": "Failed to generate workflow"
            }


async def main():
    """
    Main function for testing the prompt generator
    """
    parser = argparse.ArgumentParser(description="Generate workflows using vLLM server")
    parser.add_argument("--server-url", type=str, default="http://localhost:8000",
                        help="vLLM server URL")
    parser.add_argument("--model-name", type=str, default="checkpoint-model",
                        help="Model name on server")
    parser.add_argument("--benchmark", type=str, required=True,
                        help="Benchmark name (e.g., gsm8k, mbpp)")
    parser.add_argument("--dataset-path", type=str, required=True,
                        help="Path to dataset file")
    parser.add_argument("--num-workflows", type=int, default=10,
                        help="Number of workflows to generate")
    parser.add_argument("--batch-size", type=int, default=8,
                        help="Batch size for server requests")
    parser.add_argument("--output-dir", type=str, default="generated_workflows",
                        help="Output directory for workflows")
    
    args = parser.parse_args()
    
    # Create generator
    generator = PromptGenerator(
        server_url=args.server_url,
        model_name=args.model_name,
        output_dir=args.output_dir,
        batch_size=args.batch_size
    )
    
    # Create test tasks
    tasks = []
    for i in range(args.num_workflows):
        # Random 2-4 problems per workflow
        num_problems = random.randint(2, 4)
        data_indices = random.sample(range(100), num_problems)  # Assuming dataset has at least 100 problems
        
        task = {
            "benchmark": args.benchmark,
            "data_indices": data_indices,
            "dataset_path": args.dataset_path
        }
        tasks.append(task)
    
    # Generate workflows
    print(f"Generating {len(tasks)} workflows...")
    results = await generator.generate_workflow_batch(tasks)
    
    # Print summary
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nGeneration complete:")
    print(f"  Success: {success_count}/{len(results)}")
    print(f"  Failed: {len(results) - success_count}/{len(results)}")


if __name__ == "__main__":
    asyncio.run(main())