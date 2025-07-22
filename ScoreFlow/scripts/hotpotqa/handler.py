import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HotpotqaHandler(BenchmarkHandler):
    """
    HotpotQA 数据集的具体处理器。
    
    它实现了 BenchmarkHandler 定义的所有抽象方法，提供了
    针对 HotpotQA 多跳问答数据格式的特定处理逻辑。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 HotpotQA 数据中提取问题和上下文段落，用于生成工作流。
        
        格式为:
        Problem 1:
        Question: [question text]
        Context:
        [title1]: [sentences...]
        [title2]: [sentences...]
        ...

        Problem 2:
        ...
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for i, problem in enumerate(problems):
                # 提取问题
                question = problem['question']
                
                # 格式化上下文段落
                context_text = self._format_context(problem.get('context', {}))
                
                # 组合问题和上下文
                formatted_problem = f"Problem {i+1}:\nQuestion: {question}\n{context_text}"
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotpotQA数据中提取问题时出错: {e}")

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        格式化上下文段落，将标题和句子组合成可读的文本。
        """
        if not context:
            return "Context: No context provided."
        
        titles = context.get('title', [])
        sentences_list = context.get('sentences', [])
        
        if not titles or not sentences_list:
            return "Context: No context provided."
        
        formatted_context = ["Context:"]
        for title, sentences in zip(titles, sentences_list):
            # 将句子列表合并成段落
            paragraph = " ".join(sentences)
            formatted_context.append(f"{title}: {paragraph}")
        
        return "\n".join(formatted_context)

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 HotpotQA 问题的完整数据，用于后续的执行和验证。
        这包括问题、答案、支持事实和上下文。
        """
        return self._get_problem_by_index(index)

    def _normalize_answer(self, answer: str) -> str:
        """
        标准化答案文本，用于比较。
        去除多余空格、转小写、去除标点符号等。
        """
        # 转小写
        answer = answer.lower()
        # 去除多余空格
        answer = " ".join(answer.split())
        # 移除常见的标点符号（保留必要的如连字符）
        answer = re.sub(r'[.,;:!?"\']', '', answer)
        # 去除前后空格
        answer = answer.strip()
        return answer

    def _extract_answer_from_output(self, output: str) -> str:
        """
        从模型输出中提取答案。
        尝试识别常见的答案格式，如 "answer:", "final answer:", "the answer is" 等。
        """
        output_lower = output.lower()
        
        # 尝试多种答案标记模式
        answer_patterns = [
            r'final answer[:\s]+(.+?)(?:\n|$)',
            r'the answer is[:\s]+(.+?)(?:\n|$)',
            r'answer[:\s]+(.+?)(?:\n|$)',
            r'so we have the final results[:\s]+(.+?)(?:\n|$)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, output_lower, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到明确的答案标记，返回最后一行非空内容
        lines = output.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line:
                return line
        
        return ""

    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出的答案是否与标准答案一致。
        
        对于HotpotQA，使用文本相似度比较，因为答案可能有细微的表述差异。
        """
        try:
            # 从模型输出中提取答案
            model_answer = self._extract_answer_from_output(str(model_output))
            
            # 获取标准答案
            true_answer = ground_truth_data.get('answer', '')
            
            if not model_answer or not true_answer:
                return False
            
            # 标准化两个答案
            normalized_model = self._normalize_answer(model_answer)
            normalized_true = self._normalize_answer(true_answer)
            
            # 完全匹配
            if normalized_model == normalized_true:
                return True
            
            # 检查包含关系，但要避免接受过于简短的部分答案
            # 只有当模型答案包含完整的真实答案时才接受
            if normalized_true in normalized_model:
                return True
            
            # 对于较短的答案，要求更严格的匹配
            if len(normalized_model.split()) < len(normalized_true.split()) * 0.7:
                # 如果模型答案的单词数少于真实答案的70%，不接受部分匹配
                return False
            
            # 使用序列相似度作为备用判断（阈值设为0.8）
            similarity = SequenceMatcher(None, normalized_model, normalized_true).ratio()
            if similarity >= 0.8:
                return True
            
            return False
            
        except Exception as e:
            # 如果在判断过程中发生任何错误，安全地判定为错误
            print(f"HotpotQA Judge: 判断过程中发生错误: {e}")
            return False