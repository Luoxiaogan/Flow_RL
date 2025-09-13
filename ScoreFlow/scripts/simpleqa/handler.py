## SimpleqaHandler (handler.py)

from typing import List, Dict, Any
import re

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class SimpleqaHandler(BenchmarkHandler):
    """
    SimpleQA dataset handler for world knowledge question answering.
    
    Handles factual questions that require world knowledge to answer correctly.
    Questions span various topics like science, geography, history, etc.
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract questions from SimpleQA data and format them for workflow generation.
        
        Format:
        ---
        **QUESTION:**
        [question text]
        
        **TOPIC:**
        [topic category]
        
        **ANSWER TYPE:**
        [expected answer type: Person, Place, Date, etc.]
        
        **REFERENCE URLs:**
        [list of reference URLs if available]
        ---
        
        (If multiple indices are provided, this structure repeats)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract question and metadata
                question = problem.get('question', '')
                topic = problem.get('topic', 'General')
                answer_type = problem.get('answer_type', 'Not specified')
                urls = problem.get('urls', [])
                
                # Format reference URLs
                urls_text = ""
                if urls and isinstance(urls, list):
                    urls_text = "\n**REFERENCE URLs:**\n"
                    for url in urls[:3]:  # Limit to first 3 URLs
                        urls_text += f"- {url}\n"
                
                # Combine all information
                formatted_problem = f"""---
**QUESTION:**
{question}
"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problem from SimpleQA data: {e}")

    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        Extract questions from SimpleQA data and format them for workflow generation.
        
        Format:
        ---
        **QUESTION:**
        [question text]
        ---
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract question and metadata
                question = problem.get('question', '')
                topic = problem.get('topic', 'General')
                answer_type = problem.get('answer_type', 'Not specified')
                urls = problem.get('urls', [])
                
                # Format reference URLs
                urls_text = ""
                if urls and isinstance(urls, list):
                    urls_text = "\n**REFERENCE URLs:**\n"
                    for url in urls[:3]:  # Limit to first 3 URLs
                        urls_text += f"- {url}\n"
                
                # Combine all information
                formatted_problem = f"""---
**QUESTION:**
{question}
"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problem from SimpleQA data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single SimpleQA problem for verification.
        This includes question, answer, topic, and reference URLs.
        """
        return self._get_problem_by_index(index)
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        Judge whether the model output correctly answers the SimpleQA question.
        
        For SimpleQA, we need to:
        1. Extract the answer from the model output
        2. Compare it with the ground truth answer
        3. Handle variations in formatting and phrasing
        """
        if not model_output or not ground_truth_data:
            return False
        
        # Convert to string and clean
        output_str = str(model_output).strip()
        
        # Get ground truth answer
        correct_answer = ground_truth_data.get('answer', '').strip()
        
        if not correct_answer:
            return False
        
        # Extract answer from output
        answer = self._extract_answer(output_str)
        
        # Simple exact match check (case-insensitive)
        if answer.lower() == correct_answer.lower():
            return True
        
        # Check if correct answer is contained in the output
        if correct_answer.lower() in answer.lower():
            return True
        
        # For more complex cases, use LLM judge
        # This handles paraphrases, alternative phrasings, etc.
        return await self.llm_judge(output_str, ground_truth_data)
    
    def _extract_answer(self, text: str) -> str:
        """
        Extract the answer from model output text.
        Looks for common answer patterns.
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Look for "Final Answer:" pattern
        if "Final Answer:" in text:
            parts = text.split("Final Answer:")
            if len(parts) > 1:
                answer = parts[-1].strip()
                # Remove any trailing punctuation or quotes
                answer = answer.rstrip('.!?')
                answer = answer.strip('"\'')
                return answer
        
        # Look for "Answer:" pattern
        if "Answer:" in text:
            parts = text.split("Answer:")
            if len(parts) > 1:
                answer = parts[-1].strip()
                # Take only the first sentence/line as answer
                if '\n' in answer:
                    answer = answer.split('\n')[0]
                answer = answer.rstrip('.!?')
                answer = answer.strip('"\'')
                return answer
        
        # Look for "The answer is" pattern
        patterns = [
            r"[Tt]he answer is[:\s]+([^.!?\n]+)",
            r"[Tt]he correct answer is[:\s]+([^.!?\n]+)",
            r"[Aa]nswer[:\s]+([^.!?\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                answer = match.group(1).strip()
                answer = answer.rstrip('.!?')
                answer = answer.strip('"\'')
                return answer
        
        # If no pattern found, check if the output is short (likely just the answer)
        lines = text.strip().split('\n')
        if len(lines) == 1 and len(text) < 100:
            return text.strip()
        
        # Return last non-empty line as fallback
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('#'):
                return line
        
        return text