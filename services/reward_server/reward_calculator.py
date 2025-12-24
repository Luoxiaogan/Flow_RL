"""
Reward Calculator for New_Flow_RL

计算 Reward 的核心模块。
支持简单 outcome reward（当前）和三维度扩展（预留）。
"""

from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from src.core.logger import get_logger
from src.benchmarks import get_handler, BenchmarkHandler

logger = get_logger(__name__)


@dataclass
class RewardResult:
    """
    Reward 计算结果。

    Attributes:
        success: 计算是否成功
        score: 总分 (0.0 - 1.0)
        breakdown: 分维度得分
        details: 详细信息
    """
    success: bool
    score: float
    breakdown: Dict[str, Optional[float]] = field(default_factory=lambda: {
        "outcome": None,
        "efficiency": None,
        "preference": None
    })
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "score": self.score,
            "breakdown": self.breakdown,
            "details": self.details
        }


class RewardCalculator:
    """
    Reward 计算器。

    支持两种模式：
    1. simple: 只使用 outcome reward（答案正确性）
    2. multi_dimension: 三维度 reward（outcome + efficiency + preference）

    Usage:
        calculator = RewardCalculator(mode="simple")
        result = await calculator.calculate(
            model_answer="42",
            ground_truth_data={"answer": "42"},
            benchmark="gsm8k"
        )
    """

    def __init__(
        self,
        mode: str = "simple",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化计算器。

        Args:
            mode: 计算模式 (simple | multi_dimension)
            config: 配置参数
        """
        self.mode = mode
        self.config = config or {}

        # 维度权重（multi_dimension 模式使用）
        self.weights = {
            "outcome": self.config.get("outcome_weight", 0.6),
            "efficiency": self.config.get("efficiency_weight", 0.3),
            "preference": self.config.get("preference_weight", 0.1)
        }

        # Handler 缓存
        self._handlers: Dict[str, BenchmarkHandler] = {}

    def get_handler(
        self,
        benchmark: str,
        dataset_path: Optional[str] = None
    ) -> BenchmarkHandler:
        """
        获取或创建 benchmark handler。

        Args:
            benchmark: benchmark 名称
            dataset_path: 数据集路径

        Returns:
            BenchmarkHandler 实例
        """
        cache_key = f"{benchmark}:{dataset_path or 'default'}"

        if cache_key not in self._handlers:
            if dataset_path:
                self._handlers[cache_key] = get_handler(benchmark, dataset_path)
            else:
                # 使用默认路径
                default_paths = {
                    "gsm8k": "data/raw/gsm8k/test.jsonl",
                    "mbpp": "data/raw/mbpp/test.jsonl",
                    "hotpotqa": "data/raw/hotpotqa/test.jsonl",
                }
                path = default_paths.get(benchmark, f"data/raw/{benchmark}/test.jsonl")
                self._handlers[cache_key] = get_handler(benchmark, path)

        return self._handlers[cache_key]

    async def calculate(
        self,
        model_answer: str,
        ground_truth_data: Dict[str, Any],
        benchmark: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RewardResult:
        """
        计算 reward。

        Args:
            model_answer: 模型答案
            ground_truth_data: 标准答案数据
            benchmark: benchmark 名称
            metadata: 额外元数据（用于 efficiency 计算）

        Returns:
            RewardResult
        """
        if self.mode == "simple":
            return await self._calculate_simple(
                model_answer, ground_truth_data, benchmark
            )
        else:
            return await self._calculate_multi_dimension(
                model_answer, ground_truth_data, benchmark, metadata
            )

    def calculate_sync(
        self,
        model_answer: str,
        ground_truth_data: Dict[str, Any],
        benchmark: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RewardResult:
        """
        同步版本的 calculate。
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.calculate(model_answer, ground_truth_data, benchmark, metadata)
                )
                return future.result()
        else:
            return asyncio.run(
                self.calculate(model_answer, ground_truth_data, benchmark, metadata)
            )

    async def _calculate_simple(
        self,
        model_answer: str,
        ground_truth_data: Dict[str, Any],
        benchmark: str
    ) -> RewardResult:
        """
        简单模式：只计算 outcome reward。

        返回 1.0（正确）或 0.0（错误）
        """
        try:
            handler = self.get_handler(benchmark)

            # 使用 handler 的 judge 方法
            is_correct = await handler.judge(
                model_output=model_answer,
                ground_truth_data=ground_truth_data,
                use_llm=True  # 使用 LLM 进行智能判断
            )

            score = 1.0 if is_correct else 0.0

            return RewardResult(
                success=True,
                score=score,
                breakdown={"outcome": score, "efficiency": None, "preference": None},
                details=f"Outcome: {'CORRECT' if is_correct else 'INCORRECT'}"
            )

        except Exception as e:
            logger.error(f"Reward calculation failed: {e}")
            return RewardResult(
                success=False,
                score=0.0,
                breakdown={"outcome": None, "efficiency": None, "preference": None},
                details=f"Error: {str(e)}"
            )

    async def _calculate_multi_dimension(
        self,
        model_answer: str,
        ground_truth_data: Dict[str, Any],
        benchmark: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RewardResult:
        """
        三维度模式：outcome + efficiency + preference。

        当前只实现 outcome，其他维度预留接口。
        """
        metadata = metadata or {}

        # 1. Outcome Reward
        outcome_result = await self._calculate_simple(
            model_answer, ground_truth_data, benchmark
        )
        outcome_score = outcome_result.breakdown.get("outcome", 0.0) or 0.0

        # 2. Efficiency Reward (预留)
        efficiency_score = self._calculate_efficiency(metadata)

        # 3. Preference Reward (预留)
        preference_score = self._calculate_preference(model_answer, ground_truth_data)

        # 加权计算总分
        total_score = (
            self.weights["outcome"] * outcome_score +
            self.weights["efficiency"] * (efficiency_score or 0.0) +
            self.weights["preference"] * (preference_score or 0.0)
        )

        return RewardResult(
            success=True,
            score=total_score,
            breakdown={
                "outcome": outcome_score,
                "efficiency": efficiency_score,
                "preference": preference_score
            },
            details=(
                f"Outcome: {outcome_score:.2f}, "
                f"Efficiency: {efficiency_score}, "
                f"Preference: {preference_score}"
            )
        )

    def _calculate_efficiency(
        self,
        metadata: Dict[str, Any]
    ) -> Optional[float]:
        """
        计算效率 reward（预留实现）。

        基于：
        - Token 消耗
        - 延迟
        - API 调用次数
        - 成本

        Returns:
            效率分数 (0-1) 或 None（未启用）
        """
        # 如果没有效率相关数据，返回 None
        if not metadata:
            return None

        # 预留：基于 metadata 计算效率分数
        # token_cost = metadata.get("total_tokens", 0)
        # latency = metadata.get("latency", 0)
        # api_calls = metadata.get("api_calls", 0)

        # 当前版本返回 None（未启用）
        return None

    def _calculate_preference(
        self,
        model_answer: str,
        ground_truth_data: Dict[str, Any]
    ) -> Optional[float]:
        """
        计算偏好 reward（预留实现）。

        基于：
        - 答案格式规范性
        - 解释清晰度
        - 用户偏好对齐

        Returns:
            偏好分数 (0-1) 或 None（未启用）
        """
        # 当前版本返回 None（未启用）
        return None


def create_reward_calculator(
    mode: str = "simple",
    config: Optional[Dict[str, Any]] = None
) -> RewardCalculator:
    """
    工厂函数：创建 Reward 计算器。

    Args:
        mode: 计算模式
        config: 配置参数

    Returns:
        RewardCalculator 实例
    """
    return RewardCalculator(mode=mode, config=config)
