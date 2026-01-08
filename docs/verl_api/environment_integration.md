# verl 环境对接完整指南

本文档详细说明如何定义自定义环境并让其与 verl 框架对接，基于 ToolOrchestra 项目的实践经验。

---

## 📋 目录

1. [核心概念](#1-核心概念)
2. [verl 接口规范](#2-verl-接口规范)
3. [环境定义规范](#3-环境定义规范)
4. [两种对接模式](#4-两种对接模式)
5. [关键文件清单](#5-关键文件清单)
6. [完整实现步骤](#6-完整实现步骤)
7. [数据流转详解](#7-数据流转详解)
8. [调试与测试](#8-调试与测试)
9. [常见问题](#9-常见问题)
10. [完整示例](#10-完整示例)

---

## 1. 核心概念

### 1.1 verl 的角色定位

**重要理解**：verl **不是环境**，它是：

| 组件 | 职责 |
|------|------|
| **RL 训练引擎** | PPO/GRPO 算法实现、梯度更新 |
| **模型推理管理器** | 调用 actor 模型生成 responses |
| **数据流转协调器** | DataProto 格式转换、分布式通信 |
| **资源调度器** | Ray 集群管理、GPU 分配 |

**你的环境**负责：
- 定义 **状态空间** 和 **动作空间**
- 提供 **工具/API** 供模型调用
- 执行动作并返回 **观察** 和 **奖励**
- 判断任务是否 **完成**

### 1.2 数据流向

```
┌─────────────────────────────────────────────────────────────┐
│ 你的环境 (Environment)                                      │
│ ├─ 状态管理                                                 │
│ ├─ 工具执行 (Tools)                                        │
│ ├─ 奖励计算 (Evaluator)                                    │
│ └─ 终止判断                                                 │
└───────────┬──────────────────────────────────────────────────┘
            │
            │ Tool Results / Rewards
            ▼
┌─────────────────────────────────────────────────────────────┐
│ 对接层 (Generation Manager)                                │
│ ├─ 准备 Prompt                                             │
│ ├─ 调用 verl                                               │
│ ├─ 解析 Tool Calls                                         │
│ ├─ 执行环境操作                                            │
│ └─ 构造 DataProto                                          │
└───────────┬──────────────────────────────────────────────────┘
            │
            │ DataProto
            ▼
┌─────────────────────────────────────────────────────────────┐
│ verl 框架                                                   │
│ ├─ actor_rollout_wg.generate_sequences()                   │
│ ├─ 策略梯度计算                                            │
│ └─ 模型权重更新                                            │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 关键术语

| 术语 | 含义 | 示例 |
|------|------|------|
| **Environment** | 任务环境，管理状态和执行动作 | AirlineEnvironment, BankEnvironment |
| **Tool** | 模型可调用的函数/API | `search_flight()`, `book_reservation()` |
| **Orchestrator** | 多轮交互的主控循环 | tau2 的 Orchestrator 类 |
| **DataProto** | verl 的标准数据格式 | 包含 input_ids, responses, reward |
| **Rollout** | 执行一次完整任务的轨迹 | 从初始状态到终止的完整对话 |
| **Generation Manager** | 对接层，连接环境和 verl | LLMGenerationManager |

---

## 2. verl 接口规范

### 2.1 核心接口：BaseRollout

**文件位置**：`.reference_projects/ToolOrchestra/training/verl/workers/rollout/base.py`

```python
from abc import ABC, abstractmethod
from verl import DataProto

class BaseRollout(ABC):
    """verl 期望的 Rollout 接口"""

    @abstractmethod
    def generate_sequences(self, prompts: DataProto) -> DataProto:
        """
        生成序列的核心方法

        输入：
            prompts (DataProto):
                - batch['input_ids']: [B, L_prompt] - 输入 token IDs
                - batch['attention_mask']: [B, L_prompt] - 注意力掩码
                - batch['position_ids']: [B, L_prompt] - 位置编码

        输出：
            DataProto:
                - batch['input_ids']: [B, L_total] - prompt + response
                - batch['attention_mask']: [B, L_total]
                - batch['responses']: [B, L_response] - 仅响应部分
                - non_tensor_batch['reward']: np.array([B]) - 奖励值
        """
        pass
```

**重要说明**：
- ✅ 你**不需要直接实现** `BaseRollout`
- ✅ verl 已提供 `vLLMRollout`, `SGLangRollout` 等实现
- ✅ 你只需要在**对接层**调用 `actor_rollout_wg.generate_sequences()`

### 2.2 DataProto 数据格式

**文件位置**：`.reference_projects/ToolOrchestra/training/verl/protocol.py`

```python
from dataclasses import dataclass, field
from typing import Dict
import torch
from tensordict import TensorDict
import numpy as np

@dataclass
class DataProto:
    """verl 的标准数据格式"""

    batch: TensorDict = None              # Tensor 数据（在 GPU 上）
    non_tensor_batch: Dict = field(default_factory=dict)  # 非 Tensor 数据（在 CPU 上）
    meta_info: Dict = field(default_factory=dict)         # 元信息

    @classmethod
    def from_dict(cls, tensors: Dict[str, torch.Tensor],
                  non_tensors: Dict = None,
                  meta_info: Dict = None):
        """从字典创建 DataProto"""
        pass
```

#### 2.2.1 必需的 Tensor 字段

| 字段 | 形状 | 数据类型 | 说明 |
|------|------|---------|------|
| `input_ids` | `[B, L]` | `torch.long` | 完整序列的 token IDs（prompt + response） |
| `attention_mask` | `[B, L]` | `torch.long` | 注意力掩码（1=有效，0=padding） |
| `position_ids` | `[B, L]` | `torch.long` | 位置编码 |
| `responses` | `[B, R]` | `torch.long` | 仅响应部分的 token IDs |

#### 2.2.2 必需的非 Tensor 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `reward` | `np.ndarray([B], dtype=float)` | **最重要**，每个样本的奖励值 |
| `index` | `np.ndarray([B], dtype=object)` | 样本索引（用于跟踪） |

#### 2.2.3 创建 DataProto 示例

```python
import torch
import numpy as np
from verl import DataProto

# 准备数据
batch_size = 4
prompt_length = 100
response_length = 50
total_length = prompt_length + response_length

# Tensor 数据
tensors = {
    'input_ids': torch.randint(0, 50000, (batch_size, total_length), dtype=torch.long),
    'attention_mask': torch.ones(batch_size, total_length, dtype=torch.long),
    'position_ids': torch.arange(total_length).unsqueeze(0).repeat(batch_size, 1),
    'responses': torch.randint(0, 50000, (batch_size, response_length), dtype=torch.long),
}

# 非 Tensor 数据
non_tensors = {
    'reward': np.array([0.8, 0.5, 1.0, 0.3], dtype=float),
    'index': np.array(['task_001', 'task_002', 'task_003', 'task_004'], dtype=object),
}

# 创建 DataProto
data = DataProto.from_dict(tensors=tensors, non_tensors=non_tensors)

# 访问数据
print(data.batch['input_ids'].shape)  # torch.Size([4, 150])
print(data.non_tensor_batch['reward'])  # [0.8 0.5 1.0 0.3]
```

---

## 3. 环境定义规范

### 3.1 环境核心组件

一个完整的环境需要包含：

```
your_environment/
├── data_model.py          # Pydantic 数据模型
├── tools.py               # Tool 定义和实现
├── environment.py         # 环境主类
├── evaluator.py           # 奖励计算
└── db.py                  # 数据库/状态管理（可选）
```

### 3.2 Tool 系统设计

#### 3.2.1 Tool 基类（参考 tau2）

**文件位置**：`.reference_projects/ToolOrchestra/evaluation/tau2-bench/tau2/environment/tool.py`

```python
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any
from pydantic import BaseModel

class Tool(ABC):
    """Tool 基类"""

    name: str              # Tool 名称
    description: str       # Tool 描述
    parameters: type[BaseModel]  # 参数的 Pydantic 模型

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """执行 tool"""
        pass

    @property
    def openai_schema(self) -> Dict:
        """生成 OpenAI Function Calling 格式的 schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        # 从 Pydantic 模型自动生成
                    },
                    "required": [...]
                }
            }
        }
```

#### 3.2.2 使用装饰器定义 Tools（推荐）

**文件位置**：`.reference_projects/ToolOrchestra/evaluation/tau2-bench/tau2/environment/toolkit.py`

```python
from enum import Enum
from typing import Callable

TOOL_ATTR = "__tool__"
TOOL_TYPE_ATTR = "__tool_type__"

class ToolType(str, Enum):
    READ = "read"       # 只读操作（查询数据）
    WRITE = "write"     # 写操作（修改状态）
    THINK = "think"     # 推理操作
    GENERIC = "generic" # 通用操作

def is_tool(tool_type: ToolType = ToolType.READ):
    """装饰器：标记函数为 tool"""
    def decorator(func: Callable):
        setattr(func, TOOL_ATTR, True)
        setattr(func, TOOL_TYPE_ATTR, tool_type)
        return func
    return decorator


class ToolKitType(type):
    """元类：自动发现标记为 @is_tool 的方法"""

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        # 扫描所有方法
        func_tools = {}
        for method_name, method in attrs.items():
            if hasattr(method, TOOL_ATTR):
                func_tools[method_name] = method

        cls._func_tools = func_tools


class ToolKitBase(metaclass=ToolKitType):
    """Tool 集合基类"""

    def __init__(self, db=None):
        self.db = db

    @property
    def tools(self) -> Dict[str, Callable]:
        """获取所有 tools"""
        return {name: getattr(self, name) for name in self._func_tools.keys()}

    def use_tool(self, tool_name: str, **kwargs):
        """执行指定 tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return self.tools[tool_name](**kwargs)
```

#### 3.2.3 具体环境的 Tools 实现

```python
from pydantic import BaseModel
from typing import List

# 1. 定义参数模型
class FlightSearchParams(BaseModel):
    origin: str
    destination: str
    date: str

class DirectFlight(BaseModel):
    flight_number: str
    origin: str
    destination: str
    price: float
    departure_time: str

# 2. 定义 ToolKit
class AirlineTools(ToolKitBase):
    """航空预订系统的所有 tools"""

    @is_tool(ToolType.READ)
    def search_direct_flight(
        self,
        origin: str,
        destination: str,
        date: str
    ) -> List[DirectFlight]:
        """
        搜索直飞航班

        Args:
            origin: 出发地 IATA 代码（如 'SFO'）
            destination: 目的地 IATA 代码（如 'LAX'）
            date: 日期（YYYY-MM-DD 格式）

        Returns:
            直飞航班列表
        """
        results = []
        for flight in self.db.flights.values():
            if (flight.origin == origin and
                flight.destination == destination and
                flight.date == date):
                results.append(DirectFlight(
                    flight_number=flight.flight_number,
                    origin=flight.origin,
                    destination=flight.destination,
                    price=flight.price,
                    departure_time=flight.departure_time
                ))
        return results

    @is_tool(ToolType.WRITE)
    def book_reservation(
        self,
        user_id: str,
        flight_number: str,
        passengers: List[dict],
        payment_method: dict
    ) -> dict:
        """
        预订航班

        Args:
            user_id: 用户 ID
            flight_number: 航班号
            passengers: 乘客信息列表
            payment_method: 支付方式

        Returns:
            预订确认信息
        """
        # 验证用户
        if user_id not in self.db.users:
            raise ValueError(f"User {user_id} not found")

        # 创建预订
        reservation_id = self._generate_reservation_id()
        reservation = {
            'id': reservation_id,
            'user_id': user_id,
            'flight_number': flight_number,
            'passengers': passengers,
            'status': 'confirmed'
        }

        # 更新数据库
        self.db.reservations[reservation_id] = reservation

        return reservation
```

### 3.3 Environment 类设计

```python
from typing import Dict, Any, Optional

class Environment:
    """环境主类"""

    def __init__(self, domain: str, db=None):
        """
        初始化环境

        Args:
            domain: 领域名称（如 'airline', 'bank'）
            db: 数据库实例
        """
        self.domain = domain
        self.db = db
        self.toolkit = self._create_toolkit()

    def _create_toolkit(self) -> ToolKitBase:
        """创建 tool 集合"""
        if self.domain == 'airline':
            return AirlineTools(db=self.db)
        elif self.domain == 'bank':
            return BankTools(db=self.db)
        else:
            raise ValueError(f"Unknown domain: {self.domain}")

    def reset(self, initial_state: Optional[Dict] = None):
        """
        重置环境到初始状态

        Args:
            initial_state: 初始状态（可选）
        """
        self.db.reset()
        if initial_state:
            self._apply_initial_state(initial_state)

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        执行 tool

        Args:
            tool_name: Tool 名称
            **kwargs: Tool 参数

        Returns:
            Tool 执行结果
        """
        return self.toolkit.use_tool(tool_name, **kwargs)

    def get_tools(self) -> List[Dict]:
        """
        获取所有 tools 的 OpenAI schema

        Returns:
            Tool schemas 列表
        """
        tools = []
        for name, tool_func in self.toolkit.tools.items():
            tools.append(as_tool(tool_func).openai_schema)
        return tools

    def get_state(self) -> Dict:
        """获取当前环境状态"""
        return {
            'db_state': self.db.serialize(),
            'domain': self.domain
        }
```

### 3.4 Evaluator 设计

```python
from typing import List
from dataclasses import dataclass

@dataclass
class RewardInfo:
    """奖励信息"""
    reward: float              # 总奖励 [0, 1]
    breakdown: Dict[str, float]  # 分项奖励
    details: Dict[str, Any]    # 详细信息

class Evaluator:
    """评估器基类"""

    def __init__(self, environment: Environment):
        self.environment = environment

    def evaluate(
        self,
        task: Dict,
        messages: List[Dict],
        final_state: Dict
    ) -> RewardInfo:
        """
        评估任务完成情况

        Args:
            task: 任务定义
            messages: 完整对话历史
            final_state: 最终环境状态

        Returns:
            RewardInfo 对象
        """
        # 示例：多维度评估
        outcome_reward = self._evaluate_outcome(task, final_state)
        efficiency_reward = self._evaluate_efficiency(messages)
        communication_reward = self._evaluate_communication(messages)

        total_reward = (
            0.6 * outcome_reward +
            0.2 * efficiency_reward +
            0.2 * communication_reward
        )

        return RewardInfo(
            reward=total_reward,
            breakdown={
                'outcome': outcome_reward,
                'efficiency': efficiency_reward,
                'communication': communication_reward
            },
            details={
                'num_turns': len(messages),
                'tools_used': self._count_tools_used(messages)
            }
        )

    def _evaluate_outcome(self, task: Dict, final_state: Dict) -> float:
        """评估任务完成度"""
        # 检查最终状态是否满足任务要求
        # 例如：检查预订是否成功、数据是否正确等
        pass

    def _evaluate_efficiency(self, messages: List[Dict]) -> float:
        """评估效率（轮次、成本等）"""
        num_turns = len(messages)
        # 轮次越少越好
        return max(0, 1 - (num_turns - 5) / 20)

    def _evaluate_communication(self, messages: List[Dict]) -> float:
        """评估沟通质量"""
        # 检查是否礼貌、清晰等
        pass
```

---

## 4. 两种对接模式

### 4.1 模式对比

| 特性 | 直接集成模式 | 进程间通信模式 |
|------|-------------|---------------|
| **复杂度** | 简单 | 复杂 |
| **延迟** | 低 | 高（文件 I/O） |
| **隔离性** | 低 | 高 |
| **适用场景** | 简单任务、外部 API | 复杂多轮交互、需要隔离 |
| **实现难度** | ⭐⭐ | ⭐⭐⭐⭐ |
| **示例** | ToolOrchestra 的 QA 任务 | ToolOrchestra 的 func_call 任务 |

### 4.2 模式一：直接集成模式

**适用场景**：
- ✅ 单轮或少量轮次的任务
- ✅ 调用外部 API（如 GPT-5, Search API）
- ✅ 简单的环境状态
- ✅ 不需要复杂的对话管理

**架构图**：

```
┌───────────────────────────────────────────────────────────┐
│ Generation Manager                                        │
│                                                           │
│ FOR turn in [1..max_turns]:                              │
│   ├─ 准备 prompt                                         │
│   ├─ gen_output = actor_rollout_wg.generate_sequences() │
│   ├─ 解析 tool_calls                                     │
│   ├─ FOR each tool_call:                                 │
│   │   ├─ if tool == 'enhance_reasoning':                │
│   │   │   └─ result = call_gpt5(...)                    │
│   │   ├─ if tool == 'search':                           │
│   │   │   └─ result = call_tavily_api(...)              │
│   │   └─ if tool == 'answer':                           │
│   │       └─ result = call_answer_model(...)            │
│   ├─ 更新 prompt（添加 tool results）                    │
│   └─ 判断是否完成                                        │
│                                                           │
│ 计算 reward                                               │
│ 返回 DataProto                                            │
└───────────────────────────────────────────────────────────┘
```

**实现示例**：

```python
from verl import DataProto
import torch

class DirectIntegrationManager:
    """直接集成模式的 Generation Manager"""

    def __init__(self, tokenizer, actor_rollout_wg, config):
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.config = config

    def run_task(self, task_batch: Dict) -> DataProto:
        """
        执行任务批次

        Args:
            task_batch: {
                'problem': List[str],
                'tools': List[List[Dict]],
                'answer': List[str],
                ...
            }

        Returns:
            DataProto 包含完整轨迹和 reward
        """
        batch_size = len(task_batch['problem'])

        # 初始化
        active_mask = torch.ones(batch_size, dtype=torch.bool)
        retrieved_docs = [[] for _ in range(batch_size)]
        trajectories = [[] for _ in range(batch_size)]

        for turn in range(self.config.max_turns):
            # 1. 准备 prompt
            prompts = self._prepare_prompts(
                task_batch,
                retrieved_docs,
                active_mask
            )

            # 2. 调用 verl 生成
            prompt_ids = self._tokenize(prompts)
            active_batch = DataProto.from_dict({
                'input_ids': prompt_ids[active_mask],
                'attention_mask': self._create_attention_mask(prompt_ids[active_mask]),
                'position_ids': self._create_position_ids(prompt_ids[active_mask])
            })

            gen_output = self.actor_rollout_wg.generate_sequences(active_batch)

            # 3. 解析输出
            responses = self.tokenizer.batch_decode(gen_output.batch['responses'])
            tool_calls = self._parse_tool_calls(responses)

            # 4. 执行 tools
            for idx, (tool_call, active) in enumerate(zip(tool_calls, active_mask)):
                if not active:
                    continue

                if tool_call['name'] == 'search':
                    # 调用搜索 API
                    docs = self._call_search_api(
                        task_batch['problem'][idx],
                        topk=10
                    )
                    retrieved_docs[idx].extend(docs)

                elif tool_call['name'] == 'answer':
                    # 生成最终答案
                    answer = tool_call['arguments']['answer']
                    trajectories[idx].append({
                        'turn': turn,
                        'action': 'answer',
                        'content': answer
                    })
                    active_mask[idx] = False

            # 5. 检查是否所有任务完成
            if not active_mask.any():
                break

        # 6. 计算 reward
        rewards = self._compute_rewards(task_batch, trajectories)

        # 7. 构造最终 DataProto
        final_data = self._build_final_dataproto(
            task_batch,
            trajectories,
            rewards
        )

        return final_data

    def _call_search_api(self, query: str, topk: int) -> List[str]:
        """调用搜索 API"""
        import requests
        response = requests.post(
            'https://api.tavily.com/search',
            json={'query': query, 'max_results': topk},
            headers={'Authorization': f'Bearer {os.getenv("TAVILY_KEY")}'}
        )
        return response.json()['results']

    def _compute_rewards(self, task_batch: Dict, trajectories: List) -> np.ndarray:
        """计算奖励"""
        rewards = []
        for idx in range(len(task_batch['problem'])):
            # 提取模型答案
            final_answer = trajectories[idx][-1]['content'] if trajectories[idx] else ""
            ground_truth = task_batch['answer'][idx]

            # 计算正确性
            correctness = self._check_answer(final_answer, ground_truth)

            # 计算效率惩罚
            num_turns = len(trajectories[idx])
            efficiency_penalty = max(0, (num_turns - 3) * 0.1)

            reward = correctness - efficiency_penalty
            rewards.append(max(0, min(1, reward)))

        return np.array(rewards, dtype=float)
```

### 4.3 模式二：进程间通信模式

**适用场景**：
- ✅ 复杂的多轮交互（10+ 轮）
- ✅ 需要独立的环境状态管理
- ✅ 需要完整的对话 Orchestrator
- ✅ 需要环境隔离（避免相互干扰）

**架构图**：

```
┌─────────────────────────────────────────────────────────┐
│ verl 训练进程                                           │
│                                                         │
│ Generation Manager:                                     │
│   ├─ 启动 tau2 子进程                                  │
│   │  └─ subprocess.Popen(['python', 'tau2/cli.py'])   │
│   │                                                     │
│   └─ 主循环:                                           │
│       ├─ 等待 input_{i}.json 出现                     │
│       ├─ 读取 tau2 的请求                              │
│       │  {messages: [...], tools: [...]}              │
│       ├─ 调用 verl 模型                                │
│       │  gen_output = actor_rollout_wg.generate()     │
│       ├─ 写 output_{i}.json                           │
│       │  {content: "...", tool_calls: [...]}          │
│       └─ 等待下一个 input 或 done 文件                 │
└─────────────┬───────────────────────────────────────────┘
              │
              │ 文件系统 IPC
              │ transfer_dir/
              │ ├─ input_0.json  ← tau2 写
              │ ├─ output_0.json ← verl 写
              │ ├─ input_1.json
              │ ├─ output_1.json
              │ └─ done         ← tau2 写（任务完成）
              │
┌─────────────┴───────────────────────────────────────────┐
│ tau2 环境子进程                                         │
│                                                         │
│ Orchestrator:                                           │
│   ├─ 初始化 Environment                                │
│   │  ├─ 加载数据库                                     │
│   │  └─ 创建 ToolKit                                   │
│   │                                                     │
│   └─ 主循环:                                           │
│       ├─ 构造 messages（包含对话历史）                 │
│       ├─ 写 input_{i}.json                            │
│       ├─ 等待 output_{i}.json                         │
│       ├─ 读取模型响应                                  │
│       ├─ 解析 tool_calls                               │
│       ├─ 执行 Environment.use_tool()                   │
│       ├─ 构造 ToolMessage                              │
│       └─ 判断是否完成                                  │
│                                                         │
│   完成后:                                               │
│   ├─ Evaluator.evaluate()                              │
│   └─ 写 done 文件（包含 reward）                       │
└─────────────────────────────────────────────────────────┘
```

**IPC 协议定义**：

**input_{i}.json** (tau2 → verl)：
```json
{
  "messages": [
    {"role": "system", "content": "You are a customer service agent..."},
    {"role": "user", "content": "I want to book a flight"},
    {"role": "assistant", "tool_calls": [{"name": "search_flight", ...}]},
    {"role": "tool", "content": "[{flight_number: 'AA123', ...}]"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "book_reservation",
        "description": "Book a flight reservation",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string"},
            "flight_number": {"type": "string"}
          },
          "required": ["user_id", "flight_number"]
        }
      }
    }
  ],
  "original_tools": [...],  # 原始 tools（用于记录）
  "original_messages": [...]  # 原始 messages（用于记录）
}
```

**output_{i}.json** (verl → tau2)：
```json
{
  "content": "I'll book that flight for you.",
  "tool_calls": [
    {
      "name": "book_reservation",
      "arguments": {
        "user_id": "user123",
        "flight_number": "AA123"
      }
    }
  ],
  "model": "train",
  "input_tokens": 1024,
  "output_tokens": 256
}
```

**done** 文件 (tau2 → verl)：
```
Done!
```

**完整实现示例**：

**verl 侧（Generation Manager）**：

```python
import os
import json
import time
import subprocess
from typing import Dict, List

class IPCGenerationManager:
    """IPC 模式的 Generation Manager"""

    def __init__(self, tokenizer, actor_rollout_wg, config):
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.config = config

    def run_task(self, task_batch: Dict) -> DataProto:
        """执行任务批次"""
        batch_size = len(task_batch['index'])

        # 为每个任务创建独立的通信目录
        transfer_dirs = []
        for idx in range(batch_size):
            task_id = task_batch['index'][idx]
            transfer_dir = f"/tmp/verl_tau2/{task_id}"
            os.makedirs(transfer_dir, exist_ok=True)
            transfer_dirs.append(transfer_dir)

            # 启动 tau2 子进程
            self._launch_tau2_process(task_batch, idx, transfer_dir)

        # 主循环：处理所有任务
        active_mask = torch.ones(batch_size, dtype=torch.bool)
        final_rewards = np.zeros(batch_size, dtype=float)
        all_trajectories = [[] for _ in range(batch_size)]

        while active_mask.any():
            for idx in range(batch_size):
                if not active_mask[idx]:
                    continue

                transfer_dir = transfer_dirs[idx]

                # 检查是否完成
                if os.path.exists(f"{transfer_dir}/done"):
                    reward = self._read_final_reward(transfer_dir)
                    final_rewards[idx] = reward
                    active_mask[idx] = False
                    continue

                # 查找下一个 input 文件
                step_idx = 0
                while os.path.exists(f"{transfer_dir}/output_{step_idx}.json"):
                    step_idx += 1

                input_file = f"{transfer_dir}/input_{step_idx}.json"
                if not os.path.exists(input_file):
                    time.sleep(1)  # 等待 tau2 写入
                    continue

                # 读取请求
                with open(input_file) as f:
                    request = json.load(f)

                # 调用 verl 模型
                response = self._call_verl_model(request)

                # 写响应
                output_file = f"{transfer_dir}/output_{step_idx}.json"
                with open(output_file, 'w') as f:
                    json.dump(response, f, indent=2)

                # 记录轨迹
                all_trajectories[idx].append({
                    'step': step_idx,
                    'request': request,
                    'response': response
                })

        # 构造最终 DataProto
        return self._build_dataproto(task_batch, all_trajectories, final_rewards)

    def _launch_tau2_process(self, task_batch: Dict, idx: int, transfer_dir: str):
        """启动 tau2 子进程"""
        task_id = task_batch['index'][idx]
        domain = task_batch['domain'][idx]
        task_path = f"{transfer_dir}/task.json"

        # 写任务文件
        with open(task_path, 'w') as f:
            json.dump({
                'id': task_id,
                'domain': domain,
                'initial_state': task_batch.get('initial_state', [None])[idx],
                'goal': task_batch.get('goal', [None])[idx]
            }, f)

        # 启动子进程
        cmd = [
            'python', 'rollout/tau2/cli.py',
            '--domain', domain,
            '--agent-llm', 'train',
            '--task_path', task_path,
            '--cur_transfer_dir', transfer_dir,
            '--max-steps', '40'
        ]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _call_verl_model(self, request: Dict) -> Dict:
        """调用 verl 模型生成响应"""
        messages = request['messages']
        tools = request['tools']

        # 构造 prompt
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            tokenize=False
        )

        # 分词
        prompt_ids = self.tokenizer(
            prompt,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=self.config.max_prompt_length
        )['input_ids']

        # 创建 DataProto
        active_batch = DataProto.from_dict({
            'input_ids': prompt_ids,
            'attention_mask': (prompt_ids != self.tokenizer.pad_token_id).long(),
            'position_ids': torch.arange(prompt_ids.shape[1]).unsqueeze(0)
        })

        # 生成
        gen_output = self.actor_rollout_wg.generate_sequences(active_batch)

        # 解码
        response_text = self.tokenizer.decode(
            gen_output.batch['responses'][0],
            skip_special_tokens=True
        )

        # 解析 tool calls
        tool_calls = self._parse_tool_calls_from_text(response_text)

        return {
            'content': response_text if not tool_calls else None,
            'tool_calls': tool_calls,
            'model': 'train'
        }

    def _parse_tool_calls_from_text(self, text: str) -> List[Dict]:
        """从文本中解析 tool calls（假设使用 JSON 格式）"""
        import re
        import json

        # 查找 JSON 块
        json_pattern = r'```json\n(.*?)\n```'
        matches = re.findall(json_pattern, text, re.DOTALL)

        tool_calls = []
        for match in matches:
            try:
                parsed = json.loads(match)
                if 'name' in parsed and 'arguments' in parsed:
                    tool_calls.append(parsed)
            except json.JSONDecodeError:
                pass

        return tool_calls
```

**tau2 侧（Environment + Orchestrator）**：

参考 `.reference_projects/ToolOrchestra/training/rollout/tau2/` 的完整实现。

关键修改点：

```python
# rollout/tau2/utils/llm_utils.py

def generate(model, messages, tools, cur_transfer_dir, role='assistant', **kwargs):
    """生成响应（支持 IPC 模式）"""

    if role == 'assistant' and model == 'train':
        # IPC 模式：通过文件通信

        # 1. 找到下一个序号
        step_idx = 0
        while os.path.isfile(f"{cur_transfer_dir}/input_{step_idx}.json"):
            step_idx += 1

        # 2. 写请求
        with open(f"{cur_transfer_dir}/input_{step_idx}.json", 'w') as f:
            json.dump({
                'messages': messages,
                'tools': tools,
                'original_tools': tools
            }, f, indent=2)

        # 3. 等待响应
        output_file = f"{cur_transfer_dir}/output_{step_idx}.json"
        while not os.path.isfile(output_file):
            time.sleep(5)

        # 4. 读取响应
        with open(output_file) as f:
            response = json.load(f)

        return response

    else:
        # 直接调用 LLM API
        return call_llm_api(model, messages, tools, **kwargs)
```

---

## 5. 关键文件清单

### 5.1 verl 框架核心文件（只读，了解即可）

| 文件路径 | 用途 | 重要性 |
|---------|------|--------|
| `verl/protocol.py` | DataProto 定义 | ⭐⭐⭐⭐⭐ |
| `verl/workers/rollout/base.py` | BaseRollout 接口 | ⭐⭐⭐⭐⭐ |
| `verl/workers/rollout/schemas.py` | Message/Request 格式 | ⭐⭐⭐⭐ |
| `verl/workers/fsdp_workers.py` | ActorRolloutRefWorker | ⭐⭐⭐ |
| `verl/trainer/ppo/ray_trainer.py` | RayPPOTrainer 基类 | ⭐⭐⭐ |

### 5.2 需要实现的文件（你的代码）

#### 5.2.1 环境定义文件

```
src/environment/
├── __init__.py
├── data_model.py          # Pydantic 数据模型
│   ├── class FlightInfo(BaseModel)
│   ├── class Reservation(BaseModel)
│   └── ...
│
├── tools.py               # Tool 定义
│   ├── @is_tool decorator
│   ├── class YourToolKit(ToolKitBase)
│   └── def search_xxx(), book_xxx(), ...
│
├── environment.py         # 环境主类
│   ├── class YourEnvironment
│   ├── def reset()
│   ├── def use_tool()
│   └── def get_state()
│
├── evaluator.py           # 奖励计算
│   ├── class YourEvaluator
│   └── def evaluate()
│
└── db.py                  # 数据库（可选）
    ├── class YourDB
    ├── def reset()
    └── def serialize()
```

#### 5.2.2 对接层文件

```
src/training/
├── generation_manager.py  # Generation Manager
│   ├── class YourGenerationManager
│   ├── def run_task()
│   └── def _call_verl_model()
│
├── dataset.py             # 数据集
│   ├── class YourDataset(Dataset)
│   └── def __getitem__()
│
├── trainer.py             # 自定义 Trainer（可选）
│   └── class YourTrainer(RayPPOTrainer)
│
└── main.py                # 训练入口
    └── def main()
```

#### 5.2.3 配置文件

```
configs/
├── your_task.yaml         # 主配置文件
├── defaults/
│   ├── data.yaml
│   ├── model.yaml
│   └── algorithm.yaml
└── overrides/
    ├── small_scale.yaml
    └── large_scale.yaml
```

### 5.3 参考文件（可复用）

**ToolOrchestra 参考实现**：

| 参考文件 | 用途 | 路径 |
|---------|------|------|
| Tool 系统 | 学习装饰器模式 | `evaluation/tau2-bench/tau2/environment/toolkit.py` |
| Environment | 学习环境设计 | `evaluation/tau2-bench/tau2/environment/environment.py` |
| Evaluator | 学习奖励计算 | `evaluation/tau2-bench/tau2/evaluator/evaluator.py` |
| Generation Manager | 学习对接层 | `training/lead_agent/llm_agent/generation_quick3.py` |
| GRPO Trainer | 学习训练器 | `training/recipe/algo/grpo_ray_trainer_quick3.py` |
| 配置示例 | 学习配置 | `training/recipe/algo/config/grpo_trainer.yaml` |

---

## 6. 完整实现步骤

### Step 1: 定义数据模型

**文件**: `src/environment/data_model.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class FlightClass(str, Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"

class Flight(BaseModel):
    """航班信息"""
    flight_number: str = Field(..., description="航班号")
    origin: str = Field(..., description="出发地 IATA 代码")
    destination: str = Field(..., description="目的地 IATA 代码")
    departure_time: str = Field(..., description="出发时间")
    arrival_time: str = Field(..., description="到达时间")
    price: float = Field(..., description="价格")
    available_seats: int = Field(..., description="可用座位数")
    flight_class: FlightClass = Field(..., description="舱位等级")

class Passenger(BaseModel):
    """乘客信息"""
    name: str
    passport_number: str
    date_of_birth: str

class Reservation(BaseModel):
    """预订信息"""
    id: str
    user_id: str
    flight_number: str
    passengers: List[Passenger]
    total_price: float
    status: str  # 'confirmed', 'cancelled', etc.
```

### Step 2: 实现 Tool 系统

**文件**: `src/environment/tools.py`

```python
from .data_model import Flight, Reservation, Passenger
from typing import List
import copy

# 1. 定义装饰器和基类（复制自 tau2）
from tau2.environment.toolkit import ToolKitBase, is_tool, ToolType

# 2. 实现具体 ToolKit
class AirlineToolKit(ToolKitBase):
    """航空预订系统 ToolKit"""

    def __init__(self, db):
        super().__init__(db)

    @is_tool(ToolType.READ)
    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        flight_class: str = "economy"
    ) -> List[Flight]:
        """
        搜索航班

        Args:
            origin: 出发地（如 'SFO'）
            destination: 目的地（如 'LAX'）
            date: 日期（YYYY-MM-DD）
            flight_class: 舱位等级

        Returns:
            符合条件的航班列表
        """
        results = []
        for flight in self.db.flights.values():
            if (flight.origin == origin and
                flight.destination == destination and
                flight.date == date and
                flight.flight_class == flight_class):
                results.append(flight)
        return results

    @is_tool(ToolType.WRITE)
    def book_flight(
        self,
        user_id: str,
        flight_number: str,
        passengers: List[dict]
    ) -> Reservation:
        """
        预订航班

        Args:
            user_id: 用户 ID
            flight_number: 航班号
            passengers: 乘客列表

        Returns:
            预订确认信息
        """
        # 验证航班存在
        if flight_number not in self.db.flights:
            raise ValueError(f"Flight {flight_number} not found")

        flight = self.db.flights[flight_number]

        # 检查座位
        if flight.available_seats < len(passengers):
            raise ValueError("Not enough seats available")

        # 创建预订
        reservation_id = f"RES_{len(self.db.reservations)}"
        reservation = Reservation(
            id=reservation_id,
            user_id=user_id,
            flight_number=flight_number,
            passengers=[Passenger(**p) for p in passengers],
            total_price=flight.price * len(passengers),
            status='confirmed'
        )

        # 更新数据库
        self.db.reservations[reservation_id] = reservation
        flight.available_seats -= len(passengers)

        return reservation

    @is_tool(ToolType.READ)
    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """查询预订信息"""
        return self.db.reservations.get(reservation_id)

    @is_tool(ToolType.WRITE)
    def cancel_reservation(self, reservation_id: str) -> bool:
        """取消预订"""
        if reservation_id not in self.db.reservations:
            raise ValueError(f"Reservation {reservation_id} not found")

        reservation = self.db.reservations[reservation_id]
        reservation.status = 'cancelled'

        # 释放座位
        flight = self.db.flights[reservation.flight_number]
        flight.available_seats += len(reservation.passengers)

        return True
```

### Step 3: 实现 Environment

**文件**: `src/environment/environment.py`

```python
from .tools import AirlineToolKit
from .db import AirlineDB
from typing import Dict, List, Any

class AirlineEnvironment:
    """航空预订环境"""

    def __init__(self, db_config: Dict = None):
        """初始化环境"""
        self.db = AirlineDB(config=db_config)
        self.toolkit = AirlineToolKit(db=self.db)

    def reset(self, initial_state: Dict = None):
        """重置环境到初始状态"""
        self.db.reset()
        if initial_state:
            self._load_initial_state(initial_state)

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """执行 tool"""
        return self.toolkit.use_tool(tool_name, **kwargs)

    def get_tools(self) -> List[Dict]:
        """获取所有 tools 的 schema"""
        from tau2.environment.tool import as_tool
        return [as_tool(func).openai_schema for func in self.toolkit.tools.values()]

    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            'flights': {k: v.dict() for k, v in self.db.flights.items()},
            'reservations': {k: v.dict() for k, v in self.db.reservations.items()}
        }

    def _load_initial_state(self, state: Dict):
        """加载初始状态"""
        # 实现状态加载逻辑
        pass
```

### Step 4: 实现 Evaluator

**文件**: `src/environment/evaluator.py`

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class RewardInfo:
    reward: float
    breakdown: Dict[str, float]
    details: Dict

class AirlineEvaluator:
    """航空任务评估器"""

    def __init__(self, environment):
        self.environment = environment

    def evaluate(self, task: Dict, messages: List[Dict]) -> RewardInfo:
        """
        评估任务完成情况

        Args:
            task: {
                'goal': '预订从 SFO 到 LAX 的航班',
                'user_id': 'user123',
                'expected_outcome': {
                    'has_reservation': True,
                    'correct_route': ('SFO', 'LAX')
                }
            }
            messages: 完整对话历史

        Returns:
            RewardInfo
        """
        # 1. 检查任务完成度
        outcome_reward = self._check_outcome(task)

        # 2. 检查效率
        efficiency_reward = self._check_efficiency(messages)

        # 3. 检查沟通质量
        communication_reward = self._check_communication(messages)

        # 4. 综合评分
        total_reward = (
            0.6 * outcome_reward +
            0.2 * efficiency_reward +
            0.2 * communication_reward
        )

        return RewardInfo(
            reward=total_reward,
            breakdown={
                'outcome': outcome_reward,
                'efficiency': efficiency_reward,
                'communication': communication_reward
            },
            details={
                'num_turns': len(messages),
                'final_state': self.environment.get_state()
            }
        )

    def _check_outcome(self, task: Dict) -> float:
        """检查是否达成目标"""
        expected = task.get('expected_outcome', {})
        state = self.environment.get_state()

        score = 0.0

        # 检查是否有预订
        if expected.get('has_reservation'):
            if len(state['reservations']) > 0:
                score += 0.5

                # 检查路线是否正确
                for res in state['reservations'].values():
                    flight = state['flights'].get(res['flight_number'])
                    if flight:
                        expected_route = expected.get('correct_route')
                        actual_route = (flight['origin'], flight['destination'])
                        if expected_route == actual_route:
                            score += 0.5
                            break

        return score

    def _check_efficiency(self, messages: List[Dict]) -> float:
        """检查效率"""
        num_turns = len([m for m in messages if m['role'] == 'assistant'])

        # 理想轮数：3-5 轮
        if 3 <= num_turns <= 5:
            return 1.0
        elif num_turns < 3:
            return 0.7  # 太快可能遗漏信息
        else:
            # 每多一轮扣 0.1
            return max(0, 1.0 - (num_turns - 5) * 0.1)

    def _check_communication(self, messages: List[Dict]) -> float:
        """检查沟通质量"""
        score = 1.0

        for msg in messages:
            if msg['role'] == 'assistant':
                content = msg.get('content', '')

                # 检查是否礼貌
                if not any(word in content.lower() for word in ['please', 'thank', 'sorry']):
                    score -= 0.1

                # 检查是否过于简短
                if len(content.split()) < 5 and not msg.get('tool_calls'):
                    score -= 0.1

        return max(0, score)
```

### Step 5: 实现 Generation Manager

**文件**: `src/training/generation_manager.py`

选择模式：

**方案 A：直接集成模式**（推荐用于简单任务）

```python
# 参考前面 "4.2 模式一：直接集成模式" 的实现
```

**方案 B：IPC 模式**（用于复杂多轮交互）

```python
# 参考前面 "4.3 模式二：进程间通信模式" 的实现
```

### Step 6: 实现 Dataset

**文件**: `src/training/dataset.py`

```python
from torch.utils.data import Dataset
import json
from typing import List, Dict

class AirlineDataset(Dataset):
    """航空任务数据集"""

    def __init__(self, data_file: str, tokenizer):
        """
        Args:
            data_file: JSONL 文件路径
            tokenizer: Tokenizer 实例
        """
        self.tokenizer = tokenizer
        self.data = []

        with open(data_file) as f:
            for line in f:
                self.data.append(json.loads(line))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        """
        返回单个样本

        Returns:
            Dict with keys:
                - index: str
                - problem: str
                - tools: List[Dict]
                - answer: str (ground truth)
                - category: str
                - domain: str
                - ...
        """
        item = self.data[idx]

        return {
            'index': item['id'],
            'problem': item['user_query'],
            'tools': self._get_tools(),
            'answer': item.get('expected_outcome'),
            'category': 'airline',
            'domain': 'airline',
            'initial_state': item.get('initial_state'),
            # 添加其他需要的字段
        }

    def _get_tools(self) -> List[Dict]:
        """获取 tools schema"""
        from src.environment.environment import AirlineEnvironment
        env = AirlineEnvironment()
        return env.get_tools()


def collate_fn(batch: List[Dict]) -> Dict:
    """Collate 函数"""
    import numpy as np

    # 收集所有字段
    collated = {}
    for key in batch[0].keys():
        collated[key] = np.array([item[key] for item in batch], dtype=object)

    return collated
```

### Step 7: 实现 Trainer

**文件**: `src/training/trainer.py`

```python
from verl.trainer.ppo.ray_trainer import RayPPOTrainer
from verl import DataProto
from .generation_manager import YourGenerationManager
from .dataset import AirlineDataset, collate_fn
from torch.utils.data import DataLoader

class AirlineGRPOTrainer(RayPPOTrainer):
    """自定义 GRPO Trainer"""

    def _create_dataloader(self, place_holder1, place_holder2, place_holder3, train_sampler):
        """创建数据加载器"""

        # 训练数据集
        self.train_dataset = AirlineDataset(
            data_file=self.config.data.train_files,
            tokenizer=self.tokenizer
        )

        # 训练 DataLoader
        self.train_dataloader = DataLoader(
            dataset=self.train_dataset,
            batch_size=self.config.data.train_batch_size,
            shuffle=True,
            collate_fn=collate_fn,
            num_workers=4
        )

        # 验证数据集
        self.val_dataset = AirlineDataset(
            data_file=self.config.data.val_files,
            tokenizer=self.tokenizer
        )

        # 验证 DataLoader
        self.val_dataloader = DataLoader(
            dataset=self.val_dataset,
            batch_size=self.config.data.val_batch_size,
            shuffle=False,
            collate_fn=collate_fn,
            num_workers=4
        )

    def fit(self):
        """训练循环"""
        from .generation_manager import YourGenerationManager
        from omegaconf import OmegaConf

        # 创建 Generation Manager
        gen_config = self.config.generation
        generation_manager = YourGenerationManager(
            tokenizer=self.tokenizer,
            actor_rollout_wg=self.actor_rollout_wg,
            config=gen_config
        )

        # 训练循环
        for epoch in range(self.config.trainer.total_epochs):
            for batch_dict in self.train_dataloader:

                # 1. 生成轨迹
                final_data = generation_manager.run_task(batch_dict)

                # 2. 计算 advantages
                batch = self._compute_advantages(final_data)

                # 3. 更新 actor
                if self.config.trainer.critic_warmup <= self.global_steps:
                    actor_output = self.actor_rollout_wg.update_actor(batch)

                # 4. 更新 critic（如果使用）
                if self.use_critic:
                    critic_output = self.critic_wg.update_critic(batch)

                # 5. 记录指标
                self._log_metrics(batch, actor_output, critic_output)

                self.global_steps += 1
```

### Step 8: 配置文件

**文件**: `configs/airline_task.yaml`

```yaml
# 继承基础配置
defaults:
  - ppo_trainer  # 来自 verl
  - _self_

# 数据配置
data:
  train_files: "data/airline/train.jsonl"
  val_files: "data/airline/val.jsonl"
  train_batch_size: 8
  val_batch_size: 8
  max_prompt_length: 2048
  max_response_length: 512
  prompt_template: "qwen-base"

# Generation Manager 配置
generation:
  max_turns: 10
  max_prompt_length: 2048
  max_response_length: 512

# 模型配置
actor_rollout_ref:
  model:
    path: "/path/to/Qwen2.5-7B-Instruct"
  actor:
    strategy: "fsdp"
    ppo_micro_batch_size: 2
    ppo_mini_batch_size: 8

# 算法配置
algorithm:
  gamma: 0.99
  lam: 0.95
  kl_penalty: 0.01

# 训练器配置
trainer:
  total_epochs: 3
  n_gpus_per_node: 8
  nnodes: 1
  save_freq: 100
  project_name: "airline-rl"
  experiment_name: "airline-grpo-v1"
```

### Step 9: 主入口

**文件**: `src/training/main.py`

```python
import hydra
import ray
from omegaconf import OmegaConf
from .trainer import AirlineGRPOTrainer

@hydra.main(config_path="../../configs", config_name="airline_task", version_base=None)
def main(config):
    """训练主函数"""

    # 初始化 Ray
    if not ray.is_initialized():
        ray.init(
            num_cpus=config.ray_init.num_cpus,
            runtime_env={
                "env_vars": {
                    "TOKENIZERS_PARALLELISM": "true",
                    "NCCL_DEBUG": "WARN"
                }
            }
        )

    # 创建 Trainer
    trainer = AirlineGRPOTrainer(config=config)

    # 初始化 Workers
    trainer.init_workers()

    # 开始训练
    trainer.fit()

if __name__ == "__main__":
    main()
```

### Step 10: 数据准备

**文件**: `scripts/prepare_data.py`

```python
import json
from typing import List, Dict

def generate_airline_tasks() -> List[Dict]:
    """生成航空任务数据"""
    tasks = []

    # 示例任务 1: 搜索并预订航班
    tasks.append({
        'id': 'airline_001',
        'user_query': 'I want to book a flight from SFO to LAX on 2024-05-15',
        'domain': 'airline',
        'expected_outcome': {
            'has_reservation': True,
            'correct_route': ('SFO', 'LAX'),
            'correct_date': '2024-05-15'
        },
        'initial_state': {
            'user_id': 'user123',
            'flights': [
                {
                    'flight_number': 'AA123',
                    'origin': 'SFO',
                    'destination': 'LAX',
                    'date': '2024-05-15',
                    'price': 250.0,
                    'available_seats': 10
                }
            ]
        }
    })

    # 添加更多任务...

    return tasks

def save_to_jsonl(tasks: List[Dict], output_file: str):
    """保存为 JSONL 格式"""
    with open(output_file, 'w') as f:
        for task in tasks:
            f.write(json.dumps(task) + '\n')

if __name__ == "__main__":
    tasks = generate_airline_tasks()
    save_to_jsonl(tasks, 'data/airline/train.jsonl')
    print(f"Generated {len(tasks)} tasks")
```

---

## 7. 数据流转详解

### 7.1 完整数据流

```
用户任务 (JSONL)
  ↓
Dataset.__getitem__()
  └→ {index, problem, tools, answer, category, domain, ...}
  ↓
collate_fn()
  └→ Dict[str, np.ndarray]
  ↓
GenerationManager.run_task()
  ↓
  ├─ FOR turn in [1..max_turns]:
  │   ├─ 准备 prompt
  │   ├─ 调用 verl
  │   │   ├─ DataProto.from_dict({input_ids, attention_mask, ...})
  │   │   ├─ actor_rollout_wg.generate_sequences(DataProto)
  │   │   └→ DataProto {responses, ...}
  │   ├─ 解析 tool_calls
  │   ├─ 执行 Environment.use_tool()
  │   └─ 更新轨迹
  │
  ├─ Evaluator.evaluate()
  │   └→ RewardInfo {reward, breakdown, details}
  │
  └→ DataProto.from_dict({
      tensors: {input_ids, responses, attention_mask, ...},
      non_tensors: {reward, index, ...}
  })
  ↓
RayPPOTrainer.fit()
  ├─ compute_advantages(DataProto)
  ├─ actor_rollout_wg.update_actor(DataProto)
  └─ critic_wg.update_critic(DataProto) (可选)
```

### 7.2 关键数据转换

#### 7.2.1 Task → Prompt

```python
def prepare_prompt(task: Dict, history: List, retrieved_docs: List) -> str:
    """
    将任务转换为模型输入

    Args:
        task: {problem, tools, ...}
        history: 对话历史
        retrieved_docs: 检索到的文档

    Returns:
        Formatted prompt string
    """
    # 1. System prompt
    system = "You are a customer service agent. Use the provided tools to help the user."

    # 2. User query
    user_query = task['problem']

    # 3. Context (documents, etc.)
    context = "\n".join([f"Doc {i+1}: {doc}" for i, doc in enumerate(retrieved_docs)])

    # 4. 构造 messages
    messages = [
        {"role": "system", "content": system}
    ]
    messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"{context}\n\n{user_query}" if context else user_query
    })

    # 5. 应用 chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tools=task['tools'],
        add_generation_prompt=True,
        tokenize=False
    )

    return prompt
```

#### 7.2.2 Response → Tool Call

```python
def parse_tool_calls(response_text: str) -> List[Dict]:
    """
    从模型输出解析 tool calls

    支持多种格式:
    1. JSON 格式: {"name": "search_flights", "arguments": {...}}
    2. XML 格式: <tool_call>...</tool_call>
    3. 特殊 token 格式
    """
    import json
    import re

    tool_calls = []

    # 方法 1: JSON 块
    json_pattern = r'```json\n(.*?)\n```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, list):
                tool_calls.extend(parsed)
            elif 'name' in parsed and 'arguments' in parsed:
                tool_calls.append(parsed)
        except json.JSONDecodeError:
            pass

    # 方法 2: 特殊格式（如果使用训练过的格式）
    # 例如: <|tool_call|>{"name": "...", "arguments": {...}}<|end_tool_call|>
    tool_call_pattern = r'<\|tool_call\|>(.*?)<\|end_tool_call\|>'
    matches = re.findall(tool_call_pattern, response_text, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            tool_calls.append(parsed)
        except json.JSONDecodeError:
            pass

    return tool_calls
```

#### 7.2.3 Tool Result → Observation

```python
def format_tool_result(tool_name: str, result: Any) -> str:
    """
    格式化 tool 执行结果为观察

    Args:
        tool_name: Tool 名称
        result: Tool 返回值（可能是 Pydantic model, list, dict, etc.）

    Returns:
        Formatted string for next turn
    """
    import json
    from pydantic import BaseModel

    # 如果是 Pydantic model，转为 dict
    if isinstance(result, BaseModel):
        result = result.dict()
    elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], BaseModel):
        result = [r.dict() for r in result]

    # 格式化为 JSON
    formatted = json.dumps(result, indent=2, ensure_ascii=False)

    # 添加上下文
    observation = f"Tool '{tool_name}' returned:\n```json\n{formatted}\n```"

    return observation
```

#### 7.2.4 Trajectory → DataProto

```python
def build_dataproto_from_trajectory(
    trajectory: List[Dict],
    tokenizer,
    reward: float
) -> DataProto:
    """
    从完整轨迹构造 DataProto

    Args:
        trajectory: [
            {'turn': 0, 'prompt': "...", 'response': "...", 'tool_results': [...]},
            {'turn': 1, 'prompt': "...", 'response': "...", 'tool_results': []},
            ...
        ]
        tokenizer: Tokenizer
        reward: 最终奖励值

    Returns:
        DataProto
    """
    # 1. 拼接完整序列
    full_text = ""
    response_start_positions = []

    for step in trajectory:
        prompt = step['prompt']
        response = step['response']

        full_text += prompt
        response_start_positions.append(len(tokenizer(full_text)['input_ids']))
        full_text += response

    # 2. 分词
    full_ids = tokenizer(full_text, return_tensors='pt')['input_ids']

    # 3. 提取 response 部分
    # 这里简化处理，实际可能需要更复杂的逻辑
    last_turn = trajectory[-1]
    response_ids = tokenizer(last_turn['response'], return_tensors='pt')['input_ids']

    # 4. 创建 attention mask 和 position ids
    attention_mask = torch.ones_like(full_ids)
    position_ids = torch.arange(full_ids.shape[1]).unsqueeze(0)

    # 5. 构造 DataProto
    data = DataProto.from_dict(
        tensors={
            'input_ids': full_ids,
            'attention_mask': attention_mask,
            'position_ids': position_ids,
            'responses': response_ids
        },
        non_tensors={
            'reward': np.array([reward], dtype=float),
            'index': np.array([trajectory[0].get('task_id', 'unknown')], dtype=object)
        }
    )

    return data
```

---

## 8. 调试与测试

### 8.1 单元测试

#### 8.1.1 测试 Tool 系统

```python
# tests/test_tools.py

import pytest
from src.environment.tools import AirlineToolKit
from src.environment.db import AirlineDB
from src.environment.data_model import Flight

def test_search_flights():
    """测试搜索航班功能"""
    # 创建测试数据库
    db = AirlineDB()
    db.flights['AA123'] = Flight(
        flight_number='AA123',
        origin='SFO',
        destination='LAX',
        date='2024-05-15',
        departure_time='10:00',
        arrival_time='12:00',
        price=250.0,
        available_seats=10,
        flight_class='economy'
    )

    # 创建 toolkit
    toolkit = AirlineToolKit(db=db)

    # 执行搜索
    results = toolkit.search_flights(
        origin='SFO',
        destination='LAX',
        date='2024-05-15'
    )

    # 验证结果
    assert len(results) == 1
    assert results[0].flight_number == 'AA123'
    assert results[0].price == 250.0

def test_book_flight():
    """测试预订航班功能"""
    db = AirlineDB()
    # 添加航班
    db.flights['AA123'] = Flight(
        flight_number='AA123',
        origin='SFO',
        destination='LAX',
        date='2024-05-15',
        departure_time='10:00',
        arrival_time='12:00',
        price=250.0,
        available_seats=10,
        flight_class='economy'
    )

    toolkit = AirlineToolKit(db=db)

    # 预订航班
    reservation = toolkit.book_flight(
        user_id='user123',
        flight_number='AA123',
        passengers=[
            {'name': 'John Doe', 'passport_number': 'P123456', 'date_of_birth': '1990-01-01'}
        ]
    )

    # 验证
    assert reservation.user_id == 'user123'
    assert reservation.flight_number == 'AA123'
    assert len(reservation.passengers) == 1
    assert db.flights['AA123'].available_seats == 9  # 减少了 1 个座位

def test_cancel_reservation():
    """测试取消预订功能"""
    # 类似上面的测试...
    pass
```

#### 8.1.2 测试 Evaluator

```python
# tests/test_evaluator.py

from src.environment.evaluator import AirlineEvaluator
from src.environment.environment import AirlineEnvironment

def test_evaluator_success():
    """测试成功完成任务的评估"""
    env = AirlineEnvironment()
    evaluator = AirlineEvaluator(environment=env)

    # 模拟成功的任务
    task = {
        'goal': '预订从 SFO 到 LAX 的航班',
        'expected_outcome': {
            'has_reservation': True,
            'correct_route': ('SFO', 'LAX')
        }
    }

    # 模拟对话历史
    messages = [
        {'role': 'user', 'content': 'I want to book a flight from SFO to LAX'},
        {'role': 'assistant', 'tool_calls': [{'name': 'search_flights', ...}]},
        {'role': 'tool', 'content': '[{flight_number: "AA123", ...}]'},
        {'role': 'assistant', 'tool_calls': [{'name': 'book_flight', ...}]},
        {'role': 'tool', 'content': '{reservation_id: "RES_001", ...}'},
        {'role': 'assistant', 'content': 'Your flight has been booked!'}
    ]

    # 设置环境状态（模拟成功预订）
    env.db.reservations['RES_001'] = ...

    # 评估
    reward_info = evaluator.evaluate(task, messages)

    # 验证
    assert reward_info.reward > 0.8  # 高分
    assert reward_info.breakdown['outcome'] > 0.9
```

### 8.2 集成测试

#### 8.2.1 测试 Generation Manager

```python
# tests/test_generation_manager.py

import torch
from src.training.generation_manager import YourGenerationManager
from unittest.mock import Mock, MagicMock

def test_generation_manager_run_task():
    """测试 Generation Manager 执行任务"""
    # Mock tokenizer
    tokenizer = Mock()
    tokenizer.pad_token_id = 0
    tokenizer.apply_chat_template = Mock(return_value="mocked prompt")
    tokenizer.return_value = {'input_ids': torch.tensor([[1, 2, 3]])}
    tokenizer.batch_decode = Mock(return_value=["mocked response"])

    # Mock actor_rollout_wg
    actor_rollout_wg = Mock()
    gen_output = DataProto.from_dict({
        'input_ids': torch.tensor([[1, 2, 3, 4, 5]]),
        'responses': torch.tensor([[4, 5]])
    })
    actor_rollout_wg.generate_sequences = Mock(return_value=gen_output)

    # 创建 manager
    config = Mock(max_turns=5, max_prompt_length=2048)
    manager = YourGenerationManager(tokenizer, actor_rollout_wg, config)

    # 准备测试数据
    task_batch = {
        'problem': ['Test task'],
        'tools': [[]],
        'answer': ['Expected answer'],
        'category': ['test']
    }

    # 执行
    result = manager.run_task(task_batch)

    # 验证
    assert isinstance(result, DataProto)
    assert 'reward' in result.non_tensor_batch
    assert len(result.non_tensor_batch['reward']) == 1
```

### 8.3 端到端测试

```python
# tests/test_e2e.py

def test_full_pipeline():
    """端到端测试：从数据加载到训练一步"""
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'

    from src.training.dataset import AirlineDataset, collate_fn
    from src.training.trainer import AirlineGRPOTrainer
    from omegaconf import OmegaConf

    # 1. 准备测试配置
    config = OmegaConf.create({
        'data': {
            'train_files': 'tests/data/test_train.jsonl',
            'val_files': 'tests/data/test_val.jsonl',
            'train_batch_size': 2,
            'val_batch_size': 2,
            'max_prompt_length': 512,
            'max_response_length': 128
        },
        'actor_rollout_ref': {
            'model': {'path': '/path/to/small/model'},
            'actor': {'strategy': 'fsdp'}
        },
        'trainer': {
            'total_epochs': 1,
            'n_gpus_per_node': 1,
            'nnodes': 1
        }
    })

    # 2. 创建 trainer（不实际训练，只测试初始化）
    # trainer = AirlineGRPOTrainer(config=config)
    # trainer.init_workers()

    # 3. 测试数据加载
    dataset = AirlineDataset(config.data.train_files, tokenizer=None)
    assert len(dataset) > 0

    sample = dataset[0]
    assert 'index' in sample
    assert 'problem' in sample

    print("✓ E2E test passed")
```

### 8.4 调试技巧

#### 8.4.1 打印中间结果

```python
class DebugGenerationManager(YourGenerationManager):
    """带调试输出的 Generation Manager"""

    def run_task(self, task_batch: Dict) -> DataProto:
        print("=" * 80)
        print("DEBUG: Starting task batch")
        print(f"Batch size: {len(task_batch['problem'])}")
        print(f"First problem: {task_batch['problem'][0]}")

        # 调用原方法
        result = super().run_task(task_batch)

        print(f"Final reward: {result.non_tensor_batch['reward']}")
        print("=" * 80)

        return result
```

#### 8.4.2 保存轨迹

```python
import json
import os

def save_trajectory(trajectory: List[Dict], task_id: str, output_dir: str):
    """保存轨迹用于分析"""
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{task_id}.json")
    with open(output_file, 'w') as f:
        json.dump(trajectory, f, indent=2, ensure_ascii=False)

    print(f"Saved trajectory to {output_file}")
```

#### 8.4.3 可视化奖励分布

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_reward_distribution(rewards: List[float], save_path: str = None):
    """绘制奖励分布"""
    plt.figure(figsize=(10, 6))
    plt.hist(rewards, bins=20, alpha=0.7, edgecolor='black')
    plt.axvline(np.mean(rewards), color='r', linestyle='--', label=f'Mean: {np.mean(rewards):.3f}')
    plt.axvline(np.median(rewards), color='g', linestyle='--', label=f'Median: {np.median(rewards):.3f}')
    plt.xlabel('Reward')
    plt.ylabel('Frequency')
    plt.title('Reward Distribution')
    plt.legend()
    plt.grid(alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
```

---

## 9. 常见问题

### Q1: DataProto 的 batch 和 non_tensor_batch 有什么区别？

**A**:
- `batch` (TensorDict): 存储 **Tensor 数据**，会放在 **GPU** 上参与计算
  - 例如: `input_ids`, `attention_mask`, `responses`
  - 用于模型前向传播、梯度计算

- `non_tensor_batch` (Dict[str, np.ndarray]): 存储 **非 Tensor 数据**，保存在 **CPU** 上
  - 例如: `reward` (float), `index` (str), 自定义元信息
  - 用于追踪、日志、reward 计算

**关键原则**：
- ✅ 模型需要的 → `batch`
- ✅ 人类需要的 → `non_tensor_batch`

### Q2: 如何处理变长序列？

**A**: 使用 **padding + attention_mask**：

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# 批量分词（自动 padding）
texts = ["Short text", "This is a much longer text"]
encoded = tokenizer(
    texts,
    padding=True,           # 自动 padding 到最长
    truncation=True,
    max_length=512,
    return_tensors='pt'
)

# encoded['input_ids']:
#   [[  101,  2123,  3455,     0,     0, ...],  # padding with 0
#    [  101,  2023,  2003,  2019,  2172, ...]]

# encoded['attention_mask']:
#   [[    1,     1,     1,     0,     0, ...],  # 1=有效, 0=padding
#    [    1,     1,     1,     1,     1, ...]]
```

### Q3: reward 必须在 [0, 1] 之间吗？

**A**: **不强制**，但 **强烈推荐**：

- ✅ **推荐**: reward ∈ [0, 1]
  - 便于不同任务之间对比
  - 便于设置 baseline
  - 便于调试（容易发现异常值）

- ❌ **不推荐**: reward ∈ (-∞, +∞)
  - 可能导致训练不稳定
  - 难以解释

**归一化方法**：
```python
def normalize_reward(raw_reward: float, min_val: float = -10, max_val: float = 10) -> float:
    """将任意范围的 reward 归一化到 [0, 1]"""
    return (raw_reward - min_val) / (max_val - min_val)
```

### Q4: 如何支持多轮对话？

**A**: 在 **Generation Manager** 中维护对话历史：

```python
class MultiTurnGenerationManager:
    def run_task(self, task_batch):
        # 初始化对话历史
        conversation_histories = [[] for _ in range(batch_size)]

        for turn in range(self.config.max_turns):
            # 1. 准备 prompt（包含历史）
            prompts = []
            for idx, history in enumerate(conversation_histories):
                messages = [
                    {"role": "system", "content": "..."},
                    *history,  # 添加历史对话
                    {"role": "user", "content": task_batch['problem'][idx]}
                ]
                prompt = self.tokenizer.apply_chat_template(messages, ...)
                prompts.append(prompt)

            # 2. 生成响应
            gen_output = self._call_verl_model(prompts)

            # 3. 更新历史
            for idx, response in enumerate(responses):
                conversation_histories[idx].append({
                    "role": "assistant",
                    "content": response
                })

                # 如果有 tool call，添加 tool message
                if tool_results[idx]:
                    conversation_histories[idx].append({
                        "role": "tool",
                        "content": tool_results[idx]
                    })
```

### Q5: verl 是否支持多模态（图像+文本）？

**A**: **支持**，但需要额外处理：

```python
from PIL import Image

# 1. 使用支持多模态的 tokenizer/processor
from transformers import AutoProcessor
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B")

# 2. 准备多模态输入
image = Image.open("example.jpg")
text = "What's in this image?"

# 3. 处理
inputs = processor(
    text=[text],
    images=[image],
    return_tensors='pt'
)

# 4. 创建 DataProto
data = DataProto.from_dict({
    'input_ids': inputs['input_ids'],
    'attention_mask': inputs['attention_mask'],
    'pixel_values': inputs['pixel_values'],  # 图像特征
    'image_grid_thw': inputs['image_grid_thw']  # 图像元信息
})
```

参考：`docs/verl_api/data_interface.md` 的多模态章节。

### Q6: 如何调试 "CUDA out of memory"？

**A**: 按优先级尝试：

1. **减小 batch size**
   ```yaml
   data:
     train_batch_size: 4  # 从 8 降到 4
   ```

2. **启用梯度检查点**
   ```yaml
   actor_rollout_ref:
     actor:
       enable_gradient_checkpointing: true
   ```

3. **使用 LoRA**
   ```yaml
   actor_rollout_ref:
     actor:
       lora_rank: 32
       lora_alpha: 64
   ```

4. **减少序列长度**
   ```yaml
   data:
     max_prompt_length: 1024  # 从 2048 降到 1024
     max_response_length: 256  # 从 512 降到 256
   ```

5. **使用 CPU offload**（最后手段，会变慢）
   ```yaml
   actor_rollout_ref:
     actor:
       param_offload: true
   ```

### Q7: 如何加速训练？

**A**: 优化策略：

1. **增加并行度**
   ```yaml
   trainer:
     n_gpus_per_node: 8  # 使用所有 GPU
     nnodes: 2           # 多机训练
   ```

2. **使用 Flash Attention**
   ```yaml
   actor_rollout_ref:
     actor:
       use_flash_attn: true
   ```

3. **混合精度训练**
   ```yaml
   actor_rollout_ref:
     actor:
       dtype: "bf16"  # 或 "fp16"
   ```

4. **优化 DataLoader**
   ```yaml
   data:
     dataloader_num_workers: 8  # 增加 workers
     pin_memory: true
   ```

5. **减少验证频率**
   ```yaml
   trainer:
     val_freq: 500  # 每 500 步验证一次，而不是每步
   ```

---

## 10. 完整示例

### 10.1 最小可运行示例

**目录结构**：
```
minimal_example/
├── src/
│   ├── environment/
│   │   ├── __init__.py
│   │   ├── data_model.py
│   │   ├── tools.py
│   │   ├── environment.py
│   │   └── evaluator.py
│   └── training/
│       ├── __init__.py
│       ├── generation_manager.py
│       ├── dataset.py
│       ├── trainer.py
│       └── main.py
├── configs/
│   └── simple_task.yaml
├── data/
│   ├── train.jsonl
│   └── val.jsonl
├── scripts/
│   └── prepare_data.py
└── requirements.txt
```

**完整代码**: 参考前面 Step 1-10 的实现。

**运行步骤**：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 准备数据
python scripts/prepare_data.py

# 3. 测试环境
python -c "from src.environment.environment import YourEnvironment; env = YourEnvironment(); print(env.get_tools())"

# 4. 启动训练
python src/training/main.py

# 或使用 Hydra 覆盖参数
python src/training/main.py \
    data.train_batch_size=4 \
    trainer.total_epochs=1
```

### 10.2 ToolOrchestra 对照表

| 你的实现 | ToolOrchestra 对应文件 | 说明 |
|---------|----------------------|------|
| `src/environment/tools.py` | `evaluation/tau2-bench/tau2/domains/airline/tools.py` | Tool 定义 |
| `src/environment/environment.py` | `evaluation/tau2-bench/tau2/environment/environment.py` | 环境主类 |
| `src/environment/evaluator.py` | `evaluation/tau2-bench/tau2/evaluator/evaluator.py` | 奖励计算 |
| `src/training/generation_manager.py` | `training/lead_agent/llm_agent/generation_quick3.py` | 对接层 |
| `src/training/trainer.py` | `training/recipe/algo/grpo_ray_trainer_quick3.py` | Trainer |
| `configs/your_task.yaml` | `training/recipe/algo/config/grpo_trainer.yaml` | 配置 |

---

## 附录 A: verl API 速查表

### A.1 DataProto 常用方法

| 方法 | 用途 | 示例 |
|------|------|------|
| `DataProto.from_dict()` | 创建 | `DataProto.from_dict(tensors={...}, non_tensors={...})` |
| `data[idx]` | 索引 | `item = data[0]` |
| `data[:10]` | 切片 | `subset = data[:10]` |
| `len(data)` | 长度 | `batch_size = len(data)` |
| `data.to(device)` | 移动设备 | `data = data.to('cuda:0')` |
| `DataProto.concat([d1, d2])` | 合并 | `combined = DataProto.concat([data1, data2])` |

### A.2 常用工具函数

```python
from verl.utils.torch_functional import (
    tokenize_and_postprocess_data,  # 分词 + 后处理
    allgather_dict_tensors,          # 跨 GPU gather
)
from verl.utils.model import compute_position_id_with_mask  # 计算 position_ids
```

### A.3 配置速查

```yaml
# 最小配置
data:
  train_files: "data/train.jsonl"
  train_batch_size: 8
  max_prompt_length: 2048
  max_response_length: 512

actor_rollout_ref:
  model:
    path: "/path/to/model"
  actor:
    strategy: "fsdp"

trainer:
  n_gpus_per_node: 8
  total_epochs: 3
```

---

## 附录 B: 参考资源

### B.1 官方文档

- **verl GitHub**: https://github.com/volcengine/verl
- **ToolOrchestra GitHub**: (NVIDIA 内部)
- **tau2-bench 论文**: arXiv (搜索 "tau2-bench")

### B.2 相关论文

- **PPO**: Proximal Policy Optimization Algorithms (Schulman et al., 2017)
- **GRPO**: Group Relative Policy Optimization (检索最新论文)
- **RLHF**: Learning to summarize from human feedback (Stiennon et al., 2020)

### B.3 推荐阅读

1. **verl 框架源码**: 理解 DataProto 和 Trainer 设计
2. **ToolOrchestra generation_quick3.py**: 学习对接层最佳实践
3. **tau2-bench toolkit.py**: 学习元类和装饰器模式

---

## 版本信息

- **文档版本**: v1.0
- **作者**: Claude (基于 ToolOrchestra 分析)
- **更新日期**: 2026-01-08
- **适用框架**: verl (VolcEngine RL framework)
- **测试项目**: ToolOrchestra (NVIDIA + Bytedance)

---

## 反馈与改进

如有问题或建议，请：

1. 查阅本文档的"常见问题"章节
2. 参考 ToolOrchestra 的实现
3. 检查 verl 官方文档
4. 在项目中创建 issue

**祝训练顺利！🚀**
