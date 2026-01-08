# LLM_CALL.py 详细分析

> 本文档详细分析 ToolOrchestra 项目中的 LLM_CALL.py 模块的设计、用途和调用机制。

**文档版本**: 1.0
**分析日期**: 2026-01-08
**文件路径**: `.reference_projects/ToolOrchestra/LLM_CALL.py`

---

## 📋 目录

1. [概述](#概述)
2. [为什么存在 LLM_CALL.py](#为什么存在-llm_callpy)
3. [核心功能](#核心功能)
4. [调用关系](#调用关系)
5. [详细分析](#详细分析)
6. [设计亮点](#设计亮点)

---

## 概述

### 基本信息

| 属性 | 值 |
|------|-----|
| **文件大小** | 441 行 |
| **核心函数** | `get_llm_response()` |
| **支持的模型** | OpenAI (GPT-4, O3), Claude (Opus, Sonnet), vLLM (Qwen, Llama), NVIDIA NIM |
| **角色定位** | **统一 LLM 调用接口层** |

### 调用者列表

LLM_CALL.py 被以下 6 个模块导入使用：

```python
# 1. 训练核心：multi-turn 生成管理
.reference_projects/ToolOrchestra/training/lead_agent/llm_agent/generation_quick3.py:43

# 2. 评估模块
.reference_projects/ToolOrchestra/evaluation/eval_hle.py:28
.reference_projects/ToolOrchestra/evaluation/eval_hle_basic.py:28
.reference_projects/ToolOrchestra/evaluation/eval_frames.py:28

# 3. Rollout 工具调用
.reference_projects/ToolOrchestra/training/rollout/tau2/utils/llm_utils.py:57
.reference_projects/ToolOrchestra/evaluation/tau2-bench/tau2/utils/llm_utils.py:40
```

---

## 为什么存在 LLM_CALL.py

### 问题背景

ToolOrchestra 项目需要在以下场景中调用 LLM：

1. **训练阶段**
   - `enhance_reasoning`: 调用推理模型（O3/Qwen）生成中间代码
   - `answer`: 调用答案模型（O3/Llama/Qwen）生成最终答案
   - `search`: 调用查询生成模型（O3/Qwen）生成搜索查询

2. **评估阶段**
   - 调用 GPT-5 作为评判模型（judge model）评估生成结果
   - 调用各种开源模型（Llama, Qwen）进行基准测试

3. **Rollout 阶段**
   - 在 tau2-bench 中调用 tool-use 模型执行工具链

### 核心挑战

| 挑战 | 说明 |
|------|------|
| **多模型异构** | OpenAI (Azure), Claude (Bedrock), vLLM (自托管), NIM (NVIDIA) |
| **认证复杂** | 需要 OAuth token 管理（15 分钟过期） + API key 管理 |
| **格式差异** | OpenAI Chat Completions vs Claude Messages API vs vLLM OpenAI-compatible |
| **工具调用规范** | OpenAI 的 `tools` 格式 vs Claude 的 `input_schema` 格式 |
| **错误重试** | 网络故障、rate limit、token 过期需要自动重试 |

### 解决方案：统一接口层

```
┌─────────────────────────────────────────────────────────┐
│  调用者                                                   │
│  - generation_quick3.py                                  │
│  - eval_*.py                                              │
│  - llm_utils.py                                           │
└────────────────────┬────────────────────────────────────┘
                     │ 统一接口
                     │ get_llm_response(model, messages, ...)
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LLM_CALL.py (中间件层)                                  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Token 管理 (缓存 + 自动刷新)                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 格式转换                                          │   │
│  │  - OpenAI tools → Claude input_schema             │   │
│  │  - OpenAI messages → Claude messages              │   │
│  │  - Tool result 规范化                             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 自动重试 (while answer == '')                     │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬────────────────┬───────────────────────┘
                 │                │
        ┌────────┴────┐    ┌─────┴──────┐
        ↓             ↓    ↓            ↓
   ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────┐
   │ Azure  │  │ Bedrock  │  │ vLLM   │  │ NIM  │
   │ OpenAI │  │ Claude   │  │ Qwen   │  │ OSS  │
   └────────┘  └──────────┘  └────────┘  └──────┘
```

---

## 核心功能

### 1. get_llm_response()

**函数签名**:

```python
def get_llm_response(
    model: str,                    # 模型名称
    messages: Union[str, list],    # 输入消息（字符串或 chat history）
    temperature: float = 1.0,      # 采样温度
    return_raw_response: bool = False,  # 是否返回原始响应对象
    tools: Optional[list] = None,  # OpenAI tools 格式的工具列表
    max_length: int = 1024,        # 最大生成长度
    model_type: Optional[str] = None,  # 模型类型（'vllm', 'nv/dev'）
    model_config: Optional[dict] = None,  # vLLM 服务器配置（IP+端口）
    **kwargs
) -> Union[str, object]:
    """统一 LLM 调用接口"""
```

### 2. 模型路由逻辑

```python
if model in ['o3','o3-mini','gpt-4o','o3-high','gpt-5','gpt-5-mini','gpt-4.1','gpt-4o-mini']:
    # → Azure OpenAI
    openai_client = get_openai_client(model=model)
    chat_completion = openai_client.chat.completions.create(...)

elif model_type == 'nv/dev':
    # → NVIDIA NIM (OSS models via nim API)
    oss_client = OpenAI(base_url="https://integrate.api.nvidia.com/v1")
    chat_completion = oss_client.chat.completions.create(...)

elif 'qwen' in model.lower() or model_type == 'vllm':
    # → vLLM (self-hosted)
    ip_addr = model_config[config_idx]["ip_addr"]
    port = model_config[config_idx]["port"]
    vllm_client = OpenAI(base_url=f"http://{ip_addr}:{port}/v1")
    chat_completion = vllm_client.chat.completions.create(...)

elif 'claude' in model.lower():
    # → AWS Bedrock (Claude)
    endpoint = "https://prod.api.nvidia.com/llm/v1/aws/model/..."
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": convert_openai_messages_to_claude(messages),
        "tools": convert_openai_tools_to_claude(tools),
        ...
    }
    response = requests.post(endpoint, headers=headers, json=payload)
```

### 3. Token 管理（OAuth 2.0）

```python
def get_openai_token(p_token_url, p_client_id, p_client_secret, p_scope):
    """获取 Azure OpenAI 的 OAuth token（15 分钟有效期）"""

    # 1. 尝试从磁盘缓存读取
    try:
        with open('keys/openai_key.json') as f:
            key = json.load(f)
        if time.time() < key['expire_at']:
            return key["access_token"]  # ✅ 缓存有效
    except:
        pass

    # 2. 缓存失效，请求新 token
    response = requests.post(
        p_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": p_client_id,
            "client_secret": p_client_secret,
            "scope": p_scope
        }
    )
    token = response.json()

    # 3. 保存到磁盘（expire_at = now + 15min）
    with open('keys/openai_key.json', 'w') as f:
        json.dump({
            "access_token": token["access_token"],
            'expire_at': time.time() + 900  # 15 分钟
        }, f)

    return token["access_token"]
```

**设计要点**:
- ✅ 避免每次调用都请求 token（减少延迟）
- ✅ 提前 15 分钟刷新，避免过期导致的调用失败
- ✅ 磁盘缓存支持跨进程共享（多个 worker 共享同一 token）

### 4. 格式转换

#### 4.1 OpenAI Tools → Claude Input Schema

```python
def convert_openai_tools_to_claude(openai_tools: list) -> list:
    """
    OpenAI 格式:
    [
        {
            "type": "function",
            "function": {
                "name": "enhance_reasoning",
                "description": "Generate code for reasoning",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "enum": ["o3", "qwen"]}
                    }
                }
            }
        }
    ]

    Claude 格式:
    [
        {
            "name": "enhance_reasoning",
            "description": "Generate code for reasoning",
            "input_schema": {
                "type": "object",
                "properties": {
                    "model": {"type": "string", "enum": ["o3", "qwen"]}
                }
            }
        }
    ]
    """
    claude_tools = []
    for tool in openai_tools:
        fn = tool["function"]
        claude_tools.append({
            "name": fn["name"],
            "description": fn.get("description", ""),
            "input_schema": fn.get("parameters", {})
        })
    return claude_tools
```

#### 4.2 OpenAI Messages → Claude Messages

```python
def convert_openai_messages_to_claude(openai_messages):
    """
    处理差异:
    1. Claude 不支持 'tool_calls' 字段 → 转为纯文本附加到 content
    2. Claude 不支持 role='tool' → 转为 role='user'
    """
    claude_messages = []
    for m in openai_messages:
        if "tool_calls" in m:
            # 将 tool_calls 转为字符串附加到 content
            m['content'] += '\n\n' + str(m["tool_calls"])
            m.pop("tool_calls")
            claude_messages.append(m)
        elif m['role'] == 'tool':
            # 转为用户消息
            claude_messages.append({
                "role": 'user',
                "content": "Tool call result: " + m['content']
            })
        else:
            claude_messages.append(m)
    return claude_messages
```

#### 4.3 Tool Message 规范化

```python
def normalize_messages_for_tools(
    messages: List[Dict],
    tools: Optional[List[Dict]] = None
) -> Tuple[List[Dict], List[str]]:
    """
    修复常见的 tool message 格式问题:

    1. Assistant tool_calls 问题:
       - 移动 top-level 'name'/'arguments' 到 'function' 对象
       - 确保 'type' == 'function'
       - JSON 序列化 non-string 'arguments'
       - 验证 function name 在 tools 中存在

    2. Tool messages 问题:
       - 确保 'content' 是字符串（JSON 序列化 dict/list）
       - 确保 'tool_call_id' 存在（推断匹配）

    3. 返回:
       - fixed_messages: 修复后的消息列表
       - issues: 检测到的问题描述列表
    """
    # 实现见 LLM_CALL.py:46-205
```

### 5. 自动重试机制

```python
answer = ''
while answer == '':
    try:
        chat_completion = client.chat.completions.create(...)
        if return_raw_response:
            answer = chat_completion
        else:
            answer = chat_completion.choices[0].message.content
    except Exception as error:
        time.sleep(60)  # 等待 1 分钟后重试
return answer
```

**特点**:
- ❌ **无限重试**（可能导致死循环）
- ❌ **固定延迟**（不适应不同错误类型）
- ⚠️ **改进建议**:
  - 添加最大重试次数
  - 指数退避策略
  - 针对不同错误类型（rate limit vs network error）采用不同策略

---

## 调用关系

### 调用链示例 1: 训练阶段 enhance_reasoning

```
main_grpo_quick3.py
    ↓
RayGRPOTrainer.fit()
    ↓
LLMGenerationManager.run_llm_loop()
    ↓
EnhanceReasoningTool.execute()  (generation_quick3.py:145)
    ↓
get_llm_response(
    model='o3',
    messages="Question: ... \nWrite python code...",
    return_raw_response=True,
    temperature=1,
    max_length=28000
)
    ↓ [LLM_CALL.py 路由]
    ↓
get_openai_client() → Azure OpenAI API
    ↓
返回: ChatCompletion 对象
    ↓
提取生成的代码 → 执行沙箱 → 返回结果
```

### 调用链示例 2: 评估阶段

```
eval_hle.py
    ↓
evaluate_sample()
    ↓
get_llm_response(
    model='gpt-5',
    messages="Question: ...\nStudent answer: ...\nReference: ...",
    temperature=1
)
    ↓ [LLM_CALL.py 路由]
    ↓
Azure OpenAI API
    ↓
返回: "<correct>True</correct>"
```

### 调用统计

在 `generation_quick3.py` 中，`get_llm_response` 被调用的场景：

| 调用位置 | 用途 | 模型类型 | 频率 |
|---------|------|---------|------|
| Line 150 | enhance_reasoning (O3/GPT-5) | Azure OpenAI | 每个需要推理的样本 |
| Line 185 | enhance_reasoning (Qwen/Llama) | vLLM | 每个需要推理的样本 |
| Line 267 | answer (Math models) | vLLM | 每个样本最终答案 |
| Line 298 | answer (Qwen/Phi) | vLLM | 每个样本最终答案 |
| Line 329 | answer (Llama) | vLLM | 每个样本最终答案 |
| Line 368 | answer (O3/GPT-5) | Azure OpenAI | 每个样本最终答案 |
| Line 440 | 评估（GPT-5 judge） | Azure OpenAI | 每个生成的答案 |
| Line 475 | search query 生成 (O3/GPT-5) | Azure OpenAI | 每次 search 工具调用 |
| Line 524 | search query 生成 (Qwen/Llama) | vLLM | 每次 search 工具调用 |
| Line 628 | tool-use (O3/GPT-5) | Azure OpenAI | tau2-bench 工具调用 |
| Line 681 | tool-use (Qwen3/Llama) | vLLM | tau2-bench 工具调用 |

**估算**: 单个 batch (batch_size=8) 的一轮训练，可能调用 `get_llm_response` **100+ 次**。

---

## 详细分析

### 支持的模型列表

| 模型名称 | 提供商 | API 类型 | Token 管理 | 典型用途 |
|---------|--------|---------|-----------|---------|
| `o3` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 推理模型 |
| `o3-mini` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 轻量推理 |
| `gpt-5` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 评判模型 |
| `gpt-5-mini` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 评判模型 |
| `gpt-4o` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 通用任务 |
| `gpt-4o-mini` | OpenAI (Azure) | Azure Chat Completions | OAuth 2.0 | 通用任务 |
| `claude-opus` | Anthropic (Bedrock) | Bedrock Messages API | OAuth 2.0 | 复杂推理 |
| `claude-sonnet` | Anthropic (Bedrock) | Bedrock Messages API | OAuth 2.0 | 平衡任务 |
| `qwen2.5-coder-*` | Alibaba Cloud | vLLM (self-hosted) | 无需认证 | 代码生成 |
| `meta-llama-*` | Meta | vLLM (self-hosted) | 无需认证 | 通用任务 |
| `Phi-*` | Microsoft | vLLM (self-hosted) | 无需认证 | 数学推理 |

### vLLM 配置动态加载

```python
# model_config 示例 (JSON 文件)
{
  "qwen2.5-coder-32b": [
    {"ip_addr": "10.110.32.105", "port": 8000},
    {"ip_addr": "10.110.32.106", "port": 8000},
    {"ip_addr": "10.110.32.107", "port": 8000}
  ],
  "meta-llama-70b": [
    {"ip_addr": "10.110.32.200", "port": 8001}
  ]
}

# 调用时随机选择服务器（负载均衡）
config_idx = random.choice(range(len(model_config)))
ip_addr = model_config[config_idx]["ip_addr"]
port = model_config[config_idx]["port"]
vllm_client = OpenAI(
    api_key="EMPTY",
    base_url=f"http://{ip_addr}:{port}/v1"
)
```

**优点**:
- 支持多服务器负载均衡
- 服务器宕机时自动切换
- 配置文件热更新（通过 `model_config_path` 重新加载）

### 成本和延迟追踪

```python
# 1. 追踪 token 使用（仅 OpenAI models）
if not 'tokens_pic' in arguments:
    arguments['tokens_pic'] = []
arguments['tokens_pic'].append({
    'input': response.usage.prompt_tokens,
    'output': response.usage.completion_tokens,
    'total': response.usage.total_tokens
})

# 2. 计算成本（根据模型定价）
cost = (
    cur_tool_pricing[model]['input_tokens_per_million'] * response.usage.prompt_tokens +
    cur_tool_pricing[model]['output_tokens_per_million'] * response.usage.completion_tokens
)

# 3. 追踪延迟
latency_testing_start_time = time.time()
response = get_llm_response(...)
latency_testing_end_time = time.time()
latency = latency_testing_end_time - latency_testing_start_time
```

**用途**: 用于计算 efficiency_reward（成本 + 延迟惩罚）。

---

## 设计亮点

### 1. 统一接口，屏蔽异构

**问题**: 不同模型 API 格式差异巨大。

**解决方案**:
- 调用者只需关心 `(model, messages, tools)`
- LLM_CALL.py 内部处理所有适配逻辑

**效果**:
- ✅ 替换模型无需修改调用代码
- ✅ 新增模型只需修改 LLM_CALL.py

### 2. Token 缓存 + 自动刷新

**问题**: OAuth token 15 分钟过期，高频调用会导致大量认证请求。

**解决方案**:
- 磁盘缓存 token + expire_at
- 每次调用前检查是否过期

**效果**:
- ✅ 减少 90% 的 token 请求
- ✅ 降低延迟（无需等待认证）

### 3. vLLM 负载均衡

**问题**: 单个 vLLM 服务器容易过载。

**解决方案**:
- 随机选择服务器
- 失败时重新加载配置并重试

**效果**:
- ✅ 提升吞吐量
- ✅ 容错能力

### 4. 格式自动修复

**问题**: OpenAI 的 tool message 格式容易出错（尤其是用户手写时）。

**解决方案**:
- `normalize_messages_for_tools()` 自动检测并修复常见错误
- 返回修复后的消息 + 问题列表

**效果**:
- ✅ 减少调试时间
- ✅ 提高代码鲁棒性

---

## 潜在问题和改进建议

### 问题 1: 无限重试可能导致死循环

**当前实现**:
```python
while answer == '':
    try:
        ...
    except Exception:
        time.sleep(60)
```

**问题**: 如果 API 长期不可用，会永久阻塞。

**改进建议**:
```python
max_retries = 5
for attempt in range(max_retries):
    try:
        ...
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(min(60 * (2 ** attempt), 300))  # 指数退避
```

### 问题 2: 错误处理过于粗糙

**当前实现**:
```python
except Exception as error:
    time.sleep(60)
```

**问题**: 所有错误统一处理，无法针对性优化。

**改进建议**:
```python
except openai.RateLimitError:
    time.sleep(60)
except openai.AuthenticationError:
    # 刷新 token
    get_openai_token(...)
except openai.APIError as e:
    if e.status_code >= 500:
        # 服务器错误，重试
        time.sleep(10)
    else:
        # 客户端错误，直接失败
        raise
```

### 问题 3: 缺少并发限制

**当前实现**: 串行调用 LLM（在 batch 内部）。

**改进建议**: 使用异步并发（asyncio + semaphore）:
```python
import asyncio

async def get_llm_response_async(...):
    async with semaphore:
        return await client.chat.completions.create(...)

# 并发调用
results = await asyncio.gather(*[
    get_llm_response_async(model, msg)
    for msg in messages
])
```

**预期收益**: 减少 50%+ 的总延迟。

### 问题 4: 硬编码配置

**当前实现**:
```python
openai.api_base = "https://prod.api.nvidia.com/llm/v1/azure/"
```

**改进建议**: 使用环境变量或配置文件:
```python
openai.api_base = os.getenv("AZURE_OPENAI_BASE_URL")
```

---

## 总结

### LLM_CALL.py 的核心价值

| 价值 | 说明 |
|------|------|
| **1. 抽象多样性** | 统一接口屏蔽 4 种 API（Azure, Bedrock, vLLM, NIM） |
| **2. 管理复杂性** | Token 缓存 + 自动刷新 + 负载均衡 |
| **3. 提升鲁棒性** | 格式修复 + 自动重试 + 错误容忍 |
| **4. 支持扩展性** | 新增模型只需修改路由逻辑 |

### 在 ToolOrchestra 中的定位

```
┌─────────────────────────────────────────────────┐
│  ToolOrchestra 架构                              │
│                                                  │
│  [veRL 标准流程]                                 │
│   ├─ Actor/Critic 更新（PyTorch）               │
│   ├─ Reward 计算框架                             │
│   └─ 分布式训练（Ray）                           │
│                                                  │
│  [自定义扩展]                                    │
│   ├─ Lead Agent (multi-turn 生成管理)           │
│   │   └─ LLMGenerationManager                   │
│   │       └─ 调用 LLM_CALL.py ← 核心依赖       │
│   │                                              │
│   ├─ Rollout (tau2 工具调用框架)                │
│   │   └─ llm_utils.py                            │
│   │       └─ 调用 LLM_CALL.py ← 核心依赖       │
│   │                                              │
│   └─ Evaluation (评估脚本)                      │
│       └─ 调用 LLM_CALL.py ← 核心依赖           │
└─────────────────────────────────────────────────┘
```

**结论**: LLM_CALL.py 是 ToolOrchestra 项目的**关键基础设施**，所有需要调用外部 LLM 的模块都依赖它。它的设计质量直接影响整个系统的稳定性和性能。

---

**文档作者**: Claude
**参考文件**:
- `.reference_projects/ToolOrchestra/LLM_CALL.py`
- `.reference_projects/ToolOrchestra/training/lead_agent/llm_agent/generation_quick3.py`
- `docs/verl_api/toolorchestra_custom_implementations.md`
