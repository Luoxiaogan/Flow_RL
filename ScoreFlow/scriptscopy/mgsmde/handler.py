from typing import List, Dict, Any

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MgsmdeHandler(BenchmarkHandler):
    """
    MGSM German dataset handler.
    
    MGSM (Multilingual Grade School Math) is the multilingual version of GSM8K.
    This handler processes the German version of the dataset.
    """
    def get_prompt_text_example(self, indices: List[int]) -> str:
        """
        从 GSM8K 数据中提取问题，并格式化为带有Markdown分隔符的
        示例区块，用于生成工作流。
        
        格式:
        ---
        **QUESTION:**
        [question text]
        ---
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 只提取 question 字段
                question = problem.get('question', '[Question not found]')
                
                # 使用Markdown格式，与DROP Handler保持一致
                formatted_problem = f"""---
**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            # 使用两个换行符来分隔多个问题实例
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从mgsm数据中提取问题时出错: {e}")
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract problems from MGSM German data and format them with Markdown separators
        for workflow generation.
        
        Format:
        ---
        **QUESTION:**
        [question text in German]
        ---
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract the question field (in German)
                question = problem.get('question', '[Question not found]')
                answer = problem.get('answer', '[Answer not found]')
                # Use Markdown format, consistent with GSM8K handler
                formatted_problem = f"""---
**QUESTION:**
{question}
"""
                formatted_problems.append(formatted_problem)
            
            # Separate multiple questions with double newlines
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting questions from MGSM German data: {e}")

    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        Extract problems from MGSM German data and format them with Markdown separators
        for workflow generation.
        
        Format:
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract the question field (in German)
                question = problem.get('question', '[Question not found]')
                answer = problem.get('answer', '[Answer not found]')
                
                # Use Markdown format, consistent with GSM8K handler
                formatted_problem = f"""---
**QUESTION:**
{question}
**ANSWER:**
{answer}
"""
                formatted_problems.append(formatted_problem)
            
            # Separate multiple questions with double newlines
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting questions from MGSM German data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single MGSM German problem for execution and verification.
        """
        return self._get_problem_by_index(index)

    # judge method inherits from base class, using LLM for intelligent judgment
    # The base class LLM judge can understand mathematical problems and compare numerical answers