# generation_quick3.py 详细解释

> 本文档详细解释 ToolOrchestra 项目中最核心的文件：`training/lead_agent/llm_agent/generation_quick3.py`

**文件位置**: `.reference_projects/ToolOrchestra/training/lead_agent/llm_agent/generation_quick3.py`
**代码行数**: 2180 行
**核心职责**: Multi-turn LLM 生成循环管理器，负责工具调用、Reward 计算

---

## 📋 目录

1. [文件概览](#文件概览)
2. [核心数据结构](#核心数据结构)
3. [辅助函数](#辅助函数)
4. [工具调用函数 call_tool](#工具调用函数-call_tool)
5. [LLMGenerationManager 类](#llmgenerationmanager-类)
6. [run_llm_loop 核心方法](#run_llm_loop-核心方法)
7. [后处理方法](#后处理方法)
8. [Reward 计算](#reward-计算)
9. [完整执行流程示例](#完整执行流程示例)

---

## 文件概览

### 导入依赖

```python
from math import remainder
import random
import torch
import re
import asyncio
from collections import defaultdict
import os, json, time, subprocess
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI

# veRL 相关
from .tensor_helper import TensorHelper, TensorConfig
from verl import DataProto
import verl.utils.torch_functional as verl_F
from verl.utils.model import compute_position_id_with_mask

# LLM 调用
from LLM_CALL import get_llm_response
from transformers import AutoTokenizer
```

**关键依赖**:
- `veRL`: 用于与 veRL 框架交互（DataProto, 工具函数）
- `TensorHelper`: 自定义的 Tensor 处理工具
- `LLM_CALL.get_llm_response`: 统一的 LLM 调用接口
- `OpenAI`: 用于调用 NVIDIA OSS API

### 全局配置

```python
# NVIDIA OSS API 客户端
oss_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("OSS_KEY")
)

# 支持的工具和模型配置
ALL_TOOLS = {
    "enhance_reasoning": {
        'model': ["reasoner-1", "reasoner-2", "reasoner-3"]
    },
    "answer": {
        'model': ["answer-math-1", "answer-math-2", "answer-1", "answer-2", "answer-3", "answer-4"]
    },
    "search": {
        "model": ["search-1", "search-2", "search-3"]
    },
}
```

**工具说明**:

| 工具名称 | 模型选项 | 用途 |
|---------|---------|------|
| **enhance_reasoning** | reasoner-1/2/3 | 生成 Python 代码进行中间推理 |
| **answer** | answer-1/2/3/4, answer-math-1/2 | 生成最终答案 |
| **search** | search-1/2/3 | 检索相关文档 |

**模型选择策略**:
- `reasoner-1` < `reasoner-2` < `reasoner-3`：能力递增，成本和延迟也递增
- `answer-math-1/2`：专门用于数学问题
- `search-1/2/3`：检索服务的不同配置

---

## 核心数据结构

### GenerationConfig

```python
@dataclass
class GenerationConfig:
    """生成配置类"""
    max_turns: int                # 最大轮次（通常为 10）
    max_prompt_length: int        # 最大提示词长度（4096）
    max_response_length: int      # 最大响应长度（2048）
    num_gpus: int                 # GPU 数量（用于 padding）
    no_think_rl: bool = False     # 是否禁用 <think> 标签
    search_url: str = None        # 检索服务 URL
    topk: int = 3                 # 检索 Top-K
```

**配置说明**:
- `max_turns=10`: 每个问题最多进行 10 轮交互
- `max_prompt_length=4096`: 输入 token 限制
- `max_response_length=2048`: 单次生成 token 限制
- `num_gpus`: 影响 batch 的 padding 策略（必须是 GPU 数量的倍数）

---

## 辅助函数

### 1. merge_documents()

```python
def merge_documents(main_list, sub_list):
    """
    交错合并两个文档列表

    策略:
        如果 main_list 更长，按比例插入 sub_list 的元素

    示例:
        main_list = [A, B, C, D, E, F]
        sub_list = [X, Y]

        multiple = 6 // 2 = 3

        结果: [X, A, B, C, Y, D, E, F]

    用途:
        合并不同来源的检索结果（如密集检索 + 稀疏检索）
    """
    if len(sub_list) == 0:
        return main_list
    if len(main_list) < len(sub_list):
        return main_list + sub_list

    merged_list = []
    multiple = len(main_list) // len(sub_list)

    idx_main = 0
    idx_sub = 0

    while idx_sub < len(sub_list):
        # 插入 sub_list 的一个元素
        if sub_list[idx_sub] not in merged_list:
            merged_list.append(sub_list[idx_sub])

        # 插入 main_list 的 multiple 个元素
        for iter_idx in range(idx_main, idx_main + multiple):
            if main_list[iter_idx] not in merged_list:
                merged_list.append(main_list[iter_idx])

        idx_main += multiple
        idx_sub += 1

    # 添加剩余的 main_list 元素
    merged_list += main_list[multiple * len(sub_list):]

    return merged_list
```

### 2. cut_seq()

```python
def cut_seq(tokenizer, seq, l):
    """
    裁剪序列到指定长度（从尾部截取）

    参数:
        tokenizer: HuggingFace tokenizer
        seq: 输入字符串
        l: 最大 token 数量

    返回:
        {
            'effective_length': int,      # 原始长度
            'string_after_cut': str       # 裁剪后的字符串
        }

    用途:
        限制 context 长度，优先保留最新的信息

    示例:
        seq = "很长的文档内容...(5000 tokens)"
        l = 1000

        结果: 只保留最后 1000 tokens 对应的文本
    """
    if len(seq) == 0:
        return {
            'effective_length': 0,
            'string_after_cut': ''
        }

    token_ids = tokenizer(seq)['input_ids']

    # 只保留最后 l 个 token
    rs = tokenizer.batch_decode(token_ids[-l:], skip_special_tokens=True)

    return {
        'effective_length': len(token_ids),
        'string_after_cut': ''.join(rs)
    }
```

### 3. cut_middle_turns()

```python
def cut_middle_turns(tokenizer, messages, max_length):
    """
    裁剪消息历史（保留开头和结尾，删除中间部分）

    策略:
        当消息历史过长时，保留前半部分和后半部分，删除中间部分

    参数:
        tokenizer: HuggingFace tokenizer
        messages: 消息列表 [msg1, msg2, ...]
        max_length: 最大 token 数量

    返回:
        裁剪后的消息列表

    实现原理:
        1. 插入随机标识符标记每条消息的位置
        2. Tokenize 整个序列
        3. 保留前 max_length//2 和后 max_length//2 的 token
        4. 根据标识符确定保留哪些消息
        5. 返回 messages[:p1_idx+1] + messages[p2_idx:]

    示例:
        messages = [msg0, msg1, msg2, msg3, msg4, msg5, msg6, msg7]
        max_length = 可容纳 msg0, msg1, msg6, msg7 的长度

        结果: [msg0, msg1, msg6, msg7]
    """
    exec_count = 0
    while exec_count < 100:
        try:
            exec_count += 1
            messages_str = ''

            # 生成唯一的随机标识符
            start_identifier = generate_random_string(15)
            end_identifier = generate_random_string(15)

            # 标记每条消息的索引
            for mid, m in enumerate(messages):
                messages_str += f"{m}{start_identifier}{mid}{end_identifier}"

            token_ids = tokenizer(str(messages_str))['input_ids']

            # 如果长度未超过，直接返回
            if len(token_ids) <= max_length:
                return messages

            # 保留前半部分
            p1_tokens = tokenizer.batch_decode(token_ids[:max_length//2])
            p1 = ''.join(p1_tokens)
            p1_idx = int(p1.split(start_identifier)[-1].split(end_identifier)[0])

            # 保留后半部分
            p2_tokens = tokenizer.batch_decode(token_ids[-max_length//2:])
            p2 = ''.join(p2_tokens)
            p2_idx = int(p2.split(end_identifier)[0].split(start_identifier)[-1])

            # 返回裁剪后的消息
            return messages[:p1_idx+1] + messages[p2_idx:]

        except Exception as cut_error:
            # 如果标识符冲突，重新生成
            pass
```

---

## 工具调用函数 call_tool

`call_tool()` 函数是工具调用的核心实现，长达约 600 行。下面分模块解释：

### 函数签名

```python
def call_tool(arguments):
    """
    执行单个工具调用

    参数:
        arguments: dict，包含以下字段
            - category: 'qa' 或 'func_call'
            - tool: 工具名称（'enhance_reasoning', 'answer', 'search'）
            - model: 模型选择（如 'reasoner-1'）
            - cur_model_mapping: 模型映射（reasoner-1 → gpt-5）
            - cur_tool_pricing: 定价信息
            - context_str: 当前上下文
            - problem: 问题文本
            - vllm_model_configs: vLLM 服务配置
            - ... 其他字段

    返回:
        arguments: 更新后的字典，包含
            - generated_code: 生成的代码（如果是 enhance_reasoning）
            - exec_result: 执行结果
            - answer: 最终答案（如果是 answer）
            - documents: 检索到的文档（如果是 search）
            - cost: API 成本
            - latency: 延迟
            - tokens_pic: Token 使用记录
    """
    start_time = time.time()
```

### QA 任务 - enhance_reasoning 工具

```python
if arguments['category'] == 'qa':
    if arguments['tool'] == 'enhance_reasoning':
        cost = 0
        model_name = arguments['cur_model_mapping'][arguments['model']]
        cur_tool_pricing = arguments['cur_tool_pricing']

        # Case 1: 使用 OpenAI/NVIDIA API（o3, gpt-5 等）
        if model_name in ['o3', 'o3-mini', 'gpt-5', 'gpt-5-mini']:
            # 1. 构建 prompt
            prompt = arguments['context_str'].strip() + '\n\n'
            prompt += f"Question: {arguments['problem']}\n"
            prompt += "Instead of directly answering the question, "
            prompt += "please write additional python code that will give "
            prompt += "intermediate results after execution. Wrap the code "
            prompt += "within ```python and ```. The code should be "
            prompt += "self-contained with all the import and initialization."

            # 2. 调用 LLM
            latency_testing_start_time = time.time()
            response = get_llm_response(
                model=model_name,
                messages=prompt,
                return_raw_response=True,
                temperature=1,
                max_length=28000
            )
            latency_testing_end_time = time.time()

            # 3. 处理响应失败
            if isinstance(response, str) or not response.choices[0].message.content:
                arguments['generated_code'] = ''
                arguments['exec_result'] = ''
                arguments['cost'] = cost
                arguments['latency'] = time.time() - start_time
                return arguments

            # 4. 记录 token 使用
            if 'tokens_pic' not in arguments:
                arguments['tokens_pic'] = []

            arguments['tokens_pic'].append({
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'model': model_name,
                'latency': latency_testing_end_time - latency_testing_start_time
            })

            # 5. 计算成本
            cost += (
                cur_tool_pricing[model_name]['input_tokens_per_million'] *
                response.usage.prompt_tokens +
                cur_tool_pricing[model_name]['output_tokens_per_million'] *
                response.usage.completion_tokens
            )

            # 6. 提取代码
            try:
                generated_code = response.choices[0].message.content.split('```python')[-1].split('```')[0]
            except:
                arguments['generated_code'] = ''
                arguments['exec_result'] = ''
                arguments['cost'] = cost
                arguments['latency'] = time.time() - start_time
                return arguments

        # Case 2: 使用 vLLM 服务（Qwen2.5-Coder, Llama 等）
        elif 'qwen2.5-coder' in model_name.lower() or 'llama' in model_name.lower():
            prompt = arguments['context_str'].strip() + '\n\n'
            prompt += f"Question: {arguments['problem']}\n..."

            latency_testing_start_time = time.time()
            response = get_llm_response(
                model=model_name,
                messages=prompt,
                return_raw_response=True,
                model_type='vllm',
                max_length=8000,
                temperature=0.2,
                model_config=arguments['vllm_model_configs'][model_name],
                model_config_path=arguments['vllm_model_configs']['vllm_model_config_path'],
                model_config_idx=arguments['id']
            )
            latency_testing_end_time = time.time()

            # 如果 vLLM 服务失败，fallback 到 OSS API
            if isinstance(response, str):
                response = ''
                while not response:
                    try:
                        response = oss_client.chat.completions.create(
                            model="nvdev/qwen/qwen2.5-coder-32b-instruct",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2,
                            top_p=0.7,
                            max_tokens=30000,
                        )
                    except Exception as qwen_error:
                        time.sleep(60)

            # ... 后续处理与 Case 1 类似

        # 7. 执行生成的代码
        if generated_code:
            # 调用 Sandbox API 执行代码
            exec_result = execute_code_in_sandbox(
                code=generated_code,
                sandbox_url=arguments.get('sandbox_url'),
                timeout=30
            )

            arguments['generated_code'] = generated_code
            arguments['exec_result'] = exec_result
        else:
            arguments['generated_code'] = ''
            arguments['exec_result'] = ''

        arguments['cost'] = cost
        arguments['latency'] = time.time() - start_time
        return arguments
```

**enhance_reasoning 工具流程图**:

```
用户问题 + 上下文
    ↓
构建 prompt（请求生成 Python 代码）
    ↓
调用 LLM（gpt-5 / vLLM）
    ↓
提取 ```python...``` 代码块
    ↓
调用 Sandbox API 执行代码
    ↓
返回执行结果（stdout, stderr）
```

### QA 任务 - answer 工具

```python
elif arguments['tool'] == 'answer':
    cost = 0
    model_name = arguments['cur_model_mapping'][arguments['model']]
    cur_tool_pricing = arguments['cur_tool_pricing']

    # 1. 根据模型类型调整 context 长度
    if 'math' in cur_model_to_call.lower():
        # 数学模型：使用较短的 context
        str_cut = cut_seq(tokenizer=tokenizer, seq=code_str, l=1000)
        code_str = str_cut['string_after_cut']

        context_str = cut_seq(
            tokenizer=tokenizer,
            seq=doc_str + code_str,
            l=2000
        )
    else:
        # 通用模型：使用较长的 context
        context_str = cut_seq(
            tokenizer=tokenizer,
            seq=doc_str + code_str + attempt_str,
            l=16000
        )

    # 2. 构建 prompt
    prompt = context_str['string_after_cut'] + '\n\n'
    prompt += f"Question: {arguments['problem']}\n"
    prompt += "Please provide the final answer."

    # 3. 调用 LLM
    response = get_llm_response(
        model=model_name,
        messages=prompt,
        return_raw_response=True,
        temperature=0.7,
        max_length=2048
    )

    # 4. 提取答案
    answer = extract_answer(response.choices[0].message.content)

    # 5. 记录成本和延迟
    arguments['answer'] = answer
    arguments['cost'] = cost
    arguments['latency'] = time.time() - start_time

    return arguments
```

### QA 任务 - search 工具

```python
elif arguments['tool'] == 'search':
    # 1. 获取检索服务配置
    model_name = arguments['cur_model_mapping'][arguments['model']]
    cur_model_config = arguments['vllm_model_configs'][model_name]

    # 2. 构建查询
    query = arguments['problem']

    # 3. 调用检索服务
    payload = {
        'query': query,
        'topk': arguments.get('topk', 5)
    }

    results = requests.post(
        f'http://{cur_model_config["ip_addr"]}:{cur_model_config["port"]}/retrieve',
        json=payload
    ).json()

    # 4. 提取文档
    documents = [doc['text'] for doc in results['documents']]

    arguments['documents'] = documents
    arguments['cost'] = 0  # 检索服务通常不计费
    arguments['latency'] = time.time() - start_time

    return arguments
```

### func_call 任务处理

```python
elif arguments['category'] == 'func_call':
    # func_call 任务通过文件系统与 tau2 进程通信

    # 1. 等待 tau2 进程生成 output 文件
    transfer_idx = arguments['transfer_idx']
    cur_transfer_dir = arguments['cur_transfer_dir']

    output_path = os.path.join(cur_transfer_dir, f"output_{transfer_idx}.json")

    # 等待文件生成
    while not os.path.isfile(output_path):
        time.sleep(1)

    # 2. 读取 tau2 的响应
    with open(output_path) as f:
        output_dict = json.load(f)

    # 3. 返回结果
    arguments['tool_result'] = output_dict
    arguments['cost'] = 0
    arguments['latency'] = time.time() - start_time

    return arguments
```

### call_tool_all()

```python
def call_tool_all(all_arguments):
    """
    批量执行多个工具调用（容错版本）

    参数:
        all_arguments: dict
            - id: 样本 ID
            - all_call_arguments: List[dict]，每个元素是 call_tool 的参数

    返回:
        {
            'id': 样本 ID,
            'all_tool_call_results': List[dict]，每个工具调用的结果
        }

    容错设计:
        每个工具调用用 try-except 包裹，失败不会影响其他调用
    """
    all_return_arguments = []

    for one_arguments in all_arguments['all_call_arguments']:
        try:
            result = call_tool(one_arguments)
            all_return_arguments.append(result)
        except Exception as tool_call_error:
            # 工具调用失败，跳过
            print(f"Tool call error: {tool_call_error}")
            pass

    return {
        'id': all_arguments['id'],
        'all_tool_call_results': all_return_arguments
    }
```

---

## LLMGenerationManager 类

### 类初始化

```python
class LLMGenerationManager:
    """
    LLM 生成管理器

    职责:
        1. 管理 Multi-turn 生成循环
        2. 调用 veRL 的 Actor Worker 进行生成
        3. 执行工具调用
        4. 计算 Reward
    """

    def __init__(
        self,
        tokenizer,
        actor_rollout_wg,
        config: GenerationConfig,
        is_validation: bool = False,
        train_tool_config_path=None,
        test_tool_config_path=None,
    ):
        """
        参数:
            tokenizer: HuggingFace tokenizer
            actor_rollout_wg: veRL 的 Actor Worker Group
            config: GenerationConfig
            is_validation: 是否是验证模式
            train_tool_config_path: 训练时的工具配置文件路径
            test_tool_config_path: 测试时的工具配置文件路径
        """
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.config = config
        self.is_validation = is_validation

        # 初始化 TensorHelper
        self.tensor_fn = TensorHelper(TensorConfig(
            pad_token_id=tokenizer.pad_token_id,
            max_prompt_length=config.max_prompt_length
        ))
```

### _generate_with_gpu_padding()

```python
def _generate_with_gpu_padding(self, active_batch: DataProto) -> DataProto:
    """
    带 GPU padding 的生成包装器

    问题:
        veRL 的分布式生成要求 batch size 必须是 GPU 数量的倍数

    解决方案:
        如果 batch size 不是 GPU 数量的倍数，用第一个样本 padding

    示例:
        num_gpus = 8
        batch_size = 13

        步骤:
            1. 复制第一个样本 3 次（13 + 3 = 16，是 8 的倍数）
            2. 调用 actor_rollout_wg.generate_sequences()
            3. 移除 padding 的 3 个样本
            4. 返回原始的 13 个样本的结果

    参数:
        active_batch: DataProto

    返回:
        DataProto（生成结果）
    """
    num_gpus = self.config.num_gpus

    # 单 GPU 或 batch size 已经是倍数，直接生成
    if num_gpus <= 1:
        return self.actor_rollout_wg.generate_sequences(active_batch)

    original_batch_size = active_batch.batch['input_ids'].shape[0]

    # 检查是否需要 padding
    if original_batch_size % num_gpus == 0:
        return self.actor_rollout_wg.generate_sequences(active_batch)

    # 计算需要 padding 的数量
    padding_size = num_gpus - (original_batch_size % num_gpus)

    # 复制第一个样本
    first_sample = {
        key: tensor[0:1].repeat(padding_size, *([1] * (tensor.ndim - 1)))
        for key, tensor in active_batch.batch.items()
    }

    # 拼接
    padded_batch_dict = {
        key: torch.cat([active_batch.batch[key], first_sample[key]], dim=0)
        for key in active_batch.batch.keys()
    }

    padded_batch = DataProto.from_dict(padded_batch_dict)

    # 生成
    padded_output = self.actor_rollout_wg.generate_sequences(padded_batch)

    # 移除 padding
    output_dict = {
        key: tensor[:original_batch_size]
        for key, tensor in padded_output.batch.items()
    }

    return DataProto.from_dict(output_dict)
```

---

## run_llm_loop 核心方法

`run_llm_loop()` 是整个文件的核心，实现 Multi-turn 生成循环。

### 方法签名

```python
def run_llm_loop(
    self,
    gen_batch,                    # DataToolProto
    tokenizer_config,             # dict
    global_steps,                 # int
    topk_doc,                     # int
    use_llm_reward,              # bool
    efficiency_reward,           # bool
    exp_tag,                     # str
    use_qa_reward                # bool
):
    """
    运行 Multi-turn LLM 生成循环

    参数:
        gen_batch: DataToolProto
            - non_tensor_batch:
                - 'problem': 问题列表
                - 'category': 任务类型列表（'qa' 或 'func_call'）
                - 'index': 样本索引
                - 'repeat_id': Repeat ID（GRPO 需要）
                - 'model_mapping': 模型映射字典
                - 'tool_pricing': 定价信息
                - 'vllm_model_configs': vLLM 配置
                - 'tools': 工具配置
                - ... 其他字段

        tokenizer_config: dict
            - 'tokenizer': HuggingFace tokenizer
            - 'max_prompt_length': int
            - 'max_response_length': int
            - 'truncation': str

        global_steps: 当前训练步数
        topk_doc: 检索文档数量
        use_llm_reward: 是否使用 LLM 评估 Reward
        efficiency_reward: 是否使用效率奖励
        exp_tag: 实验标签
        use_qa_reward: 是否使用 QA Reward

    返回:
        (final_gen_batch_output, tool_avg)

        final_gen_batch_output: DataToolProto
            - batch:
                - 'prompts': Tensor [batch, prompt_len]
                - 'responses': Tensor [batch, response_len]
                - 'attention_mask': Tensor [batch, total_len]
                - 'token_level_rewards': Tensor [batch, total_len]
            - non_tensor_batch:
                - 'index': 样本索引
                - 'repeat_id': Repeat ID
                - ... 其他字段

        tool_avg: dict（工具使用统计）
    """
```

### 初始化阶段

```python
# 1. 获取 batch size
loop_batch_size = len(gen_batch.non_tensor_batch['problem'])

# 2. 初始化 active_mask（追踪哪些样本还在继续）
active_mask = torch.ones(loop_batch_size, dtype=torch.bool)

# 3. 初始化累积列表
retrieved_documents = [[] for _ in range(loop_batch_size)]  # 每个样本检索到的文档
code_snippets = [[] for _ in range(loop_batch_size)]        # 每个样本执行的代码
attempts = [[] for _ in range(loop_batch_size)]             # 每个样本的答案尝试
total_costs = [0 for _ in range(loop_batch_size)]           # 每个样本的累积成本

# 4. 初始化记录列表（用于最终返回）
all_turn_input_ids = []
all_turn_attention_mask = []
all_turn_position_ids = []
all_turn_responses = []
all_turn_index = []
all_turn_ids = []
all_turn_turn_ids = []
all_turn_repeat_ids = []
all_turn_answers = []
all_turn_answer_preds = []
all_turn_problems = []
all_turn_tools = []
all_turn_success = []
all_turn_costs = []
all_turn_latency = []
all_turn_formats = []
all_turn_valid_answers_generated = []
all_turn_used_llms = []
all_turn_steps = []
all_turn_categories = []
all_pref_vecs = {}

# 5. 其他初始化
meta_info = {}
example_correct_by_rollout_id = {}
my_output_dir = gen_batch.non_tensor_batch['my_output_dir'][0]
```

### Multi-turn 循环主体

```python
# Multi-turn 循环
for step in range(self.config.max_turns):
    # 创建输出目录
    if not os.path.isdir(os.path.join(my_output_dir, f"global_step_{global_steps}", f"rollout_step_{step}")):
        os.makedirs(os.path.join(my_output_dir, f"global_step_{global_steps}", f"rollout_step_{step}"))

    # 检查是否所有样本都完成了
    if not active_mask.sum():
        break

    # ═══════════════════════════════════════════════════════════
    # 阶段 1: 启动 func_call 任务的 tau2 进程（仅第一轮）
    # ═══════════════════════════════════════════════════════════
    if step == 0:
        for item_idx in range(loop_batch_size):
            category = gen_batch.non_tensor_batch['category'][item_idx]

            if category != 'func_call':
                continue

            # 创建临时目录
            item_index = gen_batch.non_tensor_batch['index'][item_idx]
            item_repeat_id = gen_batch.non_tensor_batch['repeat_id'][item_idx]
            iter_rollout_id = f"{item_index}_____{item_repeat_id}"

            cur_transfer_dir = os.path.join(
                gen_batch.non_tensor_batch['cur_transfer_dir'][item_idx],
                str(global_steps),
                iter_rollout_id
            )

            if not os.path.isdir(cur_transfer_dir):
                os.makedirs(cur_transfer_dir, exist_ok=True)

            # 准备 tau2 命令
            task_path = os.path.join(cur_transfer_dir, 'task.json')
            cur_domain = item_index.split('____')[0]

            func_call_cmd = [
                'python', 'rollout/tau2/cli.py',
                '--domain', cur_domain,
                '--agent-llm', 'train',
                '--user-llm', 'gpt-5',
                '--num-trials', '1',
                '--task_path', str(task_path),
                '--max-steps', '40',
                '--cur_transfer_dir', str(cur_transfer_dir),
                '--output_file', str(cur_func_call_output_path),
                '--use_model_tool'
            ]

            # 启动 tau2 进程（非阻塞）
            subprocess.Popen(func_call_cmd)

    # ═══════════════════════════════════════════════════════════
    # 阶段 2: 构建 prompt（包含累积的 context）
    # ═══════════════════════════════════════════════════════════
    all_input_ids = []
    all_attention_mask = []
    all_categories = []
    all_indices = []
    all_input_messages = []
    all_input_tools = []

    item_idx = -1
    for doc_list, code_list, attempt_list in zip(retrieved_documents, code_snippets, attempts):
        item_idx += 1

        category = gen_batch.non_tensor_batch['category'][item_idx]
        all_categories.append(category)

        item_index = gen_batch.non_tensor_batch['index'][item_idx]
        item_repeat_id = gen_batch.non_tensor_batch['repeat_id'][item_idx]

        # ─────────────────────────────────────────────────────
        # Case 1: QA 任务
        # ─────────────────────────────────────────────────────
        if category == 'qa':
            problem = gen_batch.non_tensor_batch['problem'][item_idx]
            tools = gen_batch.non_tensor_batch['tools'][item_idx]

            # 构建 context 字符串
            # 1. 文档
            doc_str = ''
            for doc_idx, doc in enumerate(doc_list):
                doc_str += f"Doc {doc_idx+1}: {doc[:4000]}\n\n"

            # 2. 代码执行结果
            code_str = ''
            for code_idx, code_piece in enumerate(code_list):
                code_str += f"```python\n{code_piece['code']}\n```\n\n"
                code_str += f"```output\n{code_piece['output']}\n```\n\n"

            # 3. 答案尝试
            attempt_str = ''
            for attempt_idx, attempt in enumerate(attempt_list):
                attempt_str += f"Attempt{attempt_idx+1} answer by {attempt['model']}: {attempt['answer']}\n"

            # 4. 裁剪到合适长度
            str_cut = cut_seq(tokenizer=tokenizer, seq=attempt_str, l=8000)
            attempt_str = str_cut['string_after_cut']

            str_cut = cut_seq(tokenizer=tokenizer, seq=code_str + attempt_str, l=16000)
            code_attempt_str = str_cut['string_after_cut']

            # 5. 合并 documents + code + attempts
            context_str = cut_seq(
                tokenizer=tokenizer,
                seq=doc_str + code_attempt_str,
                l=24000
            )
            context_str = context_str['string_after_cut']

            if len(doc_str) > 0:
                context_str = 'Documents:\n' + context_str

            # 6. 构建 chat 格式
            chat = [
                {"role": "system", "content": "You are good at using tools. "},
                {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an appropriate tool."}
            ]

            all_input_messages.append(chat)
            all_input_tools.append(tools)

        # ─────────────────────────────────────────────────────
        # Case 2: func_call 任务
        # ─────────────────────────────────────────────────────
        elif category == 'func_call':
            iter_rollout_id = f"{item_index}_____{item_repeat_id}"
            cur_transfer_dir = os.path.join(
                gen_batch.non_tensor_batch['cur_transfer_dir'][item_idx],
                str(global_steps),
                iter_rollout_id
            )

            # 等待 tau2 进程生成 input 文件
            transfer_idx = 0
            while os.path.isfile(os.path.join(cur_transfer_dir, f"output_{transfer_idx}.json")):
                transfer_idx += 1

            receive_end_signal = False

            # 轮询等待 input 文件
            while not os.path.isfile(os.path.join(cur_transfer_dir, f"input_{transfer_idx}.json")):
                # 检查是否收到结束信号
                if os.path.isfile(os.path.join(cur_transfer_dir, 'done')):
                    try:
                        with open(os.path.join(cur_transfer_dir, 'done')) as f:
                            tmp_result = f.read()

                        if tmp_result == "Done!":
                            # 读取最终 reward
                            correct = 0
                            for subfile in os.listdir(os.path.join(cur_transfer_dir, 'output')):
                                if subfile.endswith('.json'):
                                    with open(os.path.join(cur_transfer_dir, 'output', subfile)) as f:
                                        r = json.load(f)
                                    correct += r["reward_info"]["reward"]

                            simulation_reward = 1 if correct > 0 else 0
                            example_correct_by_rollout_id[iter_rollout_id] = simulation_reward
                    except:
                        pass

                    # 标记为完成
                    active_mask[item_idx] = 0
                    receive_end_signal = True
                    break

                time.sleep(5)  # 每 5 秒检查一次

            # 读取 input 文件
            if not receive_end_signal:
                with open(os.path.join(cur_transfer_dir, f"input_{transfer_idx}.json")) as f:
                    input_dict = json.load(f)

                tools = input_dict['tools']
                chat = input_dict['messages']
            else:
                # 收到结束信号，使用假数据
                tools = []
                chat = [{'role': 'user', 'content': 'fake input'}]

            all_input_messages.append(chat)
            all_input_tools.append(tools)

    # ═══════════════════════════════════════════════════════════
    # 阶段 3: Tokenize 和生成
    # ═══════════════════════════════════════════════════════════

    # 1. 应用 chat template
    prompts_with_chat_template = []
    for chat, tools in zip(all_input_messages, all_input_tools):
        prompt = tokenizer.apply_chat_template(
            chat,
            add_generation_prompt=True,
            tools=tools,
            tokenize=False
        )
        prompts_with_chat_template.append(prompt)

    # 2. Tokenize
    tokenized = []
    for prompt in prompts_with_chat_template:
        input_ids, attention_mask = verl_F.tokenize_and_postprocess_data(
            prompt=prompt,
            tokenizer=tokenizer,
            max_length=tokenizer_config['max_prompt_length'],
            pad_token_id=tokenizer.pad_token_id,
            left_pad=True,
            truncation='middle'
        )
        tokenized.append({
            'input_ids': input_ids,
            'attention_mask': attention_mask
        })

    # 3. Stack 成 batch
    batch_input_ids = torch.stack([t['input_ids'] for t in tokenized])
    batch_attention_mask = torch.stack([t['attention_mask'] for t in tokenized])

    # 4. 创建 position_ids
    batch_position_ids = compute_position_id_with_mask(
        batch_attention_mask,
        use_first_padding=True
    )

    # 5. 只保留 active 的样本
    active_indices = torch.where(active_mask)[0]

    rollings_active = DataProto.from_dict({
        'input_ids': batch_input_ids[active_indices],
        'attention_mask': batch_attention_mask[active_indices],
        'position_ids': batch_position_ids[active_indices]
    })

    # 6. 调用 veRL Actor 生成
    gen_output = self._generate_with_gpu_padding(rollings_active)

    # 7. 将结果填回完整 batch
    full_batch_responses = torch.zeros(
        loop_batch_size,
        gen_output.batch['responses'].shape[1],
        dtype=torch.long
    )
    full_batch_responses[active_indices] = gen_output.batch['responses']

    # ═══════════════════════════════════════════════════════════
    # 阶段 4: 后处理和工具调用
    # ═══════════════════════════════════════════════════════════

    # 1. Decode responses
    predictions = tokenizer.batch_decode(
        full_batch_responses,
        skip_special_tokens=True
    )

    # 2. 提取工具调用
    tool_calls, format_corrects = self.postprocess_predictions(
        predictions,
        all_categories
    )

    # 3. 执行工具调用
    new_documents, new_code, new_attempts, dones, costs, latency = self.execute_predictions(
        tool_calls,
        gen_batch,
        step,
        global_steps
    )

    # ═══════════════════════════════════════════════════════════
    # 阶段 5: 更新状态
    # ═══════════════════════════════════════════════════════════

    for i in range(loop_batch_size):
        if active_mask[i]:
            # 累积新的结果
            retrieved_documents[i] += new_documents[i]
            code_snippets[i] += new_code[i]
            attempts[i] += new_attempts[i]
            total_costs[i] += costs[i]

    # 更新 active_mask
    curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
    active_mask = active_mask * curr_active_mask

    # 记录当前 turn 的数据
    all_turn_input_ids.append(batch_input_ids)
    all_turn_responses.append(full_batch_responses)
    all_turn_attention_mask.append(batch_attention_mask)
    all_turn_costs.append(costs)
    all_turn_latency.append(latency)
    all_turn_formats.append(format_corrects)
    # ... 其他字段
```

### Reward 计算阶段

```python
# Multi-turn 循环结束后，计算 Reward

# ═══════════════════════════════════════════════════════════
# 1. 收集所有样本的正确性
# ═══════════════════════════════════════════════════════════
example_correctness = {}
for example_idx, example_repeat_id, turn_success in zip(
    all_turn_index, all_turn_repeat_ids, all_turn_success
):
    rollout_id = f"{example_idx}_____{example_repeat_id}"

    if turn_success or (rollout_id in example_correct_by_rollout_id and example_correct_by_rollout_id[rollout_id]):
        example_correctness[rollout_id] = True
    elif rollout_id not in example_correctness:
        example_correctness[rollout_id] = False

# ═══════════════════════════════════════════════════════════
# 2. 累积成本和延迟
# ═══════════════════════════════════════════════════════════
example_costs = defaultdict(int)
example_latency = defaultdict(int)

for example_idx, example_repeat_id, turn_cost, turn_latency in zip(
    all_turn_index, all_turn_repeat_ids, all_turn_costs, all_turn_latency
):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    example_costs[rollout_id] += turn_cost
    example_latency[rollout_id] += turn_latency

# ═══════════════════════════════════════════════════════════
# 3. 计算 Raw Reward（Outcome + Efficiency）
# ═══════════════════════════════════════════════════════════
rewards_by_rollout_id = {}

for rollout_id in example_correctness.keys():
    if str(efficiency_reward).lower() == 'true' and example_correctness[rollout_id]:
        # Efficiency reward: 惩罚高成本和高延迟
        cost_reward = example_costs[rollout_id] * 5
        latency_reward = example_latency[rollout_id] / 500

        if cost_reward + latency_reward > 0.8:
            rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id]) - 0.8
        else:
            rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id]) - latency_reward - cost_reward
    else:
        # 只有 Outcome reward
        rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])

# ═══════════════════════════════════════════════════════════
# 4. GRPO 归一化（组内标准化）
# ═══════════════════════════════════════════════════════════

# 4.1 收集每个问题的所有 rollout 的 reward
example_rewards = defaultdict(list)
example_indices = set()

for rollout_id, reward in rewards_by_rollout_id.items():
    example_idx = rollout_id.split('_____')[0]
    example_indices.add(example_idx)
    example_rewards[example_idx].append(reward)

# 4.2 计算每个问题的均值和标准差
example_reward_average = {}
example_reward_std = {}

for example_idx in example_indices:
    if len(example_rewards[example_idx]) > 1:
        example_reward_average[example_idx] = sum(example_rewards[example_idx]) / len(example_rewards[example_idx])
        example_reward_std[example_idx] = stdev(example_rewards[example_idx])
    else:
        example_reward_average[example_idx] = example_rewards[example_idx][0]
        example_reward_std[example_idx] = 0.0

# 4.3 归一化每个 rollout 的 reward
normalized_rewards_by_rollout_id = {}

for rollout_id, reward in rewards_by_rollout_id.items():
    example_idx = rollout_id.split('_____')[0]

    # 归一化
    if example_reward_std[example_idx] > 0:
        normalized_reward = (reward - example_reward_average[example_idx]) / (example_reward_std[example_idx] + 1e-6)
    else:
        normalized_reward = 0.0

    # Clip 到 [-3, 3]
    normalized_reward = max(-3.0, min(3.0, normalized_reward))

    normalized_rewards_by_rollout_id[rollout_id] = normalized_reward

# ═══════════════════════════════════════════════════════════
# 5. 过滤训练样本
# ═══════════════════════════════════════════════════════════
selected_indices = []

for iter_index, (rollout_id, turn_format, valid_answer) in enumerate(
    zip(all_rollout_ids, all_turn_formats, all_turn_valid_answers_generated)
):
    example_idx = rollout_id.split('_____')[0]

    # 选择条件:
    #   1. reward 标准差 > 0.1（有足够的方差）
    #   2. 格式正确
    #   3. 有有效答案
    if (example_reward_std[example_idx] > 0.1 and
        turn_format and
        rollout_id in valid_answer and
        valid_answer[rollout_id]):
        selected_indices.append(iter_index)
```

### 构建最终输出

```python
# ═══════════════════════════════════════════════════════════
# 6. 构建最终输出 DataProto
# ═══════════════════════════════════════════════════════════

if len(selected_indices) == 0:
    # 没有有效样本，返回空
    return None, {}

# 6.1 Stack 所有 tensor
all_prompts = torch.cat([all_turn_input_ids[i] for i in selected_indices], dim=0)
all_responses = torch.cat([all_turn_responses[i] for i in selected_indices], dim=0)
all_attention_masks = torch.cat([all_turn_attention_mask[i] for i in selected_indices], dim=0)

# 6.2 构建 token_level_rewards
all_rewards = []
for idx in selected_indices:
    rollout_id = all_rollout_ids[idx]
    reward = normalized_rewards_by_rollout_id[rollout_id]

    # Reward 只应用在最后一个 token
    token_rewards = torch.zeros(all_responses[idx].shape[0])
    token_rewards[-1] = reward

    all_rewards.append(token_rewards)

all_rewards = torch.stack(all_rewards)

# 6.3 创建 DataProto
final_gen_batch_output = DataProto.from_dict(
    tensors={
        'prompts': all_prompts,
        'responses': all_responses,
        'attention_mask': all_attention_masks,
        'token_level_rewards': all_rewards
    },
    non_tensors={
        'index': [all_turn_index[i] for i in selected_indices],
        'repeat_id': [all_turn_repeat_ids[i] for i in selected_indices],
        'problem': [all_turn_problems[i] for i in selected_indices],
        'category': [all_turn_categories[i] for i in selected_indices],
        # ... 其他字段
    }
)

# 6.4 计算工具使用统计
tool_avg = {
    'total_tool_calls': tool_total,
    'avg_cost_per_sample': sum(example_costs.values()) / len(example_costs),
    'avg_latency_per_sample': sum(example_latency.values()) / len(example_latency),
}

return final_gen_batch_output, tool_avg
```

---

## 后处理方法

### postprocess_predictions()

```python
def postprocess_predictions(self, predictions, all_categories):
    """
    后处理模型输出，提取 JSON 格式的工具调用

    期望格式:
        <think>推理过程</think>
        <tool_call>
        {"name": "enhance_reasoning", "arguments": {"model": "reasoner-1"}}
        </tool_call>

    验证规则:
        1. 提取 <tool_call>...</tool_call> 之间的内容
        2. 解析 JSON
        3. 验证 keys == {"name", "arguments"}
        4. 验证工具名称在 ALL_TOOLS 中
        5. 验证参数名称和值符合工具签名

    参数:
        predictions: List[str]，模型生成的文本列表
        all_categories: List[str]，任务类型列表

    返回:
        (all_tool_calls, format_corrects)

        all_tool_calls: List[List[dict]]
            每个样本的工具调用列表

        format_corrects: List[bool]
            每个样本的格式是否正确
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
                added_tools = set()  # 去重

                for c in components:
                    components1 = c.split('</tool_call>')

                    for c1 in components1:
                        try:
                            # 尝试解析 JSON
                            tmp_tool_call = json.loads(c1)

                            # 验证格式
                            assert set(list(tmp_tool_call.keys())) == {"name", "arguments"}
                            assert tmp_tool_call['name'] in ALL_TOOLS

                            # 去重
                            if tmp_tool_call['name'] in added_tools:
                                continue
                            added_tools.add(tmp_tool_call['name'])

                            # 验证参数
                            func_signature = ALL_TOOLS[tmp_tool_call['name']]
                            for parameter_name, parameter_values in func_signature.items():
                                assert tmp_tool_call["arguments"][parameter_name] in parameter_values or parameter_values == 'any'

                            cur_all_tool_calls.append(tmp_tool_call)

                        except:
                            # JSON 解析失败或验证失败，跳过
                            pass

                if len(cur_all_tool_calls) > 0:
                    format_correct = True

            elif category == 'func_call':
                # func_call 任务的格式验证（略）
                pass

        all_tool_calls.append(cur_all_tool_calls)
        format_corrects.append(format_correct)

    return all_tool_calls, format_corrects
```

**格式验证流程图**:

```
模型输出: "<think>...</think><tool_call>{...}</tool_call>"
    ↓
按 <tool_call> 分割
    ↓
按 </tool_call> 分割
    ↓
json.loads() 尝试解析
    ↓ (成功)
验证 keys == {"name", "arguments"}
    ↓ (通过)
验证 name in ALL_TOOLS
    ↓ (通过)
验证参数名称和值
    ↓ (通过)
format_correct = True
```

### execute_predictions()

```python
def execute_predictions(self, predictions, gen_batch, step, global_steps):
    """
    执行工具调用预测

    支持的工具:
        - enhance_reasoning: 调用推理模型生成代码并执行
        - search: 调用检索服务获取文档
        - answer: 调用答案模型生成最终答案

    参数:
        predictions: List[List[dict]]，每个样本的工具调用列表
        gen_batch: DataToolProto
        step: 当前轮次
        global_steps: 全局步数

    返回:
        (new_documents, new_code, new_attempts, dones, costs, latency)

        new_documents: List[List[str]]
            每个样本新检索的文档列表

        new_code: List[List[dict]]
            每个样本新执行的代码及输出
            格式: [{'code': str, 'output': str}, ...]

        new_attempts: List[List[dict]]
            每个样本新的答案尝试
            格式: [{'model': str, 'answer': str}, ...]

        dones: List[bool]
            每个样本是否完成

        costs: List[float]
            每个样本本轮的 API 成本

        latency: List[float]
            每个样本本轮的延迟
    """
    loop_batch_size = len(predictions)

    # 初始化返回列表
    new_documents = [[] for _ in range(loop_batch_size)]
    new_code = [[] for _ in range(loop_batch_size)]
    new_attempts = [[] for _ in range(loop_batch_size)]
    dones = [False for _ in range(loop_batch_size)]
    costs = [0.0 for _ in range(loop_batch_size)]
    latency = [0.0 for _ in range(loop_batch_size)]

    # 准备工具调用参数
    all_tool_call_arguments = []

    for item_idx, iter_tool_calls in enumerate(predictions):
        category = gen_batch.non_tensor_batch['category'][item_idx]

        if category == 'qa':
            for tool_call in iter_tool_calls:
                # 验证工具调用
                if not isinstance(tool_call, dict):
                    continue
                if set(list(tool_call.keys())) != {'name', "arguments"}:
                    continue
                if tool_call['name'] not in ALL_TOOLS:
                    continue

                # 准备调用参数
                arguments = {
                    'id': item_idx,
                    'category': category,
                    'tool': tool_call['name'],
                    'model': tool_call['arguments'].get('model'),
                    'cur_model_mapping': gen_batch.non_tensor_batch['model_mapping'][item_idx],
                    'cur_tool_pricing': gen_batch.non_tensor_batch['tool_pricing'][item_idx],
                    'context_str': ...,  # 当前上下文
                    'problem': gen_batch.non_tensor_batch['problem'][item_idx],
                    'vllm_model_configs': gen_batch.non_tensor_batch['vllm_model_configs'][item_idx],
                    # ... 其他字段
                }

                all_tool_call_arguments.append(arguments)

        elif category == 'func_call':
            # func_call 任务的处理（略）
            pass

    # 批量执行工具调用（并行）
    if len(all_tool_call_arguments) > 0:
        # 使用 multiprocessing 并行执行
        with mp.Pool(processes=min(32, len(all_tool_call_arguments))) as pool:
            results = pool.map(call_tool, all_tool_call_arguments)

        # 收集结果
        for result in results:
            item_idx = result['id']

            # 累积成本和延迟
            costs[item_idx] += result.get('cost', 0.0)
            latency[item_idx] += result.get('latency', 0.0)

            # 根据工具类型处理结果
            if result.get('tool') == 'enhance_reasoning':
                if result.get('generated_code'):
                    new_code[item_idx].append({
                        'code': result['generated_code'],
                        'output': result.get('exec_result', '')
                    })

            elif result.get('tool') == 'search':
                if result.get('documents'):
                    new_documents[item_idx].extend(result['documents'])

            elif result.get('tool') == 'answer':
                if result.get('answer'):
                    new_attempts[item_idx].append({
                        'model': result['model'],
                        'answer': result['answer']
                    })

                    # 检查答案是否正确
                    if check_answer_correct(result['answer'], ground_truth):
                        dones[item_idx] = True

    return new_documents, new_code, new_attempts, dones, costs, latency
```

---

## Reward 计算

Reward 计算分为三个部分：

### 1. Outcome Reward

```python
# 基础 reward：任务是否成功
if example_correctness[rollout_id]:
    base_reward = 1.0
else:
    base_reward = 0.0
```

### 2. Efficiency Reward

```python
if str(efficiency_reward).lower() == 'true' and example_correctness[rollout_id]:
    # 计算成本惩罚（API 成本）
    cost_reward = example_costs[rollout_id] * 5

    # 计算延迟惩罚
    latency_reward = example_latency[rollout_id] / 500

    # 总惩罚
    total_penalty = cost_reward + latency_reward

    # 应用惩罚
    if total_penalty > 0.8:
        # 惩罚过大，固定扣除
        raw_reward = base_reward - 0.8
    else:
        raw_reward = base_reward - total_penalty
else:
    raw_reward = base_reward
```

**Efficiency Reward 设计思想**:
- 只对成功的样本应用效率惩罚
- 鼓励模型选择更便宜、更快的工具
- 例如：能用 reasoner-1 就不用 reasoner-3

### 3. GRPO 归一化

```python
# 对于每个问题，收集所有 rollout 的 reward
example_rewards[example_idx] = [reward1, reward2, ..., reward_n]

# 计算均值和标准差
mean = sum(example_rewards[example_idx]) / len(example_rewards[example_idx])
std = stdev(example_rewards[example_idx])

# 归一化（相对于同组其他 rollout）
normalized_reward = (raw_reward - mean) / (std + 1e-6)

# Clip 到 [-3, 3]
normalized_reward = max(-3.0, min(3.0, normalized_reward))
```

**GRPO 归一化的优势**:
1. **减少方差**: 不同问题的 reward 分布差异很大，归一化后更稳定
2. **相对比较**: 同一问题的不同解法进行相对比较，而不是绝对比较
3. **防止极端值**: Clip 到 [-3, 3] 防止梯度爆炸

---

## 完整执行流程示例

假设有一个数学问题：**"一个长方形的长是宽的2倍，周长是36cm，求面积是多少？"**

### Turn 0

**输入**:
```
System: You are good at using tools.
User: Problem: 一个长方形的长是宽的2倍，周长是36cm，求面积是多少？

Documents:
(空)

Choose an appropriate tool.
```

**模型输出**:
```
<think>
这是一个数学几何问题，需要通过方程求解。
我应该先用代码来计算中间步骤。
选择 enhance_reasoning 工具，使用 reasoner-1 模型。
</think>
<tool_call>
{"name": "enhance_reasoning", "arguments": {"model": "reasoner-1"}}
</tool_call>
```

**后处理**:
- `postprocess_predictions()` 提取到：
  ```python
  {
      "name": "enhance_reasoning",
      "arguments": {"model": "reasoner-1"}
  }
  ```

**工具执行**:
- `call_tool()` 调用 reasoner-1（映射到 gpt-5）
- gpt-5 生成代码：
  ```python
  # 设 宽 = x，则 长 = 2x
  # 周长 = 2(x + 2x) = 6x = 36
  # x = 6
  x = 36 / 6
  width = x
  length = 2 * x
  area = width * length
  print(f"宽: {width}cm, 长: {length}cm, 面积: {area}cm²")
  ```
- Sandbox 执行代码，输出：
  ```
  宽: 6.0cm, 长: 12.0cm, 面积: 72.0cm²
  ```

**状态更新**:
- `code_snippets[0].append({'code': ..., 'output': ...})`
- `dones[0] = False`（还没有最终答案）
- `active_mask[0] = True`（继续下一轮）

### Turn 1

**输入**:
```
System: You are good at using tools.
User: Problem: 一个长方形的长是宽的2倍，周长是36cm，求面积是多少？

Documents:

```python
x = 36 / 6
width = x
length = 2 * x
area = width * length
print(f"宽: {width}cm, 长: {length}cm, 面积: {area}cm²")
```

```output
宽: 6.0cm, 长: 12.0cm, 面积: 72.0cm²
```

Choose an appropriate tool.
```

**模型输出**:
```
<think>
代码已经计算出了面积是 72cm²。
现在可以使用 answer 工具给出最终答案。
选择 answer-math-1 模型，因为这是数学问题。
</think>
<tool_call>
{"name": "answer", "arguments": {"model": "answer-math-1"}}
</tool_call>
```

**工具执行**:
- `call_tool()` 调用 answer-math-1（映射到 Qwen2.5-Math-72B）
- 模型生成答案：`"72"`

**答案验证**:
- 提取数字：`72`
- 与 ground truth 比较：`|72 - 72| < 0.01`
- `dones[0] = True`

**状态更新**:
- `attempts[0].append({'model': 'answer-math-1', 'answer': '72'})`
- `active_mask[0] = False`（任务完成）

### Turn 2

- `active_mask.sum() == 0`
- 退出循环

### Reward 计算

```python
# 1. Outcome
example_correctness['0_____0'] = True  # 答案正确
base_reward = 1.0

# 2. Efficiency
example_costs['0_____0'] = 0.125 (gpt-5) + 0.009 (Qwen2.5-Math) = 0.134
example_latency['0_____0'] = 2.3 + 1.2 = 3.5

cost_reward = 0.134 * 5 = 0.67
latency_reward = 3.5 / 500 = 0.007

raw_reward = 1.0 - 0.67 - 0.007 = 0.323

# 3. GRPO 归一化（假设有 8 个 rollout）
example_rewards['0'] = [0.323, 0.15, -0.2, 0.1, 0.4, -0.1, 0.2, 0.05]

mean = 0.113
std = 0.215

normalized_reward = (0.323 - 0.113) / 0.215 = 0.977
```

---

## 总结

`generation_quick3.py` 是 ToolOrchestra 的核心文件，实现了：

1. **Multi-turn 生成循环**: 最多 10 轮交互
2. **工具调用管理**: 支持 enhance_reasoning, answer, search
3. **并行执行**: Batch 内样本并行，工具调用并行
4. **容错设计**: JSON 解析失败、工具调用失败都不会导致崩溃
5. **Reward 计算**: Outcome + Efficiency + GRPO 归一化
6. **与 veRL 交互**: 只调用 `actor_rollout_wg.generate_sequences()`

**文件统计**:
- 总行数: 2180
- 核心类: `LLMGenerationManager`
- 核心方法: `run_llm_loop()` (约 600 行)
- 工具调用: `call_tool()` (约 600 行)

---

**相关文档**:
- [ToolOrchestra 自定义实现模块详解](toolorchestra_custom_implementations.md)
- [veRL API 文档](README.md)
