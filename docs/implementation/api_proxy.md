# API Proxy 实现文档

## 概述

API Proxy 是一个基于 FastAPI 的代理服务，负责将请求转发到 DashScope API，并提供速率限制和并发控制。

## 架构

```
客户端请求 (localhost:5059)
        ↓
   ┌─────────────────┐
   │   API Proxy     │
   │  ├─ 速率限制     │
   │  ├─ 并发控制     │
   │  └─ 请求转发     │
   └─────────────────┘
        ↓
   DashScope API
```

## 核心组件

### 1. RateLimiter（速率限制器）

基于滑动窗口的令牌桶算法，控制请求发送频率。

```python
class RateLimiter:
    def __init__(self, rate_per_second: int):
        self.rate_per_second = rate_per_second
        self.timestamps: deque = deque()

    async def acquire(self) -> bool:
        # 清理过期时间戳，检查是否超过限制

    async def wait_and_acquire(self):
        # 等待直到可以获取令牌
```

### 2. ConcurrencyLimiter（并发限制器）

基于信号量的并发控制，限制同时处理的请求数。

```python
class ConcurrencyLimiter:
    def __init__(self, max_concurrency: int):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def __aenter__(self):
        await self.semaphore.acquire()

    async def __aexit__(self, *args):
        self.semaphore.release()
```

### 3. ProxyConfig（配置）

从环境变量读取配置：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `PROXY_TARGET_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 目标 API |
| `DASHSCOPE_API_KEY` | - | API 密钥 |
| `PROXY_RATE_PER_SECOND` | 10 | 每秒请求数 |
| `PROXY_MAX_CONCURRENCY` | 50 | 最大并发数 |
| `PROXY_TIMEOUT` | 60 | 超时时间（秒） |

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/` | GET | 健康检查（别名） |
| `/{path:path}` | ALL | 代理转发 |

## 请求处理流程

1. **接收请求** - 客户端发送请求到 Proxy
2. **速率限制** - `RateLimiter.wait_and_acquire()` 等待令牌
3. **并发控制** - `ConcurrencyLimiter` 获取信号量
4. **构建目标 URL** - 处理路径拼接（避免 `/v1/v1` 重复）
5. **复制请求头** - 过滤 `host`，添加 `Authorization`
6. **转发请求** - 使用 `httpx.AsyncClient` 发送
7. **返回响应** - 过滤问题 headers，返回 JSON 响应

## 关键实现细节

### URL 路径处理

避免 `/v1` 重复拼接：

```python
if base_url.endswith('/v1') or base_url.endswith('/v4'):
    if path.startswith('v1/') or path.startswith('v4/'):
        base_url = base_url.rsplit('/', 1)[0]
    target_url = f"{base_url}/{path}"
```

### 响应 Header 过滤

避免 `Content-Length` 不匹配错误：

```python
skip_headers = ("content-length", "content-encoding", "transfer-encoding")
for key, value in response.headers.items():
    if key.lower() not in skip_headers:
        response_headers[key] = value
```

## 文件结构

```
services/api_proxy/
├── __init__.py
└── server.py      # 主服务文件（包含所有组件）
```

## 与原 Flow_RL_RIGHT 的对比

| 原实现 | 新实现 |
|--------|--------|
| Flask 同步 | FastAPI 异步 |
| 多 API 池 + Round-Robin | 单 API 简化版 |
| 线程锁 | asyncio 锁 |
| 模型参数注入 | 透传请求 |
| tqdm 进度条 | 简洁日志 |

新实现更轻量，适合单 API 场景。如需多 API 池支持，可参考原实现扩展。
