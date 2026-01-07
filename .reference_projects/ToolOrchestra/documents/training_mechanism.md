# ToolOrchestra 训练机制深入分析

## 1. LLM每个Turn生成的是什么？

### 生成格式
Orchestrator在每一个turn只生成**一个tool call**，不是一次生成整个workflow/chain。

生成的格式定义在 `training/recipe/algo/main_grpo_quick3.py:48-69`：
```python
# Prompt模板定义
PROMPT_TEMPLATE = """
<think>
[推理过程]
</think>
<tool_call>
[JSON格式的工具调用]
</tool_call>
"""
```

其中tool call的JSON格式为：
```json
{
  "name": "工具名称",
  "arguments": {
    "model": "模型名称"
  }
}
```

可用工具定义在 `training/tools.json:1-62`：
- `enhance_reasoning` + 模型选择（reasoner-1/2/3）
- `answer` + 模型选择（answer-1/2/3/4, answer-math-1/2）
- `search` + 模型选择（search-1/2/3）

### 具体例子

**QA任务的prompt构建**（参考 `training/lead_agent/llm_agent/generation_quick3.py:1130-1133`）：

```python
chat = [
    {"role": "system", "content": "You are good at using tools. "},
    {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an approriate tool."}
]
```

**func_call任务**：

对于τ²-bench的客服任务，prompt从τ²环境动态读取（`training/lead_agent/llm_agent/generation_quick3.py:1190-1198`）：
```python
with open(os.path.join(cur_transfer_dir,f"input_{transfer_idx}.json")) as f:
    input_dict = json.load(f)
original_tools = input_dict['original_tools']
tools = input_dict['tools']
chat = input_dict['messages']
```

---

## 2. 调用链条有并行化执行吗？

### Batch级别并行

**是的，batch内的多个sample是并行rollout的。**

启动并行τ²-bench进程的代码在 `training/lead_agent/llm_agent/generation_quick3.py:1064-1067`：
```python
func_call_cmd = ['python','rollout/tau2/cli.py','--domain',cur_domain,'--agent-llm','train',
    '--user-llm','gpt-5','--num-trials','1','--task_path',str(task_path),'--max-steps','40','--cur_transfer_dir',
    str(cur_transfer_dir),'--output_file',str(cur_func_call_output_path),'--use_model_tool']
subprocess.Popen(func_call_cmd)  # 非阻塞调用
```

### Turn级别串行

**单个rollout内的turn是串行执行的。**

Multi-turn循环定义在 `training/lead_agent/llm_agent/generation_quick3.py:1043-1047`：
```python
for step in range(self.config.max_turns):
    if not os.path.isdir(os.path.join(my_output_dir,f"global_step_{global_steps}",f"rollout_step_{step}")):
        os.makedirs(os.path.join(my_output_dir,f"global_step_{global_steps}",f"rollout_step_{step}"))
    if not active_mask.sum():
        break
```

每个turn的流程：
1. **LLM生成** (`generation_quick3.py:1236`) - 调用`self._generate_with_gpu_padding()`
2. **工具执行** (`generation_quick3.py:1289`) - 调用`self.execute_predictions()`
3. **收集结果** (`generation_quick3.py:1301-1311`) - 更新documents, code, attempts
4. **更新mask** (`generation_quick3.py:1340-1341`) - 标记完成的样本

### 工具调用的异步等待

进程间通信通过文件系统实现（`training/lead_agent/llm_agent/generation_quick3.py:1148-1174`）：
```python
while not os.path.isfile(os.path.join(cur_transfer_dir,f"input_{transfer_idx}.json")):
    if os.path.isfile(os.path.join(cur_transfer_dir,'done')):
        try:
            with open(os.path.join(cur_transfer_dir,'done')) as f:
                tmp_result = f.read()
            if tmp_result=="Done!":
                # 计算reward
                correct = 0
                for subfile in os.listdir(os.path.join(cur_transfer_dir,'output')):
                    if subfile.endswith('.json'):
                        with open(os.path.join(cur_transfer_dir,'output',subfile)) as f:
                            r = json.load(f)
                        correct += r["reward_info"]["reward"]
                simulation_reward = 1 if correct > 0 else 0
                example_correct_by_rollout_id[iter_rollout_id] = simulation_reward
        except:
            pass
        active_mask[item_idx] = 0
        receive_end_signal = True
        break
    time.sleep(5)  # 轮询等待
```

---

## 3. Multi-turn是怎么做的？

### 整体流程

Multi-turn通过`run_llm_loop`函数实现（`training/lead_agent/llm_agent/generation_quick3.py:996-1579`）。

**初始化** (`generation_quick3.py:998-1029`):
```python
loop_batch_size = len(gen_batch.non_tensor_batch['problem'])
active_mask = torch.ones(loop_batch_size, dtype=torch.bool)
retrieved_documents = [[] for _ in range(loop_batch_size)]
code_snippets = [[] for _ in range(loop_batch_size)]
attempts = [[] for _ in range(loop_batch_size)]
total_costs = [0 for _ in range(loop_batch_size)]
```

**每个turn的执行** (`generation_quick3.py:1043-1341`):
1. **构建prompt** - 包含累积的context
2. **Tokenize** (`generation_quick3.py:1206-1214`)
3. **GPU生成** (`generation_quick3.py:1236`)
4. **执行工具** (`generation_quick3.py:1289-1295`)
5. **更新状态** (`generation_quick3.py:1301-1318`)
6. **检查完成** (`generation_quick3.py:1340-1341`)

### Context累积

文档累积（`training/lead_agent/llm_agent/generation_quick3.py:1103-1105`）:
```python
doc_str = ''
for doc_idx, doc in enumerate(doc_list):
    doc_str += f"Doc {doc_idx+1}: {doc[:4000]}\n\n"
```

代码执行结果累积（`generation_quick3.py:1107-1108`）:
```python
code_str = ''
for code_idx, code_piece in enumerate(code_list):
    code_str += f"```python\n{code_piece['code']}\n```\n\n```output\n{code_piece['output']}\n```\n\n"
```

答案尝试累积（`generation_quick3.py:1109-1111`）:
```python
attempt_str = ''
for attempt_idx, attempt in enumerate(attempt_list):
    attempt_str += f"Attempt{attempt_idx+1} answer by {attempt['model']}: {attempt['answer']}\n"
```

### 终止条件

**条件1**: 达到max_turns (`generation_quick3.py:1043`)
**条件2**: active_mask全为0 (`generation_quick3.py:1046-1047`)
**条件3**: QA任务答案正确 (通过execute_predictions返回dones标志)
**条件4**: func_call任务完成 (`generation_quick3.py:1153-1173`)

---

## 4. 使用什么做RL？

### veRL框架

使用**veRL**框架（基于ByteDance的veRL）。

核心数据结构导入（`training/verl/__init__.py:39-50`）:
```python
from .protocol import DataProto
```

自定义DataProto扩展（`training/recipe/algo/grpo_ray_trainer_quick3.py:67-149`）:
```python
class DataToolProto(DataProto):
    @classmethod
    def from_dict(cls, tensors, non_tensors=None, meta_info=None, ...):
        # 支持非tensor数据（如工具调用历史）
        ...
```

### GRPO算法

