"""
Analyze bootcamp tasks using LLM to generate descriptions and evaluations.
"""

import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# LLM Configuration
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# Output types
OUTPUT_TYPES = {
    "english_detailed": {
        "prompt": """Please provide a detailed English description of this programming task. This description will be provided to other models, so it should include:
1. A complete and concise task description
2. Clear input/output format specification with examples
3. Any constraints or special requirements
4. The format should be as uniform as possible across different tasks

Task content:
{content}

Please provide only the English description without any additional formatting or markers."""
    },
    "chinese_brief": {
        "prompt": """请提供这个编程任务的中文简要描述。这个描述会提供给人看，需要：
1. 尽可能简洁明了
2. 突出任务的核心要求
3. 不需要详细的实现细节

任务内容：
{content}

请只提供中文描述，不要有其他格式标记。"""
    },
    "quality_evaluation": {
        "prompt": """Please review the complete code implementation and evaluate:
1. Task quality (1-5 scale)
2. Code correctness (incorrect/correct/unclear)
3. Implementation clarity and quality

Full code:
{full_code}

Output a JSON object with the following structure:
{{
    "quality_score": <1-5>,
    "correctness": "<incorrect|correct|unclear>",
    "evaluation": "<brief evaluation text>"
}}

Only output the JSON object, nothing else."""
    }
}


