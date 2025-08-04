# 文件: ScoreFlow/scripts/gsm8k/handler.py

import re
from typing import List, Dict, Any

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class Gsm8kHandler(BenchmarkHandler):
    """
    GSM8K 数据集的具体处理器。
    它实现了 BenchmarkHandler 定义的所有抽象方法，并适配了新的
    Markdown Prompt 格式。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 GSM8K 数据中提取问题，并格式化为带有Markdown分隔符的
        示例区块，用于生成工作流。
        
        新格式:
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
                
                # 使用新的、与DROP Handler一致的Markdown格式
                # 即使没有PASSAGE，也保持格式统一性，便于模型理解结构
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

    def _extract_answer_from_string(self, text: str) -> str:
        """
        一个健壮的辅助函数，用于从任意字符串中提取最终的数值答案。
        它首先寻找 '####' 标记，然后是 'Final Answer:', 最后是字符串中的最后一个数字。
        """
        text = str(text) # 确保输入是字符串
        
        # 1. 优先匹配 GSM8K 的标准答案格式 '#### <answer>'
        match = re.search(r'####\s*([\d,]+\.?\d*)', text)
        if match:
            return match.group(1).replace(',', '')

        # 2. 其次匹配我们自己框架的输出格式 'Final Answer: <answer>'
        match = re.search(r'Final Answer:\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '')

        # 3. 作为后备，查找字符串中出现的最后一个数字
        numbers = re.findall(r'[\d,]+\.?\d*', text)
        if numbers:
            return numbers[-1].replace(',', '')
            
        return ""

    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出的答案是否与标准答案一致。
        """
        try:
            # 1. 从模型输出中提取答案
            model_answer_str = self._extract_answer_from_string(model_output)
            
            # 2. 从标准答案数据中提取答案
            true_answer_str = self._extract_answer_from_string(ground_truth_data['answer'])

            # 3. 检查是否成功提取到答案 (如果任一为空字符串，则无法比较)
            if not model_answer_str or not true_answer_str:
                return False

            # 4. 将提取出的字符串转换为浮点数进行比较，以处理可能的浮点误差
            #    例如，模型可能输出 25.0 而标准答案是 25
            model_float = float(model_answer_str)
            true_float = float(true_answer_str)
            
            # 使用一个小的容差进行比较
            return abs(model_float - true_float) < 1e-5

        except (ValueError, TypeError, KeyError) as e:
            # 打印错误信息以便调试，但最终返回False
            print(f"GSM8K Judge: 判断过程中发生错误: {e}")
            return False