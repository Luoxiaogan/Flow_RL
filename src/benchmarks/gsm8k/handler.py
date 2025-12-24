"""
GSM8K Benchmark Handler for New_Flow_RL

GSM8K (Grade School Math 8K) 数据集处理器。
专门用于数学应用题的答案判断。
"""

import re
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from src.benchmarks.base_handler import BenchmarkHandler
from src.core.logger import get_logger

logger = get_logger(__name__)


class GSM8KHandler(BenchmarkHandler):
    """
    GSM8K 数据集处理器。

    GSM8K 数据格式：
    {
        "question": "问题文本...",
        "answer": "解题步骤... #### 最终数值答案"
    }

    Usage:
        handler = GSM8KHandler("data/raw/gsm8k/test.jsonl")
        prompt = handler.get_prompt_text([0, 1, 2])
        is_correct = handler.judge_sync(model_output, handler[0])
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        生成用于 Prompt 的问题文本。

        Args:
            indices: 问题索引列表

        Returns:
            格式化的问题文本
        """
        formatted_problems = []

        for idx in indices:
            try:
                problem = self._get_problem_by_index(idx)
                question = problem.get('question', '[Question not found]')

                formatted_problem = f"""---
**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            except (KeyError, IndexError) as e:
                logger.warning(f"Failed to get problem at index {idx}: {e}")
                continue

        return "\n\n".join(formatted_problems)

    def get_prompt_text_with_answer(self, indices: List[int]) -> str:
        """
        生成带答案的问题文本（用于 workflow generation）。

        Args:
            indices: 问题索引列表

        Returns:
            格式化的问题文本（包含答案）
        """
        formatted_problems = []

        for idx in indices:
            try:
                problem = self._get_problem_by_index(idx)
                question = problem.get('question', '[Question not found]')
                answer = problem.get('answer', '[Answer not found]')

                formatted_problem = f"""---
**QUESTION:**
{question}

**ANSWER:** (will not be provided during testing)
{answer}
---"""
                formatted_problems.append(formatted_problem)
            except (KeyError, IndexError) as e:
                logger.warning(f"Failed to get problem at index {idx}: {e}")
                continue

        return "\n\n".join(formatted_problems)

    def get_ground_truth(self, index: int) -> str:
        """
        获取标准答案。

        GSM8K 的答案格式为 "解题步骤... #### 数值答案"
        此方法提取 #### 后的数值答案。

        Args:
            index: 问题索引

        Returns:
            数值答案字符串
        """
        problem = self._get_problem_by_index(index)
        answer = problem.get('answer', '')

        # 提取 #### 后的最终答案
        if '####' in answer:
            final_answer = answer.split('####')[-1].strip()
            return final_answer

        return answer.strip()

    def extract_answer(self, output: str) -> str:
        """
        从模型输出中提取数值答案。

        尝试多种模式：
        1. #### 后的内容
        2. "answer is" 后的数字
        3. "= " 后的数字
        4. 最后一个数字

        Args:
            output: 模型原始输出

        Returns:
            提取的数值答案
        """
        output = str(output).strip()

        # 模式1: #### 格式
        if '####' in output:
            return output.split('####')[-1].strip()

        # 模式2: "the answer is X" 格式
        match = re.search(r'(?:the\s+)?answer\s+is[:\s]+([+-]?\d+(?:,\d{3})*(?:\.\d+)?)', output, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '')

        # 模式3: "= X" 格式（最后一个等号后的数字）
        match = re.search(r'=\s*([+-]?\d+(?:,\d{3})*(?:\.\d+)?)\s*$', output)
        if match:
            return match.group(1).replace(',', '')

        # 模式4: 提取最后一个数字
        numbers = re.findall(r'[+-]?\d+(?:,\d{3})*(?:\.\d+)?', output)
        if numbers:
            return numbers[-1].replace(',', '')

        return output

    def _simple_judge(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any]
    ) -> bool:
        """
        GSM8K 特定的简单判断逻辑。

        提取并比较数值答案。

        Args:
            model_output: 模型输出
            ground_truth_data: 标准答案数据

        Returns:
            是否正确
        """
        # 提取模型答案
        model_answer = self.extract_answer(str(model_output))

        # 提取标准答案
        ground_truth = ground_truth_data.get('answer', '')
        if '####' in ground_truth:
            expected = ground_truth.split('####')[-1].strip()
        else:
            expected = ground_truth.strip()

        # 清理并比较
        model_answer = model_answer.replace(',', '').strip()
        expected = expected.replace(',', '').strip()

        # 数值比较
        try:
            model_num = float(model_answer)
            expected_num = float(expected)
            # 允许小数点误差
            return abs(model_num - expected_num) < 1e-6
        except ValueError:
            # 字符串比较
            return model_answer.lower() == expected.lower()

    async def _llm_judge(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any]
    ) -> bool:
        """
        GSM8K 特定的 LLM 判断。

        针对数学问题优化的 prompt。

        Args:
            model_output: 模型输出
            ground_truth_data: 标准答案数据

        Returns:
            是否正确
        """
        question = ground_truth_data.get('question', '')
        answer = ground_truth_data.get('answer', '')

        # 提取标准数值答案
        if '####' in answer:
            expected = answer.split('####')[-1].strip()
        else:
            expected = answer.strip()

        # 提取模型答案
        model_answer = self.extract_answer(str(model_output))

        # 先尝试简单数值比较
        try:
            model_num = float(model_answer.replace(',', ''))
            expected_num = float(expected.replace(',', ''))
            if abs(model_num - expected_num) < 1e-6:
                return True
        except ValueError:
            pass

        # 如果数值比较失败，使用 LLM
        prompt = f"""You are evaluating a math problem answer.

**Question:**
{question}

**Expected Answer:**
{expected}

**Model's Answer:**
{model_output}

**Extracted Model Answer:**
{model_answer}

**Task:**
Compare the numerical values. Consider:
- Different formats are OK (e.g., "12" vs "12.0" vs "twelve")
- Units should match if specified
- The model's extracted answer should equal the expected answer

Reply with EXACTLY one word: CORRECT or INCORRECT"""

        try:
            response = self.llm_client.call(
                messages=prompt,
                temperature=0.0,
                max_tokens=10
            )

            result = response.content.strip().upper()
            return "CORRECT" in result and "INCORRECT" not in result

        except Exception as e:
            logger.error(f"LLM judge failed: {e}")
            return self._simple_judge(model_output, ground_truth_data)


def create_gsm8k_handler(
    dataset_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> GSM8KHandler:
    """
    工厂函数：创建 GSM8K handler。

    Args:
        dataset_path: 数据集路径（默认使用项目路径）
        **kwargs: 额外参数传递给 handler

    Returns:
        GSM8KHandler 实例
    """
    if dataset_path is None:
        # 尝试默认路径
        default_paths = [
            Path("data/raw/gsm8k/test.jsonl"),
            Path("data/gsm8k.jsonl"),
            Path("../data/raw/gsm8k/test.jsonl"),
        ]
        for path in default_paths:
            if path.exists():
                dataset_path = path
                break

        if dataset_path is None:
            logger.warning("GSM8K dataset not found, using empty handler")
            dataset_path = Path("data/raw/gsm8k/test.jsonl")

    return GSM8KHandler(dataset_path=dataset_path, **kwargs)