**训练入口**（`training/recipe/algo/main_grpo_quick3.py:214-231`）:
```python
from .grpo_ray_trainer_quick3 import RayGRPOTrainer

trainer = RayGRPOTrainer(
    config=config,
    tokenizer=tokenizer,
    role_worker_mapping=role_worker_mapping,
    reward_fn=reward_fn,
)
trainer.init_workers()
trainer.fit()
```

**Trainer类定义**（`training/recipe/algo/grpo_ray_trainer_quick3.py:245-300`）:
```python
class RayGRPOTrainer(RayPPOTrainer):
    def _create_dataloader(self, ...):
        self.train_dataset = JsonlDataset(
            file_path=self.config.data.train_files,
            tokenizer=self.tokenizer,
            ...
        )
```

### 分布式策略

策略选择（`training/recipe/algo/main_grpo_quick3.py:124-135`）:
```python
if config.actor_rollout_ref.actor.strategy == "fsdp":
    from verl.workers.fsdp_workers import ActorRolloutRefWorker, CriticWorker
    ray_worker_group_cls = RayWorkerGroup
elif config.actor_rollout_ref.actor.strategy == "megatron":
    from verl.workers.megatron_workers import ActorRolloutRefWorker, CriticWorker
    ray_worker_group_cls = NVMegatronRayWorkerGroup
```

### Reward计算

**Outcome + Efficiency reward**（`training/lead_agent/llm_agent/generation_quick3.py:1405-1416`）:
```python
if str(efficiency_reward).lower()=='true' and example_correctness[rollout_id]:
    cost_reward = example_costs[rollout_id]*5
    latency_reward = example_latency[rollout_id]/500
    if cost_reward+latency_reward>0.8:
        rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])-0.8
    else:
        rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])-latency_reward-cost_reward
else:
    rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])
```

**Preference reward**（`generation_quick3.py:1459-1486`）:
```python
# 基于工具使用频次、成本、延迟的偏好向量归一化
for one_feature in features:
    if tool_counts_max[example_idx][one_feature]>tool_counts_min[example_idx][one_feature]:
        rewards_by_rollout_id[rollout_id] += cur_pref_vec[one_feature]*(tool_counts[rollout_id][one_feature]-tool_counts_min[example_idx][one_feature])/(tool_counts_max[example_idx][one_feature]-tool_counts_min[example_idx][one_feature])
```

**GRPO归一化**（`generation_quick3.py:1488-1513`）:
```python
# Group内均值和标准差归一化
for example_idx in example_indices:
    example_reward_average[example_idx] = sum(example_rewards[example_idx])/len(example_rewards[example_idx])
    example_reward_std[example_idx] = stdev(example_rewards[example_idx])

# 计算normalized reward
cur_reward = (rewards_by_rollout_id[rollout_id]-example_reward_average[example_idx])/(example_reward_std[example_idx]+1e-6)
if cur_reward>3:
    cur_reward = 3
if cur_reward<-3:
    cur_reward = -3
```

---

## 5. 完整的Multi-turn执行示例

让我们通过一个具体的数学问题来演示训练后的Orchestrator模型如何工作。

### 任务场景

**问题**: "一个长方形的长是宽的2倍，周长是36cm，求面积是多少？"

**可用工具**（定义在 `training/tools.json:1-62`）:
- `enhance_reasoning`: 调用推理模型生成和执行代码
- `answer`: 调用答案模型给出最终答案
- `search`: 搜索相关信息

**配置**: `max_turns=10` (在GenerationConfig中设置)

---

### Turn 0: Orchestrator决策推理

**输入Prompt构建**（`training/lead_agent/llm_agent/generation_quick3.py:1130-1133`）:
```python
chat = [
    {"role": "system", "content": "You are good at using tools. "},
    {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an approriate tool."}
]
```

实际prompt:
```
System: You are good at using tools.
User: Problem: 一个长方形的长是宽的2倍，周长是36cm，求面积是多少？

Documents:
(空)

(空)

(空)

Choose an appropriate tool.
```

**Tokenize和生成**（`generation_quick3.py:1204-1236`）:
```python
prompt_with_chat_template = tokenizer.apply_chat_template(chat, add_generation_prompt=True, tools=tools,tokenize=False)
input_ids, attention_mask = verl_F.tokenize_and_postprocess_data(prompt=prompt_with_chat_template,
                                                                tokenizer=tokenizer,
                                                                max_length=tokenizer_config['max_prompt_length'],
                                                                pad_token_id=tokenizer.pad_token_id,
                                                                left_pad=True,
                                                                truncation='middle')
# ...
gen_output = self._generate_with_gpu_padding(rollings_active)
```

**Orchestrator生成**:
```
<think>
这是一个数学几何问题，需要通过方程求解。我应该先用代码来计算中间步骤。
选择enhance_reasoning工具，使用reasoner-1模型。
</think>
<tool_call>
{"name": "enhance_reasoning", "arguments": {"model": "reasoner-1"}}
</tool_call>
```

**JSON提取过程**（`training/lead_agent/llm_agent/generation_quick3.py:2094-2148`）:
```python
def postprocess_predictions(self, predictions, all_categories):
    for prediction, category in zip(predictions, all_categories):
        cur_all_tool_calls = []
        format_correct = False
        if isinstance(prediction, str):
            if category=='qa':
                # 提取<tool_call>标签之间的内容
                components = prediction.split('<tool_call>')
                added_tools = set()
                for c in components:
                    components1 = c.split('</tool_call>')
                    for c1 in components1:
                        try:
                            # 尝试解析JSON
                            tmp_tool_call = json.loads(c1)
                            # 验证格式
                            assert set(list(tmp_tool_call.keys()))=={"name","arguments"}
                            assert tmp_tool_call['name'] in ALL_TOOLS
                            if tmp_tool_call['name'] in added_tools:
                                continue
                            added_tools.add(tmp_tool_call['name'])
                            # 验证参数
                            func_signature = ALL_TOOLS[tmp_tool_call['name']]
                            for parameter_name,parameter_values in func_signature.items():
                                assert tmp_tool_call["arguments"][parameter_name] in parameter_values or parameter_values=='any'
                            cur_all_tool_calls.append(tmp_tool_call)
                        except:
                            pass
                if len(cur_all_tool_calls)>0:
                    format_correct = True
```

**错误处理逻辑**:
- JSON格式错误 → `json.loads(c1)`抛出异常 → 被`except`捕获 → `format_correct = False`
- 工具名称不在`ALL_TOOLS`中 → `assert`失败 → 被捕获
- 参数不合法 → `assert`失败 → 被捕获
- **关键**: 错误不会崩溃，只是该turn的`format_correct=False`

---

### Turn 0: 工具执行

**工具验证和调用准备**（`training/lead_agent/llm_agent/generation_quick3.py:1634-1689`）:
```python
for tid,tool_call in enumerate(iter_tool_calls):
    valid_tool_call = True
    if (not active) or (not isinstance(tool_call,dict)) or (set(list(tool_call.keys()))!={'name',"arguments"}) or (not tool_call['name'] in ALL_TOOLS):
        valid_tool_call = False
        continue
    func_signature = ALL_TOOLS[tool_call['name']]
    for parameter_name,parameter_values in func_signature.items():
        if (not parameter_name in tool_call["arguments"]):
            valid_tool_call = False
        if (not tool_call["arguments"][parameter_name] in parameter_values) and parameter_values!='any':
            valid_tool_call = False
    if not valid_tool_call:
        continue

    if tool_call['name']=='enhance_reasoning':
        if not tool_call["arguments"]['model'] in cur_model_mapping:
            continue
        cur_model_to_call = cur_model_mapping[tool_call["arguments"]['model']]  # reasoner-1 -> gpt-5
```