class BootcampAnalyzer:
    def __init__(self, bootcamp_dir: str, output_dir: str):
        self.bootcamp_dir = Path(bootcamp_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.results = []
        # Create output file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_file = self.output_dir / f"bootcamp_analysis_{timestamp}.jsonl"
        self.summary_file = self.output_dir / f"bootcamp_summary_{timestamp}.json"
        
    async def call_llm(self, prompt: str, max_retries: int = 3) -> str:
        """Call the LLM API with the given prompt with retry logic."""
        headers = {
            "Authorization": f"Bearer {LLM_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": LLM_CONFIG["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{LLM_CONFIG['base_url']}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result['choices'][0]['message']['content'].strip()
                        else:
                            error_text = await response.text()
                            logger.error(f"API error (attempt {attempt+1}): {response.status} - {error_text}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            return f"Error: API returned status {response.status}"
            except asyncio.TimeoutError:
                logger.error(f"Timeout calling LLM (attempt {attempt+1})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return "Error: Request timed out"
            except Exception as e:
                logger.error(f"Exception calling LLM (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return f"Error: {str(e)}"
        
        return "Error: Max retries exceeded"
    
    def extract_task_content(self, file_path: Path) -> Dict[str, str]:
        """Extract the task description and code from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the docstring (task description)
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            task_description = docstring_match.group(1) if docstring_match else ""
            
            # Remove the reference code section for description
            if "Here is a reference code" in task_description:
                task_description = task_description.split("Here is a reference code")[0].strip()
            
            return {
                "task_description": task_description,
                "full_code": content
            }
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return {"task_description": "", "full_code": ""}
    
    async def analyze_task(self, task_dir: Path) -> Dict[str, Any]:
        """Analyze a single task directory."""
        task_name = task_dir.name
        logger.info(f"Analyzing task: {task_name}")
        
        # Find the main Python file
        py_files = list(task_dir.glob("*.py"))
        if not py_files:
            logger.warning(f"No Python files found in {task_dir}")
            return None
        
        # Use the file with the same name as the directory if it exists
        main_file = None
        for f in py_files:
            if f.stem == task_name:
                main_file = f
                break
        
        if not main_file:
            main_file = py_files[0]  # Fallback to first Python file
        
        # Extract content
        content = self.extract_task_content(main_file)
        if not content["task_description"]:
            logger.warning(f"No task description found in {main_file}")
            return None
        
        result = {
            "task_name": task_name,
            "file_path": str(main_file.relative_to(self.bootcamp_dir))
        }
        
        # Generate three types of output
        for output_type, config in OUTPUT_TYPES.items():
            if output_type == "quality_evaluation":
                prompt_content = content["full_code"]
                prompt = config["prompt"].format(full_code=prompt_content)
            else:
                prompt_content = content["task_description"]
                prompt = config["prompt"].format(content=prompt_content)
            
            response = await self.call_llm(prompt)
            
            # Parse JSON for quality evaluation
            if output_type == "quality_evaluation":
                try:
                    result[output_type] = json.loads(response)
                except:
                    result[output_type] = {
                        "quality_score": 0,
                        "correctness": "unclear",
                        "evaluation": f"Failed to parse response: {response}"
                    }
            else:
                result[output_type] = response
        
        # Write result immediately to JSONL file
        self.write_result_to_file(result)
        
        return result
    
    def write_result_to_file(self, result: Dict[str, Any]):
        """Write a single result to the JSONL file immediately."""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            logger.info(f"Written result for {result['task_name']} to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to write result for {result['task_name']}: {str(e)}")
    
    async def analyze_all_tasks(self, max_concurrent: int = 10):
        """Analyze all tasks in the bootcamp directory with concurrency limit."""
        # Get all subdirectories
        task_dirs = [d for d in self.bootcamp_dir.iterdir() 
                    if d.is_dir() and not d.name.startswith('__') and d.name not in ['ChemStructure2Property', 'arc', 'arrowmaze', 'bigcodebench']]
        
        logger.info(f"Found {len(task_dirs)} task directories to analyze")
        
        # Process tasks with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(task_dir):
            async with semaphore:
                return await self.analyze_task(task_dir)
        
        # Create tasks
        tasks = [analyze_with_semaphore(task_dir) for task_dir in task_dirs]
        
        # Run tasks and collect results
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        self.results = [r for r in results if r is not None]
        
        logger.info(f"Successfully analyzed {len(self.results)} tasks")
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics from the analysis results."""
        if not self.results:
            return {}
        
        quality_scores = []
        correctness_counts = {"correct": 0, "incorrect": 0, "unclear": 0}
        
        for result in self.results:
            if "quality_evaluation" in result:
                eval_data = result["quality_evaluation"]
                if isinstance(eval_data, dict):
                    score = eval_data.get("quality_score", 0)
                    if score > 0:
                        quality_scores.append(score)
                    
                    correctness = eval_data.get("correctness", "unclear")
                    if correctness in correctness_counts:
                        correctness_counts[correctness] += 1
        
        stats = {
            "total_tasks": len(self.results),
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "quality_score_distribution": {
                "1": sum(1 for s in quality_scores if s == 1),
                "2": sum(1 for s in quality_scores if s == 2),
                "3": sum(1 for s in quality_scores if s == 3),
                "4": sum(1 for s in quality_scores if s == 4),
                "5": sum(1 for s in quality_scores if s == 5),
            },
            "correctness_distribution": correctness_counts,
            "timestamp": datetime.now().isoformat()
        }
        
        return stats
    
    def save_final_statistics(self):
        """Save final statistics to files."""
        # Write statistics as the last line of JSONL
        stats = self.generate_statistics()
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"statistics": stats}, ensure_ascii=False) + '\n')
            logger.info(f"Statistics appended to: {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to write statistics: {str(e)}")
        
        # Also save a formatted summary
        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "statistics": stats,
                    "task_count": len(self.results),
                    "tasks_analyzed": [r["task_name"] for r in self.results]
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Summary saved to: {self.summary_file}")
        except Exception as e:
            logger.error(f"Failed to write summary: {str(e)}")


async def main():
    """Main function to run the analysis."""
    # Get the bootcamp directory path
    bootcamp_dir = Path(__file__).parent.parent / "internbootcamp" / "bootcamp"
    output_dir = Path(__file__).parent / "analysis_results"
    
    analyzer = BootcampAnalyzer(bootcamp_dir, output_dir)
    
    # Analyze all tasks
    await analyzer.analyze_all_tasks(max_concurrent=20)
    
    # Save final statistics
    analyzer.save_final_statistics()
    
    print(f"\nAnalysis complete! Analyzed {len(analyzer.results)} tasks.")
    stats = analyzer.generate_statistics()
    print(f"Average quality score: {stats['average_quality_score']:.2f}")
    print(f"Correctness distribution: {stats['correctness_distribution']}")


if __name__ == "__main__":
    asyncio.run(main())