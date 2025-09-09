from typing import List, Dict, Any

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MgsmbnHandler(BenchmarkHandler):
    """
    MGSM Bengali dataset handler.
    
    MGSM (Multilingual Grade School Math) is the multilingual version of GSM8K.
    This handler processes the Bengali version of the dataset.
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract problems from MGSM Bengali data and format them with Markdown separators
        for workflow generation.
        
        Format:
        ---
        **QUESTION:**
        [question text in Bengali]
        ---
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract the question field (in Bengali)
                question = problem.get('question', '[Question not found]')
                answer = problem.get('answer', '[Answer not found]')
                
                # Use Markdown format, consistent with GSM8K handler
                formatted_problem = f"""---
**QUESTION:**
{question}
---
**ANSWER:**
{answer}
---"""
                formatted_problems.append(formatted_problem)
            
            # Separate multiple questions with double newlines
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting questions from MGSM Bengali data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single MGSM Bengali problem for execution and verification.
        """
        return self._get_problem_by_index(index)

    # judge method inherits from base class, using LLM for intelligent judgment
    # The base class LLM judge can understand mathematical problems and compare numerical answers