**调用LLM**（`training/lead_agent/llm_agent/generation_quick3.py:618-648`）:
```python
if mode_to_call in ['o3','o3-mini','gpt-5','gpt-5-mini']:
    latency_testing_start_time = time.time()
    response = get_llm_response(model=mode_to_call,messages=updated_messages,tools=arguments['input_tools'], return_raw_response=True,max_length=40000)
    latency_testing_end_time = time.time()
    if not isinstance(response,str):
        # 记录token使用和成本
        arguments['tokens_pic'].append({
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
            'model': mode_to_call,
            'latency': latency_testing_end_time-latency_testing_start_time
        })
        cost = cost + (cur_tool_pricing[mode_to_call]['input_tokens_per_million'] * response.usage.prompt_tokens + response.usage.completion_tokens * cur_tool_pricing[mode_to_call]['output_tokens_per_million'])
        response_content = response.choices[0].message.content
```

**代码执行**（在call_tool函数中，通过沙盒执行）:
```python
# 假设reasoner-1生成的代码
code = """
x = 36 / (2 * 3)
width = x
length = 2 * x
area = width * length
print(f"宽: {width}cm, 长: {length}cm, 面积: {area}cm²")
"""
# 执行后输出: "宽: 6.0cm, 长: 12.0cm, 面积: 72.0cm²"
```

**结果更新**（`generation_quick3.py:1301-1318`）:
```python
for i,c in enumerate(new_code):
    assert isinstance(c,list)
    if len(c)>0:
        code_snippets[i] += c  # 累积代码结果

for iter_idx in range(len(total_costs)):
    if active_mask[iter_idx]:
        total_costs[iter_idx] += new_costs[iter_idx]  # 累积成本
```

**`dones`判断**: 这一turn生成了代码但没有最终答案 → `dones[i] = False`

---

### Turn 1: Orchestrator基于结果决策

**输入Prompt** (已包含Turn 0的结果，context累积在 `generation_quick3.py:1103-1127`):
```
System: You are good at using tools.
User: Problem: 一个长方形的长是宽的2倍，周长是36cm，求面积是多少？

Documents:
(空)

```python
x = 36 / (2 * 3)
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

**Orchestrator生成**:
```
<think>
代码已经计算出了面积是72cm²。现在可以使用answer工具给出最终答案。
选择answer-math-1模型，因为这是数学问题。
</think>
<tool_call>
{"name": "answer", "arguments": {"model": "answer-math-1"}}
</tool_call>
```

---

### Turn 1: 工具执行

**answer工具调用**（`generation_quick3.py:1754-1838`）:
```python
elif tool_call['name']=='answer':
    if not tool_call["arguments"]['model'] in cur_model_mapping:
        continue
    cur_model_to_call = cur_model_mapping[tool_call["arguments"]['model']]  # answer-math-1 -> Qwen2.5-Math-72B

    # 根据模型类型构建不同长度的context
    if 'math' in cur_model_to_call.lower():
        # 数学模型使用较短context
        str_cut = cut_seq(tokenizer=tokenizer,seq=code_str,l=1000)
        code_str = str_cut['string_after_cut']
        context_str = cut_seq(tokenizer=tokenizer,seq=doc_str+code_str,l=2000)
```

**答案验证**（在execute_predictions中）:
```python
# 从输出中提取数字答案
predicted_answer = extract_number(response)  # 72
ground_truth = 72

# 验证答案
if abs(predicted_answer - ground_truth) < 0.01:
    attempt_correct = True
    dones[i] = True
```

**结果记录**（`generation_quick3.py:1309-1311`）:
```python
for i,a in enumerate(new_attempts):
    assert isinstance(a,list)
    if len(a)>0:
        attempts[i] += a  # 累积答案尝试
```

---

### Turn 1结束: 更新`active_mask`

```python
# generation_quick3.py:1340-1341
curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
active_mask = active_mask * curr_active_mask
# active_mask[i] = True * False = False (该样本已完成)
```

---

### Turn 2: 循环检查

```python
# generation_quick3.py:1043-1047
for step in range(self.config.max_turns):  # step=2
    if not active_mask.sum():  # active_mask全为0
        break  # 退出循环
```

**停止原因**: 所有样本都完成了 (`active_mask`全为0)

---

### 最终Reward计算

**正确性判断**（`generation_quick3.py:1388-1394`）:
```python
example_correctness = {}
for example_idx,example_repeat_id,turn_success in zip(all_turn_index,all_turn_repeat_ids,all_turn_success):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    if turn_success or (rollout_id in example_correct_by_rollout_id and example_correct_by_rollout_id[rollout_id]):
        example_correctness[rollout_id] = True
    elif not rollout_id in example_correctness:
        example_correctness[rollout_id] = False
```

**成本和延迟累积**（`generation_quick3.py:1395-1400`）:
```python
example_costs = defaultdict(int)
example_latency = defaultdict(int)
for example_idx,example_repeat_id,turn_cost,turn_latency in zip(all_turn_index,all_turn_repeat_ids,all_turn_costs,all_turn_latency):
    rollout_id = f"{example_idx}_____{example_repeat_id}"
    example_costs[rollout_id] += turn_cost
    example_latency[rollout_id] += turn_latency
```

假设:
- `example_costs[rollout_id] = 0.125 + 0.009 = 0.134`
- `example_latency[rollout_id] = 2.3 + 1.2 = 3.5`

**Efficiency reward计算**（`generation_quick3.py:1405-1416`）:
```python
if str(efficiency_reward).lower()=='true' and example_correctness[rollout_id]:
    cost_reward = example_costs[rollout_id]*5  # 0.134 * 5 = 0.67
    latency_reward = example_latency[rollout_id]/500  # 3.5 / 500 = 0.007
    if cost_reward+latency_reward>0.8:
        rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])-0.8
    else:
        rewards_by_rollout_id[rollout_id] = int(example_correctness[rollout_id])-latency_reward-cost_reward
        # = 1 - 0.007 - 0.67 = 0.323
```

**GRPO归一化**（`generation_quick3.py:1488-1513`）:
```python
# 假设该问题有4个rollout
example_rewards[example_idx] = [0.323, 0.15, -0.2, 0.1]

# 计算均值和标准差
example_reward_average[example_idx] = sum(example_rewards[example_idx])/len(example_rewards[example_idx])
# = (0.323 + 0.15 - 0.2 + 0.1) / 4 = 0.093

example_reward_std[example_idx] = stdev(example_rewards[example_idx])
# = 0.215

# 归一化
cur_reward = (rewards_by_rollout_id[rollout_id]-example_reward_average[example_idx])/(example_reward_std[example_idx]+1e-6)
# = (0.323 - 0.093) / 0.215 = 1.07

# Clip到[-3, 3]
if cur_reward>3:
    cur_reward = 3
if cur_reward<-3:
    cur_reward = -3
```

**训练样本选择**（`generation_quick3.py:1506-1508`）:
```python
if example_reward_std[example_idx]>0.1 and rollout_id in valid_answers and valid_answers[rollout_id] and turn_format:
    selected_indices.append(iter_index)  # 只选择格式正确且有有效答案的样本
    selected_for_train = True
```

