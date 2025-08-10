import re
from typing import List, Dict, Any

# 导入我们在上一步中定义的抽象基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class High_Level_MathHandler(BenchmarkHandler):
    """
    High Level Math 数据集的具体处理器。
    
    它实现了 BenchmarkHandler 定义的所有抽象方法，提供了
    针对 High Level Math 数据格式的特定处理逻辑。
    
    支持的数据集文件：
    - all.jsonl: 所有题目的集合
    - aime_2024.jsonl: AIME 2024年题目
    - aime_2025.jsonl: AIME 2025年题目
    - limr.jsonl: LIMR题目集
    - math_500.jsonl: MATH 500题目集
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 High Level Math 数据中提取并格式化问题文本，用于生成工作流。
        
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
            raise ValueError(f"从High Level Math数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 High Level Math 问题的完整数据，用于后续的执行和验证。
        对于High Level Math，这通常就是原始的、包含问题和答案的JSON对象。
        """
        return self._get_problem_by_index(index)

    def _normalize_answer(self, answer: str) -> str:
        """
        标准化数学答案格式，以便进行比较。
        处理分数、小数、整数等不同格式。
        """
        # 移除所有空格
        answer = answer.strip().replace(" ", "")
        
        # 处理分数格式（如 \frac{1}{4} 或 1/4）
        # 匹配 LaTeX 分数格式
        latex_frac_match = re.match(r'\\frac\{([^}]+)\}\{([^}]+)\}', answer)
        if latex_frac_match:
            numerator = latex_frac_match.group(1)
            denominator = latex_frac_match.group(2)
            # 尝试计算分数值
            try:
                return str(float(numerator) / float(denominator))
            except:
                return f"{numerator}/{denominator}"
        
        # 处理普通分数格式（如 1/4）
        simple_frac_match = re.match(r'(-?\d+)/(\d+)', answer)
        if simple_frac_match:
            numerator = simple_frac_match.group(1)
            denominator = simple_frac_match.group(2)
            try:
                return str(float(numerator) / float(denominator))
            except:
                return answer
        
        # 移除逗号（处理大数字）
        answer = answer.replace(',', '')
        
        # 尝试转换为浮点数
        try:
            return str(float(answer))
        except:
            return answer

    def _extract_answer_from_string(self, text: str) -> str:
        """
        从模型输出中提取答案。
        支持多种答案格式标记。
        """
        # 优先查找明确的答案标记
        # 支持多种格式：#### 答案、Answer:、Final Answer:、答案：等
        patterns = [
            r'####\s*(.+?)(?:\n|$)',
            r'[Ff]inal [Aa]nswer[:：]\s*(.+?)(?:\n|$)',
            r'[Aa]nswer[:：]\s*(.+?)(?:\n|$)',
            r'答案[:：]\s*(.+?)(?:\n|$)',
            r'Therefore,?\s+(.+?)(?:\n|$)',
            r'So,?\s+(.+?)(?:\n|$)',
            r'Thus,?\s+(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到明确标记，尝试提取最后一个数学表达式
        # 匹配数字、分数、LaTeX格式等
        math_patterns = [
            r'\\frac\{[^}]+\}\{[^}]+\}',  # LaTeX分数
            r'-?\d+/\d+',  # 普通分数
            r'-?\d+\.?\d*',  # 数字（可能带小数）
        ]
        
        all_matches = []
        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            all_matches.extend(matches)
        
        if all_matches:
            # 返回最后一个找到的数学表达式
            return all_matches[-1]
        
        return ""

    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出的答案是否与标准答案一致。
        
        支持多种数学答案格式的比较。
        """
        try:
            # 1. 从模型输出中提取答案
            model_answer = self._extract_answer_from_string(str(model_output))
            
            # 2. 获取标准答案
            true_answer = ground_truth_data.get('answer', '')
            
            # 3. 检查是否成功提取到答案
            if not model_answer or not true_answer:
                return False
            
            # 4. 标准化两个答案
            normalized_model = self._normalize_answer(model_answer)
            normalized_true = self._normalize_answer(true_answer)
            
            # 5. 比较答案
            # 首先尝试字符串比较
            if normalized_model == normalized_true:
                return True
            
            # 如果都是数字，尝试数值比较（允许小的误差）
            try:
                model_num = float(normalized_model)
                true_num = float(normalized_true)
                return abs(model_num - true_num) < 1e-6
            except:
                # 如果不能转换为数字，返回False
                return False

        except Exception as e:
            # 如果在处理过程中发生任何错误，安全地判定为错误
            return False