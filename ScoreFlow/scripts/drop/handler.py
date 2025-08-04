import re
import json
from typing import List, Dict, Any, Union
from difflib import SequenceMatcher

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class DropHandler(BenchmarkHandler):
    """
    DROP (Discrete Reasoning Over Passages) 数据集的具体处理器。
    
    它实现了 BenchmarkHandler 定义的所有抽象方法，提供了
    针对 DROP 数据格式的特定处理逻辑，支持数值推理、计数、排序等任务。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的、
        带有Markdown分隔符的文本, 用于生成工作流。
        
        新格式:
        ---
        PASSAGE:
        [passage text]

        QUESTION:
        [question text]
        ---

        (如果提供多个索引，则重复此结构)
        
        格式为:
        Problem 1:
        Question: [question text]
        Passage: [passage text]

        Problem 2:
        ...
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for i, problem in enumerate(problems):
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage']
                
                # 组合问题和段落
                formatted_problem = f"""
                ---
                **PASSAGE:**
                {passage}

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

    def _normalize_answer(self, answer: str) -> str:
        """
        标准化答案文本，用于比较。
        去除多余空格、转小写、统一数字格式等。
        """
        # 去除前后空格
        answer = answer.strip()
        
        # 如果是数字，尝试标准化
        if self._is_number(answer):
            # 移除逗号
            answer = answer.replace(',', '')
            # 尝试转换为浮点数再转回字符串，以统一格式
            try:
                num = float(answer)
                # 如果是整数，返回整数格式
                if num.is_integer():
                    return str(int(num))
                else:
                    return str(num)
            except:
                pass
        
        # 对于文本答案，转小写并去除多余空格
        answer = answer.lower()
        answer = " ".join(answer.split())
        
        return answer

    def _is_number(self, text: str) -> bool:
        """
        检查文本是否表示一个数字。
        """
        text = text.replace(',', '').strip()
        try:
            float(text)
            return True
        except ValueError:
            return False

    def _extract_answer_from_output(self, output: str) -> Union[str, List[str]]:
        """
        从模型输出中提取答案。
        DROP的答案可能是数字、单个文本跨度或多个文本跨度。
        """
        output_lower = output.lower()
        
        # 尝试多种答案标记模式
        answer_patterns = [
            r'final answer[:\s]+(.+?)(?:\n|$)',
            r'the answer is[:\s]+(.+?)(?:\n|$)',
            r'answer[:\s]+(.+?)(?:\n|$)',
            r'so we have the final results[:\s]+(.+?)(?:\n|$)',
            r'result[:\s]+(.+?)(?:\n|$)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, output_lower, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                
                # 检查是否是多个答案（用逗号、分号或"and"分隔）
                if any(sep in answer for sep in [',', ';', ' and ']):
                    # 分割多个答案
                    parts = re.split(r'[,;]|\s+and\s+', answer)
                    return [self._normalize_answer(part.strip()) for part in parts if part.strip()]
                else:
                    return self._normalize_answer(answer)
        
        # 如果没有找到明确的答案标记，尝试查找数字
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', output)
        if numbers:
            # 返回最后一个找到的数字
            return self._normalize_answer(numbers[-1])
        
        # 最后，返回最后一行非空内容
        lines = output.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line:
                return self._normalize_answer(line)
        
        return ""

    def _compare_answers(self, model_answer: Union[str, List[str]], true_answer: Union[str, List[str]]) -> bool:
        """
        比较两个答案是否匹配。
        处理数字答案、文本答案和多答案的情况。
        """
        # 确保两个答案都是列表格式
        if isinstance(model_answer, str):
            model_answer = [model_answer]
        if isinstance(true_answer, str):
            true_answer = [true_answer]
        
        # 标准化所有答案
        model_answer = [self._normalize_answer(ans) for ans in model_answer]
        true_answer = [self._normalize_answer(ans) for ans in true_answer]
        
        # 对于单答案情况
        if len(model_answer) == 1 and len(true_answer) == 1:
            model_ans = model_answer[0]
            true_ans = true_answer[0]
            
            # 完全匹配
            if model_ans == true_ans:
                return True
            
            # 数字比较（考虑浮点误差）
            if self._is_number(model_ans) and self._is_number(true_ans):
                try:
                    return abs(float(model_ans) - float(true_ans)) < 0.001
                except:
                    pass
            
            # 文本相似度比较
            similarity = SequenceMatcher(None, model_ans, true_ans).ratio()
            if similarity >= 0.85:
                return True
        
        # 对于多答案情况，检查是否所有真实答案都被包含
        else:
            # 转换为集合进行比较
            model_set = set(model_answer)
            true_set = set(true_answer)
            
            # 检查是否完全匹配或真实答案是模型答案的子集
            if true_set.issubset(model_set):
                return True
        
        return False

    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出的答案是否与标准答案一致。
        
        DROP数据集的答案可能是：
        1. 数字（如 "3", "150"）
        2. 单个文本跨度（如 "Los Angeles Lakers"）
        3. 多个文本跨度（如多个球队名称）
        """
        try:
            # 从模型输出中提取答案
            model_answer = self._extract_answer_from_output(str(model_output))
            
            # 获取标准答案
            # DROP数据集可能有 'answer' 或 'all_answers' 字段
            if 'all_answers' in ground_truth_data and ground_truth_data['all_answers']:
                # all_answers 是一个列表，包含所有可接受的答案
                true_answers = ground_truth_data['all_answers']
            elif 'answer' in ground_truth_data:
                true_answers = [ground_truth_data['answer']]
            else:
                return False
            
            # 检查模型答案是否匹配任何一个真实答案
            for true_answer in true_answers:
                if self._compare_answers(model_answer, true_answer):
                    return True
            
            return False
            
        except Exception as e:
            # 如果在判断过程中发生任何错误，安全地判定为错误
            print(f"DROP Judge: 判断过程中发生错误: {e}")
            return False