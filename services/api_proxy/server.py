"""
API Proxy Server for New_Flow_RL

基于 FastAPI 的 API 代理服务。
提供速率限制、负载均衡和请求转发功能。
"""

import os
import time
import asyncio
import httpx
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from src.core.logger import setup_logger, get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Models
# =============================================================================

@dataclass
class ProxyConfig:
    """代理配置"""
    target_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    target_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 5059
    rate_per_second: int = 10
    max_concurrency: int = 50
    timeout: int = 60


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    queue_size: int
    total_requests: int
    successful_requests: int
    failed_requests: int


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """
    令牌桶速率限制器。

    使用滑动窗口实现平滑的速率限制。
    """

    def __init__(self, rate_per_second: int):
        """
        初始化速率限制器。

        Args:
            rate_per_second: 每秒允许的请求数
        """
        self.rate_per_second = rate_per_second
        self.window_size = 1.0  # 1 秒窗口
        self.timestamps: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        尝试获取令牌。

        Returns:
            是否成功获取
        """
        async with self._lock:
            now = time.time()

            # 清理过期的时间戳
            while self.timestamps and self.timestamps[0] < now - self.window_size:
                self.timestamps.popleft()

            # 检查是否超过限制
            if len(self.timestamps) >= self.rate_per_second:
                return False

            # 添加新时间戳
            self.timestamps.append(now)
            return True

    async def wait_and_acquire(self):
        """等待直到可以获取令牌"""
        while not await self.acquire():
            await asyncio.sleep(0.1)


class ConcurrencyLimiter:
    """并发限制器"""

    def __init__(self, max_concurrency: int):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.current = 0
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self.semaphore.acquire()
        async with self._lock:
            self.current += 1

    async def __aexit__(self, *args):
        async with self._lock:
            self.current -= 1
        self.semaphore.release()


# =============================================================================
# Proxy Server
# =============================================================================

# 全局状态
_config: Optional[ProxyConfig] = None
_rate_limiter: Optional[RateLimiter] = None
_concurrency_limiter: Optional[ConcurrencyLimiter] = None
_client: Optional[httpx.AsyncClient] = None
_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global _config, _rate_limiter, _concurrency_limiter, _client

    # Startup
    logger.info("Starting API Proxy Server...")

    _config = ProxyConfig(
        target_url=os.getenv("PROXY_TARGET_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        target_api_key=os.getenv("PROXY_TARGET_API_KEY", os.getenv("DASHSCOPE_API_KEY", "")),
        host=os.getenv("PROXY_HOST", "0.0.0.0"),
        port=int(os.getenv("PROXY_PORT", "5059")),
        rate_per_second=int(os.getenv("PROXY_RATE_PER_SECOND", "10")),
        max_concurrency=int(os.getenv("PROXY_MAX_CONCURRENCY", "50")),
        timeout=int(os.getenv("PROXY_TIMEOUT", "60"))
    )

    _rate_limiter = RateLimiter(_config.rate_per_second)
    _concurrency_limiter = ConcurrencyLimiter(_config.max_concurrency)
    _client = httpx.AsyncClient(timeout=_config.timeout, verify=False)

    logger.info(f"Target URL: {_config.target_url}")
    logger.info(f"Rate limit: {_config.rate_per_second} req/s")
    logger.info(f"Max concurrency: {_config.max_concurrency}")

    yield

    # Shutdown
    logger.info("Shutting down API Proxy Server...")
    if _client:
        await _client.aclose()


# 创建 FastAPI 应用
app = FastAPI(
    title="New_Flow_RL API Proxy",
    description="API 代理服务 - 提供速率限制和负载均衡",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        queue_size=0,  # 当前实现不使用队列
        total_requests=_stats["total_requests"],
        successful_requests=_stats["successful_requests"],
        failed_requests=_stats["failed_requests"]
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查（别名）"""
    return await health_check()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_request(path: str, request: Request):
    """
    代理请求到目标 API。

    Args:
        path: 请求路径
        request: 原始请求

    Returns:
        代理响应
    """
    global _stats

    _stats["total_requests"] += 1

    # 等待速率限制
    await _rate_limiter.wait_and_acquire()

    # 并发限制
    async with _concurrency_limiter:
        try:
            # 构建目标 URL - 处理路径重复问题
            base_url = _config.target_url.rstrip('/')

            # 如果 base_url 以 /v1 或 /v4 结尾，需要特殊处理
            if base_url.endswith('/v1') or base_url.endswith('/v4'):
                if path.startswith('v1/') or path.startswith('v4/'):
                    # path 已经包含版本前缀，去掉 base_url 的版本
                    base_url = base_url.rsplit('/', 1)[0]
                target_url = f"{base_url}/{path}" if path else f"{base_url}/chat/completions"
            else:
                target_url = f"{base_url}/{path}" if path else base_url

            # 复制请求头
            headers = dict(request.headers)
            headers.pop("host", None)

            # 添加认证头
            if _config.target_api_key:
                headers["Authorization"] = f"Bearer {_config.target_api_key}"

            # 获取请求体
            body = await request.body()

            # 发送请求
            response = await _client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=body
            )

            _stats["successful_requests"] += 1

            # 返回响应 - 不复制原始 headers 避免 Content-Length 不匹配
            response_headers = {}
            for key, value in response.headers.items():
                # 跳过会导致问题的 headers
                if key.lower() not in ("content-length", "content-encoding", "transfer-encoding"):
                    response_headers[key] = value

            if response.headers.get("content-type", "").startswith("application/json"):
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=response_headers
                )
            else:
                from fastapi.responses import Response
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.headers.get("content-type", "text/plain")
                )

        except httpx.HTTPStatusError as e:
            _stats["failed_requests"] += 1
            logger.error(f"HTTP error for {path}: {e}")
            return JSONResponse(
                content={"error": str(e), "status_code": e.response.status_code},
                status_code=e.response.status_code
            )

        except Exception as e:
            _stats["failed_requests"] += 1
            logger.error(f"Proxy error for {path}: {e}")
            return JSONResponse(
                content={"error": str(e)},
                status_code=500
            )


# =============================================================================
# Server Runner
# =============================================================================

def run_server(
    host: str = "0.0.0.0",
    port: int = 5059,
    reload: bool = False,
    workers: int = 1
):
    """
    运行 API Proxy 服务器。

    Args:
        host: 监听地址
        port: 监听端口
        reload: 是否启用热重载
        workers: worker 数量
    """
    setup_logger("api_proxy", level="INFO")
    logger.info(f"Starting API Proxy Server at {host}:{port}")

    uvicorn.run(
        "services.api_proxy.server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API Proxy Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=5059, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )
