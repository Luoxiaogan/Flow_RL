"""
Reward Server for New_Flow_RL

基于 FastAPI 的 Reward 计算服务。
提供 HTTP API 接收 model output 并返回 reward。
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.reward_server.reward_calculator import (
    RewardCalculator,
    RewardResult,
    create_reward_calculator
)
from services.reward_server.execution_manager import (
    ExecutionManager,
    get_execution_manager
)
from services.reward_server.workflow_executor import (
    WorkflowExecutionResult,
    ProblemResult
)
from src.core.logger import setup_logger, get_logger
from src.core.config_manager import ConfigManager

logger = get_logger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================

class RewardRequest(BaseModel):
    """Reward 计算请求"""
    task_id: str = Field(..., description="任务ID")
    question: str = Field(..., description="原始问题")
    ground_truth: str = Field(..., description="标准答案")
    model_answer: str = Field(..., description="模型答案")
    benchmark: str = Field(..., description="Benchmark名称")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class RewardResponse(BaseModel):
    """Reward 计算响应"""
    success: bool = Field(..., description="是否成功")
    score: float = Field(..., description="总分")
    breakdown: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {
            "outcome": None,
            "efficiency": None,
            "preference": None
        },
        description="分维度得分"
    )
    details: Optional[str] = Field(None, description="评分详情")
    task_id: str = Field(..., description="任务ID")


class BatchRewardRequest(BaseModel):
    """批量 Reward 计算请求"""
    requests: List[RewardRequest] = Field(..., description="请求列表")


class BatchRewardResponse(BaseModel):
    """批量 Reward 计算响应"""
    results: List[RewardResponse] = Field(..., description="结果列表")
    total: int = Field(..., description="总数")
    success_count: int = Field(..., description="成功数")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    mode: str = Field(..., description="Reward模式")
    version: str = Field(default="1.0.0", description="版本号")


# =============================================================================
# Workflow Execution Models (Multi-turn Support)
# =============================================================================

class WorkflowExecuteRequest(BaseModel):
    """Workflow 执行请求"""
    workflow_code: str = Field(..., description="Workflow Python 代码")
    test_problems: List[Dict[str, Any]] = Field(..., description="测试问题列表")
    benchmark: str = Field(default="gsm8k", description="Benchmark 名称")
    timeout: int = Field(default=60, description="超时时间（秒）")


class ProblemResultResponse(BaseModel):
    """单个问题执行结果"""
    problem_id: str = Field(..., description="问题ID")
    success: bool = Field(..., description="执行是否成功")
    correct: bool = Field(..., description="答案是否正确")
    model_answer: Optional[str] = Field(None, description="模型答案")
    expected_answer: Optional[str] = Field(None, description="期望答案")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(default=0.0, description="执行时间")


class WorkflowExecuteResponse(BaseModel):
    """Workflow 执行响应（支持 Multi-turn 修复）"""
    success: bool = Field(..., description="执行是否成功（无致命错误）")
    score: float = Field(..., description="准确率 (correct / total)")
    error: Optional[str] = Field(None, description="错误信息（用于 Multi-turn 修复）")
    traceback: Optional[str] = Field(None, description="详细 traceback（用于修复 prompt）")
    details: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total": 0,
            "correct": 0,
            "failed": []
        },
        description="执行详情"
    )
    problem_results: List[ProblemResultResponse] = Field(
        default_factory=list,
        description="各问题执行结果"
    )


# =============================================================================
# Server Setup
# =============================================================================

# 全局实例
_calculator: Optional[RewardCalculator] = None
_execution_manager: Optional[ExecutionManager] = None


def get_calculator() -> RewardCalculator:
    """获取全局计算器实例"""
    global _calculator
    if _calculator is None:
        mode = os.getenv("REWARD_MODE", "simple")
        _calculator = create_reward_calculator(mode=mode)
    return _calculator


def get_exec_manager() -> ExecutionManager:
    """获取全局执行管理器实例"""
    global _execution_manager
    if _execution_manager is None:
        problem_timeout = int(os.getenv("PROBLEM_TIMEOUT", "60"))
        workflow_timeout = int(os.getenv("WORKFLOW_TIMEOUT", "300"))
        max_concurrency = int(os.getenv("MAX_CONCURRENCY", "10"))
        _execution_manager = get_execution_manager(
            problem_timeout=problem_timeout,
            workflow_timeout=workflow_timeout,
            max_concurrency=max_concurrency
        )
    return _execution_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info("Starting Reward Server...")
    global _calculator, _execution_manager

    # Initialize reward calculator
    mode = os.getenv("REWARD_MODE", "simple")
    _calculator = create_reward_calculator(mode=mode)
    logger.info(f"Reward Calculator initialized (mode={mode})")

    # Initialize execution manager
    _execution_manager = get_exec_manager()
    logger.info("Execution Manager initialized")

    yield

    # Shutdown
    logger.info("Shutting down Reward Server...")


# 创建 FastAPI 应用
app = FastAPI(
    title="New_Flow_RL Reward Server",
    description="Reward 计算服务 - 支持 outcome reward 和三维度扩展",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    calculator = get_calculator()
    return HealthResponse(
        status="healthy",
        mode=calculator.mode,
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查（别名）"""
    return await health_check()