---

## 6. 错误处理详解

### 6.1 JSON提取错误

**场景1**: 模型生成格式错误

输出:
```
<think>需要推理</think>
<tool_call>
{"name": "enhance_reasoning" "arguments": {"model": "reasoner-1"}}  # 缺少逗号
</tool_call>
```

**处理**（`generation_quick3.py:2112-2124`）:
```python
try:
    tmp_tool_call = json.loads(c1)  # 抛出JSONDecodeError
    assert set(list(tmp_tool_call.keys()))=={"name","arguments"}
    assert tmp_tool_call['name'] in ALL_TOOLS
    # ...
    cur_all_tool_calls.append(tmp_tool_call)
except:
    pass  # 跳过，format_correct保持False
```

**结果**: 该turn的`format_correct=False`，训练时会被过滤掉

---

**场景2**: 工具名称错误

输出:
```
<tool_call>
{"name": "reasoning_tool", "arguments": {"model": "reasoner-1"}}  # 工具名不存在
</tool_call>
```

**处理**（`generation_quick3.py:2115`）:
```python
assert tmp_tool_call['name'] in ALL_TOOLS  # AssertionError
# 被except捕获，跳过
```

---

**场景3**: 参数值不合法

输出:
```
<tool_call>
{"name": "answer", "arguments": {"model": "gpt-4o"}}  # gpt-4o不在answer模型列表中
</tool_call>
```

**处理**（`generation_quick3.py:1644-1650`）:
```python
valid_tool_call = True
func_signature = ALL_TOOLS[tool_call['name']]
for parameter_name,parameter_values in func_signature.items():
    if (not parameter_name in tool_call["arguments"]):
        valid_tool_call = False
    if (not tool_call["arguments"][parameter_name] in parameter_values) and parameter_values!='any':
        valid_tool_call = False  # gpt-4o not in ['answer-1', 'answer-2', ...]

if not valid_tool_call:
    continue  # 跳过该工具调用
```

**结果**: 该turn没有有效工具调用 → 不执行 → `dones[i] = False` → 继续下一turn

---

### 6.2 工具调用错误

**场景**: 代码执行超时或报错

**处理**（`generation_quick3.py:732-742`）:
```python
def call_tool_all(all_arguments):
    all_return_arguments = []
    for one_arguments in all_arguments['all_call_arguments']:
        try:
            all_return_arguments.append(call_tool(one_arguments))
        except Exception as tool_call_error:
            pass  # 忽略错误，继续处理下一个
    return {
        'id': all_arguments['id'],
        'all_tool_call_results': all_return_arguments
    }
```

**容错设计**: 工具调用失败不会导致整个rollout失败，只是该turn没有结果，可以在下一turn重试或选择其他工具

---

## 7. Multi-turn停止条件总结

### 7.1 达到最大轮数
**代码位置**: `training/lead_agent/llm_agent/generation_quick3.py:1043`
```python
for step in range(self.config.max_turns):  # 通常max_turns=10
```

### 7.2 所有样本完成
**代码位置**: `training/lead_agent/llm_agent/generation_quick3.py:1046-1047`
```python
if not active_mask.sum():  # active_mask全为0
    break
```

### 7.3 QA任务: 生成正确答案
在`execute_predictions`中判断答案正确性，设置`dones[i] = True`，然后在turn结束时：
```python
# generation_quick3.py:1340-1341
curr_active_mask = torch.tensor([not done for done in dones], dtype=torch.bool)
active_mask = active_mask * curr_active_mask
```

### 7.4 func_call任务: τ²-bench进程完成
**代码位置**: `training/lead_agent/llm_agent/generation_quick3.py:1152-1173`
```python
if os.path.isfile(os.path.join(cur_transfer_dir,'done')):
    try:
        with open(os.path.join(cur_transfer_dir,'done')) as f:
            tmp_result = f.read()
        if tmp_result=="Done!":
            # 计算最终reward
            correct = 0
            for subfile in os.listdir(os.path.join(cur_transfer_dir,'output')):
                if subfile.endswith('.json'):
                    with open(os.path.join(cur_transfer_dir,'output',subfile)) as f:
                        r = json.load(f)
                    correct += r["reward_info"]["reward"]
            if correct>0:
                simulation_reward = 1
            else:
                simulation_reward = 0
            example_correct_by_rollout_id[iter_rollout_id] = simulation_reward
    except:
        pass
    active_mask[item_idx] = 0  # 标记为完成
    receive_end_signal = True
    break
```

### 7.5 格式错误导致无法训练
虽然不会直接停止rollout，但`format_correct=False`的turn不会被选入训练：

**代码位置**: `training/lead_agent/llm_agent/generation_quick3.py:1506`
```python
if example_reward_std[example_idx]>0.1 and rollout_id in valid_answers and valid_answers[rollout_id] and turn_format:
    selected_indices.append(iter_index)  # 只有format正确才选入训练
    selected_for_train = True
```

---

---

## 8. Batch处理和Rollout重复机制

### 8.1 一个batch处理多个问题，每个问题生成多个答案

**核心机制**：使用`repeat`方法将batch重复n_agent次，为每个问题生成多个rollout用于GRPO算法的优势估计。

**代码位置**：`training/recipe/algo/grpo_ray_trainer_quick3.py:381`
```python
batch = batch.repeat(repeat_times=self.config.actor_rollout_ref.rollout.n_agent, interleave=True)
```

**n_agent配置**：
- 脚本位置：`training/resume_run_h100.sh:19`
```bash
ROLLOUT=8
```

- 传递配置：`training/resume_run_h100.sh:143`
```bash
+actor_rollout_ref.rollout.n_agent=$ROLLOUT \
```

**具体例子**：

假设训练配置：
- `train_batch_size = 16`（一个batch有16个问题）
- `n_agent = 8`（每个问题生成8个rollout）
- `interleave = True`（交错重复模式）

**Repeat前**：
```python
batch = [问题1, 问题2, ..., 问题16]  # 16个问题
```

**Repeat后**（interleave=True）：
```python
batch = [
    问题1_rollout1, 问题2_rollout1, ..., 问题16_rollout1,  # 第1轮
    问题1_rollout2, 问题2_rollout2, ..., 问题16_rollout2,  # 第2轮
    ...
    问题1_rollout8, 问题2_rollout8, ..., 问题16_rollout8   # 第8轮
]  # 总共 16 * 8 = 128 个rollout
```

**repeat方法实现**：`training/recipe/algo/grpo_ray_trainer_quick3.py:108-144`
```python
@classmethod
def repeat(cls, data: 'DataToolProto', repeat_times: int, interleave=False):
    new_tensors = {}
    for key, val in data.batch.items():
        if interleave:
            # repeat_interleave: [1,2,3] -> [1,1,2,2,3,3]
            new_tensors[key] = val.repeat_interleave(repeats=repeat_times, dim=0)
        else:
            # repeat: [1,2,3] -> [1,2,3,1,2,3]
            new_tensors[key] = val.repeat(repeat_times, 1)

    new_non_tensors = {}
    for key, val in data.non_tensor_batch.items():
        new_val = []
        if interleave:
            for v in val:
                for _ in range(repeat_times):
                    new_val.append(v)
        else:
            for _ in range(repeat_times):
                for v in val:
                    new_val.append(v)
        new_non_tensors[key] = new_val

    return cls(batch=new_tensors, non_tensor_batch=new_non_tensors)
```

