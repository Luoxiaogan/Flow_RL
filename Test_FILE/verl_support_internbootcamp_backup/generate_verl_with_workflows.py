"""
Unified VERL Data Generator with Workflow Integration
Generates VERL training data with actual MetaGPT workflows using ScoreFlow
"""
import os
import sys
import json
import asyncio
import argparse
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflow_generator_scoreflow import WorkflowGenerator
from workflow_executor_scoreflow import InternBootcampWorkflowExecutor
from internbootcamp_utils import InternBootcampManager, classify_ability, get_task_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VERLWorkflowGenerator:
    """Generates VERL data with integrated workflow generation and execution"""
    
    def __init__(self, config: Dict[str, Any], workflow_type: str = "predefined"):
        self.config = config
        self.workflow_type = workflow_type
        self.manager = InternBootcampManager()
        self.workflow_generator = WorkflowGenerator(config, workflow_type)
        self.workflow_executor = InternBootcampWorkflowExecutor()
        
    def create_verl_messages(self, task_name: str, task_examples: List[Dict[str, Any]], 
                           task_description: str, workflow_code: str) -> List[Dict[str, str]]:
        """Create HuggingFace chat format messages for VERL"""
        
        # System message
        system_message = {
            "role": "system",
            "content": f"""You are an expert at designing problem-solving workflows using {'predefined operators' if self.workflow_type == 'predefined' else 'flexible custom operators'}. Your task is to create MetaGPT workflows that can solve various instances of specific problem types."""
        }
        
        # User message
        user_content = f"""Task Type: {task_name}

Task Description:
{task_description}

Here are some example problems of this type:

{self.format_examples_for_prompt(task_examples)}

Please create a MetaGPT workflow that can solve any problem of this type. The workflow should:
1. Use {'the predefined operators (Custom, Review, Reflect, Programmer, ScEnsemble)' if self.workflow_type == 'predefined' else 'the FlexibleCustom operator with appropriate reasoning patterns'}
2. Handle different problem instances flexibly
3. Ensure correct output format
4. Be executable in MetaGPT environment"""
        
        user_message = {
            "role": "user",
            "content": user_content
        }
        
        # Assistant message with the generated workflow
        assistant_message = {
            "role": "assistant",
            "content": workflow_code
        }
        
        return [system_message, user_message, assistant_message]
    
    def format_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for prompt"""
        formatted = []
        for i, example in enumerate(examples[:3], 1):  # Limit to 3 examples
            formatted.append(f"Example {i}:\n{json.dumps(example, indent=2, ensure_ascii=False)}")
        return "\n\n".join(formatted)
    
    async def generate_and_execute_workflow(self, task_name: str, entry_id: int,
                                          llm_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate workflow and execute it to get reward"""
        try:
            # Generate workflow entry
            workflow_entry = self.workflow_generator.generate_workflow_entry(
                task_name, entry_id, llm_config
            )
            
            if not workflow_entry:
                return None
            
            # Execute workflow to get reward
            execution_result = await self.workflow_executor.execute_single_workflow(
                workflow_entry, timeout=self.config.get('execution_timeout', 180)
            )
            
            # Get examples and description for VERL entry
            examples = workflow_entry['examples']
            description = workflow_entry['description']
            workflow_code = workflow_entry['workflow_code']
            
            # Create VERL messages
            messages = self.create_verl_messages(task_name, examples, description, workflow_code)
            
            # Create VERL entry
            verl_entry = {
                "data_source": f"internbootcamp_{task_name}",
                "prompt": messages,  # HF chat format with workflow
                "ability": classify_ability(task_name),
                "reward_model": {
                    "task_name": task_name,
                    "test_cases": [ex["identity"] for ex in examples],
                    "average_reward": execution_result.get('average_reward', 0.0),
                    "successful_examples": execution_result.get('successful_examples', 0),
                    "total_examples": execution_result.get('total_examples', len(examples))
                },
                "extra_info": {
                    "entry_id": entry_id,
                    "task_type": get_task_type(task_name),
                    "workflow_type": self.workflow_type,
                    "num_examples": len(examples),
                    "timestamp": datetime.now().isoformat(),
                    "execution_results": execution_result.get('results', [])
                }
            }
            
            return verl_entry
            
        except Exception as e:
            logger.error(f"Failed to generate/execute workflow for {task_name}: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='Generate VERL data with integrated workflows')
    
    # Workflow type
    parser.add_argument('--workflow-type', choices=['predefined', 'flexible'], default='predefined',
                       help='Type of workflow to generate')
    
    # Task selection
    task_group = parser.add_mutually_exclusive_group()
    task_group.add_argument('--tasks', nargs='+', help='Specific tasks to process')
    task_group.add_argument('--all', action='store_true', help='Process all available tasks')
    
    # Generation parameters
    parser.add_argument('--entries-per-task', type=int, default=5,
                       help='Number of VERL entries per task')
    parser.add_argument('--examples-per-entry', type=int, default=3,
                       help='Number of examples per VERL entry')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--output-dir', help='Output directory')
    
    # LLM parameters
    parser.add_argument('--llm-model', help='LLM model to use')
    parser.add_argument('--llm-base-url', help='LLM API base URL')
    parser.add_argument('--llm-api-key', help='LLM API key')
    parser.add_argument('--temperature', type=float, default=0.7, help='LLM temperature')
    
    # Execution parameters
    parser.add_argument('--max-workers', type=int, default=5, help='Max concurrent workers')
    parser.add_argument('--execution-timeout', type=int, default=180, help='Workflow execution timeout')
    parser.add_argument('--dry-run', action='store_true', help='Test run without saving')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Override config
    if args.entries_per_task:
        config['generation_config']['prompts_per_task'] = args.entries_per_task
    if args.examples_per_entry:
        config['generation_config']['examples_per_task'] = args.examples_per_entry
    if args.output_dir:
        config['verl_config']['data_dir'] = args.output_dir
    if args.execution_timeout:
        config['execution_timeout'] = args.execution_timeout
    
    # Setup LLM config
    llm_config = {
        "model": args.llm_model or os.getenv("OPENAI_MODEL", "gpt-4"),
        "base_url": args.llm_base_url or os.getenv("OPENAI_BASE_URL"),
        "api_key": args.llm_api_key or os.getenv("OPENAI_API_KEY"),
        "temperature": args.temperature
    }
    
    # Create output directory
    output_dir = Path(config['verl_config']['data_dir']) / f"verl_with_workflows_{args.workflow_type}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    logger.info(f"Initializing VERL workflow generator (type: {args.workflow_type})...")
    generator = VERLWorkflowGenerator(config, args.workflow_type)
    
    # Get available tasks
    manager = InternBootcampManager()
    available_tasks = manager.get_available_tasks()
    
    # Select tasks
    if args.tasks:
        selected_tasks = [t for t in args.tasks if t in available_tasks]
    elif args.all:
        selected_tasks = available_tasks
    else:
        # Default: random selection
        count = min(10, len(available_tasks))
        selected_tasks = random.sample(available_tasks, count)
    
    logger.info(f"Selected {len(selected_tasks)} tasks for VERL generation")
    
    # Generate VERL entries
    all_entries = []
    failed_tasks = []
    entry_id = 0
    
    # Create event loop for async execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        for task_name in selected_tasks:
            logger.info(f"Processing task: {task_name}")
            task_success_count = 0
            
            for i in range(args.entries_per_task):
                # Generate and execute workflow
                verl_entry = loop.run_until_complete(
                    generator.generate_and_execute_workflow(task_name, entry_id, llm_config)
                )
                
                if verl_entry:
                    all_entries.append(verl_entry)
                    task_success_count += 1
                    entry_id += 1
                    
                    reward = verl_entry['reward_model']['average_reward']
                    logger.info(f"Generated entry {entry_id} for {task_name} (reward: {reward:.3f})")
                else:
                    logger.warning(f"Failed to generate entry {i+1} for {task_name}")
            
            if task_success_count == 0:
                failed_tasks.append(task_name)
            else:
                logger.info(f"Generated {task_success_count}/{args.entries_per_task} entries for {task_name}")
                
    finally:
        loop.close()
    
    # Summary
    logger.info(f"\nGeneration complete:")
    logger.info(f"- Total entries: {len(all_entries)}")
    logger.info(f"- Successful tasks: {len(selected_tasks) - len(failed_tasks)}")
    logger.info(f"- Failed tasks: {len(failed_tasks)}")
    
    # Calculate reward statistics
    rewards = [e['reward_model']['average_reward'] for e in all_entries]
    if rewards:
        avg_reward = sum(rewards) / len(rewards)
        high_reward_count = sum(1 for r in rewards if r > 0.5)
        logger.info(f"- Average reward: {avg_reward:.3f}")
        logger.info(f"- High reward entries (>0.5): {high_reward_count}")
    
    if args.dry_run:
        logger.info("\nDry run mode - showing first entry:")
        if all_entries:
            print(json.dumps(all_entries[0], indent=2, ensure_ascii=False))
        return
    
    # Split train/test
    train_ratio = config['verl_config']['train_ratio']
    random.shuffle(all_entries)
    
    split_idx = int(len(all_entries) * train_ratio)
    train_entries = all_entries[:split_idx]
    test_entries = all_entries[split_idx:]
    
    # Save data
    output_format = config['verl_config']['output_format']
    
    if output_format == 'parquet':
        # Save as parquet
        train_df = pd.DataFrame(train_entries)
        test_df = pd.DataFrame(test_entries)
        
        train_path = output_dir / f"verl_train_{args.workflow_type}.parquet"
        test_path = output_dir / f"verl_test_{args.workflow_type}.parquet"
        
        train_df.to_parquet(train_path, index=False)
        test_df.to_parquet(test_path, index=False)
        
    else:
        # Save as JSON
        train_path = output_dir / f"verl_train_{args.workflow_type}.json"
        test_path = output_dir / f"verl_test_{args.workflow_type}.json"
        
        with open(train_path, 'w', encoding='utf-8') as f:
            json.dump(train_entries, f, indent=2, ensure_ascii=False)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            json.dump(test_entries, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved training data to {train_path} ({len(train_entries)} entries)")
    logger.info(f"Saved test data to {test_path} ({len(test_entries)} entries)")
    
    # Save metadata
    metadata = {
        "generation_time": datetime.now().isoformat(),
        "workflow_type": args.workflow_type,
        "config": config,
        "llm_config": {k: v for k, v in llm_config.items() if k != "api_key"},
        "stats": {
            "total_entries": len(all_entries),
            "train_entries": len(train_entries),
            "test_entries": len(test_entries),
            "successful_tasks": len(selected_tasks) - len(failed_tasks),
            "failed_tasks": failed_tasks,
            "average_reward": avg_reward if rewards else 0.0,
            "high_reward_entries": high_reward_count if rewards else 0
        }
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved metadata to {metadata_path}")


if __name__ == "__main__":
    main()