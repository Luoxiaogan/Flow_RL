"""
Batch Inference Engine - Handles concurrent inference requests
Supports batching, retries, and progress tracking
"""
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from tqdm.asyncio import tqdm
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class InferenceTask:
    """Single inference task"""
    task_id: str
    prompt: Any  # Can be string or list of messages
    metadata: Dict[str, Any]  # Additional metadata
    
    
@dataclass 
class InferenceResult:
    """Result of an inference task"""
    task_id: str
    response: str
    success: bool
    error: Optional[str] = None
    inference_time: float = 0.0
    metadata: Dict[str, Any] = None


class BatchInferenceEngine:
    """Handles batch inference with concurrency control"""
    
    def __init__(
        self,
        inference_fn: Callable,
        max_workers: int = 10,
        batch_size: int = 100,
        retry_times: int = 3,
        timeout: int = 60
    ):
        """
        Initialize batch inference engine
        
        Args:
            inference_fn: Async function for inference
            max_workers: Maximum concurrent workers
            batch_size: Size of each batch
            retry_times: Number of retries for failed requests
            timeout: Timeout for each request in seconds
        """
        self.inference_fn = inference_fn
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.retry_times = retry_times
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_workers)
        
    async def _process_single_task(self, task: InferenceTask) -> InferenceResult:
        """Process a single inference task with retries"""
        last_error = None
        
        for attempt in range(self.retry_times):
            try:
                async with self.semaphore:
                    start_time = time.time()
                    
                    # Apply timeout
                    response = await asyncio.wait_for(
                        self.inference_fn(task.prompt),
                        timeout=self.timeout
                    )
                    
                    inference_time = time.time() - start_time
                    
                    return InferenceResult(
                        task_id=task.task_id,
                        response=response,
                        success=True,
                        inference_time=inference_time,
                        metadata=task.metadata
                    )
                    
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout} seconds"
                logger.warning(f"Task {task.task_id} timeout (attempt {attempt + 1}/{self.retry_times})")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Task {task.task_id} failed (attempt {attempt + 1}/{self.retry_times}): {e}")
                
            # Wait before retry
            if attempt < self.retry_times - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        return InferenceResult(
            task_id=task.task_id,
            response="",
            success=False,
            error=last_error,
            metadata=task.metadata
        )
    
    async def process_batch(
        self,
        tasks: List[InferenceTask],
        progress_bar: bool = True
    ) -> List[InferenceResult]:
        """
        Process a batch of tasks concurrently
        
        Args:
            tasks: List of inference tasks
            progress_bar: Whether to show progress bar
            
        Returns:
            List of inference results
        """
        if progress_bar:
            # Create async tasks with progress bar
            async_tasks = []
            for task in tasks:
                async_tasks.append(self._process_single_task(task))
            
            # Process with progress bar
            results = []
            for coro in tqdm.as_completed(async_tasks, total=len(tasks), desc="Inference"):
                result = await coro
                results.append(result)
                
        else:
            # Process without progress bar
            async_tasks = [self._process_single_task(task) for task in tasks]
            results = await asyncio.gather(*async_tasks)
        
        # Sort results by task_id to maintain order
        results.sort(key=lambda x: x.task_id)
        
        # Log statistics
        success_count = sum(1 for r in results if r.success)
        logger.info(f"Batch completed: {success_count}/{len(tasks)} successful")
        
        return results
    
    async def process_dataset(
        self,
        dataset: pd.DataFrame,
        prompt_column: str = "prompt",
        id_column: str = None,
        save_intermediate: bool = True,
        output_dir: Path = None
    ) -> pd.DataFrame:
        """
        Process entire dataset with batching
        
        Args:
            dataset: Pandas DataFrame with prompts
            prompt_column: Column name containing prompts
            id_column: Column name for IDs (auto-generated if None)
            save_intermediate: Save intermediate results
            output_dir: Directory to save intermediate results
            
        Returns:
            DataFrame with results
        """
        # Prepare tasks
        tasks = []
        for idx, row in dataset.iterrows():
            task_id = str(row[id_column] if id_column else idx)
            prompt = row[prompt_column]
            
            # Extract metadata
            metadata = row.to_dict()
            
            tasks.append(InferenceTask(
                task_id=task_id,
                prompt=prompt,
                metadata=metadata
            ))
        
        # Process in batches
        all_results = []
        for i in range(0, len(tasks), self.batch_size):
            batch = tasks[i:i + self.batch_size]
            logger.info(f"Processing batch {i // self.batch_size + 1}/{(len(tasks) - 1) // self.batch_size + 1}")
            
            results = await self.process_batch(batch)
            all_results.extend(results)
            
            # Save intermediate results
            if save_intermediate and output_dir:
                self._save_intermediate_results(all_results, output_dir, i // self.batch_size + 1)
        
        # Convert to DataFrame
        results_df = self._results_to_dataframe(all_results)
        
        # Merge with original dataset
        if id_column:
            final_df = dataset.merge(results_df, left_on=id_column, right_on='task_id', how='left')
        else:
            final_df = pd.concat([dataset, results_df.drop(columns=['task_id'])], axis=1)
        
        return final_df
    
    def _results_to_dataframe(self, results: List[InferenceResult]) -> pd.DataFrame:
        """Convert results to DataFrame"""
        data = []
        for result in results:
            data.append({
                'task_id': result.task_id,
                'response': result.response,
                'success': result.success,
                'error': result.error,
                'inference_time': result.inference_time
            })
        return pd.DataFrame(data)
    
    def _save_intermediate_results(
        self,
        results: List[InferenceResult],
        output_dir: Path,
        batch_num: int
    ):
        """Save intermediate results to file"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSONL
        output_file = output_dir / f"batch_{batch_num}_results.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                import json
                f.write(json.dumps({
                    'task_id': result.task_id,
                    'response': result.response,
                    'success': result.success,
                    'error': result.error,
                    'inference_time': result.inference_time,
                    'metadata': result.metadata
                }, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved intermediate results to {output_file}")


class ConcurrentScorer:
    """Handles concurrent scoring using scoreflow_reward"""
    
    def __init__(
        self,
        score_fn: Callable,
        max_workers: int = 5,
        timeout: int = 180
    ):
        """
        Initialize concurrent scorer
        
        Args:
            score_fn: Function to compute scores
            max_workers: Maximum concurrent workers
            timeout: Timeout for each scoring request
        """
        self.score_fn = score_fn
        self.max_workers = max_workers
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def _score_single(
        self,
        data_source: str,
        solution_str: str,
        ground_truth: str,
        extra_info: Dict
    ) -> float:
        """Score a single solution"""
        try:
            async with self.semaphore:
                # Run score_fn in executor since it might be blocking
                loop = asyncio.get_event_loop()
                score = await loop.run_in_executor(
                    None,
                    self.score_fn,
                    data_source,
                    solution_str,
                    ground_truth,
                    extra_info
                )
                return score
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return 0.0
    
    async def score_batch(
        self,
        tasks: List[Dict],
        progress_bar: bool = True
    ) -> List[float]:
        """
        Score a batch of solutions
        
        Args:
            tasks: List of scoring tasks
            progress_bar: Whether to show progress bar
            
        Returns:
            List of scores
        """
        async_tasks = []
        for task in tasks:
            async_tasks.append(self._score_single(
                task['data_source'],
                task['solution_str'],
                task['ground_truth'],
                task['extra_info']
            ))
        
        if progress_bar:
            scores = []
            for coro in tqdm.as_completed(async_tasks, total=len(tasks), desc="Scoring"):
                score = await coro
                scores.append(score)
            # Maintain original order
            return scores
        else:
            return await asyncio.gather(*async_tasks)


# Example usage
if __name__ == "__main__":
    async def mock_inference(prompt):
        """Mock inference function for testing"""
        await asyncio.sleep(0.1)  # Simulate inference time
        return f"Response to: {prompt[:50]}..."
    
    async def test():
        # Create engine
        engine = BatchInferenceEngine(
            inference_fn=mock_inference,
            max_workers=5,
            batch_size=10
        )
        
        # Create test tasks
        tasks = [
            InferenceTask(
                task_id=f"task_{i}",
                prompt=f"Test prompt {i}",
                metadata={"index": i}
            )
            for i in range(20)
        ]
        
        # Process batch
        results = await engine.process_batch(tasks)
        
        # Print results
        for result in results[:5]:
            print(f"{result.task_id}: {result.response[:50]}... (success={result.success})")
    
    # asyncio.run(test())