### 8.2 为什么需要多个rollout？

**GRPO算法需求**：

Group Relative Policy Optimization需要在同一个问题的多个rollout之间计算相对优势。

代码位置：`training/lead_agent/llm_agent/generation_quick3.py:1488-1513`
```python
# 对每个问题，收集所有rollout的reward
for example_idx in example_indices:
    example_rewards[example_idx] = []
    for rollout_id in rollout_ids_for_example:
        example_rewards[example_idx].append(rewards_by_rollout_id[rollout_id])

    # 计算该问题所有rollout的均值和标准差
    example_reward_average[example_idx] = sum(example_rewards[example_idx])/len(example_rewards[example_idx])
    example_reward_std[example_idx] = stdev(example_rewards[example_idx])

# 归一化每个rollout的reward（相对于同组其他rollout）
for rollout_id in rollout_ids:
    cur_reward = (rewards_by_rollout_id[rollout_id] - example_reward_average[example_idx]) / (example_reward_std[example_idx] + 1e-6)
    # Clip到[-3, 3]
    cur_reward = max(-3, min(3, cur_reward))
```

**优势**：
1. **样本效率**：从一个问题生成多个答案，增加训练样本数量
2. **相对比较**：同一问题的不同解法可以比较优劣
3. **稳定训练**：通过组内标准化减少reward的方差

---

## 9. 并行度控制的完整层次结构

### 9.1 整体并行度控制

#### Ray集群级别

**配置位置**：`training/resume_run_h100.sh:110`
```bash
ray status && lscpu && ray job submit --address=http://localhost:8265 \
```

- **Ray服务地址**：`http://localhost:8265`
- **节点管理**：通过SLURM分配多节点
  - `training/resume_run_h100.sh:6`：`#SBATCH --nodes 2`
  - `training/resume_run_h100.sh:66-80`：节点IP配置
  ```bash
  nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
  nodes_array=($nodes)
  head_node=${nodes_array[0]}
  head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)
  ```

#### Batch级别并行

**subprocess并行启动τ²-bench进程**：

代码位置：`training/lead_agent/llm_agent/generation_quick3.py:1064-1067`
```python
func_call_cmd = ['python','rollout/tau2/cli.py','--domain',cur_domain,'--agent-llm','train',
    '--user-llm','gpt-5','--num-trials','1','--task_path',str(task_path),'--max-steps','40',
    '--cur_transfer_dir',str(cur_transfer_dir),'--output_file',str(cur_func_call_output_path),
    '--use_model_tool']
subprocess.Popen(func_call_cmd)  # 非阻塞并行调用
```

**并行数量**：等于batch中active样本的数量（由`active_mask`控制）

---

### 9.2 API调用并行度控制

#### ThreadPoolExecutor控制

**Sandbox工具API调用**：

代码位置：`training/verl/utils/reward_score/sandbox_fusion/utils.py:429`
```python
with concurrent.futures.ThreadPoolExecutor(max_workers=max(32, os.cpu_count() * 5)) as executor:
    futures = []
    for case in cases:
        future = executor.submit(_process_single_case, case, ..., concurrent_semaphore)
        futures.append(future)
```

**并行度**：`max(32, os.cpu_count() * 5)`
- 假设CPU有16核，则max_workers = max(32, 80) = 80

**τ²-bench运行**：

代码位置：`training/rollout/tau2/run.py:355`
```python
with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
    futures = [executor.submit(run_trial, ...) for trial in trials]
```

**并行度**：由`max_concurrency`参数决定

#### Semaphore速率限制

**Sandbox API调用**：

代码位置：`training/verl/trainer/ppo/reward.py:112`
```python
_concurrent_semaphore = sandbox_manager.Semaphore(sandbox_config.get("max_concurrent", 64))
```

**默认并发数**：64

使用位置：`training/verl/utils/reward_score/sandbox_fusion/utils.py:254-258`
```python
async with concurrent_semaphore:
    async with session.post(sandbox_fusion_url, json=payload, timeout=timeout) as response:
        result = await response.json()
```

**LLM生成的Semaphore**：

代码位置：`training/lead_agent/llm_agent/generation_quick3.py:756,758`
```python
semaphore = asyncio.Semaphore(2)
with ThreadPoolExecutor(max_workers=2) as executor:
```

**并发数**：2（控制同时进行的LLM API调用）

---

### 9.3 Tool调用并行度控制

#### SandboxFusionTool配置

**配置文件**：`training/examples/sglang_multiturn/config/tool_config/sandbox_fusion_tool_config.yaml`
```yaml
tools:
  - class_name: "verl.tools.sandbox_fusion_tools.SandboxFusionTool"
    config:
      sandbox_fusion_url: "https://xxx.apigateway-cn-beijing.volceapi.com/run_code"
      num_workers: 10
      enable_global_rate_limit: true
      rate_limit: 10
      default_timeout: 30
```

**代码实现**：`training/verl/tools/sandbox_fusion_tools.py:65`
```python
self._semaphore = threading.Semaphore(rate_limit)  # rate_limit=10
```

**并发控制**：
- `num_workers`: 10（工作线程数）
- `rate_limit`: 10（同时最多10个并发请求）

#### SearchTool配置

**配置文件**：`training/examples/sglang_multiturn/config/tool_config/search_tool_config.yaml`
```yaml
tools:
  - class_name: verl.tools.search_tool.SearchTool
    config:
      retrieval_service_url: http://127.0.0.1:8000/retrieve
      num_workers: 120
      rate_limit: 120
      timeout: 30
```

**代码实现**：`training/verl/tools/search_tool.py:70`
```python
self._semaphore = threading.Semaphore(rate_limit)  # rate_limit=120
```

**并发控制**：
- `num_workers`: 120
- `rate_limit`: 120

**为什么SearchTool的rate_limit更高？**
- 搜索服务是本地部署的retrieval服务，延迟低
- Sandbox是外部API，需要限制并发避免超出配额

---

### 9.4 并行度控制总结

| 层次 | 控制机制 | 并发数 | 代码位置 |
|------|----------|--------|----------|
| **Ray集群** | SLURM + Ray | 多节点×8 GPU/节点 | `resume_run_h100.sh:6,110` |
| **Batch并行** | subprocess.Popen | batch_size个进程 | `generation_quick3.py:1064-1067` |
| **Sandbox API** | ThreadPoolExecutor + Semaphore | max(32, CPU×5), 默认64 | `sandbox_fusion/utils.py:429`, `reward.py:112` |
| **τ²-bench** | ThreadPoolExecutor | max_concurrency | `tau2/run.py:355` |
| **LLM生成** | Semaphore + ThreadPoolExecutor | 2 | `generation_quick3.py:756,758` |
| **SandboxFusionTool** | Semaphore | 10 | `sandbox_fusion_tools.py:65` |
| **SearchTool** | Semaphore | 120 | `search_tool.py:70` |

---

## 10. Docker使用原因和环境隔离

### 10.1 为什么使用Docker容器？

**不是在普通Python环境中直接安装veRL**，而是通过容器化部署。

#### 容器化部署配置

**代码位置**：`training/resume_run_h100.sh:62-64`
```bash
MAIN_CONTAINER="/lustre/fsw/portfolios/nvr/users/hongjins/containers/s1.sqsh"

MOUNTS="--container-mounts=${GPFS}:${GPFS},/lustre:/lustre,${GPFS}:/verl"
```

