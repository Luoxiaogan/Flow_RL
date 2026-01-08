# ToolOrchestra 自定义实现模块详解

> 本文档详细说明 ToolOrchestra 项目中不遵循 veRL 官方接口的自定义实现，包括 lead_agent、recipe、rollout(tau2) 三大模块。

**文档版本**: 1.0
**最后更新**: 2026-01-08

---

## 📋 目录

1. [总览](#总览)
2. [Lead Agent 模块](#1-lead-agent-模块)
3. [Recipe 模块](#2-recipe-模块)
4. [Rollout (tau2) 模块](#3-rollout-tau2-模块)
5. [架构对比与设计原理](#架构对比与设计原理)

---

## 总览

ToolOrchestra 在标准 veRL 框架基础上，添加了三大自定义模块以支持 Multi-turn 工具调用训练：

| 模块 | 路径 | 核心职责 | 与 veRL 关系 | 代码量 |
|------|------|----------|-------------|--------|
| **Lead Agent** | `training/lead_agent/` | Multi-turn 生成 + 工具调用管理 | ❌ 完全自定义 | ~2500 行 |
| **Recipe** | `training/recipe/` | GRPO/DAPO 训练算法入口 | ⚠️ 扩展 veRL | ~1350 行 |
| **Rollout (tau2)** | `training/rollout/tau2/` | 多域任务执行和评估框架 | ❌ 完全独立 | ~8000+ 行 |

### 调用关系链

```
main_grpo_quick3.py (训练入口)
    ↓
RayGRPOTrainer.fit() (扩展 veRL)
    ↓
LLMGenerationManager.run_llm_loop() (自定义)
    ├─ actor_rollout_wg.generate_sequences() (调用 veRL)
    ├─ 工具调用执行 (自定义)
    └─ Reward 计算 (自定义)
    ↓
返回 DataProto → veRL 标准流程
    ├─ compute_log_prob() (veRL)
    ├─ compute_advantage() (veRL)
    └─ update_actor/critic() (veRL)
```

---

## 1. Lead Agent 模块

**位置**: `.reference_projects/ToolOrchestra/training/lead_agent/`

**核心职责**: 实现 Multi-turn LLM 生成循环，管理工具调用和 Reward 计算。

### 目录结构

```
training/lead_agent/
├── __init__.py
└── llm_agent/
    ├── __init__.py
    ├── generation_quick3.py          ⭐ 核心：多轮生成管理器
    ├── tensor_helper.py              工具：Tensor 处理
    └── tools.py                      工具：查询和答案生成器
```

---

### 1.1 generation_quick3.py

**文件位置**: `training/lead_agent/llm_agent/generation_quick3.py`
**代码行数**: ~2150 行
**核心类**: `LLMGenerationManager`, `GenerationConfig`

#### 核心数据结构

```python
@dataclass
class GenerationConfig:
    """生成配置"""
    max_turns: int = 10                # 最大轮次
    max_prompt_length: int = 4096      # 最大提示词长度
    max_response_length: int = 2048    # 最大响应长度
    num_gpus: int = 8                  # GPU 数量
    search_url: str = "http://..."     # 搜索服务 URL
    topk: int = 5                      # 检索 Top-K
```

#### 核心类和方法

```python
class LLMGenerationManager:
    """LLM 生成管理器"""

    def __init__(self, tokenizer, actor_rollout_wg, config,
                 train_tool_config_path, test_tool_config_path):
        """
        参数:
            tokenizer: HuggingFace tokenizer
            actor_rollout_wg: veRL 的 Actor Worker Group
            config: GenerationConfig
            train_tool_config_path: 训练时的工具配置
            test_tool_config_path: 测试时的工具配置
        """
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.config = config

        # 加载工具配置（search, sandbox, etc.）
        with open(train_tool_config_path) as f:
            self.train_tools = json.load(f)

    def run_llm_loop(self, gen_batch, tokenizer_config, global_steps,
                     topk_doc, use_llm_reward, efficiency_reward,
                     exp_tag, use_qa_reward):
        """
        核心方法：运行多轮 LLM 生成循环

        输入:
            gen_batch: DataToolProto（包含问题、任务信息）
            tokenizer_config: Tokenizer 配置字典
            global_steps: 当前训练步数
            topk_doc: 检索文档数量
            use_llm_reward: 是否使用 LLM 评估 Reward
            efficiency_reward: 是否使用效率奖励（成本+延迟）
            exp_tag: 实验标签
            use_qa_reward: 是否使用 QA Reward

        输出:
            final_gen_batch_output: 最终生成结果（DataToolProto）
            tool_avg: 工具使用统计字典

        流程:
            1. 初始化状态（active_mask, documents, code, attempts）
            2. 多轮循环（max_turns）
               a. 构建带历史的 prompt
               b. Tokenize 和 GPU 生成（调用 veRL Actor）
               c. 后处理和工具调用
               d. 执行工具并收集结果
               e. 更新 active_mask（标记完成的样本）
            3. 计算 Reward（GRPO 归一化）
            4. 返回结果
        """

        # 1. 初始化状态
        loop_batch_size = len(gen_batch.non_tensor_batch['problem'])
        active_mask = torch.ones(loop_batch_size, dtype=torch.bool)

        retrieved_documents = [[] for _ in range(loop_batch_size)]
        code_snippets = [[] for _ in range(loop_batch_size)]
        attempts = [[] for _ in range(loop_batch_size)]
        total_costs = [0 for _ in range(loop_batch_size)]
        total_latency = [0 for _ in range(loop_batch_size)]

        # 2. Multi-turn 循环
        for step in range(self.config.max_turns):
            if not active_mask.sum():
                break

            # 2.1 构建 prompt（包含累积的 context）
            prompts = self._build_prompts_with_history(
                gen_batch, retrieved_documents, code_snippets, attempts
            )

            # 2.2 Tokenize
            input_ids, attention_mask = self._tokenize_prompts(prompts)

            # 2.3 GPU 生成（调用 veRL Actor）
            gen_output = self._generate_with_gpu_padding(
                DataToolProto.from_dict({
                    'input_ids': input_ids,
                    'attention_mask': attention_mask,
                }, non_tensors={
                    'active_mask': active_mask.numpy(),
                })
            )

            # 2.4 后处理：提取工具调用
            predictions = self.tokenizer.batch_decode(gen_output.batch['responses'])
            tool_calls, format_corrects = self.postprocess_predictions(
                predictions, gen_batch.non_tensor_batch['category']
            )

            # 2.5 执行工具
            new_documents, new_code, new_attempts, dones, costs, latency = \
                self.execute_predictions(
                    tool_calls, gen_batch, step, global_steps
                )

            # 2.6 累积结果
            for i in range(loop_batch_size):
                if active_mask[i]:
                    retrieved_documents[i] += new_documents[i]
                    code_snippets[i] += new_code[i]
                    attempts[i] += new_attempts[i]
                    total_costs[i] += costs[i]
                    total_latency[i] += latency[i]

            # 2.7 更新 active_mask
            curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
            active_mask = active_mask * curr_active_mask

        # 3. 计算 Reward
        rewards = self._compute_rewards(
            correctness_dict, total_costs, total_latency, efficiency_reward
        )

        # 4. 构建最终输出
        final_gen_batch_output = self._create_final_batch(
            gen_batch, prompts, responses, rewards
        )

        return final_gen_batch_output, tool_avg

    def _generate_with_gpu_padding(self, batch):
        """
        调用 veRL 的 Actor Worker 进行生成

        这是与 veRL 框架的唯一交互点
        """
        return self.actor_rollout_wg.generate_sequences(batch)

    def execute_predictions(self, predictions, categories, gen_batch, step, global_steps):
        """
        执行工具调用预测

        支持的工具:
            - enhance_reasoning: 调用推理模型生成代码并执行
            - search: 调用检索服务获取文档
            - answer: 调用答案模型生成最终答案

        返回:
            new_documents: 每个样本新检索的文档列表
            new_code: 每个样本新执行的代码及输出
            new_attempts: 每个样本新的答案尝试
            dones: 每个样本是否完成的标志
            costs: 每个样本本轮的 API 成本
            latency: 每个样本本轮的延迟
        """
        # 实现略（详见源代码）
        pass

    def postprocess_predictions(self, predictions, all_categories):
        """
        后处理模型输出，提取 JSON 格式的工具调用

        期望格式:
            <think>推理过程</think>
            <tool_call>
            {"name": "enhance_reasoning", "arguments": {"model": "reasoner-1"}}
            </tool_call>

        验证:
            1. 提取 <tool_call>...</tool_call> 之间的内容
            2. 解析 JSON
            3. 验证工具名称在 ALL_TOOLS 中
            4. 验证参数名称和值符合工具签名

        返回:
            all_tool_calls: 每个样本的工具调用列表
            format_corrects: 每个样本的格式是否正确
        """
        all_tool_calls = []
        format_corrects = []

        for prediction, category in zip(predictions, all_categories):
            cur_all_tool_calls = []
            format_correct = False

            if isinstance(prediction, str):
                if category == 'qa':
                    # 提取 <tool_call> 标签
                    components = prediction.split('<tool_call>')
                    for c in components:
                        components1 = c.split('</tool_call>')
                        for c1 in components1:
                            try:
                                # 尝试解析 JSON
                                tmp_tool_call = json.loads(c1)

                                # 验证格式
                                assert set(list(tmp_tool_call.keys())) == {"name", "arguments"}
                                assert tmp_tool_call['name'] in ALL_TOOLS

                                # 验证参数
                                func_signature = ALL_TOOLS[tmp_tool_call['name']]
                                for parameter_name, parameter_values in func_signature.items():
                                    assert tmp_tool_call["arguments"][parameter_name] in parameter_values or parameter_values == 'any'

                                cur_all_tool_calls.append(tmp_tool_call)
                            except:
                                pass  # 跳过格式错误的工具调用

                    if len(cur_all_tool_calls) > 0:
                        format_correct = True

            all_tool_calls.append(cur_all_tool_calls)
            format_corrects.append(format_correct)

        return all_tool_calls, format_corrects

    def _compute_rewards(self, example_correctness, example_costs,
                         example_latency, efficiency_reward):
        """
        计算 GRPO 归一化的 Reward

        公式:
            1. Outcome + Efficiency Reward:
               if correct:
                   cost_reward = cost * 5
                   latency_reward = latency / 500
                   raw_reward = 1 - cost_reward - latency_reward
               else:
                   raw_reward = 0

            2. GRPO 归一化（组内标准化）:
               normalized_reward = (raw_reward - group_mean) / (group_std + 1e-6)
               normalized_reward = clip(normalized_reward, -3, 3)

        返回:
            rewards: Tensor of shape [batch_size]
        """
        # 实现略（详见源代码 line 1405-1513）
        pass
```

#### 关键设计决策

| 问题 | 解决方案 | 原因 |
|------|---------|------|
| **Multi-turn 如何实现？** | `for step in range(max_turns)` 循环 | veRL 标准流程只支持单轮生成 |
| **如何累积上下文？** | 字符串拼接 `doc_str + code_str + attempt_str` | 每轮需要看到之前所有结果 |
| **如何追踪完成状态？** | `active_mask` Tensor | Batch 内不同样本完成时间不同 |
| **如何处理格式错误？** | `try-except` 包裹，`format_correct=False` | 训练中模型会生成错误格式，不应崩溃 |
| **如何与 veRL 交互？** | 只调用 `actor_rollout_wg.generate_sequences()` | 最小化对 veRL 的依赖 |

#### 调用位置

**被调用**: `training/recipe/algo/grpo_ray_trainer_quick3.py:386`

```python
class RayGRPOTrainer(RayPPOTrainer):
    def fit(self):
        # 初始化 GenerationManager
        generation_manager = LLMGenerationManager(...)

        for batch_dict in self.train_dataloader:
            # ⭐ 调用 multi-turn 生成
            final_gen_batch_output, tool_avg = generation_manager.run_llm_loop(
                gen_batch=batch,
                ...
            )
```

---

### 1.2 tools.py

**文件位置**: `training/lead_agent/llm_agent/tools.py`
**代码行数**: ~116 行
**核心类**: `QueryWriter`, `AnswerGenerator`

#### QueryWriter

```python
class QueryWriter:
    """查询生成器：从文档生成搜索查询"""

    def __init__(self, model='o3'):
        self.model = model

    def execute(self, prompt_dict: dict) -> dict:
        """
        输入:
            documents: 当前文档列表
            user_question: 用户问题

        输出:
            query: 生成的搜索查询
            think: 推理过程

        示例:
            输入: {
                "documents": ["文档1内容", "文档2内容"],
                "user_question": "如何计算面积？"
            }

            输出: {
                "query": "长方形面积计算公式",
                "think": "用户想了解面积计算，需要搜索相关数学公式"
            }
        """
        documents = prompt_dict.get('documents', [])
        question = prompt_dict['user_question']

        # 构建 prompt
        doc_str = '\n\n'.join(f"Doc {i+1}: {doc}" for i, doc in enumerate(documents))
        prompt = f"""
        已有文档:
        {doc_str}

        用户问题: {question}

        请生成一个搜索查询以获取更多相关信息。

        输出格式:
        <think>你的推理过程</think>
        <query>搜索查询</query>
        """

        # 调用 LLM
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = get_llm_response(model=self.model, messages=messages)

        # 提取 query
        query = self._extract_between_tags(response, 'query')
        think = self._extract_between_tags(response, 'think')

        return {"query": query, "think": think}

    def _extract_between_tags(self, text, tag):
        """提取 XML 标签之间的内容"""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = text.find(start_tag)
        end = text.find(end_tag)
        if start != -1 and end != -1:
            return text[start + len(start_tag):end].strip()
        return ""
```

#### AnswerGenerator

```python
class AnswerGenerator:
    """答案生成器：从文档生成最终答案"""

    def __init__(self, model='o3'):
        self.model = model

    def execute(self, prompt_dict: dict) -> dict:
        """
        输入:
            documents: 检索到的文档
            code_results: 代码执行结果（可选）
            user_question: 用户问题

        输出:
            answer: 最终答案
            think: 推理过程
        """
        documents = prompt_dict.get('documents', [])
        code_results = prompt_dict.get('code_results', [])
        question = prompt_dict['user_question']

        # 构建 prompt
        doc_str = '\n\n'.join(f"Doc {i+1}: {doc}" for i, doc in enumerate(documents))
        code_str = '\n\n'.join(
            f"```python\n{c['code']}\n```\n```output\n{c['output']}\n```"
            for c in code_results
        )

        prompt = f"""
        参考资料:
        {doc_str}

        代码执行结果:
        {code_str}

        用户问题: {question}

        请给出最终答案。

        输出格式:
        <think>你的推理过程</think>
        <answer>最终答案</answer>
        """

        # 调用 LLM
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = get_llm_response(model=self.model, messages=messages)

        # 提取 answer
        answer = self._extract_between_tags(response, 'answer')
        think = self._extract_between_tags(response, 'think')

        return {"answer": answer, "think": think}
```

#### 工具注册

```python
TOOLS_MAP = {
    "query_writer": QueryWriter,
    "answer_generator": AnswerGenerator,
}
```

**为什么需要这些工具？**

1. **QueryWriter**: 实现迭代检索（根据已有文档判断是否需要更多信息）
2. **AnswerGenerator**: 综合多种信息源（文档 + 代码）生成答案
3. **XML 标签**: 结构化输出，便于解析和验证

---

### 1.3 tensor_helper.py

**文件位置**: `training/lead_agent/llm_agent/tensor_helper.py`
**代码行数**: ~95 行
**核心类**: `TensorHelper`, `TensorConfig`

#### TensorConfig

```python
@dataclass
class TensorConfig:
    """Tensor 配置"""
    pad_token_id: int
    bos_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
```

#### TensorHelper

```python
class TensorHelper:
    """Tensor 辅助工具（用于 Multi-turn 的 padding 和拼接）"""

    def __init__(self, config: TensorConfig):
        self.pad_token_id = config.pad_token_id
        self.bos_token_id = config.bos_token_id
        self.eos_token_id = config.eos_token_id

    def cut_to_effective_len(self, input_ids: torch.Tensor,
                             attention_mask: torch.Tensor):
        """
        裁剪 padding

        输入:
            input_ids: [batch, seq_len]
            attention_mask: [batch, seq_len]

        输出:
            input_ids: [batch, effective_len]  # 移除 padding
            attention_mask: [batch, effective_len]
        """
        # 找到最大有效长度
        effective_lens = attention_mask.sum(dim=-1)
        max_effective_len = effective_lens.max().item()

        # 裁剪
        return input_ids[:, :max_effective_len], attention_mask[:, :max_effective_len]

    def convert_pad_structure(self, input_ids, attention_mask, to_left_pad: bool):
        """
        转换 padding 方向

        参数:
            to_left_pad: True=转为左填充, False=转为右填充

        示例:
            右填充: [1, 2, 3, 0, 0]
            左填充: [0, 0, 1, 2, 3]
        """
        if to_left_pad:
            # 右填充 → 左填充
            for i in range(len(input_ids)):
                effective_len = attention_mask[i].sum().item()
                input_ids[i] = torch.cat([
                    input_ids[i, -effective_len:],  # 有效内容
                    input_ids[i, :-effective_len],  # padding
                ])
                attention_mask[i] = torch.cat([
                    attention_mask[i, -effective_len:],
                    attention_mask[i, :-effective_len],
                ])
        else:
            # 左填充 → 右填充（逻辑类似）
            pass

        return input_ids, attention_mask

    def create_attention_mask(self, input_ids: torch.Tensor):
        """
        生成 attention mask

        输入: input_ids: [batch, seq_len]
        输出: attention_mask: [batch, seq_len]

        规则: 1 表示有效 token，0 表示 padding
        """
        return (input_ids != self.pad_token_id).long()

    def create_position_ids(self, attention_mask: torch.Tensor):
        """
        生成 position IDs

        输入: attention_mask: [batch, seq_len]
        输出: position_ids: [batch, seq_len]

        示例:
            attention_mask: [0, 0, 1, 1, 1]
            position_ids:   [0, 0, 0, 1, 2]
        """
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids.masked_fill_(attention_mask == 0, 0)
        return position_ids

    def concatenate_with_padding(self, prompt_ids, response_ids,
                                  prompt_mask, response_mask, left_pad=True):
        """
        拼接 prompt 和 response（处理 padding）

        步骤:
            1. 移除 prompt 的右侧 padding（如果是左填充）
            2. 拼接 response
            3. 重新添加 padding 对齐 batch

        参数:
            prompt_ids: [batch, prompt_len]
            response_ids: [batch, response_len]
            left_pad: 是否使用左填充

        输出:
            combined_ids: [batch, prompt_len + response_len]
            combined_mask: [batch, prompt_len + response_len]
        """
        batch_size = prompt_ids.shape[0]
        combined_ids = []
        combined_masks = []

        for i in range(batch_size):
            # 提取有效部分
            prompt_effective_len = prompt_mask[i].sum().item()
            response_effective_len = response_mask[i].sum().item()

            if left_pad:
                # 左填充：有效内容在右侧
                prompt_effective = prompt_ids[i, -prompt_effective_len:]
                response_effective = response_ids[i, -response_effective_len:]
            else:
                # 右填充：有效内容在左侧
                prompt_effective = prompt_ids[i, :prompt_effective_len]
                response_effective = response_ids[i, :response_effective_len]

            # 拼接
            combined = torch.cat([prompt_effective, response_effective])
            combined_ids.append(combined)
            combined_masks.append(torch.ones_like(combined))

        # Padding 到最大长度
        max_len = max(len(ids) for ids in combined_ids)
        padded_ids = []
        padded_masks = []

        for ids, mask in zip(combined_ids, combined_masks):
            pad_len = max_len - len(ids)
            if left_pad:
                padded_ids.append(torch.cat([
                    torch.full((pad_len,), self.pad_token_id, dtype=ids.dtype),
                    ids
                ]))
                padded_masks.append(torch.cat([
                    torch.zeros(pad_len, dtype=mask.dtype),
                    mask
                ]))
            else:
                padded_ids.append(torch.cat([
                    ids,
                    torch.full((pad_len,), self.pad_token_id, dtype=ids.dtype)
                ]))
                padded_masks.append(torch.cat([
                    mask,
                    torch.zeros(pad_len, dtype=mask.dtype)
                ]))

        return torch.stack(padded_ids), torch.stack(padded_masks)
```

**为什么需要 TensorHelper？**

| 场景 | 问题 | 解决方案 |
|------|------|---------|
| **Multi-turn 拼接** | 每轮需要拼接新的 response 到 prompt | `concatenate_with_padding()` |
| **Padding 方向** | veRL 可能使用左填充，其他服务使用右填充 | `convert_pad_structure()` |
| **动态长度** | Batch 内样本长度不同 | `cut_to_effective_len()` + padding |

---

## 2. Recipe 模块

**位置**: `.reference_projects/ToolOrchestra/training/recipe/`

**核心职责**: 扩展 veRL 的 Trainer，添加 Multi-turn 支持和自定义 Reward 函数。

### 目录结构

```
training/recipe/
├── algo/                             GRPO 算法
│   ├── main_grpo_quick3.py          ⭐ 训练入口
│   ├── grpo_ray_trainer_quick3.py   ⭐ Ray 分布式 Trainer
│   └── config/
│       └── grpo_trainer.yaml        配置文件
│
└── dapo/                             DAPO 算法
    ├── main_dapo.py                 ⭐ 训练入口
    ├── dapo_ray_trainer.py          ⭐ Ray 分布式 Trainer
    ├── config/
    │   └── dapo_trainer.yaml        配置文件
    └── test_dapo_*.sh               测试脚本（6个）
```

---

### 2.1 GRPO 算法实现

#### main_grpo_quick3.py

**文件位置**: `training/recipe/algo/main_grpo_quick3.py`
**代码行数**: ~230 行
**核心职责**: GRPO 训练的主入口

```python
import hydra
from omegaconf import DictConfig
from transformers import AutoTokenizer
from verl.workers.fsdp_workers import ActorRolloutRefWorker, CriticWorker
from verl.workers.megatron_workers import ActorRolloutRefWorker as MegatronActorRolloutRefWorker
from .grpo_ray_trainer_quick3 import RayGRPOTrainer

@hydra.main(config_path='config', config_name='grpo_trainer', version_base=None)
def main(config: DictConfig):
    """
    GRPO 训练主函数

    配置文件: recipe/algo/config/grpo_trainer.yaml
    """

    # 1. 定义 Reward 函数
    def compute_score_em(data: DataProto) -> torch.Tensor:
        """
        计算格式分数（验证 <think> 和 <answer> 标签）

        验证规则:
            1. 必须包含 <think>...</think>
            2. 必须包含 <answer>...</answer>
            3. <answer> 内容必须是 '1' 或 '2'
               - 1 = 调用 query_writer
               - 2 = 调用 answer_generator

        返回:
            scores: Tensor of shape [batch_size]
                   1.0 = 格式正确
                   0.0 = 格式错误
        """
        responses = data.batch['responses']  # 模型生成的输出
        scores = []

        for response in responses:
            response_str = tokenizer.decode(response, skip_special_tokens=True)

            # 检查 <think> 标签
            if '<think>' in response_str and '</think>' in response_str:
                # 检查 <answer> 标签
                if '<answer>' in response_str and '</answer>' in response_str:
                    # 提取 answer 内容
                    start = response_str.find('<answer>') + len('<answer>')
                    end = response_str.find('</answer>')
                    answer = response_str[start:end].strip()

                    # 验证 answer 是 1 或 2
                    if answer in ['1', '2']:
                        scores.append(1.0)
                    else:
                        scores.append(0.0)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)

        return torch.tensor(scores)

    # 2. Reward Manager（管理奖励信号）
    class RewardManager:
        """
        奖励管理器

        优先级:
            1. 如果 batch 中有 'rm_scores'（来自 generation_quick3），使用它
            2. 否则，从 non_tensor_batch 读取预计算的 reward
        """
        def __call__(self, data: DataProto, global_step: int):
            if 'rm_scores' in data.batch:
                return data.batch['rm_scores']
            else:
                # 从 non_tensor_batch 读取
                rewards = []
                for item in data.non_tensor_batch:
                    rewards.append(item.get('reward', 0.0))
                return torch.tensor(rewards)

    # 3. 初始化 Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.model.path,
        trust_remote_code=True
    )

    # 4. 选择分布式策略
    if config.actor_rollout_ref.actor.strategy == "fsdp":
        from verl.workers.fsdp_workers import ActorRolloutRefWorker, CriticWorker
        from verl.single_controller.ray import RayWorkerGroup
        ray_worker_group_cls = RayWorkerGroup
    elif config.actor_rollout_ref.actor.strategy == "megatron":
        from verl.workers.megatron_workers import ActorRolloutRefWorker, CriticWorker
        from verl.single_controller.ray.megatron import NVMegatronRayWorkerGroup
        ray_worker_group_cls = NVMegatronRayWorkerGroup
    else:
        raise ValueError(f"Unknown strategy: {config.actor_rollout_ref.actor.strategy}")

    # 5. 设置 Worker 映射
    role_worker_mapping = {
        'actor_rollout': ActorRolloutRefWorker,
        'critic': CriticWorker,
        'ref_policy': ActorRolloutRefWorker,
    }

    # 6. 创建 Trainer（⭐ 自定义的 RayGRPOTrainer）
    trainer = RayGRPOTrainer(
        config=config,
        tokenizer=tokenizer,
        role_worker_mapping=role_worker_mapping,
        reward_fn=RewardManager(),  # 自定义奖励函数
        ray_worker_group_cls=ray_worker_group_cls,
    )

    # 7. 初始化 Workers 并训练
    trainer.init_workers()
    trainer.fit()

if __name__ == '__main__':
    main()
```

**关键创新点**:

1. **自定义 Reward Manager**: 支持从 generation_quick3 传递的动态 reward
2. **格式验证**: `compute_score_em()` 确保模型输出符合预期格式
3. **灵活的分布式策略**: 支持 FSDP 和 Megatron

---

#### grpo_ray_trainer_quick3.py

**文件位置**: `training/recipe/algo/grpo_ray_trainer_quick3.py`
**代码行数**: ~501 行
**核心类**: `DataToolProto`, `JsonlDataset`, `RayGRPOTrainer`

##### 1. DataToolProto（扩展 veRL 的 DataProto）

```python
from verl import DataProto
from tensordict import TensorDict
import numpy as np

class DataToolProto(DataProto):
    """
    扩展 veRL 的 DataProto，支持非 Tensor 数据

    veRL 原版只支持:
        batch: TensorDict (所有数据必须是 Tensor)

    ToolOrchestra 扩展:
        batch: TensorDict (Tensor 数据)
        non_tensor_batch: Dict[str, np.ndarray[object]] (非 Tensor 数据)

    用途:
        - 传递问题文本（字符串）
        - 传递 vLLM 模型配置（字典）
        - 传递任务类型（'qa' 或 'func_call'）
    """

    @classmethod
    def from_dict(cls, tensors, non_tensors=None, meta_info=None,
                  num_batch_dims=1, auto_padding=False):
        """
        从字典创建 DataToolProto

        参数:
            tensors: Dict[str, Tensor]
                例: {
                    'input_ids': Tensor([batch, seq_len]),
                    'attention_mask': Tensor([batch, seq_len]),
                }

            non_tensors: Dict[str, List]
                例: {
                    'problem': ['问题1', '问题2', ...],
                    'category': ['qa', 'qa', ...],
                    'vllm_model_configs': [{...}, {...}, ...],
                }

            meta_info: Dict (可选)
            num_batch_dims: int (batch 维度数量，默认 1)

        返回:
            DataToolProto 实例
        """
        if non_tensors is None:
            non_tensors = {}
        if meta_info is None:
            meta_info = {}

        # 验证 batch size 一致性
        batch_size = None
        for key, tensor in tensors.items():
            if batch_size is None:
                batch_size = tensor.shape[:num_batch_dims]
            else:
                current_batch = tensor.shape[:num_batch_dims]
                assert batch_size == current_batch, \
                    f"Batch size mismatch: {key} has {current_batch}, expected {batch_size}"

        for key, val in non_tensors.items():
            if batch_size is None:
                batch_size = (len(val),)
            else:
                assert batch_size[0] == len(val), \
                    f"Non-tensor {key} has length {len(val)}, expected {batch_size[0]}"

            # 转为 numpy object array（支持任意 Python 对象）
            non_tensors[key] = np.array(val, dtype=object)

        tensor_dict = TensorDict(source=tensors, batch_size=batch_size)
        return cls(batch=tensor_dict, non_tensor_batch=non_tensors, meta_info=meta_info)

    def repeat(self, repeat_times=2, interleave=True):
        """
        重复数据（用于 GRPO 的多个 rollout）

        参数:
            repeat_times: 重复次数（通常是 n_agent=8）
            interleave: 是否交错
                True:  [A, B] → [A, B, A, B, A, B, ...]
                False: [A, B] → [A, A, A, B, B, B, ...]

        示例:
            输入: batch_size=16, repeat_times=8
            输出: batch_size=128
                  每个问题生成 8 个 rollout

        返回:
            新的 DataToolProto 实例
        """
        # 重复 tensors
        if self.batch is not None:
            if interleave:
                repeated_tensors = {
                    key: tensor.repeat_interleave(repeat_times, dim=0)
                    for key, tensor in self.batch.items()
                }
            else:
                repeated_tensors = {
                    key: tensor.unsqueeze(0).expand(repeat_times, *tensor.shape).reshape(-1, *tensor.shape[1:])
                    for key, tensor in self.batch.items()
                }

            repeated_batch = TensorDict(
                source=repeated_tensors,
                batch_size=(self.batch.batch_size[0] * repeat_times,),
            )
        else:
            repeated_batch = None

        # 重复 non_tensors
        repeated_non_tensor_batch = {}
        for key, val in self.non_tensor_batch.items():
            if interleave:
                repeated_non_tensor_batch[key] = np.repeat(val, repeat_times, axis=0)
            else:
                repeated_non_tensor_batch[key] = np.tile(val, (repeat_times,) + (1,) * (val.ndim - 1))

        # 添加 repeat_id（标记这是第几个 repeat）
        if 'repeat_id' not in repeated_non_tensor_batch:
            repeated_non_tensor_batch['repeat_id'] = []
            index_count = defaultdict(int)
            for example_index in repeated_non_tensor_batch['index']:
                repeated_non_tensor_batch['repeat_id'].append(index_count[example_index])
                index_count[example_index] += 1
            repeated_non_tensor_batch['repeat_id'] = np.array(
                repeated_non_tensor_batch['repeat_id'], dtype=object
            )

        return DataToolProto(
            batch=repeated_batch,
            non_tensor_batch=repeated_non_tensor_batch,
            meta_info=self.meta_info,
        )
```

**为什么需要 non_tensors？**

| 数据 | 类型 | 为什么不能是 Tensor | 用途 |
|------|------|-------------------|------|
| `problem` | str | 字符串不能直接转 Tensor | 传递给 LLMGenerationManager 构建 prompt |
| `vllm_model_configs` | dict | 嵌套字典，无法转 Tensor | 配置外部推理服务地址和端口 |
| `category` | str | 枚举值（'qa', 'func_call'） | 决定使用哪种工具调用模式 |
| `index` | int | 可以是 Tensor，但为了统一放在 non_tensors | 追踪样本 ID |

---

##### 2. JsonlDataset（自定义数据集）

```python
from torch.utils.data import Dataset

class JsonlDataset(Dataset):
    """
    从 JSONL 文件加载数据

    文件格式:
        {"problem": "问题文本", "category": "qa", "index": 0}
        {"problem": "问题文本", "category": "func_call", "index": 1}
        ...

    返回格式:
        {
            'problem': str,
            'category': str,
            'index': int,
            'turn_id': int,
            'id': int,
            'vllm_model_configs': dict,
            'my_output_dir': str,
            'cur_transfer_dir': str,
            'model_type': str,
        }
    """

    def __init__(self, file_path, tokenizer, prompt_key='prompt',
                 max_prompt_length=1024, vllm_model_config_path=None,
                 my_output_dir=None, cur_transfer_dir=None, model_type=None):

        self.file_path = file_path
        self.tokenizer = tokenizer
        self.prompt_key = prompt_key
        self.max_prompt_length = max_prompt_length
        self.model_type = model_type

        # 加载数据
        self.dataset = []
        if isinstance(self.file_path, str):
            with open(self.file_path) as f:
                for line in f:
                    self.dataset.append(json.loads(line))
        else:
            # 支持多个文件
            for one_file in self.file_path:
                with open(one_file) as f:
                    for line in f:
                        self.dataset.append(json.loads(line))

        # 加载 vLLM 模型配置
        with open(vllm_model_config_path) as f:
            self.vllm_model_configs = json.load(f)

        self.my_output_dir = my_output_dir
        self.cur_transfer_dir = cur_transfer_dir

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, item):
        """
        返回单个样本

        注意: 不进行 tokenize（在 LLMGenerationManager 中进行）
        """
        row_dict = self.dataset[item]
        row_dict['turn_id'] = 0  # 初始 turn
        row_dict['id'] = row_dict['index']
        row_dict['vllm_model_configs'] = self.vllm_model_configs
        row_dict['my_output_dir'] = self.my_output_dir
        row_dict['cur_transfer_dir'] = self.cur_transfer_dir
        row_dict['model_type'] = self.model_type
        return row_dict

def collate_fn(data_list):
    """
    自定义 collate 函数

    功能: 分离 tensors 和 non_tensors

    输入: data_list: List[Dict]
    输出: Dict (包含 tensors 和 non_tensors)
    """
    tensors = {}
    non_tensors = {}

    for data in data_list:
        for key, val in data.items():
            if isinstance(val, torch.Tensor):
                if key not in tensors:
                    tensors[key] = []
                tensors[key].append(val)
            else:
                if key not in non_tensors:
                    non_tensors[key] = []
                non_tensors[key].append(val)

    # Stack tensors
    for key, val in tensors.items():
        tensors[key] = torch.stack(val, dim=0)

    # 转为 numpy object array
    for key, val in non_tensors.items():
        non_tensors[key] = np.array(val, dtype=object)

    # 合并（DataToolProto.from_dict 会自动分离）
    output = {}
    output.update(tensors)
    output.update(non_tensors)
    return output
```

---

##### 3. RayGRPOTrainer（扩展 veRL 的 RayPPOTrainer）

```python
from verl.trainer.ppo.ray_trainer import RayPPOTrainer
from lead_agent.llm_agent.generation_quick3 import LLMGenerationManager, GenerationConfig

class RayGRPOTrainer(RayPPOTrainer):
    """
    扩展 veRL 的 RayPPOTrainer，添加 Multi-turn 支持

    核心修改:
        1. _create_dataloader(): 使用自定义 JsonlDataset
        2. fit(): 注入 LLMGenerationManager
    """

    def _create_dataloader(self, place_holder1, place_holder2, place_holder3, train_sampler):
        """
        重写数据加载器创建方法

        修改点:
            1. 使用 JsonlDataset 而非 veRL 的标准 Dataset
            2. 使用自定义 collate_fn
        """
        from torch.utils.data import DataLoader
        from verl.trainer.main_ppo import create_rl_sampler
        from torchdata.stateful_dataloader import StatefulDataLoader

        # 创建训练数据集
        self.train_dataset = JsonlDataset(
            file_path=self.config.data.train_files,
            tokenizer=self.tokenizer,
            prompt_key=self.config.data.prompt_key,
            max_prompt_length=self.config.data.max_prompt_length,
            vllm_model_config_path=self.config.data.vllm_model_configs,
            my_output_dir=self.config.data.my_output_dir,
            cur_transfer_dir=self.config.data.cur_transfer_dir,
            model_type=self.config.data.model_type
        )

        # 创建 sampler
        if train_sampler is None:
            train_sampler = create_rl_sampler(self.config.data, self.train_dataset)

        # 创建 DataLoader
        self.train_dataloader = StatefulDataLoader(
            dataset=self.train_dataset,
            batch_size=self.config.data.train_batch_size,
            num_workers=self.config.data.get("dataloader_num_workers", 8),
            drop_last=True,
            collate_fn=collate_fn,  # ⭐ 自定义 collate
            sampler=train_sampler,
        )

        # 创建验证数据集（类似）
        self.val_dataset = JsonlDataset(...)
        self.val_dataloader = StatefulDataLoader(...)

        # 计算总训练步数
        total_training_steps = len(self.train_dataloader) * self.config.trainer.total_epochs
        self.total_training_steps = total_training_steps

        # 注入到 config（用于 optimizer 的 lr scheduler）
        OmegaConf.set_struct(self.config, True)
        with open_dict(self.config):
            self.config.actor_rollout_ref.actor.optim.total_training_steps = total_training_steps
            self.config.critic.optim.total_training_steps = total_training_steps

    def _create_loss_mask(self, batch, metrics):
        """
        创建损失 mask（只计算 response 部分的损失）

        veRL 默认计算整个序列的损失，但我们只想优化 response
        """
        response_length = batch.batch['responses'].shape[-1]
        response_mask = batch.batch['attention_mask'][:, -response_length:]
        batch.batch['loss_mask'] = response_mask
        return batch, metrics

    def fit(self):
        """
        训练主循环（⭐ 核心修改）

        修改点:
            1. 初始化 LLMGenerationManager
            2. 在生成阶段调用 generation_manager.run_llm_loop()
            3. 生成后接回 veRL 标准流程
        """
        from omegaconf import OmegaConf
        from verl.utils.tracking import Tracking

        # 1. 初始化 Logger
        logger = Tracking(
            project_name=self.config.trainer.project_name,
            experiment_name=self.config.trainer.experiment_name,
            default_backend=self.config.trainer.logger,
            config=OmegaConf.to_container(self.config, resolve=True),
        )

        self.global_steps = 0

        # 2. ⭐ 初始化 GenerationManager
        gen_config = GenerationConfig(
            max_turns=self.config.max_turns,
            max_prompt_length=self.config.data.max_prompt_length,
            max_response_length=self.config.data.max_response_length,
            num_gpus=self.config.trainer.n_gpus_per_node * self.config.trainer.nnodes,
            search_url=self.config.retriever.url,
            topk=self.config.retriever.topk,
        )

        generation_manager = LLMGenerationManager(
            tokenizer=self.tokenizer,
            actor_rollout_wg=self.actor_rollout_wg,  # ⭐ 传递 veRL 的 Actor Worker
            config=gen_config,
            train_tool_config_path=self.config.data.train_tool_config_path,
            test_tool_config_path=self.config.data.test_tool_config_path,
        )

        # 3. 加载 checkpoint（如果有）
        self._load_checkpoint()

        # 4. 训练循环
        progress_bar = tqdm(total=self.total_training_steps, initial=self.global_steps)
        self.global_steps += 1

        timing_raw = defaultdict(float)

        for epoch in range(self.config.trainer.total_epochs):
            for batch_dict in self.train_dataloader:
                metrics = {}
                timing_raw = {}

                # 4.1 转为 DataToolProto
                batch: DataToolProto = DataToolProto.from_single_dict(batch_dict)

                # 4.2 重复数据（每个问题生成 n_agent 个 rollout）
                batch = batch.repeat(
                    repeat_times=self.config.actor_rollout_ref.rollout.n_agent,
                    interleave=True
                )

                with _timer('step', timing_raw):
                    # 4.3 ⭐ Multi-turn 生成
                    with _timer('gen', timing_raw):
                        generation_manager.timing_raw = timing_raw
                        try:
                            final_gen_batch_output, tool_avg = generation_manager.run_llm_loop(
                                gen_batch=batch,
                                tokenizer_config={
                                    'tokenizer': self.tokenizer,
                                    'max_prompt_length': self.config.data.max_prompt_length,
                                    'max_response_length': self.config.data.max_response_length,
                                    'truncation': 'error'
                                },
                                global_steps=self.global_steps,
                                topk_doc=self.config.data.topk_doc,
                                use_llm_reward=self.config.data.use_llm_reward,
                                efficiency_reward=self.config.data.efficiency_reward,
                                exp_tag=self.config.data.exp_tag,
                                use_qa_reward=self.config.data.use_qa_reward
                            )
                        except Exception as error_inference:
                            # 生成失败，跳过这个 batch
                            continue

                        if not final_gen_batch_output:
                            # 空结果，复制上一个 checkpoint
                            import shutil
                            shutil.copytree(
                                os.path.join(self.config.data.my_output_dir, 'ckpt', f"global_step_{self.global_steps-1}"),
                                os.path.join(self.config.data.my_output_dir, 'ckpt', f"global_step_{self.global_steps}")
                            )
                            continue

                    # 4.4 转换数据类型（确保是 long）
                    for key in final_gen_batch_output.batch.keys():
                        final_gen_batch_output.batch[key] = final_gen_batch_output.batch[key].long()

                    batch = final_gen_batch_output
                    batch.non_tensor_batch['uid'] = batch.non_tensor_batch['index'].copy()

                    # 4.5 GRPO 需要的 repeat（n=1，实际上不重复）
                    batch = batch.repeat(repeat_times=self.config.actor_rollout_ref.rollout.n, interleave=True)

                    # 4.6 平衡 batch（分配到不同 GPU）
                    self._balance_batch(batch, metrics=metrics)

                    # 4.7 创建 response_mask
                    batch.batch["response_mask"] = compute_response_mask(batch)
                    batch.meta_info["global_token_num"] = torch.sum(batch.batch["attention_mask"], dim=-1).tolist()

                    # 4.8 ⭐ 从这里开始是标准 veRL 流程

                    # 重新计算 old_log_probs（使用最新的 policy）
                    with _timer("old_log_prob", timing_raw):
                        old_log_prob = self.actor_rollout_wg.compute_log_prob(batch)
                        entropys = old_log_prob.batch["entropys"]
                        response_masks = batch.batch["response_mask"]
                        loss_agg_mode = self.config.actor_rollout_ref.actor.loss_agg_mode
                        entropy_loss = agg_loss(loss_mat=entropys, loss_mask=response_masks, loss_agg_mode=loss_agg_mode)
                        old_log_prob_metrics = {"actor/entropy_loss": entropy_loss.detach().item()}
                        metrics.update(old_log_prob_metrics)
                        old_log_prob.batch.pop("entropys")
                        batch = batch.union(old_log_prob)

                    # 计算 reference policy 的 log_probs
                    if self.use_reference_policy:
                        with _timer('ref', timing_raw):
                            ref_log_prob = self.ref_policy_wg.compute_ref_log_prob(batch)
                            batch = batch.union(ref_log_prob)

                    # 计算 value（Critic）
                    if self.use_critic:
                        with _timer('values', timing_raw):
                            values = self.critic_wg.compute_values(batch)
                            batch = batch.union(values)

                    # 计算 advantage
                    with _timer('adv', timing_raw):
                        # RM score（如果有）
                        if self.use_rm:
                            reward_tensor = self.rm_wg.compute_rm_score(batch)
                            batch = batch.union(reward_tensor)

                        # Reward 函数（来自 main_grpo_quick3.py 的 RewardManager）
                        reward_tensor = self.reward_fn(batch, global_step=self.global_steps)
                        batch.batch['token_level_scores'] = reward_tensor

                        # 应用 KL penalty
                        if not self.config.actor_rollout_ref.actor.use_kl_loss:
                            batch, kl_metrics = apply_kl_penalty(
                                batch,
                                kl_ctrl=self.kl_ctrl,
                                kl_penalty=self.config.algorithm.kl_penalty
                            )
                            metrics.update(kl_metrics)
                        else:
                            batch.batch['token_level_rewards'] = batch.batch['token_level_scores']

                        # 计算 advantage（GAE）
                        batch = compute_advantage(
                            batch,
                            adv_estimator=self.config.algorithm.adv_estimator,
                            gamma=self.config.algorithm.gamma,
                            lam=self.config.algorithm.lam,
                            num_repeat=self.config.actor_rollout_ref.rollout.n
                        )

                    # 更新 Critic
                    if self.use_critic:
                        with _timer('update_critic', timing_raw):
                            critic_output = self.critic_wg.update_critic(batch)
                        critic_output_metrics = reduce_metrics(critic_output.meta_info['metrics'])
                        metrics.update(critic_output_metrics)

                    # 更新 Actor
                    if self.config.trainer.critic_warmup <= self.global_steps:
                        with _timer('update_actor', timing_raw):
                            batch, metrics = self._create_loss_mask(batch, metrics)
                            actor_output = self.actor_rollout_wg.update_actor(batch)
                        actor_output_metrics = reduce_metrics(actor_output.meta_info['metrics'])
                        metrics.update(actor_output_metrics)

                    # 保存 checkpoint
                    if self.config.trainer.save_freq > 0 and \
                            self.global_steps % self.config.trainer.save_freq == 0:
                        with _timer('save_checkpoint', timing_raw):
                            self._save_checkpoint()

                # 5. 收集 metrics
                metrics.update(compute_data_metrics(batch=batch, use_critic=self.use_critic))
                metrics.update(compute_timing_metrics(batch=batch, timing_raw=timing_raw))
                n_gpus = self.resource_pool_manager.get_n_gpus()
                metrics.update(compute_throughout_metrics(batch=batch, timing_raw=timing_raw, n_gpus=n_gpus))

                # 6. 记录 metrics
                logger.log(data=metrics, step=self.global_steps)

                self.global_steps += 1
                progress_bar.update(1)
```

**关键设计**:

| 设计点 | 实现 | 目的 |
|--------|------|------|
| **DataToolProto** | 添加 `non_tensor_batch` | 传递字符串和字典给 LLMGenerationManager |
| **JsonlDataset** | 不进行 tokenize | Tokenize 在 multi-turn 循环中动态进行 |
| **LLMGenerationManager 注入** | `generation_manager.run_llm_loop()` | 替换 veRL 的单轮生成 |
| **接回 veRL** | 生成后返回标准 DataProto | 后续流程使用 veRL 的 compute_log_prob、update_actor |

---

### 2.2 DAPO 算法实现

**DAPO vs GRPO 的主要区别**:

| 特性 | GRPO | DAPO |
|------|------|------|
| **Clip 方式** | 统一 clip_ratio | 解耦的 clip_ratio_low 和 clip_ratio_high |
| **采样策略** | 固定采样 | 动态采样（过滤低方差组） |
| **Overlong 处理** | 无 | Overlong reward shaping |
| **Group 过滤** | 无 | 根据 reward 方差过滤 |

**文件结构与 GRPO 类似**:
- `main_dapo.py`: 训练入口（结构与 main_grpo_quick3.py 相同）
- `dapo_ray_trainer.py`: 扩展 RayPPOTrainer（添加 DAPO 特有逻辑）

**DAPO 特有功能** (dapo_ray_trainer.py):

```python
class RayDAPOTrainer(RayPPOTrainer):
    def fit(self):
        # ... 前面与 GRPO 相同

        # DAPO 特有：动态过滤低方差组
        if self.config.algorithm.filter_groups.enable:
            filtered_batch = self._filter_low_variance_groups(batch)

        # DAPO 特有：Overlong reward shaping
        if self.config.reward_model.overlong_buffer.enable:
            batch = self._apply_overlong_penalty(batch)

        # 其余流程与 GRPO 相同
        ...

    def _filter_low_variance_groups(self, batch):
        """
        过滤低方差的 group

        原理:
            如果一个问题的所有 rollout 的 reward 方差很小，
            说明不同策略的效果差异不大，这样的 group 对训练贡献小。

        实现:
            1. 计算每个 group（同一问题的多个 rollout）的 reward 方差
            2. 过滤掉方差 < threshold 的 group
        """
        pass

    def _apply_overlong_penalty(self, batch):
        """
        对超长输出施加惩罚

        原理:
            如果模型生成的序列长度超过 max_response_length，
            说明模型没有学会合理的停止条件。

        实现:
            对超长的样本，reward 减去一个固定的 penalty
        """
        pass
```

---

## 3. Rollout (tau2) 模块

**位置**: `.reference_projects/ToolOrchestra/training/rollout/tau2/`

**核心职责**: 提供多域任务执行和评估框架，完全独立于 veRL。

**与 veRL 的关系**: ❌ 完全独立（可以单独使用）

### 核心架构

```
tau2 = 13个域 + Agent/User 模拟器 + Orchestrator + 4种 Evaluator
```

### 目录结构

```
training/rollout/tau2/
├── registry.py           ⭐ 域注册中心（管理 13 个域）
├── cli.py                ⭐ 命令行入口（tau2 run --domain airline）
├── run.py                ⭐ 主执行逻辑（运行任务并评估）
│
├── agent/                Agent 实现
│   ├── base.py           抽象基类（BaseAgent）
│   └── llm_agent.py      LLM Agent（支持工具调用）
│
├── user/                 User 模拟器
│   ├── base.py           抽象基类（BaseUser）
│   └── user_simulator.py 基于 LLM 的用户模拟
│
├── environment/          执行环境
│   ├── environment.py    Environment 类（管理工具和状态）
│   ├── toolkit.py        ToolKitBase 抽象基类
│   ├── tool.py           @tool 装饰器
│   └── server.py         FastAPI 服务器（可选）
│
├── orchestrator/         消息路由
│   ├── orchestrator.py   Agent-User-Env 三方通信
│   └── environment_manager.py  多实例管理
│
├── evaluator/            评估器（4 种）
│   ├── evaluator.py      统一评估入口
│   ├── evaluator_env.py  基于环境状态评估
│   ├── evaluator_action.py  基于动作序列评估
│   ├── evaluator_communicate.py  通信质量评估
│   └── evaluator_nl_assertions.py  自然语言断言评估
│
├── domains/              13 个域的实现
│   ├── airline/          航空预订
│   ├── bank/             银行服务
│   ├── basketball/       篮球信息查询
│   ├── ecommerce/        电商购物
│   ├── medicine/         医疗咨询
│   ├── mock/             测试域
│   ├── movie/            电影推荐
│   ├── railway/          火车票预订
│   ├── restaurant/       餐厅预订
│   ├── retail/           零售服务
│   ├── school/           学校管理
│   ├── telecom/          电信服务（⭐ 最复杂）
│   ├── travel/           旅游规划
│   └── weather/          天气查询
│
├── data_model/           数据模型
│   ├── message.py        消息类型（User/Assistant/Tool/System）
│   ├── simulation.py     SimulationRun, RewardInfo
│   └── tasks.py          Task, Action, RewardType
│
├── metrics/              指标计算
│   ├── agent_metrics.py  成功率、错误数等
│   └── break_down_metrics.py  细粒度指标
│
├── scripts/              实用脚本
│   ├── show_domain_doc.py  显示域 API 文档
│   ├── start_servers.py    启动 FastAPI 服务器
│   └── view_simulations.py 分析模拟结果
│
└── utils/                工具函数
    ├── display.py        Rich 控制台显示
    ├── io_utils.py       文件 I/O
    ├── llm_utils.py      LLM API 封装
    └── pydantic_utils.py Pydantic 辅助工具
```

---

### 3.1 核心文件详解

#### registry.py

**文件位置**: `training/rollout/tau2/registry.py`
**代码行数**: ~250 行
**核心职责**: 注册和管理所有域、Agent、User、Task

```python
from typing import Dict, List, Type, Callable
from dataclasses import dataclass

@dataclass
class DomainInfo:
    """域信息"""
    name: str
    get_environment: Callable  # 返回 Environment 实例的函数
    get_tasks: Callable        # 返回 Task 列表的函数
    description: str

class Registry:
    """全局注册中心"""

    def __init__(self):
        self.domains: Dict[str, DomainInfo] = {}
        self.agents: Dict[str, Type[BaseAgent]] = {}
        self.users: Dict[str, Type[BaseUser]] = {}

    def register_domain(self, name: str, get_env_fn: Callable,
                       get_tasks_fn: Callable, description: str):
        """
        注册一个域

        参数:
            name: 域名（如 'airline'）
            get_env_fn: 环境构造函数
            get_tasks_fn: 任务加载函数
            description: 域描述
        """
        self.domains[name] = DomainInfo(
            name=name,
            get_environment=get_env_fn,
            get_tasks=get_tasks_fn,
            description=description,
        )

    def register_agent(self, name: str, agent_cls: Type[BaseAgent]):
        """注册一个 Agent 类"""
        self.agents[name] = agent_cls

    def register_user(self, name: str, user_cls: Type[BaseUser]):
        """注册一个 User 类"""
        self.users[name] = user_cls

    def get_env_constructor(self, domain_name: str) -> Callable:
        """获取域的环境构造函数"""
        return self.domains[domain_name].get_environment

    def get_tasks(self, domain_name: str) -> List[Task]:
        """获取域的任务列表"""
        return self.domains[domain_name].get_tasks()

    def get_agent(self, agent_name: str) -> Type[BaseAgent]:
        """获取 Agent 类"""
        return self.agents[agent_name]

    def get_user(self, user_name: str) -> Type[BaseUser]:
        """获取 User 类"""
        return self.users[user_name]

    def list_domains(self) -> List[str]:
        """列出所有注册的域"""
        return list(self.domains.keys())

# 全局单例
registry = Registry()

# 注册 13 个域
from tau2.domains import (
    airline, bank, basketball, ecommerce, medicine, mock,
    movie, railway, restaurant, retail, school, telecom,
    travel, weather
)

registry.register_domain('airline', airline.get_environment, airline.get_tasks, "航空预订服务")
registry.register_domain('bank', bank.get_environment, bank.get_tasks, "银行账户管理")
registry.register_domain('basketball', basketball.get_environment, basketball.get_tasks, "篮球信息查询")
registry.register_domain('ecommerce', ecommerce.get_environment, ecommerce.get_tasks, "电商购物平台")
registry.register_domain('medicine', medicine.get_environment, medicine.get_tasks, "医疗咨询服务")
registry.register_domain('mock', mock.get_environment, mock.get_tasks, "测试域")
registry.register_domain('movie', movie.get_environment, movie.get_tasks, "电影推荐服务")
registry.register_domain('railway', railway.get_environment, railway.get_tasks, "火车票预订")
registry.register_domain('restaurant', restaurant.get_environment, restaurant.get_tasks, "餐厅预订服务")
registry.register_domain('retail', retail.get_environment, retail.get_tasks, "零售商店服务")
registry.register_domain('school', school.get_environment, school.get_tasks, "学校管理系统")
registry.register_domain('telecom', telecom.get_environment, telecom.get_tasks, "电信客服系统")
registry.register_domain('travel', travel.get_environment, travel.get_tasks, "旅游规划服务")
registry.register_domain('weather', weather.get_environment, weather.get_tasks, "天气查询服务")

# 注册 Agent
from tau2.agent.llm_agent import LLMAgent, LLMGTAgent, LLMSoloAgent
registry.register_agent('llm', LLMAgent)
registry.register_agent('llm_gt', LLMGTAgent)
registry.register_agent('llm_solo', LLMSoloAgent)

# 注册 User
from tau2.user.user_simulator import UserSimulator, DummyUser
registry.register_user('user_simulator', UserSimulator)
registry.register_user('dummy_user', DummyUser)
```

**为什么需要 Registry？**

1. **统一接口**: 13 个域都遵循相同的接口（get_environment, get_tasks）
2. **动态加载**: `tau2 run --domain airline` 可以动态选择域
3. **可扩展**: 添加新域只需实现接口并注册

---

#### run.py

**文件位置**: `training/rollout/tau2/run.py`
**代码行数**: ~400 行
**核心函数**: `run_domain()`

```python
from tau2.registry import registry
from tau2.orchestrator import Orchestrator
from tau2.evaluator import evaluate_simulation
from tqdm import tqdm

def run_domain(
    domain_name: str,
    agent_name: str = 'llm',
    user_name: str = 'user_simulator',
    agent_llm: str = 'gpt-4o',
    user_llm: str = 'gpt-4o',
    num_trials: int = 10,
    max_steps: int = 20,
    max_errors: int = 3,
    task_path: Optional[str] = None,
    output_file: Optional[str] = None,
    max_concurrency: int = 5,
) -> List[SimulationRun]:
    """
    运行一个域的所有任务

    参数:
        domain_name: 域名（如 'airline'）
        agent_name: Agent 类型（'llm', 'llm_gt', 'llm_solo'）
        user_name: User 类型（'user_simulator', 'dummy_user'）
        agent_llm: Agent 使用的 LLM 模型
        user_llm: User 使用的 LLM 模型
        num_trials: 每个任务运行几次
        max_steps: 单个任务最大步数
        max_errors: 最大错误次数
        task_path: 任务文件路径（可选）
        output_file: 输出文件路径（可选）
        max_concurrency: 最大并发数

    返回:
        所有任务的 SimulationRun 列表
    """

    # 1. 从 Registry 获取域信息
    env_constructor = registry.get_env_constructor(domain_name)
    if task_path is None:
        tasks = registry.get_tasks(domain_name)
    else:
        tasks = load_tasks_from_file(task_path)

    # 2. 创建环境
    environment = env_constructor()

    # 3. 获取 Agent 和 User 类
    agent_cls = registry.get_agent(agent_name)
    user_cls = registry.get_user(user_name)

    # 4. 运行所有任务
    all_results = []

    # 使用 ThreadPoolExecutor 并行运行
    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = []

        for task in tasks:
            for trial in range(num_trials):
                future = executor.submit(
                    run_single_trial,
                    task=task,
                    environment=environment,
                    agent_cls=agent_cls,
                    user_cls=user_cls,
                    agent_llm=agent_llm,
                    user_llm=user_llm,
                    max_steps=max_steps,
                    max_errors=max_errors,
                )
                futures.append(future)

        # 收集结果
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Running {domain_name}"):
            try:
                simulation_run = future.result()
                all_results.append(simulation_run)
            except Exception as e:
                print(f"Error in simulation: {e}")

    # 5. 计算统计信息
    metrics = compute_metrics(all_results)
    print(f"\n{domain_name} Results:")
    print(f"  Success Rate: {metrics['success_rate']:.2%}")
    print(f"  Avg Steps: {metrics['avg_steps']:.2f}")
    print(f"  Avg Reward: {metrics['avg_reward']:.2f}")

    # 6. 保存结果
    if output_file:
        save_results(all_results, output_file)
        print(f"  Results saved to: {output_file}")

    return all_results

def run_single_trial(task, environment, agent_cls, user_cls,
                     agent_llm, user_llm, max_steps, max_errors):
    """
    运行单个任务的一次试验

    流程:
        1. 初始化 Agent 和 User
        2. 创建 Orchestrator
        3. 运行任务
        4. 评估结果

    返回:
        SimulationRun（包含 reward_info）
    """
    # 1. 初始化 Agent
    agent = agent_cls(
        model=agent_llm,
        system_message=environment.get_system_message(),
        tools=environment.get_tools(),  # 工具签名列表
    )

    # 2. 初始化 User
    user = user_cls(
        model=user_llm,
        task=task,
    )

    # 3. 创建 Orchestrator
    orchestrator = Orchestrator(
        agent=agent,
        user=user,
        environment=environment,
        max_steps=max_steps,
        max_errors=max_errors,
    )

    # 4. 运行任务
    simulation_run = orchestrator.run(task)

    # 5. 评估结果
    reward_info = evaluate_simulation(
        simulation_run=simulation_run,
        environment=environment,
        task=task,
    )
    simulation_run.reward_info = reward_info

    return simulation_run
```

**执行流程图**:

```
run_domain(domain='airline', num_trials=10)
    ↓
加载 airline 域的环境和任务
    ↓
for task in tasks:
    for trial in range(10):
        ↓
        run_single_trial()
            ↓
            [初始化 Agent, User, Environment]
            ↓
            Orchestrator.run(task)
                ↓
                [Multi-turn 交互: Agent ↔ User ↔ Environment]
                ↓
                返回 SimulationRun
            ↓
            evaluate_simulation()
                ↓
                [选择 Evaluator 并计算 reward]
                ↓
                返回 RewardInfo
            ↓
            保存结果
    ↓
计算统计指标并输出
```

---

#### orchestrator.py

**文件位置**: `training/rollout/tau2/orchestrator/orchestrator.py`
**代码行数**: ~300 行
**核心类**: `Orchestrator`

```python
from tau2.data_model.message import (
    Message, UserMessage, AssistantMessage, ToolMessage, SystemMessage
)
from tau2.data_model.simulation import SimulationRun
from tau2.agent.base import BaseAgent
from tau2.user.base import BaseUser
from tau2.environment.environment import Environment

class Orchestrator:
    """
    消息路由器：管理 Agent-User-Environment 三方的消息路由

    职责:
        1. 路由消息: Agent → User, Agent → Environment → Agent
        2. 追踪状态: 步数、错误数、终止条件
        3. 记录历史: 保存所有消息
    """

    def __init__(self, agent: BaseAgent, user: BaseUser,
                 environment: Environment, max_steps: int = 20,
                 max_errors: int = 3):
        self.agent = agent
        self.user = user
        self.environment = environment
        self.max_steps = max_steps
        self.max_errors = max_errors

        self.messages: List[Message] = []
        self.turn_count = 0
        self.error_count = 0

    def run(self, task: Task) -> SimulationRun:
        """
        运行一个任务

        流程:
            1. User 发起初始请求
            2. Agent 响应（可能调用工具）
            3. Environment 执行工具并返回结果
            4. Agent 根据工具结果继续响应
            5. 重复 2-4 直到终止条件满足

        终止条件:
            - 达到 max_steps
            - Agent 错误达到 max_errors
            - User 满意（任务完成）
            - Agent 明确表示完成

        返回:
            SimulationRun（包含消息历史、终止原因、环境状态）
        """

        # 1. 初始化环境和 Agent 状态
        self.environment.reset(task.initialization_data)
        self.agent.reset()
        self.user.reset()

        # 2. User 发起请求
        user_message = self.user.generate_initial_message(task)
        self.messages.append(user_message)

        # 3. Multi-turn 循环
        while self.turn_count < self.max_steps:
            self.turn_count += 1

            # 3.1 Agent 生成响应
            try:
                agent_message = self.agent.generate_next_message(
                    message_history=self.messages,
                )
                self.messages.append(agent_message)
            except Exception as e:
                self.error_count += 1
                error_message = SystemMessage(
                    content=f"Agent error: {str(e)}"
                )
                self.messages.append(error_message)

                if self.error_count >= self.max_errors:
                    return self._create_simulation_run(termination_reason='max_errors')
                continue

            # 3.2 检查是否是工具调用
            if isinstance(agent_message, AssistantMessage) and agent_message.tool_calls:
                # 执行工具
                tool_results = []
                for tool_call in agent_message.tool_calls:
                    try:
                        result = self.environment.execute_tool(
                            tool_name=tool_call['function']['name'],
                            arguments=tool_call['function']['arguments']
                        )
                        tool_results.append({
                            'tool_call_id': tool_call['id'],
                            'result': result
                        })
                    except Exception as e:
                        tool_results.append({
                            'tool_call_id': tool_call['id'],
                            'error': str(e)
                        })

                # 创建 ToolMessage
                for tool_result in tool_results:
                    tool_message = ToolMessage(
                        content=json.dumps(tool_result['result'] if 'result' in tool_result else {'error': tool_result['error']}),
                        tool_call_id=tool_result['tool_call_id'],
                    )
                    self.messages.append(tool_message)

                # 继续循环（Agent 需要根据工具结果给出最终答案）
                continue

            # 3.3 检查是否是最终答案（发给 User）
            if isinstance(agent_message, AssistantMessage) and not agent_message.tool_calls:
                # Agent 给出了最终答案，发给 User
                user_response = self.user.generate_response(agent_message)
                self.messages.append(user_response)

                # 检查 User 是否满意
                if self.user.is_satisfied():
                    return self._create_simulation_run(termination_reason='success')

                # User 不满意，继续对话
                # （User 会在 generate_response 中提供反馈）
                continue

            # 3.4 其他情况（错误格式）
            self.error_count += 1
            if self.error_count >= self.max_errors:
                return self._create_simulation_run(termination_reason='max_errors')

        # 4. 达到最大步数
        return self._create_simulation_run(termination_reason='max_steps')

    def _create_simulation_run(self, termination_reason: str) -> SimulationRun:
        """创建 SimulationRun 对象"""
        return SimulationRun(
            messages=self.messages,
            termination_reason=termination_reason,
            environment_state=self.environment.get_state(),
            turn_count=self.turn_count,
            error_count=self.error_count,
        )
```

**消息流示例** (airline 域 - 预订航班):

```
Turn 0:
  UserMessage(content="我想预订从北京到上海的航班，明天出发")

Turn 1:
  AssistantMessage(
      content="好的，让我查询一下可用的航班",
      tool_calls=[{
          "id": "call_1",
          "function": {
              "name": "search_flights",
              "arguments": {"from": "北京", "to": "上海", "date": "2026-01-09"}
          }
      }]
  )

Turn 2:
  ToolMessage(
      tool_call_id="call_1",
      content='{"flights": [
          {"id": "CA1234", "departure": "08:00", "price": 800},
          {"id": "MU5678", "departure": "14:00", "price": 600}
      ]}'
  )

Turn 3:
  AssistantMessage(
      content="找到了两个航班...",
      tool_calls=[{
          "id": "call_2",
          "function": {
              "name": "book_flight",
              "arguments": {"flight_id": "MU5678", "passenger_name": "张三", "passenger_id": "110..."}
          }
      }]
  )

Turn 4:
  ToolMessage(
      tool_call_id="call_2",
      content='{"status": "success", "booking_id": "BK789012"}'
  )

Turn 5:
  AssistantMessage(
      content="已为您预订 MU5678 航班，预订号是 BK789012"
  )

Turn 6:
  UserMessage(content="好的，谢谢")

终止原因: success (User.is_satisfied() == True)
```

---

#### evaluator.py

**文件位置**: `training/rollout/tau2/evaluator/evaluator.py`
**代码行数**: ~150 行
**核心函数**: `evaluate_simulation()`

```python
from enum import Enum
from tau2.data_model.simulation import SimulationRun, RewardInfo
from tau2.data_model.tasks import Task, RewardType
from tau2.environment.environment import Environment

class EvaluationType(Enum):
    """评估类型"""
    ENV = "env"                    # 基于环境状态
    NL_ASSERTIONS = "nl_assertions"  # 基于自然语言断言
    COMMUNICATE = "communicate"      # 基于通信质量
    ACTION = "action"                # 基于动作序列
    ALL = "all"                      # 全部

def evaluate_simulation(
    simulation_run: SimulationRun,
    environment: Environment,
    task: Task,
) -> RewardInfo:
    """
    评估一个 SimulationRun

    根据 task.reward_type 选择 Evaluator:
        - RewardType.ENV → EnvironmentEvaluator
        - RewardType.NL_ASSERTIONS → NLAssertionsEvaluator
        - RewardType.COMMUNICATE → CommunicateEvaluator
        - RewardType.ACTION → ActionEvaluator

    返回:
        RewardInfo（包含 reward 和详细信息）
    """

    # 1. 选择 Evaluator
    if task.reward_type == RewardType.ENV:
        from .evaluator_env import EnvironmentEvaluator
        evaluator = EnvironmentEvaluator()

    elif task.reward_type == RewardType.NL_ASSERTIONS:
        from .evaluator_nl_assertions import NLAssertionsEvaluator
        evaluator = NLAssertionsEvaluator()

    elif task.reward_type == RewardType.COMMUNICATE:
        from .evaluator_communicate import CommunicateEvaluator
        evaluator = CommunicateEvaluator()

    elif task.reward_type == RewardType.ACTION:
        from .evaluator_action import ActionEvaluator
        evaluator = ActionEvaluator()

    else:
        raise ValueError(f"Unknown reward type: {task.reward_type}")

    # 2. 评估
    reward_info = evaluator.evaluate(
        simulation_run=simulation_run,
        environment=environment,
        task=task,
    )

    return reward_info
```

**4 种 Evaluator 对比**:

| Evaluator | 评估依据 | 适用场景 | 示例域 |
|-----------|---------|---------|--------|
| **EnvironmentEvaluator** | 环境最终状态 | 需要检查数据库状态 | airline（检查预订记录） |
| **NLAssertionsEvaluator** | 自然语言断言（LLM 判断） | 难以形式化的条件 | medicine（诊断是否合理） |
| **CommunicateEvaluator** | 通信质量（礼貌、清晰、效率） | 客服类任务 | telecom（客服质量） |
| **ActionEvaluator** | 动作序列 | 需要特定操作顺序 | bank（转账需先验证身份） |

---

### 3.2 域实现模式

每个域需要实现 3 个核心文件：

#### 1. data_model.py

```python
# airline/data_model.py

from pydantic import BaseModel
from typing import List

class Flight(BaseModel):
    """航班数据模型"""
    id: str
    from_city: str
    to_city: str
    departure_time: str
    price: float
    available_seats: int

class Booking(BaseModel):
    """预订数据模型"""
    booking_id: str
    flight_id: str
    passenger_name: str
    status: str

class DB:
    """模拟数据库"""

    def __init__(self):
        self.flights: List[Flight] = []
        self.bookings: List[Booking] = []

    def initialize(self, init_data: dict):
        """根据任务初始化数据"""
        for flight_data in init_data.get('flights', []):
            self.flights.append(Flight(**flight_data))

    def search_flights(self, from_city, to_city, date):
        """搜索航班"""
        return [f for f in self.flights
                if f.from_city == from_city and f.to_city == to_city]

    def book_flight(self, flight_id, passenger_name, passenger_id):
        """预订航班"""
        flight = next((f for f in self.flights if f.id == flight_id), None)
        if flight and flight.available_seats > 0:
            booking = Booking(
                booking_id=self._generate_booking_id(),
                flight_id=flight_id,
                passenger_name=passenger_name,
                status='confirmed',
            )
            self.bookings.append(booking)
            flight.available_seats -= 1
            return booking
        else:
            raise ValueError("Flight not available")

    def get_state(self) -> dict:
        """获取当前状态（用于评估）"""
        return {
            'flights': [f.dict() for f in self.flights],
            'bookings': [b.dict() for b in self.bookings],
        }
```

#### 2. tools.py

```python
# airline/tools.py

from tau2.environment.toolkit import ToolKitBase, tool

class AirlineToolKit(ToolKitBase):
    """航空域的工具集"""

    def __init__(self, db: DB):
        self.db = db

    @tool
    def search_flights(self, from_city: str, to_city: str, date: str) -> list:
        """
        搜索航班

        参数:
            from_city: 出发城市
            to_city: 目的地城市
            date: 日期（格式：YYYY-MM-DD）

        返回:
            航班列表
        """
        flights = self.db.search_flights(from_city, to_city, date)
        return [f.dict() for f in flights]

    @tool
    def book_flight(self, flight_id: str, passenger_name: str,
                    passenger_id: str) -> dict:
        """
        预订航班

        参数:
            flight_id: 航班 ID
            passenger_name: 乘客姓名
            passenger_id: 身份证号

        返回:
            预订信息
        """
        booking = self.db.book_flight(flight_id, passenger_name, passenger_id)
        return booking.dict()
```

**@tool 装饰器的魔法**:
- 自动从函数签名提取工具定义
- 自动生成 JSON Schema（用于 LLM 的 function calling）
- 自动注册到 Environment

生成的工具定义:
```json
{
  "name": "search_flights",
  "description": "搜索航班",
  "parameters": {
    "type": "object",
    "properties": {
      "from_city": {"type": "string", "description": "出发城市"},
      "to_city": {"type": "string", "description": "目的地城市"},
      "date": {"type": "string", "description": "日期（格式：YYYY-MM-DD）"}
    },
    "required": ["from_city", "to_city", "date"]
  }
}
```

#### 3. environment.py

```python
# airline/environment.py

from tau2.environment.environment import Environment
from .data_model import DB
from .tools import AirlineToolKit

def get_environment() -> Environment:
    """创建 airline 域的环境"""

    db = DB()
    toolkit = AirlineToolKit(db=db)

    environment = Environment(
        domain_name='airline',
        toolkit=toolkit,
        system_message="""
        你是一个航空公司的客服 Agent。
        你可以使用以下工具帮助用户：
        - search_flights: 搜索航班
        - book_flight: 预订航班

        请根据用户的需求选择合适的工具。
        """,
    )

    return environment

def get_tasks() -> List[Task]:
    """加载 airline 域的任务"""
    tasks = [
        Task(
            task_id='airline_001',
            initialization_data={
                'flights': [
                    {'id': 'CA1234', 'from_city': '北京', 'to_city': '上海', ...},
                    {'id': 'MU5678', 'from_city': '北京', 'to_city': '上海', ...},
                ]
            },
            user_instruction="我想预订从北京到上海的航班，明天出发，价格不要超过 700 元",
            evaluation_criteria={
                'type': 'env_state',
                'constraints': [
                    {'field': 'bookings', 'condition': 'length >= 1'},
                    {'field': 'bookings[0].flight_id', 'condition': "== 'MU5678'"},
                ]
            },
            reward_type=RewardType.ENV,
        ),
        # 更多任务...
    ]
    return tasks
```

---

### 3.3 使用方式

#### 命令行

```bash
# 运行 airline 域的所有任务
tau2 run --domain airline --agent llm --user user_simulator --num-trials 10

# 运行指定任务文件
tau2 run --domain airline --task-path tasks/airline_custom.json

# 查看域文档
tau2 domain airline

# 列出所有域
tau2 list-domains
```

#### Python API

```python
from tau2.run import run_domain

results = run_domain(
    domain_name='airline',
    agent_name='llm',
    user_name='user_simulator',
    agent_llm='gpt-4o',
    user_llm='gpt-4o',
    num_trials=10,
    max_steps=20,
)

# 分析结果
success_rate = sum(r.reward_info.reward > 0.9 for r in results) / len(results)
print(f"Success Rate: {success_rate:.2%}")
```

---

## 架构对比与设计原理

### 完整架构图

```
┌────────────────────────────────────────────────────────────────┐
│  ToolOrchestra Training Pipeline                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  1. 数据准备（可选使用 tau2）                             │ │
│  │     tau2 run --domain airline → 生成对话数据              │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   ↓                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  2. 训练入口 (recipe/algo/ 或 recipe/dapo/)              │ │
│  │     main_grpo_quick3.py / main_dapo.py                   │ │
│  │     - 定义 Reward 函数                                    │ │
│  │     - 初始化 Trainer                                      │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   ↓                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  3. 训练循环 (recipe/)                                    │ │
│  │     RayGRPOTrainer / RayDAPOTrainer                      │ │
│  │     ├─ 加载 JsonlDataset（自定义）                        │ │
│  │     ├─ 初始化 LLMGenerationManager（自定义）              │ │
│  │     └─ 训练循环                                           │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   ↓                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  4. Multi-turn 生成 (lead_agent/)                        │ │
│  │     LLMGenerationManager.run_llm_loop()                  │ │
│  │     ├─ 循环 max_turns=10 轮                               │ │
│  │     ├─ 调用 veRL Actor 生成                               │ │
│  │     ├─ 执行工具（search, enhance_reasoning, answer）      │ │
│  │     └─ 计算 Reward（GRPO 归一化）                         │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   ↓                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  5. veRL 标准流程                                         │ │
│  │     ├─ compute_log_prob() (veRL)                         │ │
│  │     ├─ compute_advantage() (veRL)                        │ │
│  │     ├─ update_critic() (veRL)                            │ │
│  │     └─ update_actor() (veRL)                             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  Tau2 独立框架（可选）                                          │
├────────────────────────────────────────────────────────────────┤
│  Registry (13 domains) → Orchestrator → Evaluator              │
│  ├─ 13 个域（airline, bank, ...）                              │
│  ├─ Agent (LLM-based)                                          │
│  ├─ User (Simulator)                                           │
│  └─ Environment (Tools + DB)                                   │
└────────────────────────────────────────────────────────────────┘
```

### 核心设计思想

| 设计点 | 实现方式 | 原因 |
|--------|----------|------|
| **Multi-turn 支持** | LLMGenerationManager 循环 | veRL 只支持单轮生成 |
| **工具调用管理** | execute_predictions() | 需要管理多种工具（search, code, answer） |
| **非 Tensor 数据传递** | DataToolProto.non_tensor_batch | 传递字符串和字典给生成器 |
| **与 veRL 最小耦合** | 只调用 actor_rollout_wg.generate_sequences() | 保持灵活性，易于维护 |
| **独立评估框架** | tau2 完全独立 | 可用于其他项目，不依赖 veRL |
| **容错设计** | try-except + format_correct | 训练中模型会生成错误输出 |
| **效率奖励** | 成本 + 延迟惩罚 | 训练高效的 Orchestrator |
| **GRPO 归一化** | 组内标准化 | 稳定训练，减少方差 |

### 为什么这样设计？

**问题**: veRL 是为单轮 RLHF 设计的，不支持 Multi-turn 工具调用。

**解决方案**: 在 veRL 外包裹一层自定义逻辑：

1. **生成阶段**: 使用 LLMGenerationManager 进行 Multi-turn 生成
   - 每轮调用 veRL 的 Actor 生成一次
   - 执行工具并累积上下文
   - 最终返回完整的 prompt + response

2. **优化阶段**: 使用 veRL 的标准流程
   - compute_log_prob: 计算当前 policy 的 log prob
   - compute_advantage: GAE 优势估计
   - update_actor: PPO/GRPO 更新

**优势**:
- ✅ 复用 veRL 的分布式训练、优化器、Checkpoint
- ✅ 保持代码解耦，易于维护
- ✅ 可以独立升级 veRL 版本

---

## 总结

ToolOrchestra 项目通过三大自定义模块扩展了 veRL，实现了 Multi-turn 工具调用的 RL 训练：

1. **Lead Agent**: 实现 Multi-turn 生成循环和工具调用管理
2. **Recipe**: 扩展 veRL Trainer，注入自定义数据加载和生成逻辑
3. **Rollout (tau2)**: 提供独立的多域任务执行和评估框架

这种设计既保持了对 veRL 的最小依赖，又充分利用了 veRL 的分布式训练能力。

---

**参考文档**:
- [veRL 官方文档](https://verl.readthedocs.io/)
- [ToolOrchestra 论文](https://arxiv.org/abs/...)
- [GRPO 算法论文](https://arxiv.org/abs/...)
