# Multi-turn RL 训练实现方案深度思考

> 本文档记录了 New_Flow_RL 项目在设计 multi-turn RL 训练时的思考过程、方案对比和最终决策。

## 目录

1. [背景与问题定义](#1-背景与问题定义)
2. [Multi-turn 的两种含义](#2-multi-turn-的两种含义)
3. [现有系统对比分析](#3-现有系统对比分析)
4. [VERL 官方 Multi-turn 支持](#4-verl-官方-multi-turn-支持)
5. [实现方案对比](#5-实现方案对比)
6. [推荐方案详解](#6-推荐方案详解)
7. [与 Reward Server 的集成](#7-与-reward-server-的集成)
8. [关键设计决策](#8-关键设计决策)
9. [实施路线图](#9-实施路线图)

---

## 1. 背景与问题定义

### 1.1 核心目标

New_Flow_RL 的目标是训练一个能够生成高质量 workflow 的模型。与 ToolOrchestra 不同，我们的模型需要：

- **生成 workflow 代码**：而不是简单地选择预定义工具
- **处理执行错误**：生成的 workflow 可能执行失败，需要重新生成
- **验证泛化能力**：一个 workflow 需要在多个问题上测试

### 1.2 核心挑战

```
Single-turn 场景：
  prompt → 模型生成 workflow → 执行 → reward
  （简单，但无法处理执行失败的情况）

Multi-turn 场景：
  prompt → 模型生成 workflow_v1 → 执行失败
        → [错误信息] → 模型修复生成 workflow_v2 → 执行成功 → reward
  （复杂，需要设计如何与 VERL 对接）
```

### 1.3 关键问题

1. **VERL 接口**：是否需要修改 VERL 的训练逻辑？
2. **Reward 分配**：多轮生成后，reward 如何分配到每轮？
3. **数据格式**：返回给 VERL 的数据应该是什么结构？
4. **执行效率**：如何高效地并行执行多个 workflow 测试？

---

## 2. Multi-turn 的两种含义

### 2.1 执行层 Multi-turn（错误重试）

**触发条件**：workflow 执行报错（语法错误、运行时异常等）

```
Turn 1: 生成 workflow_v1 → 执行 → ERROR: division by zero
Turn 2: [错误信息] → 生成 workflow_v2 → 执行 → 成功
```

**特点**：
- 必须处理，否则无法获得有效 reward
- 错误信息对模型修复有重要指导意义
- 类似于"编译-修复"循环

### 2.2 优化层 Multi-turn（结果改进）

**触发条件**：workflow 执行成功，但结果不够好（如 6/10 正确）

```
Turn 1: 生成 workflow_v1 → 测试 → 6/10 正确
Turn 2: [反馈信息] → 生成 workflow_v2 → 测试 → 8/10 正确
Turn 3: [反馈信息] → 生成 workflow_v3 → 测试 → 9/10 正确
```

**特点**：
- 可选的优化过程
- 适用于推理时（inference-time）优化
- 对于 RL 训练，通常不需要（让 RL 自己学习生成更好的 workflow）

### 2.3 关键决策

| 场景 | 执行层 Multi-turn | 优化层 Multi-turn |
|------|------------------|------------------|
| **RL 训练** | ✅ 需要（处理执行错误） | ❌ 不需要（让 RL 学习） |
| **推理/部署** | ✅ 需要 | ✅ 可选（迭代优化） |

**结论**：当前阶段只实现执行层 multi-turn，优化层留待后续扩展。

---

## 3. 现有系统对比分析

### 3.1 Flow_RL (原版) vs ToolOrchestra

| 方面 | Flow_RL | ToolOrchestra |
|------|---------|---------------|
| **模型输出** | 完整的 workflow 代码 | 工具调用指令 |
| **执行方式** | MetaGPT `exec()` 动态执行 | 预定义 `call_tool()` 函数 |
| **灵活性** | 高（可生成任意 workflow） | 低（固定工具集） |
| **安全性** | 低（动态执行代码） | 高（预定义函数） |
| **Multi-turn 含义** | 生成-执行-修复循环 | 工具链的多步骤调用 |

### 3.2 ToolOrchestra 的 Multi-turn 实现

ToolOrchestra 的核心是 `LLMGenerationManager.run_llm_loop()`：

```python
# 伪代码
for step in range(max_turns):
    # 1. 构建 prompt（包含历史 context）
    prompts = build_prompts(history, problems)

    # 2. 模型生成
    responses = model.generate(prompts)

    # 3. 执行工具调用
    results = execute_tools(responses)

    # 4. 收集本轮数据
    all_turns.append({
        'input_ids': prompts,
        'responses': responses,
        'turn_id': step,
    })

    # 5. 更新状态
    update_history(results)
    update_active_mask(results.dones)

# 6. 计算 reward（基于最终结果）
rewards = compute_trajectory_rewards()

# 7. 展平返回
return flatten_all_turns(all_turns, rewards)
```

### 3.3 ToolOrchestra 的关键发现

**核心洞察：Multi-turn 被展平成 Single-turn Samples**

```
原始 Trajectory (一个问题的多轮交互):
┌─────────────────────────────────────────────────────────────────┐
│ Turn 0: prompt_0 → response_0 (call search)                     │
│ Turn 1: prompt_1 (含 search 结果) → response_1 (call answer)    │
│ Turn 2: prompt_2 → response_2 (最终答案)                        │
│ → trajectory_reward = 1.0 (答对了)                              │
└─────────────────────────────────────────────────────────────────┘

展平后给 VERL 的 Samples:
┌─────────────────────────────────────────────────────────────────┐
│ Sample 0: input=prompt_0, response=response_0, reward=1.0       │
│ Sample 1: input=prompt_1, response=response_1, reward=1.0       │
│ Sample 2: input=prompt_2, response=response_2, reward=1.0       │
│ （所有 samples 共享同一个 trajectory reward）                   │
└─────────────────────────────────────────────────────────────────┘
```

**Reward 计算方式**：

```python
# 1. 计算每个 trajectory 的最终 reward
trajectory_reward = int(final_answer_correct)

# 2. GRPO 归一化（同一问题的多个 rollout）
normalized_reward = (trajectory_reward - mean) / (std + eps)

# 3. 每个 turn 获得相同的 reward
for turn in trajectory.turns:
    turn.reward = normalized_reward
```

---

## 4. VERL 官方 Multi-turn 支持

### 4.1 官方文档概述

根据 [VERL 官方文档](https://verl.readthedocs.io/en/latest/sglang_multiturn/multiturn.html)，VERL 提供了多种 multi-turn 支持方式：

| 组件 | 说明 | 文档链接 |
|------|------|---------|
| **Multi-turn Rollout** | 基础的多轮对话支持 | [multiturn.html](https://verl.readthedocs.io/en/latest/sglang_multiturn/multiturn.html) |
| **Agent Loop** | 通用的 agent 循环接口 | [agent_loop.html](https://verl.readthedocs.io/en/latest/advance/agent_loop.html) |
| **verl-tool** | 统一的 tool-agent 训练框架 | [GitHub](https://github.com/TIGER-AI-Lab/verl-tool) |

### 4.2 两种主流实现方式

#### 方式 A：Trajectory 整体处理（官方推荐）

```
特点：
- 保持完整的 trajectory 结构
- 使用 delta-based tokenization
- 只对 assistant 生成的 token 计算 loss
- 需要实现 AgentLoopBase 接口

代表项目：verl-tool, Agent Loop
```

#### 方式 B：展平成 Turns（工程简化）

```
特点：
- 每个 turn 作为独立的 training sample
- 同一 trajectory 的 turns 共享 reward
- 不需要修改 VERL trainer
- 兼容现有 single-turn 训练流程

代表项目：ToolOrchestra
```

### 4.3 对比分析

| 方面 | Trajectory 整体处理 | 展平成 Turns |
|------|-------------------|-------------|
| **架构正确性** | ✅ 更正确 | ⚠️ 近似 |
| **实现复杂度** | 较高（需实现 AgentLoopBase） | 较低 |
| **VERL 修改** | 需要适配 agent_loop 接口 | 几乎不需要 |
| **训练效率** | 更高（避免重复编码） | 略低 |
| **调试难度** | 较高 | 较低 |

### 4.4 ToolOrchestra 是否是标准实现？

**答案：不完全是。**

ToolOrchestra 的"展平"方式是一种**工程简化**，而非 VERL 官方推荐的标准方式。

**优点**：
- 快速验证，不需要深度修改 VERL
- 兼容现有训练流程

**缺点**：
- 同一 trajectory 的 turns 被当作独立 samples，可能引入偏差
- 无法利用 VERL 的 delta-based tokenization 优化

---

## 5. 实现方案对比

### 5.1 方案 A：在 Reward Server 内部处理 Multi-turn

```
架构：
┌──────────┐     ┌──────────┐     ┌──────────────────────────┐
│  VERL    │────▶│  Model   │────▶│     Reward Server        │
│  Trainer │     │ (一次)   │     │  内部处理多轮修复         │
└──────────┘     └──────────┘     └──────────────────────────┘

Reward Server 内部：
  workflow_v1 → 执行报错
    → 调用外部 LLM 修复 → workflow_v2 → 执行成功
    → 返回 reward
```

**问题**：修复用的是外部 LLM，**被训练的模型学不到"如何修复"**

❌ **不推荐**

### 5.2 方案 B：展平成独立 Samples（ToolOrchestra 风格）

```
架构：
┌─────────────────────────────────────────────────────────────────┐
│                    Generation Manager (新增)                     │
│   处理 multi-turn 循环，收集所有 turns                           │
└──────────────────────────────────┬──────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VERL Trainer (不改)                           │
│         接收展平的 turns，每个 turn 当成独立 sample 训练         │
└─────────────────────────────────────────────────────────────────┘

数据示例：
  Sample 1 (直接成功):
    prompt: "为 GSM8K 设计 workflow..."
    response: workflow_v1
    reward: 0.8

  Sample 2 (首次失败):
    prompt: "为 GSM8K 设计 workflow..."
    response: workflow_v1 (有 bug)
    reward: 0

  Sample 3 (修复成功):
    prompt: "为 GSM8K 设计 workflow...
             你之前生成的 workflow: {workflow_v1}
             执行报错: {traceback}
             请修复。"
    response: workflow_v2
    reward: 0.9
```

**特点**：
- ✅ 不需要修改 VERL 接口
- ✅ 模型学会两种能力：直接生成 + 错误修复
- ⚠️ Sample 2 和 Sample 3 是独立的（VERL 不知道它们有关联）

✅ **推荐作为初始方案**

### 5.3 方案 C：真正的 Multi-turn Rollout（标准方式）

```
架构：
┌─────────────────────────────────────────────────────────────────┐
│                    实现 AgentLoopBase                            │
│   处理 multi-turn，返回完整 trajectory                          │
└──────────────────────────────────┬──────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VERL Trainer (agent_loop 模式)                │
│         处理完整 trajectory，delta-based tokenization           │
└─────────────────────────────────────────────────────────────────┘

Trajectory 结构：
{
    "prompt_ids": [...],           # 初始 prompt
    "response_ids": [...],         # 所有轮次的 response 拼接
    "response_mask": [1,1,0,0,1,1,...],  # 1=LLM生成, 0=工具输出
    "reward": 0.9                  # 整个 trajectory 的 reward
}
```

**特点**：
- ✅ 架构正确，符合 VERL 官方推荐
- ✅ 利用 delta-based tokenization 优化
- ❌ 需要适配 VERL 的 agent_loop 接口
- ❌ 实现复杂度较高

✅ **推荐作为长期目标**

---

## 6. 推荐方案详解

### 6.1 渐进式实施策略

```
阶段 1（当前）：方案 B - 展平成独立 Samples
  - 快速验证 multi-turn 效果
  - 不修改 VERL trainer
  - 验证模型能否学会"错误修复"

阶段 2（后续）：方案 C - 真正的 Multi-turn Rollout
  - 迁移到 AgentLoopBase 接口
  - 利用 VERL 的优化
  - 支持更复杂的 agent 场景
```

### 6.2 方案 B 详细设计

#### 6.2.1 核心组件：WorkflowGenerationManager

```python
class WorkflowGenerationManager:
    """
    处理 multi-turn workflow 生成和执行。
    负责：
    1. 调用模型生成 workflow
    2. 调用 reward_server 执行 workflow
    3. 处理执行错误，构建修复 prompt
    4. 收集所有 turns 的数据
    5. 计算 reward 并展平返回
    """

    def __init__(
        self,
        tokenizer,
        actor_rollout_wg,  # VERL 的 actor worker group
        reward_server_url: str,
        max_turns: int = 3,
        test_problems_per_workflow: int = 10,
    ):
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.reward_client = RewardClient(reward_server_url)
        self.max_turns = max_turns
        self.test_problems_per_workflow = test_problems_per_workflow

    async def run_generation_loop(
        self,
        gen_batch: DataProto,
        global_steps: int,
    ) -> DataProto:
        """
        主循环：处理一个 batch 的 multi-turn 生成。
        """
        batch_size = len(gen_batch.non_tensor_batch['problem'])
        active_mask = torch.ones(batch_size, dtype=torch.bool)

        # 收集所有 turns 的数据
        all_turns = []

        # 每个样本的历史记录
        histories = [[] for _ in range(batch_size)]

        for turn in range(self.max_turns):
            if not active_mask.sum():
                break

            # 1. 构建 prompts
            prompts = self._build_prompts(gen_batch, histories, active_mask)

            # 2. 调用模型生成
            gen_output = self._generate(prompts, active_mask)

            # 3. 提取 workflow 代码
            workflows = self._extract_workflows(gen_output.responses)

            # 4. 并行执行 workflows
            results = await self._execute_workflows_parallel(
                workflows,
                gen_batch.non_tensor_batch['test_problems'],
                active_mask
            )

            # 5. 收集本轮数据
            turn_data = self._collect_turn_data(
                gen_output, results, turn, active_mask
            )
            all_turns.append(turn_data)

            # 6. 更新状态
            for i, result in enumerate(results):
                if not active_mask[i]:
                    continue
                if result.success:
                    # 成功：标记为完成
                    active_mask[i] = False
                    histories[i].append({
                        'workflow': workflows[i],
                        'result': 'success',
                        'accuracy': result.accuracy,
                    })
                else:
                    # 失败：记录错误，下一轮继续
                    histories[i].append({
                        'workflow': workflows[i],
                        'result': 'error',
                        'error': result.error,
                        'traceback': result.traceback,
                    })

        # 7. 计算 reward
        rewards = self._compute_rewards(all_turns, histories)

        # 8. 展平并返回
        return self._flatten_turns(all_turns, rewards)
```

#### 6.2.2 Prompt 构建策略

```python
def _build_prompts(self, gen_batch, histories, active_mask):
    """
    构建每个样本的 prompt。

    首次生成：标准 prompt
    修复生成：包含之前的 workflow 和错误信息
    """
    prompts = []

    for i in range(len(active_mask)):
        if not active_mask[i]:
            prompts.append(None)
            continue

        base_prompt = gen_batch.non_tensor_batch['prompt'][i]

        if len(histories[i]) == 0:
            # 首次生成
            prompts.append(base_prompt)
        else:
            # 修复生成
            last_attempt = histories[i][-1]
            fix_prompt = f"""{base_prompt}

你之前生成的 workflow:
```python
{last_attempt['workflow']}
```

执行时报错:
```
{last_attempt['traceback']}
```

请分析错误原因并修复 workflow。注意：
1. 仔细阅读错误信息
2. 检查变量名、函数调用、数据类型
3. 生成完整的修正后 workflow
"""
            prompts.append(fix_prompt)

    return prompts
```

#### 6.2.3 并行执行 Workflows

```python
async def _execute_workflows_parallel(
    self,
    workflows: List[str],
    test_problems: List[List[dict]],
    active_mask: torch.Tensor
) -> List[ExecutionResult]:
    """
    并行执行多个 workflows，每个 workflow 在多个测试问题上运行。
    """
    tasks = []

    for i, (workflow, problems) in enumerate(zip(workflows, test_problems)):
        if not active_mask[i]:
            tasks.append(None)
            continue

        # 创建执行任务
        task = self.reward_client.execute_workflow(
            workflow_code=workflow,
            test_problems=problems[:self.test_problems_per_workflow],
        )
        tasks.append(task)

    # 并行执行
    results = await asyncio.gather(*[t for t in tasks if t is not None])

    # 填充结果
    full_results = []
    result_idx = 0
    for i in range(len(workflows)):
        if not active_mask[i]:
            full_results.append(ExecutionResult(success=False, skipped=True))
        else:
            full_results.append(results[result_idx])
            result_idx += 1

    return full_results
```

#### 6.2.4 Reward 计算

```python
def _compute_rewards(self, all_turns, histories):
    """
    计算每个 turn 的 reward。

    策略：
    1. 首先计算每个 trajectory 的最终 reward（基于最终准确率）
    2. 同一个问题的多个 rollout 进行 GRPO 归一化
    3. 每个 turn 获得其所属 trajectory 的 reward
    """
    # 1. 计算 trajectory 级别的 reward
    trajectory_rewards = {}
    for i, history in enumerate(histories):
        if len(history) > 0 and history[-1]['result'] == 'success':
            trajectory_rewards[i] = history[-1]['accuracy']
        else:
            trajectory_rewards[i] = 0.0

    # 2. GRPO 归一化（如果有多个 rollout）
    # ... 省略归一化代码 ...

    # 3. 分配到每个 turn
    turn_rewards = []
    for turn_data in all_turns:
        for sample_idx in turn_data['sample_indices']:
            turn_rewards.append(trajectory_rewards[sample_idx])

    return turn_rewards
```

#### 6.2.5 数据展平

```python
def _flatten_turns(self, all_turns, rewards) -> DataProto:
    """
    将所有 turns 展平成 VERL 需要的格式。
    """
    all_input_ids = []
    all_attention_mask = []
    all_responses = []
    all_indices = []
    all_turn_ids = []

    reward_idx = 0
    for turn_id, turn_data in enumerate(all_turns):
        for i in range(len(turn_data['input_ids'])):
            all_input_ids.append(turn_data['input_ids'][i])
            all_attention_mask.append(turn_data['attention_mask'][i])
            all_responses.append(turn_data['responses'][i])
            all_indices.append(turn_data['sample_indices'][i])
            all_turn_ids.append(turn_id)

    return DataProto.from_dict({
        'input_ids': torch.stack(all_input_ids),
        'attention_mask': torch.stack(all_attention_mask),
        'responses': torch.stack(all_responses),
        'index': np.array(all_indices),
        'turn_id': np.array(all_turn_ids),
        'reward': np.array(rewards),
    })
```

---

## 7. 与 Reward Server 的集成

### 7.1 Reward Server 需要返回的信息

```python
# 当前 reward_server 返回
{
    "success": True,
    "score": 0.8,
}

# 需要扩展为
{
    "success": True,           # 是否执行成功（无报错）
    "score": 0.8,              # 如果成功，在测试问题上的准确率
    "error": None,             # 如果失败，错误类型
    "traceback": "...",        # 详细的 traceback（用于下一轮 prompt）
    "details": {               # 详细信息
        "total_problems": 10,
        "correct_problems": 8,
        "failed_problems": [
            {"id": 3, "error": "计算错误", "expected": "42", "got": "40"},
            {"id": 7, "error": "格式错误", "expected": "12", "got": "twelve"},
        ]
    }
}
```

### 7.2 Reward Server 的修改点

```python
# services/reward_server/server.py

class RewardRequest(BaseModel):
    workflow_code: str
    test_problems: List[Dict]  # 新增：测试问题列表
    timeout: int = 60

class RewardResponse(BaseModel):
    success: bool
    score: float
    error: Optional[str] = None
    traceback: Optional[str] = None
    details: Optional[Dict] = None

@app.post("/compute_reward")
async def compute_reward(request: RewardRequest) -> RewardResponse:
    try:
        # 执行 workflow
        results = await execute_workflow_on_problems(
            request.workflow_code,
            request.test_problems,
            timeout=request.timeout
        )

        # 计算准确率
        correct = sum(1 for r in results if r.correct)
        accuracy = correct / len(results)

        return RewardResponse(
            success=True,
            score=accuracy,
            details={
                "total_problems": len(results),
                "correct_problems": correct,
                "failed_problems": [
                    {"id": r.id, "error": r.error}
                    for r in results if not r.correct
                ]
            }
        )
    except Exception as e:
        return RewardResponse(
            success=False,
            score=0.0,
            error=str(e),
            traceback=traceback.format_exc(),
        )
```

### 7.3 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERL Trainer                                  │
│                                                                  │
│   for step in training_steps:                                    │
│       batch = dataloader.next()                                  │
│       gen_output = generation_manager.run_generation_loop(batch) │
│       loss = compute_ppo_loss(gen_output)                        │
│       optimizer.step()                                           │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│              WorkflowGenerationManager (新增)                    │
│                                                                  │
│   for turn in range(max_turns):                                  │
│       prompts = build_prompts(histories)                         │
│       workflows = model.generate(prompts)                        │
│       results = reward_server.execute(workflows)  ──────────┐    │
│       update_histories(results)                              │    │
│                                                              │    │
│   return flatten_turns(all_turns, rewards)                   │    │
└──────────────────────────────────────────────────────────────│───┘
                                                               │
                                                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Reward Server (扩展)                          │
│                                                                  │
│   POST /compute_reward                                           │
│   {                                                              │
│       workflow_code: "...",                                      │
│       test_problems: [...]                                       │
│   }                                                              │
│   → 并行执行 workflow 在多个问题上                               │
│   → 返回 {success, score, error, traceback, details}            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 关键设计决策

### 8.1 决策 1：执行层 vs 优化层 Multi-turn

**决策**：当前只实现执行层 multi-turn

**理由**：
- 执行层是必须的（否则无法获得有效 reward）
- 优化层对于 RL 训练不必要（让 RL 自己学习）
- 简化实现复杂度

### 8.2 决策 2：展平 vs 保持 Trajectory

**决策**：采用展平方案（方案 B）

**理由**：
- 快速验证，不需要深度修改 VERL
- ToolOrchestra 已验证可行
- 后续可迁移到标准方式（方案 C）

### 8.3 决策 3：Reward 分配策略

**决策**：同一 trajectory 的所有 turns 获得相同 reward

**理由**：
- 符合 ToolOrchestra 的做法
- 简单且直观
- 后续可探索更精细的 credit assignment

### 8.4 决策 4：并行测试多个问题

**决策**：每个 workflow 在 N 个问题上并行测试

**理由**：
- 验证 workflow 的泛化能力
- 单个问题的结果可能有噪声
- N=10 是一个合理的平衡点

### 8.5 决策 5：最大轮次限制

**决策**：max_turns = 3

**理由**：
- 大多数错误可以在 2-3 轮内修复
- 避免无限循环
- 后续可根据实验调整

---

## 9. 实施路线图

### 9.1 Phase 1：基础 Multi-turn 支持（当前）

- [ ] 扩展 Reward Server 返回 error/traceback
- [ ] 实现 WorkflowGenerationManager
- [ ] 实现 prompt 构建策略
- [ ] 实现 reward 计算和展平
- [ ] 集成到 VERL trainer

### 9.2 Phase 2：优化和验证

- [ ] 并行执行优化（异步 + 批处理）
- [ ] 实验验证：multi-turn vs single-turn 效果对比
- [ ] 调整超参数（max_turns, test_problems_per_workflow）
- [ ] 错误分类和针对性 prompt 优化

### 9.3 Phase 3：迁移到标准方式（可选）

- [ ] 研究 VERL AgentLoopBase 接口
- [ ] 实现 WorkflowAgentLoop
- [ ] 利用 delta-based tokenization 优化
- [ ] 对比两种方式的训练效果

### 9.4 Phase 4：高级功能（远期）

- [ ] 优化层 multi-turn（推理时迭代改进）
- [ ] 更精细的 credit assignment
- [ ] 支持更复杂的 workflow 结构
- [ ] Multi-agent 协作

---

## 附录

### A. 参考资料

1. [VERL 官方文档 - Multi-turn Rollout](https://verl.readthedocs.io/en/latest/sglang_multiturn/multiturn.html)
2. [VERL 官方文档 - Agent Loop](https://verl.readthedocs.io/en/latest/advance/agent_loop.html)
3. [verl-tool GitHub](https://github.com/TIGER-AI-Lab/verl-tool)
4. [VerlTool 论文](https://arxiv.org/abs/2509.01055)
5. [VERL GitHub](https://github.com/volcengine/verl)
6. [ToolOrchestra 代码](training/lead_agent/llm_agent/generation_quick3.py)

### B. 术语表

| 术语 | 定义 |
|------|------|
| **Turn** | 一次模型生成 + 执行的循环 |
| **Trajectory** | 一个问题从开始到结束的完整交互序列 |
| **Rollout** | 一次完整的数据采样过程 |
| **Active Mask** | 标记哪些样本还需要继续处理 |
| **Delta-based Tokenization** | 只对新增内容进行 tokenization |

### C. 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2024-12-24 | 初始版本，记录 multi-turn 实现方案讨论 |
