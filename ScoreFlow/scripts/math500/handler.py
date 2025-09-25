from typing import List, Dict, Any

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class Math500Handler(BenchmarkHandler):
    """
    MATH-500 high-level mathematics benchmark handler.
    
    Handles 500 challenging mathematical problems spanning various topics
    and difficulty levels from competition mathematics.
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract problems from MATH-500 data and format them with Markdown separators
        for workflow generation.
        
        Format:
        ---
        **QUESTION:**
        [question text with mathematical notation]
        ---
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract question field
                question = problem.get('question', '[Question not found]')
                
                # Use Markdown format, consistent with GSM8K Handler
                formatted_problem = f"""---
**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            # Separate multiple problem instances with double newlines
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problems from MATH-500 data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single MATH-500 problem for execution and verification.
        """
        return self._get_problem_by_index(index)

    # judge method inherits from base class, using LLM for intelligent judgment
    # Base class LLM judge can understand complex mathematical problems and compare solutions