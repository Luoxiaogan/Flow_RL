"""
Benchmarks Module for New_Flow_RL

提供各种 Benchmark 的统一处理接口。
"""

from src.benchmarks.base_handler import BenchmarkHandler
from src.benchmarks.gsm8k.handler import GSM8KHandler, create_gsm8k_handler


# Handler 注册表
HANDLER_REGISTRY = {
    'gsm8k': GSM8KHandler,
    # 'mbpp': MBPPHandler,  # TODO
    # 'hotpotqa': HotpotQAHandler,  # TODO
}


def get_handler(benchmark_name: str, dataset_path: str, **kwargs) -> BenchmarkHandler:
    """
    获取 benchmark handler。

    Args:
        benchmark_name: benchmark 名称
        dataset_path: 数据集路径
        **kwargs: 额外参数

    Returns:
        BenchmarkHandler 实例
    """
    benchmark_name = benchmark_name.lower()

    if benchmark_name not in HANDLER_REGISTRY:
        raise ValueError(
            f"Unknown benchmark: {benchmark_name}. "
            f"Available: {list(HANDLER_REGISTRY.keys())}"
        )

    handler_class = HANDLER_REGISTRY[benchmark_name]
    return handler_class(dataset_path=dataset_path, **kwargs)


def list_benchmarks():
    """列出所有支持的 benchmarks"""
    return list(HANDLER_REGISTRY.keys())


__all__ = [
    'BenchmarkHandler',
    'GSM8KHandler',
    'create_gsm8k_handler',
    'get_handler',
    'list_benchmarks',
    'HANDLER_REGISTRY',
]
