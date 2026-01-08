# ToolOrchestra Multi-Turn 逻辑实现详解

> 基于 `.reference_projects/ToolOrchestra/training/lead_agent` 的代码分析

## 概述

ToolOrchestra 是一个基于 VERL 框架的多轮强化学习训练系统，用于训练能够进行工具调用和推理的 LLM Agent。其核心特点是：

- **多轮交互**: 支持多步骤的工具调用和推理
- **混合任务**: 同时支持 QA（问答）和 Function Call（函数调用）两种任务类型
- **异步工具执行**: 使用多进程并行执行工具调用
- **动态状态管理**: 维护多轮对话中的上下文和历史信息

---

## 目录结构

```
.reference_projects/ToolOrchestra/training/lead_agent/
├── __init__.py
└── llm_agent/
    ├── __init__.py
    ├── generation_quick3.py    # 核心实现文件
    ├── tensor_helper.py         # Tensor 操作辅助工具
    └── tools.py                 # 工具定义（QueryWriter, AnswerGenerator）
```

---

## 核心组件

### 1. `LLMGenerationManager` 类

位置: `generation_quick3.py:816`

**职责**: 管理整个 multi-turn RL 训练的生成和执行流程

**关键属性**:
```python
class LLMGenerationManager:
    - tokenizer: 分词器
    - actor_rollout_wg: Actor 模型的推理接口
    - config: GenerationConfig（包含 max_turns、max_prompt_length 等）
    - tensor_fn: TensorHelper 实例（处理 tensor 操作）
```

**核心方法**:
- `run_llm_loop()`: 主循环，执行多轮交互
- `execute_predictions()`: 执行模型预测的工具调用
- `postprocess_predictions()`: 解析模型输出的工具调用格式

---

### 2. `TensorHelper` 类

位置: `tensor_helper.py:27`

**职责**: 处理 multi-turn 中的 tensor 拼接、padding、mask 等操作

**关键方法**:
- `cut_to_effective_len()`: 裁剪到有效长度
- `convert_pad_structure()`: 转换 padding 结构（left/right）
- `create_attention_mask()`: 创建 attention mask
- `create_position_ids()`: 创建 position IDs
- `concatenate_with_padding()`: 拼接多个 tensor 并处理 padding

---

### 3. 工具定义

位置: `generation_quick3.py:80-90`

```python
ALL_TOOLS = {
    "enhance_reasoning": {
        'model': ["reasoner-1", "reasoner-2", "reasoner-3"]
    },
    "answer": {
        'model': ["answer-math-1", "answer-math-2", "answer-1", ...]
    },
    "search": {
        "model": ["search-1", "search-2", "search-3"]
    },
}
```

每个工具对应一个特定功能：
- **enhance_reasoning**: 生成代码进行推理
- **answer**: 生成最终答案
- **search**: 搜索相关文档

---

## Multi-Turn 核心流程

### 整体流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    run_llm_loop 主循环                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌──────────────────────────────────────────────────────┐
    │  Step 1: 初始化状态                                   │
    │  - retrieved_documents (检索文档列表)                │
    │  - code_snippets (代码片段列表)                      │
    │  - attempts (尝试答案列表)                           │
    │  - active_mask (活跃样本掩码)                        │
    └──────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌──────────────────────────────────────────────────────┐
    │  Loop: for step in range(max_turns)                  │
    └──────────────────────────────────────────────────────┘
              │                                          │
              │ ┌────────────────────────────────────┐  │
              ├─│ Step 2: 构建 Prompt                │  │
              │ │ - 拼接历史信息                     │  │
              │ │ - 应用 chat template               │  │
              │ │ - Tokenize 并创建 tensor           │  │
              │ └────────────────────────────────────┘  │
              │                                          │
              │ ┌────────────────────────────────────┐  │
              ├─│ Step 3: 模型生成                   │  │
              │ │ - 调用 actor_rollout_wg.generate   │  │
              │ │ - 处理 GPU padding                 │  │
              │ │ - 返回生成的 tool call             │  │
              │ └────────────────────────────────────┘  │
              │                                          │
              │ ┌────────────────────────────────────┐  │
              ├─│ Step 4: 后处理 & 解析              │  │
              │ │ - postprocess_predictions()        │  │
              │ │ - 提取 <tool_call> 标签            │  │
              │ │ - 验证工具调用格式                 │  │
              │ └────────────────────────────────────┘  │
              │                                          │
              │ ┌────────────────────────────────────┐  │
              ├─│ Step 5: 执行工具调用               │  │
              │ │ - execute_predictions()            │  │
              │ │ - 异步并行执行                     │  │
              │ │ - 收集执行结果                     │  │
              │ └────────────────────────────────────┘  │
              │                                          │
              │ ┌────────────────────────────────────┐  │
              ├─│ Step 6: 更新状态                   │  │
              │ │ - 更新 retrieved_documents         │  │
              │ │ - 更新 code_snippets               │  │
              │ │ - 更新 attempts                    │  │
              │ │ - 更新 active_mask                 │  │
              │ └────────────────────────────────────┘  │
              │                                          │
              │ ┌────────────────────────────────────┐  │
              └─│ Step 7: 判断终止条件               │  │
                │ - 所有样本完成？                   │  │
                │ - 达到 max_turns？                 │  │
                └────────────────────────────────────┘  │
                              │                          │
                              ▼                          │
    ┌──────────────────────────────────────────────────────┐
    │  计算奖励 & 数据筛选                                  │
    │  - 计算 accuracy, cost, latency                      │
    │  - 基于 preference vector 计算奖励                   │
    │  - 筛选用于训练的样本                                │
    └──────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌──────────────────────────────────────────────────────┐
    │  返回 DataProto                                       │
    │  - 包含所有轮次的 input_ids, responses, rewards      │
    └──────────────────────────────────────────────────────┘
