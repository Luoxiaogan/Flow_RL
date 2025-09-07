from typing import List, Dict, Any

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class Gsm8k_reasoning_v2Handler(BenchmarkHandler):
    """
    GSM8K 数据集的具体处理器。
    
    简化版本：移除了所有rule-based的判断逻辑，完全依赖LLM进行智能判断。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
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
            raise ValueError(f"从GSM8K数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 GSM8K 问题的完整数据，用于后续的执行和验证。
        """
        return self._get_problem_by_index(index)

    # judge方法继承自基类，使用LLM进行智能判断
    # 基类的LLM judge能够理解数学问题并比较数值答案