@app.post("/reward", response_model=RewardResponse)
async def calculate_reward(request: RewardRequest):
    """
    计算单个 reward。

    Args:
        request: RewardRequest

    Returns:
        RewardResponse
    """
    calculator = get_calculator()

    try:
        # 构建 ground_truth_data
        ground_truth_data = {
            "question": request.question,
            "answer": request.ground_truth,
        }
        ground_truth_data.update(request.metadata.get("ground_truth_data", {}))

        # 计算 reward
        result: RewardResult = await calculator.calculate(
            model_answer=request.model_answer,
            ground_truth_data=ground_truth_data,
            benchmark=request.benchmark,
            metadata=request.metadata
        )

        return RewardResponse(
            success=result.success,
            score=result.score,
            breakdown=result.breakdown,
            details=result.details,
            task_id=request.task_id
        )

    except Exception as e:
        logger.error(f"Reward calculation failed for task {request.task_id}: {e}")
        return RewardResponse(
            success=False,
            score=0.0,
            breakdown={"outcome": None, "efficiency": None, "preference": None},
            details=f"Error: {str(e)}",
            task_id=request.task_id
        )


@app.post("/reward/batch", response_model=BatchRewardResponse)
async def calculate_batch_reward(request: BatchRewardRequest):
    """
    批量计算 reward。

    Args:
        request: BatchRewardRequest

    Returns:
        BatchRewardResponse
    """
    results = []
    success_count = 0

    # 并发处理所有请求
    tasks = [calculate_reward(req) for req in request.requests]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for response in responses:
        if isinstance(response, Exception):
            results.append(RewardResponse(
                success=False,
                score=0.0,
                breakdown={"outcome": None, "efficiency": None, "preference": None},
                details=f"Error: {str(response)}",
                task_id="unknown"
            ))
        else:
            results.append(response)
            if response.success:
                success_count += 1

    return BatchRewardResponse(
        results=results,
        total=len(results),
        success_count=success_count
    )


@app.get("/config")
async def get_config():
    """获取当前配置"""
    calculator = get_calculator()
    return {
        "mode": calculator.mode,
        "weights": calculator.weights,
        "supported_benchmarks": ["gsm8k", "mbpp", "hotpotqa"]
    }


# =============================================================================
# Workflow Execution Endpoints (Multi-turn Support)
# =============================================================================

@app.post("/execute_workflow", response_model=WorkflowExecuteResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    """
    执行 Workflow 并返回详细结果。

    支持 Multi-turn 修复：
    - 如果执行失败，返回详细的 error 和 traceback
    - 客户端可以使用这些信息构建修复 prompt

    Args:
        request: WorkflowExecuteRequest

    Returns:
        WorkflowExecuteResponse with detailed results
    """
    exec_manager = get_exec_manager()

    try:
        # Execute workflow on all test problems
        result = await exec_manager.execute_workflow_parallel(
            workflow_code=request.workflow_code,
            problems=request.test_problems,
            benchmark=request.benchmark,
            timeout=request.timeout
        )

        # Convert problem results to response format
        problem_results = []
        failed_problems = []

        for pr in result.problem_results:
            problem_results.append(ProblemResultResponse(
                problem_id=pr.problem_id,
                success=pr.success,
                correct=pr.correct,
                model_answer=pr.model_answer,
                expected_answer=pr.expected_answer,
                error=pr.error,
                execution_time=pr.execution_time
            ))

            if not pr.success or not pr.correct:
                failed_problems.append({
                    "id": pr.problem_id,
                    "error": pr.error or "Incorrect answer",
                    "expected": pr.expected_answer,
                    "got": pr.model_answer
                })

        return WorkflowExecuteResponse(
            success=result.success,
            score=result.score,
            error=result.error,
            traceback=result.traceback,
            details={
                "total": result.total_problems,
                "correct": result.correct_count,
                "failed": failed_problems
            },
            problem_results=problem_results
        )

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Workflow execution failed: {e}")
        return WorkflowExecuteResponse(
            success=False,
            score=0.0,
            error=str(e),
            traceback=tb,
            details={
                "total": len(request.test_problems),
                "correct": 0,
                "failed": []
            },
            problem_results=[]
        )


# =============================================================================
# Server Runner
# =============================================================================

def run_server(
    host: str = "0.0.0.0",
    port: int = 7788,
    reload: bool = False,
    workers: int = 1
):
    """
    运行 Reward 服务器。

    Args:
        host: 监听地址
        port: 监听端口
        reload: 是否启用热重载
        workers: worker 数量
    """
    setup_logger("reward_server", level="INFO")
    logger.info(f"Starting Reward Server at {host}:{port}")

    uvicorn.run(
        "services.reward_server.server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reward Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=7788, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )
