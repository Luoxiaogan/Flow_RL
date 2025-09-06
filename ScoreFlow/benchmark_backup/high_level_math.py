import re
from typing import Callable, List, Optional, Tuple

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from ScoreFlow.benchmark.benchmark import BaseBenchmark
from metagpt.logs import logger


class HighLevelMathBenchmark(BaseBenchmark):
    def __init__(self, name: str, file_path: str, log_path: str):
        super().__init__(name, file_path, log_path)
    
    def extract_answer(self, text: str) -> Optional[str]:
        """Extract mathematical answer from text, supporting various formats"""
        if not text:
            return None
            
        # Remove all spaces for easier pattern matching
        text_normalized = str(text).strip()
        
        # Priority patterns for answer extraction
        patterns = [
            # Explicit answer markers
            r'####\s*(.+?)(?:\n|$)',
            r'[Ff]inal [Aa]nswer[:：]\s*(.+?)(?:\n|$)',
            r'[Aa]nswer[:：]\s*(.+?)(?:\n|$)',
            r'答案[:：]\s*(.+?)(?:\n|$)',
            r'Therefore,?\s+the answer is\s+(.+?)(?:\n|$)',
            r'So,?\s+the answer is\s+(.+?)(?:\n|$)',
            r'Thus,?\s+the answer is\s+(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_normalized, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit marker, try to find mathematical expressions at the end
        # This includes fractions, numbers, mathematical symbols
        math_patterns = [
            r'(?:=|is)\s*([^\n]+?)(?:\.|,|\n|$)',  # After equals or "is"
            r'\\frac\{[^}]+\}\{[^}]+\}',  # LaTeX fractions
            r'-?\d+/\d+',  # Simple fractions
            r'-?\d+\.?\d*',  # Numbers
        ]
        
        # Get the last 200 characters to focus on the end
        text_end = text_normalized[-200:] if len(text_normalized) > 200 else text_normalized
        
        all_matches = []
        for pattern in math_patterns:
            matches = re.findall(pattern, text_end)
            all_matches.extend(matches)
        
        if all_matches:
            # Return the last match found
            return all_matches[-1].strip()
        
        return None
    
    def normalize_answer(self, answer: str) -> str:
        """Normalize mathematical answers for comparison"""
        if not answer:
            return ""
            
        answer = answer.strip()
        
        # Handle LaTeX fractions
        latex_frac = re.match(r'\\frac\{([^}]+)\}\{([^}]+)\}', answer)
        if latex_frac:
            try:
                num = float(latex_frac.group(1))
                den = float(latex_frac.group(2))
                return str(num / den)
            except:
                return f"{latex_frac.group(1)}/{latex_frac.group(2)}"
        
        # Handle simple fractions
        simple_frac = re.match(r'(-?\d+)/(\d+)', answer)
        if simple_frac:
            try:
                num = float(simple_frac.group(1))
                den = float(simple_frac.group(2))
                return str(num / den)
            except:
                pass
        
        # Remove commas from numbers
        answer = answer.replace(',', '')
        
        # Try to convert to float for numerical comparison
        try:
            return str(float(answer))
        except:
            return answer

    def calculate_score(self, expected_output: str, prediction: str) -> Tuple[float, str]:
        if prediction is None or expected_output is None:
            return 0.0, str(prediction)
        
        # Normalize both answers
        norm_expected = self.normalize_answer(expected_output)
        norm_prediction = self.normalize_answer(prediction)
        
        # First try exact string match
        if norm_expected == norm_prediction:
            return 1.0, prediction
        
        # Try numerical comparison if both can be converted to floats
        try:
            expected_num = float(norm_expected)
            prediction_num = float(norm_prediction)
            if abs(expected_num - prediction_num) < 1e-6:
                return 1.0, prediction
        except:
            pass
        
        return 0.0, prediction

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1), retry=retry_if_exception_type(Exception), reraise=True)
    async def _generate_outputs(self, graph):
        return await graph()

    async def _filter(self, extraction, question, answer):
        return await extraction(question, answer)

    def get_input_text(self, problem):
        input_text = problem["question"]
        return input_text

    async def judge_answer(self, judger, question, model_answer, right_answer):
        return await judger(question, model_answer, right_answer)
    
    def get_graph_input_text(self, problem):
        input_text = problem["question"]
        return input_text

    def get_problem_id(self, problem):
        return problem.get("id", problem.get("index", 0))

    def convert_to_binary(self, s):
        if str(s).strip() == "1":
            return 1
        else:
            return 0
    
    async def evaluate_problem(self, problem: dict, extraction: Optional[Callable], judger: Optional[Callable], graph: Callable) -> Tuple[str, str, str, float]:
        judger = None  # We use our own scoring logic
        input_text = self.get_input_text(problem)
        expected_output = problem.get("answer", "")
        
        try:
            output = await self._generate_outputs(graph)
            
            if extraction is not None:
                output = await self._filter(extraction, input_text, output)
            
            # Extract answer from output
            predicted_answer = self.extract_answer(output)
            
            if judger is None:
                score, extracted_output = self.calculate_score(expected_output, predicted_answer)
            else:
                score = await self.judge_answer(judger, input_text, str(predicted_answer), str(expected_output))
                score = self.convert_to_binary(score)
                extracted_output = predicted_answer

            return input_text, str(extracted_output), expected_output, score
        
        except Exception as e:
            logger.info(f"Maximum retries reached. Skipping this sample. Error: {e}")
            return input_text, str(e), expected_output, 0.0

    def get_result_columns(self) -> List[str]:
        return ["question", "prediction", "expected_output", "score"]