from multiprocessing.connection import answer_challenge
from typing import List, Dict, Any
import json

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class DropHandler(BenchmarkHandler):
    """
    DROP (Discrete Reasoning Over Passages) 数据集的具体处理器。
    
    简化版本: 移除了所有rule-based的判断逻辑, 完全依赖LLM进行智能判断。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **PASSAGE:**
        [passage text]

        **QUESTION:**
        [question text]

        **ANSWER:**
        [answer text]

        **ALL ANSWERS:(sometimes there are multiple answers, but the verification is that if you find one correct answer, you are right)**
        [all_answers text]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage']
                answer = problem['answer']
                all_answers = problem['all_answers']

                # 组合问题和段落
                formatted_problem = f"""---
**PASSAGE:**
{passage}

**QUESTION:**
{question}

**ANSWER:(in the testing of the workflow, this will not be provided to the workflow)**
{answer}

**ALL ANSWERS:(in the testing of the workflow, this will not be provided to the workflow; sometimes there are multiple answers, but the verification is that if you find one correct answer, you are right)**
{all_answers}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从DROP数据中提取问题时出错: {e}")
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **PASSAGE:**
        [passage text]

        **QUESTION:**
        [question text]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage']
                answer = problem['answer']
                all_answers = problem['all_answers']

                # 组合问题和段落
                formatted_problem = f"""---
**PASSAGE:**
{passage}

**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从DROP数据中提取问题时出错: {e}")
        
    def get_prompt_text_example(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **PASSAGE:**
        [passage text]

        **QUESTION:**
        [question text]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage'][:350]
                
                # 组合问题和段落
                formatted_problem = f"""---
**PASSAGE:**
{passage} ......


**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从DROP数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 DROP 问题的完整数据，用于后续的执行和验证。
        这包括问题、段落、答案等信息。
        """
        return self._get_problem_by_index(index)

    # judge方法继承自基类，使用LLM进行智能判断
    # 如果需要特殊处理，可以覆盖该方法