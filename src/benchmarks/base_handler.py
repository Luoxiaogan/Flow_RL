"""
Base Benchmark Handler for New_Flow_RL

为不同 Benchmark 提供统一接口的抽象基类。
替代原 Flow_RL_RIGHT 的 base_handler.py，移除 MetaGPT 依赖。
"""

import abc
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.llm_call import LLMClient, get_llm_response
from src.core.logger import get_logger

logger = get_logger(__name__)


class BenchmarkHandler(abc.ABC):
    """
    Benchmark 抽象基类。

    定义处理不同数据集的标准接口：
    1. 加载数据
    2. 提取问题文本用于生成 Prompt
    3. 评判答案是否正确

    Usage:
        class GSM8KHandler(BenchmarkHandler):
            def get_prompt_text(self, indices):
                ...
            def get_ground_truth(self, index):
                ...
    """

    def __init__(
        self,
        dataset_path: Union[str, Path],
        llm_client: Optional[LLMClient] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化处理器。

        Args:
            dataset_path: 数据集文件路径 (.jsonl)
            llm_client: LLM 客户端（用于 LLM judge）
            config: 额外配置
        """
        self.dataset_path = Path(dataset_path)
        self._llm_client = llm_client
        self.config = config or {}

        # 从类名推断 benchmark 名称
        self.benchmark_name = self.__class__.__name__.replace("Handler", "").lower()

        # 加载数据
        self.data: List[Dict[str, Any]] = []
        if self.dataset_path.exists():
            self.data = self._load_data()
        else:
            logger.warning(f"Dataset not found: {self.dataset_path}")

    @property
    def llm_client(self) -> LLMClient:
        """懒加载 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = LLMClient.from_env()
        return self._llm_client

    def _load_data(self) -> List[Dict[str, Any]]:
        """
        从 .jsonl 文件加载数据。

        Returns:
            数据列表
        """
        records = []
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            logger.info(f"Loaded {len(records)} records from {self.dataset_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse dataset: {self.dataset_path}, error: {e}")
        return records

    def _get_problem_by_index(self, index: int) -> Dict[str, Any]:
        """
        通过索引获取问题。

        优先匹配数据中的 'index' 字段，否则使用列表索引。

        Args:
            index: 问题索引

        Returns:
            问题数据字典
        """
        # 优先使用数据中的 'index' 字段
        for problem in self.data:
            if problem.get('index') == index:
                return problem

        # 退回到列表索引
        if 0 <= index < len(self.data):
            return self.data[index]

        raise IndexError(f"Problem index {index} not found in dataset")

    def __len__(self) -> int:
        """返回数据集大小"""
        return len(self.data)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """支持下标访问"""
        return self._get_problem_by_index(index)

    @abc.abstractmethod
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        【子类必须实现】
        根据问题索引列表，生成用于 Prompt 的问题描述文本。

        Args:
            indices: 问题索引列表

        Returns:
            格式化的问题文本
        """
        pass

    @abc.abstractmethod
    def get_ground_truth(self, index: int) -> str:
        """
        【子类必须实现】
        获取指定问题的标准答案。

        Args:
            index: 问题索引

        Returns:
            标准答案字符串
        """
        pass

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取用于验证的完整数据。

        Args:
            index: 问题索引

        Returns:
            包含问题、答案等的完整数据
        """
        return self._get_problem_by_index(index)

    async def judge(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any],
        use_llm: bool = True
    ) -> bool:
        """
        评判模型输出是否正确。

        Args:
            model_output: 模型输出
            ground_truth_data: 包含标准答案的数据
            use_llm: 是否使用 LLM 进行智能判断

        Returns:
            是否正确
        """
        if use_llm:
            return await self._llm_judge(model_output, ground_truth_data)
        else:
            return self._simple_judge(model_output, ground_truth_data)

    def judge_sync(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any],
        use_llm: bool = True
    ) -> bool:
        """
        同步版本的 judge 方法。

        Args:
            model_output: 模型输出
            ground_truth_data: 包含标准答案的数据
            use_llm: 是否使用 LLM 进行智能判断

        Returns:
            是否正确
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # 已有事件循环，使用 run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.judge(model_output, ground_truth_data, use_llm)
                )
                return future.result()
        else:
            return asyncio.run(self.judge(model_output, ground_truth_data, use_llm))

    def _simple_judge(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any]
    ) -> bool:
        """
        简单的字符串比较判断。

        Args:
            model_output: 模型输出
            ground_truth_data: 包含标准答案的数据

        Returns:
            是否匹配
        """
        # 获取标准答案
        ground_truth = ground_truth_data.get('answer', '')
        if not ground_truth:
            ground_truth = str(ground_truth_data)

        # 简单字符串比较（忽略大小写和空白）
        model_str = str(model_output).strip().lower()
        truth_str = str(ground_truth).strip().lower()

        return model_str == truth_str

    async def _llm_judge(
        self,
        model_output: Any,
        ground_truth_data: Dict[str, Any]
    ) -> bool:
        """
        使用 LLM 进行智能判断。

        Args:
            model_output: 模型输出
            ground_truth_data: 包含标准答案的数据

        Returns:
            是否正确
        """
        # 提取问题和答案
        question = ground_truth_data.get('question', 'N/A')
        ground_truth_context = json.dumps(ground_truth_data, indent=2, ensure_ascii=False)

        # 构建判断 prompt
        prompt = f"""You are a meticulous evaluator for a question-answering system.
Your task is to determine if the "Model's Response" correctly answers the question.

**Question:**
{question}

**Ground Truth Data:**
{ground_truth_context}

**Model's Response:**
{model_output}

**Evaluation Rules:**
1. If the Ground Truth Data contains 'all_answers', the response is CORRECT if it matches ANY of them.
2. Otherwise, compare with the 'answer' field.
3. Accept semantically equivalent answers (e.g., "4" and "four" are equivalent).
4. Be strict about the actual question being answered.

**Your Decision:**
Reply with EXACTLY one word: CORRECT or INCORRECT"""

        try:
            response = self.llm_client.call(
                messages=prompt,
                temperature=0.0,  # 确定性输出
                max_tokens=10
            )

            result = response.content.strip().upper()

            if "INCORRECT" in result:
                return False
            elif "CORRECT" in result:
                return True
            else:
                logger.warning(f"Unexpected LLM judge response: {result}")
                return False

        except Exception as e:
            logger.error(f"LLM judge failed: {e}")
            # 回退到简单比较
            return self._simple_judge(model_output, ground_truth_data)

    def extract_answer(self, output: str) -> str:
        """
        从模型输出中提取答案。

        子类可以覆盖此方法提供特定的提取逻辑。

        Args:
            output: 模型原始输出

        Returns:
            提取的答案
        """
        return output.strip()

    def format_problem(self, problem: Dict[str, Any]) -> str:
        """
        格式化单个问题用于展示。

        子类可以覆盖此方法。

        Args:
            problem: 问题数据

        Returns:
            格式化的问题文本
        """
        question = problem.get('question', '[Question not found]')
        return f"**QUESTION:**\n{question}"