```

---

## 详细流程解析

### Phase 1: 初始化 (run_llm_loop 开始)

**位置**: `generation_quick3.py:996-1042`

```python
def run_llm_loop(self, gen_batch, ...):
    loop_batch_size = len(gen_batch.non_tensor_batch['problem'])
    active_mask = torch.ones(loop_batch_size, dtype=torch.bool)

    # 初始化状态变量
    retrieved_documents = [[] for _ in range(loop_batch_size)]  # 存储检索到的文档
    code_snippets = [[] for _ in range(loop_batch_size)]        # 存储生成的代码
    attempts = [[] for _ in range(loop_batch_size)]             # 存储尝试的答案
    total_costs = [0 for _ in range(loop_batch_size)]           # 累计成本

    # 存储所有轮次的数据（用于训练）
    all_turn_input_ids = []
    all_turn_responses = []
    all_turn_tools = []
    all_turn_success = []
    ...
```

**关键点**:
1. `active_mask`: 标记哪些样本还在继续执行（未完成）
2. 累积列表 (`retrieved_documents`, `code_snippets`, `attempts`): 在多轮中逐步积累信息
3. `all_turn_*`: 记录每一轮的数据，用于最终的训练

---

### Phase 2: 多轮循环 (step 0 → max_turns)

**位置**: `generation_quick3.py:1043-1342`

#### 2.1 构建当前轮的 Prompt

**QA 任务** (`generation_quick3.py:1096-1138`):

```python
# 拼接历史信息
doc_str = ''
for doc_idx, doc in enumerate(doc_list):
    doc_str += f"Doc {doc_idx+1}: {doc[:4000]}\n\n"

code_str = ''
for code_idx, code_piece in enumerate(code_list):
    code_str += f"```python\n{code_piece['code']}\n```\n\n"
    code_str += f"```output\n{code_piece['output']}\n```\n\n"

attempt_str = ''
for attempt_idx, attempt in enumerate(attempt_list):
    attempt_str += f"Attempt{attempt_idx+1} answer by {attempt['model']}: {attempt['answer']}\n"

# 应用长度限制（token-based truncation）
context_str = cut_seq(tokenizer, doc_str+code_str+attempt_str, l=24000)