**启动方式**：
- 使用`.sqsh`格式的SquashFS容器镜像
- 通过`--container-mounts`挂载宿主机目录到容器

#### 环境变量配置

**代码位置**：`training/resume_run_h100.sh:39-40`
```bash
export RAY_USAGE_STATS_ENABLED=0
export RAY_DISABLE_DOCKER_CPU_WARNING=1
```

---

### 10.2 Dockerfile依赖分析

**Dockerfile位置**：`training/docker/Dockerfile.ngc.vllm`

#### 基础镜像

**Line 2**：
```dockerfile
FROM nvcr.io/nvidia/pytorch:24.05-py3
```

使用NVIDIA官方的PyTorch容器，已包含CUDA和cuDNN。

#### 卸载NVIDIA PyTorch分支

**Line 5-11**：
```dockerfile
RUN pip3 uninstall pytorch-quantization \
    pytorch-triton \
    torch \
    torch-tensorrt \
    torchvision \
    xgboost transformer_engine flash_attn \
    apex megatron-core -y
```

#### 安装特定版本的PyTorch

**Line 13**：
```dockerfile
RUN pip3 install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124
```

**关键依赖**：PyTorch 2.4.0 with CUDA 12.4

#### Megatron依赖（可选）

**Line 17-19（apex）**：
```dockerfile
RUN MAX_JOBS=4 pip3 install -v --disable-pip-version-check --no-cache-dir --no-build-isolation \
    --config-settings "--build-option=--cpp_ext" --config-settings "--build-option=--cuda_ext" \
    git+https://github.com/NVIDIA/apex
```

**Line 44-45（Transformer Engine）**：
```dockerfile
RUN MAX_JOBS=4 NINJA_FLAGS="-j4" pip3 install flash-attn==2.5.8 --no-cache-dir --no-build-isolation
RUN MAX_JOBS=1 NINJA_FLAGS="-j1" TE_BUILD_WITH_NINJA=0 pip3 install git+https://github.com/eric-haibin-lin/TransformerEngine.git@v1.7.0
```

#### 核心依赖安装

**Line 22-37**：
```dockerfile
RUN pip3 install --no-cache-dir \
    accelerate \
    codetiming \
    datasets \
    hydra-core \
    numpy \
    'pandas' \
    'peft' \
    'pyarrow>=15.0.0' \
    'pybind11' \
    'pylatexenc' \
    'ray>=2.10' \
    'tensordict<0.6' \
    'transformers' \
    'vllm==0.6.3.post1' \
    'wandb'
```

**关键依赖**：
- `vllm==0.6.3.post1`：快速推理引擎
- `ray>=2.10`：分布式计算框架
- `transformers`：Hugging Face模型库
- `flash-attn==2.5.8`：Flash Attention加速

---

### 10.3 Docker的优势

#### 1. 环境一致性

**问题**：在裸机上安装可能遇到：
- CUDA版本不匹配
- PyTorch与vLLM版本冲突
- Flash Attention编译失败

**解决**：Docker镜像固定所有依赖版本，确保：
```
PyTorch 2.4.0 + CUDA 12.4 + vLLM 0.6.3.post1 + Flash Attention 2.5.8
```

#### 2. 集群级别部署

**代码位置**：`training/resume_run_h100.sh:66-80`
```bash
nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
nodes_array=($nodes)
head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)
```

**场景**：SLURM管理的多节点集群（如2节点×8 GPU）

**好处**：
- 所有节点使用相同的容器镜像
- 避免在每个节点上重复安装依赖
- 快速扩展到更多节点

#### 3. GPU驱动兼容性

**NVIDIA Container Toolkit**：
- 容器自动继承宿主机的GPU驱动
- 无需在容器内安装NVIDIA驱动
- 支持多种GPU架构（A100, H100等）

#### 4. 避免依赖冲突

**问题**：veRL项目依赖：
- Megatron-Core（需要特定版本的apex）
- vLLM（需要特定版本的Flash Attention）
- Ray（需要特定版本的grpcio）

**解决**：容器隔离环境，不影响宿主机其他Python项目。

---

### 10.4 容器架构详解：不是微服务

#### 常见误解

❌ **错误理解**：veRL、vLLM、Ray等组件各自作为独立容器封装，通过API互相调用（微服务架构）

✅ **实际架构**：单个大容器包含所有组件，代码通过目录挂载注入，Ray在容器内管理分布式执行

---

#### 实际的容器使用方式

**代码位置**：`training/resume_run_h100.sh:86,95,109`

**Head节点启动容器**：
```bash
srun --container-image="$MAIN_CONTAINER" $MOUNTS bash -c "ray start --head ..."
```

**Worker节点启动容器**：
```bash
srun --container-image="$MAIN_CONTAINER" $MOUNTS bash -c "ray start --address ..."
```

**在容器内提交训练任务**：
```bash
srun --container-image="$MAIN_CONTAINER" $MOUNTS bash -c \
"ray job submit --address=http://localhost:8265 \
    --runtime-env-json='{\"working_dir\": \"/verl\"}' \
    -- python3 -u -m recipe.algo.main_grpo_quick3 ..."
```

---

#### 关键理解1：所有组件在同一个容器内

容器内包含（通过Dockerfile安装）：
- ✅ PyTorch 2.4.0
- ✅ vLLM 0.6.3.post1
- ✅ Ray >= 2.10
- ✅ veRL框架（作为Python包）
- ✅ transformers, flash-attn等

**不是独立容器**，而是同一个容器内的不同Python包。

---

#### 关键理解2：代码通过挂载注入，不是封装

**代码位置**：`training/resume_run_h100.sh:64`
```bash
MOUNTS="--container-mounts=${GPFS}:${GPFS},/lustre:/lustre,${GPFS}:/verl"
```

**挂载关系**：
- 宿主机目录：`/lustre/fsw/portfolios/nvr/users/sdiao/toolorchestra_code/ToolOrchestra/training/verl`
- 容器内路径：`/verl`
- **代码是动态挂载的，不是打包在容器镜像里**

**优势**：
- 修改代码后无需重新构建镜像
- 开发调试更快速
- 容器镜像保持不变，只包含依赖环境

---

#### 关键理解3：Ray在容器内管理分布式执行

**架构示意图**：

```
┌─────────────────────────────────────────────────┐
│  物理节点 1 (宿主机)                            │
│  ┌───────────────────────────────────────────┐  │
│  │  Docker容器 (MAIN_CONTAINER)             │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │  Ray Head (Python进程)              │  │  │
│  │  │  ├─ ActorRolloutRefWorker (Ray Actor)│ │  │
│  │  │  ├─ CriticWorker (Ray Actor)         │  │  │
│  │  │  └─ RewardManager (Ray Actor)        │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  │  /verl ← 挂载自 /lustre/.../verl         │  │
│  │  环境: PyTorch + vLLM + Ray + veRL        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    ↕ Ray通信 (TCP/IP)
┌─────────────────────────────────────────────────┐
│  物理节点 2 (宿主机)                            │
│  ┌───────────────────────────────────────────┐  │
│  │  Docker容器 (相同镜像MAIN_CONTAINER)      │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │  Ray Worker (Python进程)            │  │  │
│  │  │  ├─ ActorRolloutRefWorker (Ray Actor)│ │  │
│  │  │  └─ CriticWorker (Ray Actor)         │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  │  /verl ← 挂载自 /lustre/.../verl         │  │
│  │  环境: PyTorch + vLLM + Ray + veRL        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

#### 执行流程详解

**步骤1：容器启动（每个节点）**

**Head节点**（`training/resume_run_h100.sh:86`）：
```bash
srun --container-image="$MAIN_CONTAINER" \
     --container-mounts="${GPFS}:/verl" \
     bash -c "ray start --head --node-ip-address=$head_node_ip --port=6379"
