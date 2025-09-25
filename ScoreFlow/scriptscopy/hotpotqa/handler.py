from typing import List, Dict, Any
# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HotpotqaHandler(BenchmarkHandler):
    """
    HotPotQA (Multi-hop Question Answering) 数据集的具体处理器。
    处理多文档推理问题，需要跨文档连接信息来回答问题。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题，格式化为清晰的文本用于生成工作流。

        注意：使用 VectorSearch operator 动态检索文档，不再预先提供上下文。

        格式:
        ---
        **QUESTION:**
        [question text]

        **NOTE:**
        Relevant documents will be retrieved dynamically using VectorSearch operator.

        **ANSWER:(for reference only, not provided during execution)**
        [answer text]

        **SUPPORTING FACTS:(for reference only, not provided during execution)**
        [supporting facts list]
        ---
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []

            for problem in problems:
                # 提取问题
                question = problem['question']
                answer = problem.get('answer', 'N/A')  # 答案可选
                # 尝试获取 original_supporting_facts (validation_vector.jsonl) 或 supporting_facts (原始格式)
                supporting_facts = problem.get('original_supporting_facts', problem.get('supporting_facts', []))

                # 不再包含预定义的文档，说明将通过 VectorSearch 动态检索
                formatted_problem = f"""---
**QUESTION:**
{question}

**NOTE:**
Relevant documents will be retrieved dynamically using VectorSearch operator.
The workflow should initialize and use VectorSearch to find relevant information
from the knowledge base to answer this multi-hop question.

**ANSWER:(for reference only, not provided during execution)**
{answer}

**SUPPORTING FACTS:(for reference only, not provided during execution)**
{supporting_facts}
---"""
                formatted_problems.append(formatted_problem)

            return "\n\n".join(formatted_problems)

        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotPotQA数据中提取问题时出错: {e}")
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题，格式化为清晰的文本用于工作流执行。

        注意：此方法用于支持 VectorSearch 的执行阶段，不再提供预定义的上下文文档。
        相关文档将通过 VectorSearch operator 动态检索。

        格式:
        ---
        **QUESTION:**
        [question text]
        ---
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []

            for problem in problems:
                # 提取问题
                question = problem['question']
                # 注意：answer 和 supporting_facts 仅用于评估，不包含在提示文本中

                # 简化格式：仅提供问题
                # VectorSearch operator 将在 workflow 执行时动态检索相关文档
                formatted_problem = f"""---
**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)

            return "\n\n".join(formatted_problems)
        
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotPotQA数据中提取问题时出错: {e}")
    
    def get_prompt_text_example(self, indices: List[int]) -> str:
        """
        从 HotPotQA 数据中提取问题，格式化为清晰的文本用于生成工作流示例。

        注意：使用 VectorSearch operator 动态检索文档，不再预先提供上下文。
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []

            for problem in problems:
                # 提取问题
                question = problem['question']

                # 简化格式：只包含问题和说明
                formatted_problem = f"""---
**QUESTION:**
{question}

**NOTE:**
This is a multi-hop reasoning question that requires finding and connecting
information from multiple sources. Use VectorSearch operator to retrieve
relevant documents from the knowledge base.
---"""
                formatted_problems.append(formatted_problem)

            return "\n\n".join(formatted_problems)

        except (KeyError, IndexError) as e:
            raise ValueError(f"从HotPotQA数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 HotPotQA 问题的完整数据，用于后续的执行和验证。
        这包括问题、上下文文档、答案、支持事实等信息。
        """
        return self._get_problem_by_index(index)
    
    # judge方法继承自基类，使用LLM进行智能判断
    # 如果需要特殊处理，可以覆盖该方法