"""
InternBootcamp Benchmark implementation for ScoreFlow
Supports all InternBootcamp task types through dynamic bootcamp class loading
"""
import re
import sys
import json
import importlib
import traceback
from typing import Callable, List, Optional, Tuple, Dict, Any
from pathlib import Path

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from ScoreFlow.benchmark.benchmark import BaseBenchmark
from metagpt.logs import logger

# Add InternBootcamp to Python path
internbootcamp_root = Path(__file__).parent.parent.parent / "InternBootcamp"
sys.path.insert(0, str(internbootcamp_root))


class InternBootcampBenchmark(BaseBenchmark):
    """
    InternBootcamp benchmark implementation
    Dynamically loads and uses bootcamp classes for validation
    """
    
    def __init__(self, name: str, file_path: str, log_path: str):
        super().__init__(name, file_path, log_path)
        self._bootcamp_cache = {}  # Cache loaded bootcamp classes
        
    def _load_bootcamp_class(self, task_name: str):
        """Dynamically load the corresponding bootcamp class"""
        if task_name in self._bootcamp_cache:
            return self._bootcamp_cache[task_name]
        
        try:
            # Import the corresponding bootcamp module
            module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
            module = importlib.import_module(module_path)
            
            # Get bootcamp class (class name is usually TasknameBootcamp format)
            class_name = f"{task_name.capitalize()}bootcamp"
            bootcamp_class = getattr(module, class_name)
            
            self._bootcamp_cache[task_name] = bootcamp_class
            return bootcamp_class
            
        except Exception as e:
            logger.error(f"Failed to load bootcamp class for {task_name}: {e}")
            return None
    
    def extract_answer(self, text: str, task_name: str) -> Optional[Any]:
        """
        Extract answer from model output using bootcamp's extract_output method
        """
        bootcamp_class = self._load_bootcamp_class(task_name)
        if not bootcamp_class:
            return None
            
        try:
            # Use bootcamp's extract_output method
            return bootcamp_class.extract_output(str(text))
        except Exception as e:
            logger.debug(f"Failed to extract answer for {task_name}: {e}")
            return None
    
    def calculate_score(self, expected_output: Dict, prediction: str, task_name: str) -> Tuple[float, Any]:
        """
        Calculate score using bootcamp's verify_score method
        """
        if not task_name or not expected_output:
            return 0.0, None
            
        bootcamp_class = self._load_bootcamp_class(task_name)
        if not bootcamp_class:
            return 0.0, None
        
        try:
            # Use bootcamp's verify_score method
            score = bootcamp_class.verify_score(
                model_output=str(prediction),
                identity=expected_output,
                format_score=0.1,  # Give some score for correct format
                short_penalty=False,  # Don't penalize short outputs
                format_penalty=False  # Don't require think tags
            )
            
            # Extract answer for logging
            extracted = self.extract_answer(prediction, task_name)
            
            return float(score), extracted
            
        except Exception as e:
            logger.error(f"Error calculating score for {task_name}: {e}")
            return 0.0, None
    
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1), retry=retry_if_exception_type(Exception), reraise=True)
    async def _generate_outputs(self, graph):
        """Generate outputs with retry mechanism"""
        return await graph()
    
    async def _filter(self, extraction, question, answer):
        """Filter function for extraction"""
        return await extraction(question, answer)
    
    def get_input_text(self, problem: Dict) -> str:
        """Get input text from problem"""
        # Use the first test case's prompt as input
        if problem.get("test_cases") and len(problem["test_cases"]) > 0:
            return problem["test_cases"][0].get("prompt", "")
        return problem.get("task_description", "")
    
    def get_graph_input_text(self, problem: Dict) -> str:
        """Get graph input text (same as input text for InternBootcamp)"""
        return self.get_input_text(problem)
    
    def get_problem_id(self, problem: Dict) -> int:
        """Get problem ID"""
        return problem.get("id", -1)
    
    def get_result_columns(self) -> List[str]:
        """Get column names for result CSV"""
        return ["question_id", "question", "answer", "correctness", "cost", "score", "extracted_output", "task_name", "task_type"]
    
    async def evaluate_problem(self, problem: dict, extraction: Optional[Callable], graph: Callable) -> Tuple[Any, ...]:
        """
        Evaluate a single problem
        """
        try:
            # Get problem details
            problem_id = self.get_problem_id(problem)
            input_text = self.get_input_text(problem)
            task_name = problem.get("task_name", "unknown")
            task_type = problem.get("task_type", "unknown")
            
            # Generate model output
            graph_input = self.get_graph_input_text(problem)
            output_dict = await self._generate_outputs(lambda: graph(graph_input))
            
            # Get the answer from output
            answer = output_dict.get("answer", "") if isinstance(output_dict, dict) else str(output_dict)
            
            # Calculate score for all test cases
            total_score = 0.0
            total_cases = len(problem.get("test_cases", []))
            extracted_outputs = []
            
            for test_case in problem.get("test_cases", []):
                case_data = test_case.get("case", {})
                score, extracted = self.calculate_score(case_data, answer, task_name)
                total_score += score
                extracted_outputs.append(extracted)
            
            # Average score across all test cases
            avg_score = total_score / total_cases if total_cases > 0 else 0.0
            
            # Determine correctness
            correctness = self.PASS if avg_score >= 0.9 else self.FAIL
            
            # Get cost
            cost = output_dict.get("cost", 0) if isinstance(output_dict, dict) else 0
            
            # Log if failed
            if correctness == self.FAIL:
                self.log_mismatch(
                    input_text,
                    problem.get("test_cases", []),
                    answer,
                    extracted_outputs,
                    f"InternBootcamp {task_name} extraction"
                )
            
            return (problem_id, input_text, answer, correctness, cost, avg_score, extracted_outputs, task_name, task_type)
            
        except Exception as e:
            logger.error(f"Error evaluating problem {problem.get('id', 'unknown')}: {e}")
            traceback.print_exc()
            return (
                problem.get("id", -1),
                self.get_input_text(problem),
                str(e),
                self.FAIL,
                0,
                0.0,
                None,
                problem.get("task_name", "unknown"),
                problem.get("task_type", "unknown")
            )