```

**发生了什么**：
1. SLURM在物理节点启动Docker容器
2. 挂载`/lustre/.../verl`到容器的`/verl`
3. 容器内执行`ray start --head`
4. Ray head进程在容器内监听端口6379

**Worker节点**（`training/resume_run_h100.sh:95`）：
```bash
srun --container-image="$MAIN_CONTAINER" \
     bash -c "ray start --address $ip_head"
```

**发生了什么**：
1. 启动相同的容器镜像
2. 容器内执行`ray start --address`连接到head节点
3. 形成Ray集群（跨容器，但同一网络）

---

**步骤2：提交训练任务（在容器内）**

**代码位置**：`training/resume_run_h100.sh:110-112`
```bash
srun --container-image="$MAIN_CONTAINER" bash -c \
"ray job submit --address=http://localhost:8265 \
    --runtime-env-json='{\"working_dir\": \"/verl\"}' \
    -- python3 -u -m recipe.algo.main_grpo_quick3 ..."
```

**发生了什么**：
1. 在head节点的**容器内**运行`ray job submit`
2. Ray接收任务，在容器内的`/verl`目录运行Python脚本
3. Python脚本 `import verl`（从容器内已安装的包）
4. Python脚本读取配置和数据（从挂载的`/verl`目录）

---

**步骤3：Ray调度Worker（在容器内）**

**训练代码**：`training/recipe/algo/main_grpo_quick3.py:214-231`
```python
trainer = RayGRPOTrainer(
    config=config,
    tokenizer=tokenizer,
    role_worker_mapping=role_worker_mapping,
    reward_fn=reward_fn,
)
trainer.init_workers()  # 创建Ray Actor
trainer.fit()
```

**`init_workers()`内部**：
```python
# 创建Ray Actor（在容器内，不是新容器）
self.actor_rollout_ref_workers = ray_worker_group_cls(
    num_workers=config.actor_rollout_ref.rollout.gpu_per_node,
    cls=ActorRolloutRefWorker,
    ...
)
```

**这些Worker是**：
- ✅ 容器内的Ray Actor（Python进程）
- ✅ 可能分布在不同物理节点的容器中
- ❌ **不是**新的Docker容器

---

#### 微服务架构对比

**不是这样**（微服务架构）：
```
┌──────────┐   HTTP/gRPC   ┌──────────┐
│ veRL容器 │ ←────────────→ │ vLLM容器 │
└──────────┘               └──────────┘
     ↕ API                      ↕ API
┌──────────┐               ┌──────────┐
│ Ray容器  │               │ Redis容器│
└──────────┘               └──────────┘
```

**而是这样**（单体容器 + Ray分布式）：
```
┌─────────────────────────────────────────┐
│  一个大容器                              │
│  ┌───────────────────────────────────┐  │
│  │  Ray进程                          │  │
│  │  ├─ import verl (Python包)       │  │
│  │  ├─ import vllm (Python包)       │  │
│  │  ├─ import torch (Python包)      │  │
│  │  └─ 调用关系: 直接函数调用        │  │
│  └───────────────────────────────────┘  │
│  /verl ← 挂载自宿主机                   │
└─────────────────────────────────────────┘
```

---

#### 架构对比表

| 维度 | 微服务架构 | ToolOrchestra实际架构 |
|------|-----------|---------------------|
| **容器数量** | 每个服务一个容器 | 主容器1个 + 可选外部服务容器 |
| **veRL位置** | 独立veRL容器 | ❌ 在主容器内作为Python包 |
| **vLLM位置** | 独立vLLM容器 | ❌ 在主容器内作为Python包 |
| **Ray位置** | 独立Ray容器 | ❌ 在主容器内管理进程 |
| **通信方式** | HTTP/gRPC（跨容器） | ✅ 容器内直接函数调用 + Ray分布式（跨物理节点） |
| **代码部署** | 打包在镜像内 | ✅ 挂载目录，动态加载 |
| **延迟** | 高（网络序列化） | 低（内存直接调用） |
| **资源共享** | 难（需要外部存储） | 易（共享GPU显存、系统内存） |
| **独立扩展** | 易（K8s HPA） | 通过Ray动态扩展Worker |
| **开发迭代** | 慢（需重新构建镜像） | 快（修改代码即生效） |
| **依赖管理** | 简单（各容器独立） | 需要固定版本避免冲突 |

---

#### 为什么选择单体容器架构？

**优势**：

1. **低延迟**：
   - veRL调用vLLM：直接Python函数调用（微秒级）
   - 微服务架构：HTTP请求 + 序列化/反序列化（毫秒级）
   - **对于RL训练，每个step需要数百次推理调用，延迟影响巨大**

2. **资源共享**：
   - GPU显存可以在vLLM推理和PyTorch训练之间动态分配
   - 避免容器间数据拷贝

3. **开发友好**：
   - 修改veRL代码后，重启Ray job即可（秒级）
   - 微服务需要重新构建镜像、推送registry、更新deployment（分钟级）

4. **简化部署**：
   - 只需管理一个容器镜像
   - SLURM原生支持容器调度

**劣势（及应对）**：

1. ❌ 容器镜像大（6-10GB）
   - ✅ 应对：使用SquashFS (.sqsh)格式，共享存储避免重复下载

2. ❌ 无法独立扩展组件
   - ✅ 应对：通过Ray动态创建/销毁Worker实现扩展

3. ❌ 依赖冲突风险
   - ✅ 应对：Dockerfile固定所有版本（PyTorch 2.4.0 + vLLM 0.6.3 + ...）

---

#### 例外情况：使用多个容器的场景

**代码位置**：`training/verl/nvidia/scripts/deepseek_evaluation.sh:76,84,98`

```bash
# Sandbox代码执行服务 - 独立容器
srun --container-image=$CODE_SANDBOX_IMAGE bash -c \
    "python /workspace/.../launch_default_reward_server.py" &

# Reasoning reward服务 - 独立容器
srun --container-image=${SANDBOX_IMAGE} bash -c \
    "python scripts/host_reward_server.py" &