# 构建最终 prompt
chat = [
    {"role": "system", "content": "You are good at using tools."},
    {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an appropriate tool."}
]
```

**Function Call 任务** (`generation_quick3.py:1141-1202`):

```python
# 从文件读取输入（与外部环境交互）
cur_transfer_dir = os.path.join(..., f"{item_index}_____{item_repeat_id}")
with open(os.path.join(cur_transfer_dir, f"input_{transfer_idx}.json")) as f:
    input_dict = json.load(f)

tools = input_dict['tools']
chat = input_dict['messages']

# 应用长度限制
tools_length = len(tokenizer(str(tools))['input_ids'])
chat = cut_middle_turns(tokenizer, messages=chat, max_length=23000-tools_length)
```

**关键函数**: `cut_middle_turns()` (`generation_quick3.py:108-130`)

```python
def cut_middle_turns(tokenizer, messages, max_length):
    """
    当 messages 超过 max_length 时，保留开头和结尾的消息，
    删除中间的消息，确保总长度不超过 max_length。
    """
    messages_str = ''
    for mid, m in enumerate(messages):
        messages_str += f"{m}{start_identifier}{mid}{end_identifier}"

    token_ids = tokenizer(messages_str)['input_ids']
    if len(token_ids) <= max_length:
        return messages

    # 保留前一半和后一半
    p1_tokens = tokenizer.batch_decode(token_ids[:max_length//2])
    p1_idx = int(p1.split(start_identifier)[-1].split(end_identifier)[0])

    p2_tokens = tokenizer.batch_decode(token_ids[-max_length//2:])
    p2_idx = int(p2.split(end_identifier)[0].split(start_identifier)[-1])

    return messages[:p1_idx+1] + messages[p2_idx:]
```

#### 2.2 Tokenization & Tensor 处理

```python
# 应用 chat template
prompt_with_chat_template = tokenizer.apply_chat_template(
    chat,
    add_generation_prompt=True,
    tools=tools,
    tokenize=False
)

# Tokenize 并处理 padding
input_ids, attention_mask = verl_F.tokenize_and_postprocess_data(
    prompt=prompt_with_chat_template,
    tokenizer=tokenizer,
    max_length=max_prompt_length,
    pad_token_id=tokenizer.pad_token_id,
    left_pad=True,          # 左侧 padding
    truncation='middle'     # 中间截断
)

# 创建 position_ids
position_ids = compute_position_id_with_mask(attention_mask)
```

#### 2.3 模型生成

```python
# 准备输入
rollings.batch['input_ids'] = input_ids
rollings.batch['attention_mask'] = attention_mask
rollings.batch['position_ids'] = position_ids

# 裁剪到有效长度
rollings.batch = self.tensor_fn.cut_to_effective_len(
    rollings.batch,
    keys=['input_ids', 'attention_mask', 'position_ids']
)

# 只对活跃样本生成
rollings_active = DataProto.from_dict({
    k: v[active_mask] for k, v in rollings.batch.items()
})

# 调用生成（处理 GPU padding）
gen_output = self._generate_with_gpu_padding(rollings_active)
responses_ids, responses_str = self._postprocess_responses(
    gen_output.batch['responses']
)
```

**GPU Padding 机制** (`generation_quick3.py:945-994`):

```python
def _generate_with_gpu_padding(self, active_batch):
    """
    确保 batch_size 能被 num_gpus 整除，否则用第一个样本 padding。
    """
    batch_size = active_batch.batch['input_ids'].shape[0]
    remainder = batch_size % num_gpus

    if remainder == 0:
        return self.actor_rollout_wg.generate_sequences(active_batch)

    # 添加 padding
    padding_size = num_gpus - remainder
    padded_batch = {}
    for k, v in active_batch.batch.items():
        pad_sequence = v[0:1].repeat(padding_size, *[1] * (len(v.shape) - 1))
        padded_batch[k] = torch.cat([v, pad_sequence], dim=0)

    # 生成后移除 padding
    padded_output = self.actor_rollout_wg.generate_sequences(padded_active_batch)
    trimmed_batch = {k: v[:-padding_size] for k, v in padded_output.batch.items()}

    return trimmed_output
```

---

### Phase 3: 后处理 & 工具执行

#### 3.1 解析工具调用

**位置**: `generation_quick3.py:2094-2144`

```python
def postprocess_predictions(self, predictions, all_categories):
    tool_calls = []
    formats = []

    for prediction, category in zip(predictions, all_categories):
        cur_all_tool_calls = []
        format_correct = False

        if category == 'qa':
            # 提取 <think>...</think> 中的思考过程
            cur_thought = prediction.split('<think>')[-1].split('</think>')[0]

            # 提取 <tool_call>...</tool_call> 中的工具调用
            components = prediction.split('<tool_call>')
            for c in components:
                components1 = c.split('</tool_call>')
                for c1 in components1:
                    try:
                        tmp_tool_call = json.loads(c1)
                        # 验证格式
                        assert set(list(tmp_tool_call.keys())) == {"name", "arguments"}
                        assert tmp_tool_call['name'] in ALL_TOOLS

                        # 验证参数
                        func_signature = ALL_TOOLS[tmp_tool_call['name']]
                        for param_name, param_values in func_signature.items():
                            assert tmp_tool_call["arguments"][param_name] in param_values

                        cur_all_tool_calls.append(tmp_tool_call)
                    except:
                        pass

            if len(cur_all_tool_calls) > 0:
                format_correct = True

        elif category == 'func_call':
            # Function Call 任务的解析逻辑类似
            ...

        tool_calls.append(cur_all_tool_calls)
        formats.append(format_correct)

    return tool_calls, contents, formats
```

**输出格式示例**:

```json
{
  "name": "enhance_reasoning",
  "arguments": {
    "model": "reasoner-1"
  }
}
```

或

```json
{
  "name": "answer",
  "arguments": {
    "model": "answer-math-1"
  }
}
```

#### 3.2 执行工具调用

**位置**: `generation_quick3.py:1613-2091`

```python
def execute_predictions(self, predictions, ...):
    # 1. 解析工具调用
    cur_tool_calls, contents, format_correctness = self.postprocess_predictions(
        predictions, all_categories
    )

    # 2. 为每个工具调用准备参数
    all_call_tool_arguments = []
    for i, (iter_tool_calls, active, doc_list, ...) in enumerate(zip(...)):
        call_tool_arguments = []

        if cur_category == 'qa':
            for tid, tool_call in enumerate(iter_tool_calls):
                # 验证工具调用有效性
                if not valid_tool_call:
                    continue

                # 准备工具调用参数
                if tool_call['name'] == 'enhance_reasoning':
                    # 构建上下文
                    context_str = build_context(doc_list, code_list, ...)
                    call_tool_arguments.append({
                        'tool': tool_call['name'],
                        'model': tool_call["arguments"]['model'],
                        'context_str': context_str,
                        'problem': user_problem,
                        ...
                    })

                elif tool_call['name'] == 'answer':
                    # 类似的处理
                    ...

                elif tool_call['name'] == 'search':
                    # 类似的处理
                    ...

        elif cur_category == 'func_call':
            # Function Call 任务的处理
            call_tool_arguments.append({
                'tool': iter_tool_calls,
                'input_messages': cur_input_messages,
                'input_tools': cur_input_tools,
                'transfer_path': cur_transfer_path,
                ...
            })

        all_call_tool_arguments.append(call_tool_arguments)

    # 3. 异步并行执行所有工具调用
    tool_call_list = []
    for iter_call_argument in all_call_tool_arguments:
        if len(iter_call_argument) > 0:
            tool_call_list.append([
                call_tool_all,
                {'id': iter_call_argument[0]['id'], 'all_call_arguments': iter_call_argument}
            ])

    tool_call_results = asyncio.run(run_all(tool_call_list))

    # 4. 收集结果
    tool_responses = {}
    for return_contents in tool_call_results:
        tool_responses[return_contents['id']] = return_contents['all_tool_call_results']

    # 5. 整理返回值
    cur_documents, cur_code, cur_attempts, dones, costs, ... = [], [], [], [], [], ...
    for i, active in enumerate(active_mask):
        if i in tool_responses:
            for tool_result in tool_responses[i]:
                if tool_result['tool'] == 'enhance_reasoning':
                    cur_code[i].append({
                        'code': tool_result['generated_code'],
                        'output': tool_result['exec_result']
                    })
                elif tool_result['tool'] == 'answer':
                    cur_attempts[i].append({
                        'answer': tool_result['pred'],
                        'model': tool_result['model']
                    })
                    attempt_correct[i] = tool_result['correctness']
                elif tool_result['tool'] == 'search':
                    cur_documents[i].extend(tool_result['search_results_data'])

                costs[i] += tool_result['cost']

    return cur_documents, cur_code, cur_attempts, dones, attempt_correct, costs, ...
```

---

### Phase 4: 工具调用实现

**位置**: `generation_quick3.py:136-731`

#### 4.1 enhance_reasoning 工具

```python
def call_tool(arguments):
    if arguments['tool'] == 'enhance_reasoning':
        # 1. 构建 prompt
        prompt = arguments['context_str'].strip() + '\n\n'
        prompt += f"Question: {arguments['problem']}\n"
        prompt += "Instead of directly answering the question, please write additional "
        prompt += "python code that will give intermediate results after execution. "
        prompt += "Wrap the code within ```python and ```."

        # 2. 调用 LLM 生成代码
        response = get_llm_response(
            model=model_name,
            messages=prompt,
            return_raw_response=True,
            temperature=1,
            max_length=28000
        )

        # 3. 提取代码
        generated_code = response.choices[0].message.content.split('```python')[-1].split('```')[0]

        # 4. 在沙箱中执行代码
        code_path = os.path.join(arguments['cur_output_dir'], f'exec_code_{arguments["id"]}.py')
        with open(code_path, 'w') as f:
            f.write(generated_code)

        exec_result = subprocess.run(
            ['python', code_path],
            timeout=60,
            capture_output=True,
            text=True
        )
        exec_result = exec_result.stdout

        # 5. 返回结果
        return {
            'generated_code': generated_code,
            'exec_result': exec_result,
            'cost': cost,
            'latency': latency,
            ...
        }
```

#### 4.2 answer 工具

```python
def call_tool(arguments):
    if arguments['tool'] == 'answer':
        # 1. 构建 prompt
        prompt = arguments['context_str'].strip() + '\n\n' + arguments['problem']

        # 2. 根据模型类型调整 prompt
        if 'math' in cur_answer_model.lower():
            prompt += "\nLet's think step by step and output the final answer within \\boxed{}."
        else:
            prompt += "\nWrap the thinking process between <think> and </think> "
            prompt += "and wrap only the exact answer within <answer> and </answer>."

        # 3. 调用 LLM 生成答案
        response = get_llm_response(
            model=model_name,
            messages=prompt,
            return_raw_response=True,
            temperature=0.2,
            max_length=8000
        )

        # 4. 提取答案
        if 'math' in cur_answer_model.lower():
            pred = response.choices[0].message.content.split('\\boxed{')[-1].split('}')[0].strip()
        else:
            pred = response.choices[0].message.content.split('<answer>')[-1].split('</answer>')[0].strip()

        # 5. 评估正确性
        if pred.strip().lower() == arguments['answer'].strip().lower():
            correctness = True
        else:
            # 使用 LLM 评估答案是否匹配
            eval_prompt = f"Question: {arguments['problem']}\n\n"
            eval_prompt += f"Student answer: {pred}\n\n"
            eval_prompt += f"Reference answer: {arguments['answer']}\n\n"
            eval_prompt += "Output <correct>True</correct> if the student answer matches."

            eval_result = get_llm_response(model='gpt-5', messages=eval_prompt)
            correctness = eval_result.split('<correct>')[-1].split('</correct>')[0].lower() == 'true'

        # 6. 返回结果
        return {
            'response': response_str,
            'pred': pred,
            'correctness': correctness,
            'cost': cost,
            'latency': latency,
            ...
        }
```

#### 4.3 search 工具

```python
def call_tool(arguments):
    if arguments['tool'] == 'search':
        # 1. 生成搜索 query
        prompt = arguments['context_str'].strip() + '\n\n'
        prompt += f"Question: {arguments['problem']}\n"
        prompt += "Write a query to search for relevant information. "
        prompt += "Wrap the query within <query> and </query>."

        response = get_llm_response(model=cur_query_writer, messages=prompt)
        query_to_call = response.split('<query>')[-1].split('</query>')[0]

        # 2. 调用搜索 API
        payload = {
            "queries": [query_to_call[:390]],
            "topk": arguments['topk_doc'],
            "return_scores": True,
            "eid": arguments['cur_index'].split('____')[-1]
        }

        results = requests.post(
            f'http://{cur_model_config["ip_addr"]}:{cur_model_config["port"]}/retrieve',
            json=payload
        ).json()

        # 3. 提取文档内容
        contents = []
        if results:
            for r in results[0]:
                if 'content' in r['document']:
                    contents.append(r['document']['content'])

        # 4. 返回结果
        return {
            'search_results_data': contents,
            'cost': cost,
            'latency': latency,
            ...
        }
```

---

### Phase 5: 状态更新

**位置**: `generation_quick3.py:1289-1341`

```python
# 1. 合并新检索的文档
for i, iter_docs in enumerate(new_documents):
    retrieved_documents[i] = merge_documents(
        main_list=retrieved_documents[i],
        sub_list=iter_docs
    )

# 2. 追加新生成的代码
for i, c in enumerate(new_code):
    if len(c) > 0:
        code_snippets[i] += c

# 3. 追加新的答案尝试
for i, a in enumerate(new_attempts):
    if len(a) > 0:
        attempts[i] += a

# 4. 累计成本
for iter_idx in range(len(total_costs)):
    if active_mask[iter_idx]:
        total_costs[iter_idx] += new_costs[iter_idx] + main_agent_cost[iter_idx]

# 5. 记录当前轮次的数据（用于训练）
all_turn_input_ids.append(round_input_ids)
all_turn_responses.append(responses_ids)
all_turn_tools += cur_turn_tools
all_turn_success += cur_turn_success
all_turn_costs += cur_turn_costs

# 6. 更新 active_mask（标记完成的样本）
curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
active_mask = active_mask * curr_active_mask
```

**`merge_documents()` 实现** (`generation_quick3.py:58-78`):

```python
def merge_documents(main_list, sub_list):
    """
    将 sub_list 的文档插入到 main_list 中，保持相对顺序。
    策略: 每隔 multiple 个 main_list 元素插入一个 sub_list 元素。
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
        # 添加 sub_list 元素
        if not sub_list[idx_sub] in merged_list:
            merged_list.append(sub_list[idx_sub])

        # 添加 multiple 个 main_list 元素
        for iter_idx in range(idx_main, idx_main + multiple):
            if not main_list[iter_idx] in merged_list:
                merged_list.append(main_list[iter_idx])

        idx_main = idx_main + multiple
        idx_sub += 1

    merged_list += main_list[multiple * len(sub_list):]
    return merged_list
```

---

### Phase 6: 奖励计算 & 数据筛选

**位置**: `generation_quick3.py:1382-1578`

#### 6.1 计算每个 rollout 的正确性

```python
example_correctness = {}
for example_idx, example_repeat_id, turn_success in zip(all_turn_index, all_turn_repeat_ids, all_turn_success):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    if turn_success or (rollout_id in example_correct_by_rollout_id and example_correct_by_rollout_id[rollout_id]):
        example_correctness[rollout_id] = True
    elif not rollout_id in example_correctness:
        example_correctness[rollout_id] = False
```

#### 6.2 累计成本和延迟

```python
example_costs = defaultdict(int)
example_latency = defaultdict(int)
for example_idx, example_repeat_id, turn_cost, turn_latency in zip(...):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    example_costs[rollout_id] += turn_cost
    example_latency[rollout_id] += turn_latency
```

#### 6.3 基于 Preference Vector 计算奖励

```python
# 1. 统计每个 example 的工具使用情况
tool_counts = {}  # {rollout_id: {tool_name: count}}
tool_counts_min = {}  # {example_idx: {tool_name: min_count}}
tool_counts_max = {}  # {example_idx: {tool_name: max_count}}

for rollout_id, tool_nums in tool_counts.items():
    example_idx, example_repeat_id = rollout_id.split('_____')
    for tn, tc in tool_nums.items():
        if not tn in tool_counts_min[example_idx]:
            tool_counts_min[example_idx][tn] = tc
        if not tn in tool_counts_max[example_idx]:
            tool_counts_max[example_idx][tn] = tc
        tool_counts_min[example_idx][tn] = min(tool_counts_min[example_idx][tn], tc)
        tool_counts_max[example_idx][tn] = max(tool_counts_max[example_idx][tn], tc)

# 2. 计算每个 rollout 的奖励
rewards_by_rollout_id = {}
for rollout_id in all_rollout_ids:
    if not example_correctness[rollout_id]:
        rewards_by_rollout_id[rollout_id] = 0
        continue

    cur_pref_vec = all_pref_vecs[rollout_id]  # {feature_name: preference_weight}
    features = list(tool_counts_min[example_idx].keys())

    # 归一化特征值并加权求和
    reward = 0
    for one_feature in features:
        if tool_counts_max[example_idx][one_feature] > tool_counts_min[example_idx][one_feature]:
            normalized_value = (
                (tool_counts[rollout_id][one_feature] - tool_counts_min[example_idx][one_feature]) /
                (tool_counts_max[example_idx][one_feature] - tool_counts_min[example_idx][one_feature])
            )
            reward += cur_pref_vec[one_feature] * normalized_value

    # 添加 accuracy, latency, cost 的贡献
    # （类似的归一化处理）
    ...

    rewards_by_rollout_id[rollout_id] = reward
```

#### 6.4 标准化奖励

```python
# 计算每个 example 的奖励均值和标准差
example_reward_average = {}
example_reward_std = {}
for example_idx in example_indices:
    example_reward_average[example_idx] = sum(example_rewards[example_idx]) / len(example_rewards[example_idx])
    example_reward_std[example_idx] = stdev(example_rewards[example_idx])

# 标准化奖励
rewards = []
for example_idx, example_repeat_id in zip(all_turn_index, all_turn_repeat_ids):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    cur_reward = (rewards_by_rollout_id[rollout_id] - example_reward_average[example_idx]) / (example_reward_std[example_idx] + 1e-6)

    # Clip 到 [-3, 3]
    if cur_reward > 3:
        cur_reward = 3
    if cur_reward < -3:
        cur_reward = -3

    rewards.append(cur_reward)
```

#### 6.5 筛选训练样本

```python
selected_indices = []
for iter_index, (example_idx, example_repeat_id, turn_format) in enumerate(zip(...)):
    rollout_id = f"{example_idx}_____{example_repeat_id}"

    # 筛选条件:
    # 1. 标准差 > 0.1 (有足够的 diversity)
    # 2. 生成了有效答案
    # 3. 格式正确
    if (example_reward_std[example_idx] > 0.1 and
        rollout_id in valid_answers and
        valid_answers[rollout_id] and
        turn_format):
        selected_indices.append(iter_index)
```

#### 6.6 组装最终数据

```python
# 确保 batch_size 能被 num_gpus 整除
total_nodes = self.config.num_gpus
cur_remainder = len(selected_indices) % total_nodes
if cur_remainder != 0:
    selected_indices = selected_indices[:-cur_remainder]

if len(selected_indices) < total_nodes:
    return None  # 样本不足，跳过这个 batch

# 筛选数据
indices = torch.tensor(selected_indices)
all_turn_input_ids = torch.index_select(all_turn_input_ids, dim=0, index=indices)
all_turn_responses = torch.index_select(all_turn_responses, dim=0, index=indices)
rewards = selection_list(rewards, selected_indices)
...

# 返回 DataProto
final_dict = {
    'input_ids': all_turn_input_ids,
    'attention_mask': all_turn_attention_mask,
    'position_ids': all_turn_position_ids,
    'responses': all_turn_responses,
    'reward': np.array(rewards),
    ...
}
return_dict = DataProto.from_single_dict(final_dict, meta_info=meta_info)
return return_dict, tool_total / loop_batch_size
```

---

## 两种任务类型对比

### QA (问答) 任务

**特点**:
- 完全在内存中执行，不依赖外部文件系统
- 工具调用直接由模型决定
- 支持 3 种工具: `enhance_reasoning`, `answer`, `search`

**Prompt 构建**:
```python
chat = [
    {"role": "system", "content": "You are good at using tools."},
    {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an appropriate tool."}
]
```

**工具输出格式**:
```
<think>
我需要先搜索相关信息...
</think>

<tool_call>
{"name": "search", "arguments": {"model": "search-1"}}
</tool_call>
```

**终止条件**:
- 调用了 `answer` 工具且生成了有效答案
- 达到 `max_turns`

---

### Function Call (函数调用) 任务

**特点**:
- 通过文件系统与外部环境交互
- 支持真实的 API 调用（如 Tavily 工具）
- 更复杂的终止判定逻辑

**交互流程**:

1. **初始化** (step 0):
```python
# 启动外部进程
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
subprocess.Popen(func_call_cmd)
```

2. **每个 step**:
```python
# 等待外部进程写入 input_{transfer_idx}.json
transfer_idx = 0
while not os.path.isfile(os.path.join(cur_transfer_dir, f"input_{transfer_idx}.json")):
    # 检查是否收到终止信号
    if os.path.isfile(os.path.join(cur_transfer_dir, 'done')):
        active_mask[item_idx] = 0
        break
    time.sleep(5)

# 读取输入
with open(os.path.join(cur_transfer_dir, f"input_{transfer_idx}.json")) as f:
    input_dict = json.load(f)

tools = input_dict['tools']
chat = input_dict['messages']
```

3. **模型生成并写回**:
```python
# 模型生成工具调用
response = model_generate(chat, tools)

# 写回给外部进程
with open(os.path.join(cur_transfer_dir, f"output_{transfer_idx}.json"), 'w') as f:
    json.dump(response, f)
```

**工具输出格式**:
```
<think>
用户想要搜索天气信息，我应该调用 search_weather 工具
</think>

<tool_call>
{"name": "search_weather", "arguments": {"location": "Beijing"}}
</tool_call>
```

或者只返回消息:
```
<message>
我已经为您找到了天气信息...
</message>
```

**终止条件**:
- 外部进程写入 `done` 文件
- 达到 `max_turns`

---

## 关键设计模式

### 1. Active Mask 机制

**目的**: 在多轮循环中，不同样本可能在不同的轮次完成，使用 `active_mask` 标记哪些样本还在继续执行。

```python
active_mask = torch.ones(batch_size, dtype=torch.bool)

for step in range(max_turns):
    if not active_mask.sum():
        break  # 所有样本都完成了

    # 只对活跃样本生成
    rollings_active = DataProto.from_dict({
        k: v[active_mask] for k, v in rollings.batch.items()
    })

    # 生成...

    # 更新 active_mask
    curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
    active_mask = active_mask * curr_active_mask
```

### 2. 累积上下文机制

**目的**: 在多轮中逐步积累信息（文档、代码、答案尝试），供后续轮次使用。

```python
# 初始化
retrieved_documents = [[] for _ in range(batch_size)]
code_snippets = [[] for _ in range(batch_size)]
attempts = [[] for _ in range(batch_size)]

# 每轮更新
for i, iter_docs in enumerate(new_documents):
    retrieved_documents[i] = merge_documents(retrieved_documents[i], iter_docs)

for i, c in enumerate(new_code):
    if len(c) > 0:
        code_snippets[i] += c

for i, a in enumerate(new_attempts):
    if len(a) > 0:
        attempts[i] += a
```

### 3. Tensor 操作与 Padding

**左侧 Padding**:
```python
# Prompt 阶段使用左侧 padding
input_ids, attention_mask = tokenize_and_postprocess_data(
    prompt=prompt,
    left_pad=True,
    ...
)

# 好处: 方便拼接 response
```

**右侧 Padding**:
```python
# Response 和 Info 阶段使用右侧 padding
responses, responses_with_info_mask = self._info_masked_concatenate_with_padding(
    right_side['responses'],
    right_side['responses_with_info_mask'],
    cur_responses,
    next_obs_ids,
    pad_to_left=False
)
```

**裁剪到有效长度**:
```python
effective_len = attention_mask.sum(dim=1).max()
max_len = min(self.config.max_prompt_length, effective_len)
tensor = tensor[:, -max_len:]  # 左侧裁剪
# 或
tensor = tensor[:, :max_len]   # 右侧裁剪
```

### 4. GPU Padding 机制

**目的**: 确保分布式训练时，每个 GPU 分到的 batch_size 相同。

```python
batch_size = active_batch.batch['input_ids'].shape[0]
remainder = batch_size % num_gpus

if remainder != 0:
    # 用第一个样本 padding
    padding_size = num_gpus - remainder
    for k, v in active_batch.batch.items():
        pad_sequence = v[0:1].repeat(padding_size, *[1] * (len(v.shape) - 1))
        padded_batch[k] = torch.cat([v, pad_sequence], dim=0)

    # 生成后移除 padding
    output = generate(padded_batch)
    output = {k: v[:-padding_size] for k, v in output.items()}
```

### 5. 异步并行工具执行

**目的**: 多个工具调用并行执行，提高效率。

```python
# 准备所有工具调用
tool_call_list = []
for iter_call_argument in all_call_tool_arguments:
    if len(iter_call_argument) > 0:
        tool_call_list.append([
            call_tool_all,  # 函数引用
            {'id': ..., 'all_call_arguments': iter_call_argument}  # 参数
        ])

# 异步并行执行
tool_call_results = asyncio.run(run_all(tool_call_list))
```

**`run_all()` 实现** (未在代码中显示，但推测使用 `asyncio.gather()`):
```python
async def run_all(task_list):
    tasks = []
    for func, args in task_list:
        tasks.append(asyncio.create_task(func(**args)))
    results = await asyncio.gather(*tasks)
    return results
```

---

## 与 VERL 框架的集成

### 数据流

```
VERL Framework
      │
      ├─> Actor Rollout (生成数据)
      │         │
      │         ├─> LLMGenerationManager.run_llm_loop()
      │         │         │
      │         │         ├─> Multi-turn 循环
      │         │         │         │
      │         │         │         ├─> 模型生成
      │         │         │         ├─> 工具执行
      │         │         │         └─> 状态更新
      │         │         │
      │         │         └─> 奖励计算 & 数据筛选
      │         │
      │         └─> 返回 DataProto
      │
      ├─> PPO Trainer (更新模型)
      │
      └─> Iteration++
```

### DataProto 结构

```python
DataProto.from_single_dict({
    # Tensor 数据
    'input_ids': torch.Tensor,          # [batch_size, seq_len]
    'attention_mask': torch.Tensor,     # [batch_size, seq_len]
    'position_ids': torch.Tensor,       # [batch_size, seq_len]
    'responses': torch.Tensor,          # [batch_size, response_len]
    'reward': np.ndarray,               # [batch_size]

    # Non-tensor 数据
    'id': np.ndarray,                   # [batch_size]
    'index': np.ndarray,                # [batch_size]
    'turn_id': np.ndarray,              # [batch_size]
    'repeat_id': np.ndarray,            # [batch_size]
    'answer': np.ndarray,               # [batch_size]
}, meta_info=meta_info)
```

---

## 总结

### 核心特点

1. **Multi-Turn RL**: 支持多轮工具调用和推理，逐步积累信息
2. **混合任务**: 同时支持 QA 和 Function Call 两种任务类型
3. **灵活的工具系统**: 3 种核心工具 (enhance_reasoning, answer, search)
4. **Preference-Based 奖励**: 基于用户偏好向量计算奖励，支持 multi-objective 优化
5. **高效的并行执行**: 异步并行执行工具调用，支持分布式训练

### 与标准 RL 的区别

| 维度 | 标准 RL | ToolOrchestra Multi-Turn RL |
|------|---------|------------------------------|
| 状态 | 固定维度向量 | 动态长度的文本 + 累积历史 |
| 动作 | 离散/连续空间 | 结构化工具调用 (JSON) |
| 奖励 | 单步奖励 | 基于最终结果 + 偏好向量 |
| 终止 | 环境判定 | 模型自主决定 (调用 answer 工具) |
| 数据 | 单轮 (s, a, r, s') | 多轮累积 + 筛选 |

### 适用场景

- **问答任务**: 需要多步推理、代码执行、信息检索的复杂问题
- **工具调用**: 需要与外部 API 交互的任务（如智能助手、代码生成）
- **偏好优化**: 需要在准确性、成本、延迟等多个目标之间权衡

---

## 参考代码位置

| 功能 | 文件 | 行号 |
|------|------|------|
| LLMGenerationManager 类 | `generation_quick3.py` | 816-2180 |
| run_llm_loop 主循环 | `generation_quick3.py` | 996-1579 |
| execute_predictions 工具执行 | `generation_quick3.py` | 1613-2091 |
| postprocess_predictions 后处理 | `generation_quick3.py` | 2094-2152 |
| call_tool 工具实现 | `generation_quick3.py` | 136-731 |
| TensorHelper 类 | `tensor_helper.py` | 27-95 |
| cut_middle_turns 函数 | `generation_quick3.py` | 108-130 |
| merge_documents 函数 | `generation_quick3.py` | 58-78 |

---

**文档版本**: 1.0
**最后更新**: 2026-01-08
**作者**: Claude Code (基于代码分析)
