import re
from typing import List, Dict, Any

# 导入我们在上一步中定义的抽象基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class Gsm8kHandler(BenchmarkHandler):
    """
    GSM8K 数据集的具体处理器。
    
    它实现了 BenchmarkHandler 定义的所有抽象方法，提供了
    针对 GSM8K 数据格式的特定处理逻辑。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 GSM8K 数据中提取并格式化问题文本，用于生成工作流。
        
        格式为:
        Problem 1:
        [question text]

        Problem 2:
        [question text]
        ...
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            # 从每个问题字典中提取 'question' 字段并拼接
            return "\n\n".join([f"Problem {i+1}:\n{p['question']}" for i, p in enumerate(problems)])
        except (KeyError, IndexError) as e:
            raise ValueError(f"从GSM8K数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 GSM8K 问题的完整数据，用于后续的执行和验证。
        对于GSM8K，这通常就是原始的、包含问题和答案的JSON对象。
        """
        return self._get_problem_by_index(index)

    def _extract_answer_from_string(self, text: str) -> str:
        """
        一个辅助函数，用于从任意字符串（模型的输出或标准答案）中提取
        最终的数值答案。
        
        它首先寻找 '####' 标记，如果找不到，则返回字符串中的最后一个数字。
        """
        # 优先匹配 '####' 格式，这是GSM8K的标准答案格式
        match = re.search(r'####\s*([\d,]+\.?\d*)', text)
        if match:
            # 移除逗号以正确转换成数字
            return match.group(1).replace(',', '')
        
        # 如果没有 '####'，则尝试查找字符串中出现的最后一个数字
        # 这对于处理格式不完全规范的模型输出很有用
        numbers = re.findall(r'[\d,]+\.?\d*', text)
        if numbers:
            # 返回最后一个找到的数字，同样移除逗号
            return numbers[-1].replace(',', '')
            
        # 如果两种方法都找不到，返回空字符串
        return ""

    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出的答案是否与标准答案一致。
        
        这整合了原来 _extract_final_answer 和 judger 的逻辑。
        """
        try:
            # 1. 从模型输出中提取答案
            model_answer_str = self._extract_answer_from_string(str(model_output))
            
            # 2. 从标准答案数据中提取答案
            # ground_truth_data['answer'] 包含了推理过程和最终答案
            true_answer_str = self._extract_answer_from_string(ground_truth_data['answer'])

            # 3. 检查是否成功提取到答案
            if not model_answer_str or not true_answer_str:
                return False # 如果任一答案无法提取，则判定为错误

            # 4. 将提取出的字符串转换为浮点数进行比较，以兼容整数和小数
            return float(model_answer_str) == float(true_answer_str)

        except (ValueError, TypeError, KeyError):
            # 如果在提取或转换过程中发生任何错误（如KeyError, float转换失败），
            # 都安全地判定为错误。
            return False