# 主训练容器
srun --container-image="$container_name" $MOUNTS bash -c "ray start --head"
```

**这里有3个容器**：
1. `CODE_SANDBOX_IMAGE` - 代码执行沙盒
2. `SANDBOX_IMAGE` - Reasoning reward服务
3. `container_name` - 主训练容器（veRL + Ray）

**为什么这些服务要分开容器？**

1. **安全性**：
   - 代码执行必须隔离（避免恶意代码影响训练环境）
   - Sandbox容器有严格的资源限制和网络隔离

2. **依赖隔离**：
   - Reward服务可能需要不同的Python版本或CUDA版本
   - 避免与主训练环境冲突

3. **独立扩展**：
   - 可以在不同节点启动更多sandbox容器
   - 不影响训练容器的稳定性

4. **生命周期管理**：
   - Sandbox服务可能需要独立重启或更新
   - 不需要中断训练任务

**交互方式**：
- 主容器 ←HTTP→ Sandbox容器（通过localhost端口）
- 这些服务通过HTTP API调用（见第11节）

---

#### 核心设计理念

> 用一个大容器提供**运行环境**（依赖隔离），用Ray提供**分布式调度**（资源管理），用目录挂载提供**代码灵活性**（快速迭代）。

**这不是"包裹了一层"，而是"提供了沙盒环境"**！

- **容器的作用**：隔离依赖，确保环境一致性
- **Ray的作用**：管理分布式计算，跨节点调度
- **挂载的作用**：开发便捷，无需重构镜像

---

## 11. API和Tool调用的localhost架构

### 11.1 Retrieval服务（localhost）

#### 服务配置

**训练脚本配置**：`training/resume_run_h100.sh:185`
```bash
+retriever.url=http://127.0.0.1:8000/retrieve \
+retriever.topk=5 \
```

**Tool配置文件**：`training/examples/sglang_multiturn/config/tool_config/search_tool_config.yaml:4`
```yaml
retrieval_service_url: http://127.0.0.1:8000/retrieve
```

#### 服务启动

**代码位置**：`training/examples/sglang_multiturn/search_r1_like/local_dense_retriever/retrieval_server.py:399-400`
```python
# 3) Launch the server. By default, it listens on http://127.0.0.1:8000
uvicorn.run(app, host="0.0.0.0", port=8000)
```

**服务类型**：FastAPI应用
**监听地址**：`0.0.0.0:8000`（接受所有网卡的连接）
**访问地址**：`http://127.0.0.1:8000/retrieve`（本地访问）

#### API调用

**代码位置**：`training/lead_agent/llm_agent/generation_quick3.py:587`
```python
results = requests.post(f'http://{cur_model_config["ip_addr"]}:{cur_model_config["port"]}/retrieve',
                       json=payload).json()
```

---

### 11.2 Sandbox Fusion API（外部服务）

#### 服务配置

**Tool配置文件**：`training/examples/sglang_multiturn/config/tool_config/sandbox_fusion_tool_config.yaml:4`
```yaml
sandbox_fusion_url: "https://xxx.apigateway-cn-beijing.volceapi.com/run_code"
```

**重要**：这**不是localhost服务**，是外部的代码执行API（火山引擎的Sandbox Fusion服务）。

#### 为什么使用外部API？

1. **安全性**：代码执行需要沙盒隔离，避免恶意代码影响训练环境
2. **可扩展性**：外部服务可以水平扩展，支持高并发
3. **专业性**：Sandbox Fusion提供安全的代码执行环境

---

### 11.3 Ray集群服务（localhost）

#### 服务配置

**启动Ray集群**：`training/resume_run_h100.sh:110`
```bash
ray status && lscpu && ray job submit --address=http://localhost:8265 \
```

**Ray地址环境变量**：`training/recipe/dapo/run_dapo_qwen2.5_32b.sh:34`
```bash
RAY_ADDRESS=${RAY_ADDRESS:-"http://localhost:8265"}
```

**服务类型**：Ray Dashboard和Job提交服务
**默认端口**：8265

---

### 11.4 τ²-bench模拟环境服务（localhost）

#### 服务启动

**代码位置**：`training/rollout/tau2/api_service/simulation_service.py:73`
```python
uvicorn.run(app, host="127.0.0.1", port=API_PORT)
```

**配置**：`training/rollout/tau2/config.py:51`
```python
REDIS_HOST = "localhost"
```

**服务类型**：FastAPI应用，提供τ²-bench环境交互接口

#### 环境管理器

**代码位置**：`training/rollout/tau2/orchestrator/environment_manager.py:147`
```python
def __init__(
    self,
    host: str = "localhost",
    port: int = 8000,
    ...
):
```

---

### 11.5 LLM推理服务

#### 服务配置

**代码位置**：`training/resume_h100.py:130`
```python
testing = requests.post(f'http://{serve_ip1}:{testing_port}/retrieve', json=payload).json()
```

**vLLM Server**：

代码位置：`training/verl/workers/rollout/chat_scheduler.py:366`
```python
client = AsyncOpenAI(base_url=f"http://{address}/v1", api_key="token-abc123", timeout=None, max_retries=0)
```

**服务类型**：OpenAI兼容的vLLM推理服务
**API格式**：`http://{address}/v1/chat/completions`

---

### 11.6 服务架构总结

| 服务名称 | 地址 | 端口 | 类型 | 代码位置 |
|---------|------|------|------|----------|
| **Retrieval服务** | localhost | 8000 | 本地FastAPI | `retrieval_server.py:400` |
| **Sandbox Fusion** | 外部API | 443(HTTPS) | 远程沙盒 | `sandbox_fusion_tool_config.yaml:4` |
| **Ray集群** | localhost | 8265 | 本地Ray | `resume_run_h100.sh:110` |
| **τ²-bench模拟** | localhost | API_PORT | 本地FastAPI | `simulation_service.py:73` |
| **vLLM推理** | 配置IP | 配置端口 | 推理服务 | `chat_scheduler.py:366` |

#### 服务交互流程

```
训练脚本 (main_grpo_quick3.py)
    ↓
Ray集群 (localhost:8265) ← 调度所有Worker
    ↓
┌──────────────────────────────────────┐
│  Rollout Worker (generation_quick3)  │
│  ↓                                   │
│  LLM生成 → vLLM服务 (http://{ip}:{port}/v1)
│  ↓                                   │
│  Tool执行:                           │
│    - SearchTool → Retrieval服务 (localhost:8000)
│    - SandboxFusionTool → 外部API (https://...)
│    - τ²-bench → 模拟服务 (localhost:API_PORT)
└──────────────────────────────────────┘
```

---

## 总结

| 方面 | 实现方式 | 代码位置 |
|------|----------|----------|
| **单turn生成** | 一个tool call决策（工具+模型） | `generation_quick3.py:1236` |
| **Batch处理** | 多个问题，每个问题n_agent=8个rollout | `grpo_ray_trainer_quick3.py:381` |
| **并行化** | Batch内多sample并行，turn内串行 | `generation_quick3.py:1064-1067, 1043-1047` |
| **并发控制** | Ray集群 + ThreadPoolExecutor + Semaphore | `reward.py:112`, `utils.py:429` |
| **Docker部署** | 容器化环境，固定依赖版本 | `Dockerfile.ngc.vllm`, `resume_run_h100.sh:62` |
| **Localhost服务** | Retrieval(8000), Ray(8265), τ²-bench | `retrieval_server.py:400`, `resume_run_h100.sh:110` |
| **Multi-turn** | 循环 + context累积 + active_mask追踪 | `generation_quick3.py:996-1579` |
| **RL框架** | veRL + GRPO算法 + Ray分布式 | `main_grpo_quick3.py:214-231` |
| **JSON提取** | try-except包裹，失败则format_correct=False | `generation_quick3.py:2094-2148` |
| **错误处理** | 容错设计，错误turn不参与训练但不中断rollout | `generation_quick3.py:732-742, 2123-2124` |
| **停止条件** | max_turns / active_mask=0 / 答案正确 / 任务完成 | `generation_quick3.py:1043, 1046-1047, 1152-1173` |
