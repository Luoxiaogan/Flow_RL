# ToolOrchestra 上下文维护机制详解

> 基于 `.reference_projects/ToolOrchestra/training/lead_agent` 的深度分析

## 目录

1. [核心理念](#核心理念)
2. [上下文的三个层次](#上下文的三个层次)
3. [完整示例：从零到答案](#完整示例从零到答案)
4. [长度控制机制](#长度控制机制)
5. [上下文传递路径](#上下文传递路径)
6. [两种任务类型对比](#两种任务类型对比)
7. [关键技巧与最佳实践](#关键技巧与最佳实践)

---

## 核心理念

### 类比：人类解题过程

想象你在解决一道复杂的数学竞赛题：

```
┌─────────────────────────────────────────────────────────┐
│ 1. 阅读题目 → 初始问题                                  │
│ 2. 翻书查公式 → 检索文档                                │
│ 3. 草稿纸计算 → 生成代码                                │
│ 4. 写下答案 → 生成答案                                  │
│ 5. 检查不对？回到步骤2，但保留所有草稿纸！              │
└─────────────────────────────────────────────────────────┘
```

**关键点**：你不会扔掉之前的草稿，每次都在前面的基础上继续推进。

ToolOrchestra 的上下文维护机制模拟的就是这个"保留所有草稿"的过程。

---

## 上下文的三个层次

### 层次 1：应用层上下文（Application Layer）

**本质**：人类可读的数据结构

**核心变量**：
```python
retrieved_documents = [[] for _ in range(batch_size)]  # 检索到的文档
code_snippets = [[] for _ in range(batch_size)]        # 生成的代码片段
attempts = [[] for _ in range(batch_size)]             # 尝试的答案
```

**特性**：
- ✅ 只增不减（accumulative）
- ✅ 人类可读
- ✅ 完整保留所有历史

**可视化**：

```
轮次 0:  retrieved_documents[0] = []
         code_snippets[0] = []
         attempts[0] = []
         ↓
轮次 1:  retrieved_documents[0] = [doc1, doc2]
         code_snippets[0] = []
         attempts[0] = []
         ↓
轮次 2:  retrieved_documents[0] = [doc1, doc2]
         code_snippets[0] = [code1]
         attempts[0] = []
         ↓
轮次 3:  retrieved_documents[0] = [doc1, doc2, doc3]
         code_snippets[0] = [code1]
         attempts[0] = [answer1]
```

---

### 层次 2：提示层上下文（Prompt Layer）

**本质**：模型可见的文本格式

**转换过程**：
```python
# 应用层 → 提示层
retrieved_documents[i] → doc_str
code_snippets[i] → code_str
attempts[i] → attempt_str
                    ↓
            context_str (合并 + 截断)
                    ↓
            chat (添加系统提示 + 问题)
```

**代码实现** (`generation_quick3.py:1103-1132`)：

```python
def build_context(retrieved_documents, code_snippets, attempts, problem):
    # 步骤1: 格式化文档
    doc_str = ''
    for doc_idx, doc in enumerate(retrieved_documents):
        doc_str += f"Doc {doc_idx+1}: {doc[:4000]}\n\n"

    # 步骤2: 格式化代码片段
    code_str = ''
    for code_idx, code_piece in enumerate(code_snippets):
        code_str += f"```python\n{code_piece['code']}\n```\n\n"
        code_str += f"```output\n{code_piece['output']}\n```\n\n"

    # 步骤3: 格式化答案尝试
    attempt_str = ''
    for attempt_idx, attempt in enumerate(attempts):
        attempt_str += f"Attempt{attempt_idx+1} answer by {attempt['model']}: {attempt['answer']}\n"

    # 步骤4: 合并并截断
    context_str = cut_seq(tokenizer, doc_str + code_str + attempt_str, l=24000)

    # 步骤5: 构建最终 prompt
    chat = [
        {"role": "system", "content": "You are good at using tools."},
        {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an appropriate tool."}
    ]

    return chat
```

---

### 层次 3：张量层上下文（Tensor Layer）

**本质**：PyTorch 计算图中的 tensor

**核心变量**：
```python
all_turn_input_ids = []        # 每轮的完整输入 (prompt + response)
all_turn_attention_mask = []   # 对应的 attention mask
all_turn_position_ids = []     # 对应的 position IDs
all_turn_responses = []        # 每轮的 response
```

**Tensor 构建** (`generation_quick3.py:1222-1246`)：

```python
# 左侧 padding + prompt + response
input_padding = torch.ones((batch_size, padding_len), dtype=torch.long) * pad_token_id
round_input_ids = torch.cat([
    input_padding,                           # [batch, padding_len]
    rollings_active.batch['input_ids'],     # [batch, prompt_len]
    responses_ids                            # [batch, response_len]
], dim=1)

# 对应的 attention mask
mask_padding = torch.zeros((batch_size, padding_len), dtype=torch.long)
round_attention_mask = torch.cat([
    mask_padding,
    self.tensor_fn.create_attention_mask(rollings_active.batch['input_ids']),
    self.tensor_fn.create_attention_mask(responses_ids)
], dim=1)

# Position IDs（从0开始递增）
round_position_ids = self.tensor_fn.create_position_ids(round_attention_mask)
```

**可视化示例**（假设 max_length=20, pad_token_id=0）：

```
第一轮:
input_ids:       [0  0  0  0  0  问题: 1  2  3  4] [响应: 5  6  7  8  9]
attention_mask:  [0  0  0  0  0         1  1  1  1] [       1  1  1  1  1]
position_ids:    [0  0  0  0  0         0  1  2  3] [       4  5  6  7  8]
                 └─ padding ─┘ └── prompt (4) ──┘  └── response (5) ──┘

第二轮 (上下文更长了):
input_ids:       [0  问题+文档: 1  2  3  4  5  6  7  8  9] [响应: 10 11 12 13]
attention_mask:  [0             1  1  1  1  1  1  1  1  1] [       1  1  1  1]
position_ids:    [0             0  1  2  3  4  5  6  7  8] [       9 10 11 12]
                 └─ padding ─┘ └──── prompt (9) ────────┘  └── response (4) ─┘

第三轮 (上下文继续增长):
input_ids:       [问题+文档+代码: 1  2  3  4  5  6  7  8  9  10 11 12] [响应: 13 14 15]
attention_mask:  [               1  1  1  1  1  1  1  1  1  1  1  1]  [       1  1  1]
position_ids:    [               0  1  2  3  4  5  6  7  8  9 10 11]  [      12 13 14]
                 └─ no padding ─┘ └───────── prompt (12) ──────────┘  └─ response (3) ┘
```

**关键点**：
1. **左侧 padding**: prompt 部分使用左侧 padding，方便拼接 response
2. **Position IDs 连续**: 忽略 padding，从第一个有效 token 开始计数
3. **长度动态增长**: 每轮的 prompt 长度不断增加

---

## 完整示例：从零到答案

让我们通过一个真实的例子，详细展示上下文如何在多轮中演化。

### 场景设定

**问题**：计算 15! (15的阶乘) 的值

**初始状态**：
```python
retrieved_documents[0] = []
code_snippets[0] = []
attempts[0] = []
active_mask[0] = True
total_costs[0] = 0.0
```

---

### 第一轮：搜索阶乘定义

#### Step 1: 构建 Prompt

**应用层上下文**：
```python
retrieved_documents[0] = []  # 空
code_snippets[0] = []        # 空
attempts[0] = []             # 空
```

**提示层上下文**：
```python
context_str = ""  # 没有历史信息

chat = [
    {"role": "system", "content": "You are good at using tools."},
    {"role": "user", "content": "Problem: 计算 15! (15的阶乘) 的值\n\nChoose an appropriate tool."}
]
```

**模型看到的完整 prompt**：
```
<|im_start|>system
You are good at using tools.<|im_end|>
<|im_start|>user
Problem: 计算 15! (15的阶乘) 的值

Choose an appropriate tool.<|im_end|>
<|im_start|>assistant
```

#### Step 2: 模型生成

**模型输出**：
```
<think>
这个问题需要计算阶乘，我应该先搜索阶乘的定义和计算方法
</think>

<tool_call>
{"name": "search", "arguments": {"model": "search-1"}}
</tool_call>
```

#### Step 3: 解析工具调用

**后处理结果**：
```python
tool_calls = [
    {"name": "search", "arguments": {"model": "search-1"}}
]
```

#### Step 4: 执行搜索工具

**搜索过程**：
```python
# 1. 生成搜索 query
query_prompt = "Problem: 计算 15! (15的阶乘) 的值\n\n"
query_prompt += "Write a query to search for relevant information. "
query_prompt += "Wrap the query within <query> and </query>."

query_response = llm_call(query_prompt)
# 输出: "<query>阶乘的定义和计算方法</query>"

query = "阶乘的定义和计算方法"

# 2. 调用搜索 API
search_results = search_api.search(query, topk=3)

# 返回结果
search_results = [
    "阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。",
    "对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。",
    "在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。"
]
```

**工具返回**：
```python
result = {
    'search_results_data': [
        "阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。",
        "对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。",
        "在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。"
    ],
    'cost': 0.002,
    'latency': 1.5
}
```

#### Step 5: 更新上下文

**应用层状态**：
```python
retrieved_documents[0] = [
    "阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。",
    "对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。",
    "在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。"
]
code_snippets[0] = []  # 保持不变
attempts[0] = []       # 保持不变
active_mask[0] = True  # 还未完成
total_costs[0] = 0.002
```

#### Step 6: 保存到训练数据

**张量层数据**：
```python
all_turn_input_ids.append(round_input_ids)        # [1, max_len]
all_turn_attention_mask.append(round_attention_mask)
all_turn_position_ids.append(round_position_ids)
all_turn_responses.append(responses_ids)          # 模型生成的 tool_call
all_turn_tools.append([("search", "search-1")])   # 使用的工具
all_turn_success.append(False)                    # 还没有正确答案
```

---

### 第二轮：生成代码计算

#### Step 1: 构建 Prompt（包含第一轮的上下文）

**应用层上下文**（现在有内容了）：
```python
retrieved_documents[0] = [doc1, doc2, doc3]  # 上一轮搜索的结果
code_snippets[0] = []
attempts[0] = []
```

**提示层上下文**：
```python
# 格式化文档
doc_str = """Doc 1: 阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。

Doc 2: 对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。

Doc 3: 在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。

"""

# 没有代码和答案尝试
code_str = ""
attempt_str = ""

context_str = doc_str  # 只有文档

chat = [
    {"role": "system", "content": "You are good at using tools."},
    {"role": "user", "content": f"Problem: 计算 15! (15的阶乘) 的值\n\n{context_str}\n\nChoose an appropriate tool."}
]
```

**模型看到的完整 prompt**：
```
<|im_start|>system
You are good at using tools.<|im_end|>
<|im_start|>user
Problem: 计算 15! (15的阶乘) 的值

Doc 1: 阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。

Doc 2: 对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。

Doc 3: 在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。

Choose an appropriate tool.<|im_end|>
<|im_start|>assistant
```

#### Step 2: 模型生成

**模型输出**：
```
<think>
根据文档，我知道Python有math.factorial()函数，我应该写代码来计算15!
</think>

<tool_call>
{"name": "enhance_reasoning", "arguments": {"model": "reasoner-1"}}
</tool_call>
```

#### Step 3: 执行 enhance_reasoning 工具

**代码生成过程**：
```python
# 1. 构建 prompt 让 LLM 生成代码
code_gen_prompt = """Doc 1: 阶乘是基斯顿·卡曼...
Doc 2: 对于正整数n...
Doc 3: 在Python中可以使用...

Question: 计算 15! (15的阶乘) 的值

Instead of directly answering the question, please write additional python code
that will give intermediate results after execution. Wrap the code within ```python and ```.
The code should be self-contained with all the import and initialization."""

# 2. 调用 LLM 生成代码
code_response = llm_call(code_gen_prompt, model='o3')

# 输出
generated_code = """import math

# 计算 15 的阶乘
result = math.factorial(15)
print(f"15! = {result}")

# 验证：手动计算前几个
manual = 1
for i in range(1, 16):
    manual *= i
print(f"手动验证: {manual}")
"""

# 3. 在沙箱中执行代码
exec_result = subprocess.run(['python', 'code.py'], capture_output=True, text=True)
# 输出
exec_output = """15! = 1307674368000
手动验证: 1307674368000
"""
```

**工具返回**：
```python
result = {
    'generated_code': """import math

# 计算 15 的阶乘
result = math.factorial(15)
print(f"15! = {result}")

# 验证：手动计算前几个
manual = 1
for i in range(1, 16):
    manual *= i
print(f"手动验证: {manual}")""",
    'exec_result': """15! = 1307674368000
手动验证: 1307674368000""",
    'cost': 0.008,
    'latency': 3.2
}
```

#### Step 4: 更新上下文

**应用层状态**：
```python
retrieved_documents[0] = [doc1, doc2, doc3]  # 保持不变

code_snippets[0] = [  # 新增代码片段
    {
        'code': """import math

# 计算 15 的阶乘
result = math.factorial(15)
print(f"15! = {result}")

# 验证：手动计算前几个
manual = 1
for i in range(1, 16):
    manual *= i
print(f"手动验证: {manual}")""",
        'output': """15! = 1307674368000
手动验证: 1307674368000"""
    }
]

attempts[0] = []  # 保持不变
active_mask[0] = True
total_costs[0] = 0.002 + 0.008 = 0.010
```

---

### 第三轮：给出最终答案

#### Step 1: 构建 Prompt（包含所有历史）

**应用层上下文**（现在更丰富了）：
```python
retrieved_documents[0] = [doc1, doc2, doc3]
code_snippets[0] = [code1]  # 有代码和执行结果
attempts[0] = []
```

**提示层上下文**：
```python
# 格式化文档
doc_str = """Doc 1: 阶乘是基斯顿·卡曼...
Doc 2: 对于正整数n...
Doc 3: 在Python中可以使用...

"""

# 格式化代码片段
code_str = """```python
import math

# 计算 15 的阶乘
result = math.factorial(15)
print(f"15! = {result}")

# 验证：手动计算前几个
manual = 1
for i in range(1, 16):
    manual *= i
print(f"手动验证: {manual}")
```

```output
15! = 1307674368000
手动验证: 1307674368000
```

"""

context_str = doc_str + code_str

chat = [
    {"role": "system", "content": "You are good at using tools."},
    {"role": "user", "content": f"Problem: 计算 15! (15的阶乘) 的值\n\n{context_str}\n\nChoose an appropriate tool."}
]
```

**模型看到的完整 prompt**：
```
<|im_start|>system
You are good at using tools.<|im_end|>
<|im_start|>user
Problem: 计算 15! (15的阶乘) 的值

Doc 1: 阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。

Doc 2: 对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。

Doc 3: 在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。

```python
import math

# 计算 15 的阶乘
result = math.factorial(15)
print(f"15! = {result}")

# 验证：手动计算前几个
manual = 1
for i in range(1, 16):
    manual *= i
print(f"手动验证: {manual}")
```

```output
15! = 1307674368000
手动验证: 1307674368000
```

Choose an appropriate tool.<|im_end|>
<|im_start|>assistant
```

#### Step 2: 模型生成

**模型输出**：
```
<think>
根据代码执行的结果，我已经得到了15!的值，现在可以给出最终答案了
</think>

<tool_call>
{"name": "answer", "arguments": {"model": "answer-1"}}
</tool_call>
```

#### Step 3: 执行 answer 工具

**答案生成过程**：
```python
# 1. 构建 prompt
answer_prompt = """Doc 1: 阶乘是基斯顿·卡曼...
Doc 2: 对于正整数n...
Doc 3: 在Python中可以使用...

```python
import math
result = math.factorial(15)
print(f"15! = {result}")
...
```

```output
15! = 1307674368000
手动验证: 1307674368000
```

Question: 计算 15! (15的阶乘) 的值

Wrap the thinking process between <think> and </think> and wrap only the exact answer
within <answer> and </answer>."""

# 2. 调用 LLM 生成答案
answer_response = llm_call(answer_prompt, model='meta-llama')

# 输出
answer_full = """<think>
根据代码执行的结果，15的阶乘等于1307674368000。
这个结果已经通过两种方法验证：
1. 使用math.factorial(15)
2. 手动循环计算

两种方法得到相同的结果，说明答案是正确的。
</think>

<answer>
1307674368000
</answer>"""

# 3. 提取答案
pred = "1307674368000"

# 4. 评估正确性（假设标准答案是 "1307674368000"）
correctness = (pred == "1307674368000")  # True
```

**工具返回**：
```python
result = {
    'response': answer_full,
    'pred': '1307674368000',
    'correctness': True,
    'cost': 0.004,
    'latency': 1.8
}
```

#### Step 4: 更新上下文并终止

**应用层状态**：
```python
retrieved_documents[0] = [doc1, doc2, doc3]  # 保持不变
code_snippets[0] = [code1]                    # 保持不变

attempts[0] = [  # 新增答案尝试
    {
        'answer': '1307674368000',
        'model': 'answer-1'
    }
]

active_mask[0] = False  # 标记为完成（因为调用了 answer 工具且生成了有效答案）
total_costs[0] = 0.010 + 0.004 = 0.014
```

**终止条件满足**：
- ✅ 调用了 `answer` 工具
- ✅ 生成了有效答案（非空）
- ✅ 答案正确

---

### 最终状态总结

**应用层上下文（完整历史）**：
```python
retrieved_documents[0] = [
    "阶乘是基斯顿·卡曼（Christian Kramp）于1808年发明的运算符号。阶乘亦可以递归方式定义：0!=1，n!=(n-1)!×n。",
    "对于正整数n，n的阶乘定义为：n! = 1 × 2 × 3 × ... × n。例如：5! = 1 × 2 × 3 × 4 × 5 = 120。",
    "在Python中可以使用math.factorial()函数计算阶乘，或者使用循环实现。"
]

code_snippets[0] = [
    {
        'code': 'import math\nresult = math.factorial(15)\n...',
        'output': '15! = 1307674368000\n手动验证: 1307674368000'
    }
]

attempts[0] = [
    {
        'answer': '1307674368000',
        'model': 'answer-1'
    }
]
```

**张量层数据（用于训练）**：
```python
all_turn_input_ids = [
    round_1_input_ids,   # [1, 512] - 包含初始问题
    round_2_input_ids,   # [1, 768] - 包含问题 + 文档
    round_3_input_ids    # [1, 1024] - 包含问题 + 文档 + 代码
]

all_turn_responses = [
    round_1_response,    # <tool_call>{"name": "search", ...}</tool_call>
    round_2_response,    # <tool_call>{"name": "enhance_reasoning", ...}</tool_call>
    round_3_response     # <tool_call>{"name": "answer", ...}</tool_call>
]

all_turn_tools = [
    [("search", "search-1")],
    [("enhance_reasoning", "reasoner-1")],
    [("answer", "answer-1")]
]

all_turn_success = [False, False, True]
all_turn_costs = [0.002, 0.008, 0.004]
```

**轨迹可视化**：

```
Turn 0: [问题]
          ↓ 生成: search
Turn 1: [问题 + 文档]
          ↓ 生成: enhance_reasoning
Turn 2: [问题 + 文档 + 代码]
          ↓ 生成: answer
Turn 3: [终止] ✓ 正确答案
```

---

## 长度控制机制

随着轮次增加，上下文会不断膨胀。ToolOrchestra 使用**分级截断策略**来控制长度。

### 优先级金字塔

```
                    ┌──────────────┐
                    │   Problem    │  永远保留
                    │  (必须完整)   │
                    └──────────────┘
                           ↑
                  ┌────────────────────┐
                  │  Code & Output     │  优先级 1
                  │  (最新的推理过程)   │
                  └────────────────────┘
                           ↑
              ┌──────────────────────────────┐
              │      Attempts                │  优先级 2
              │    (答案尝试历史)              │
              └──────────────────────────────┘
                           ↑
          ┌────────────────────────────────────────┐
          │         Documents                      │  优先级 3
          │       (检索到的文档)                    │  最先被截断
          └────────────────────────────────────────┘
```

### 截断算法

**代码位置**：`generation_quick3.py:1112-1132`

```python
def build_context_with_truncation(
    tokenizer,
    problem,
    retrieved_documents,
    code_snippets,
    attempts,
    max_length=24000
):
    # Step 1: 格式化所有部分
    doc_str = format_documents(retrieved_documents)
    code_str = format_code_snippets(code_snippets)
    attempt_str = format_attempts(attempts)

    # Step 2: 从低优先级开始截断
    # 2.1 先截断 attempts 到 8000 tokens
    attempt_str_cut = cut_seq(tokenizer, attempt_str, l=8000)
    attempt_str = attempt_str_cut['string_after_cut']

    # 2.2 截断 code + attempts 到 16000 tokens
    code_attempt_str_cut = cut_seq(tokenizer, code_str + attempt_str, l=16000)
    code_attempt_str = code_attempt_str_cut['string_after_cut']
    code_attempt_len = code_attempt_str_cut['effective_length']

    # 2.3 根据剩余空间决定是否保留文档
    remaining = max_length - 2000  # 留2000给问题和指令

    if code_attempt_len < remaining:
        # 有空间，加入文档
        context_str_cut = cut_seq(
            tokenizer,
            doc_str + code_attempt_str,
            l=remaining
        )
        context_str = context_str_cut['string_after_cut']

        # 如果文档被部分截断，确保格式正确
        if len(doc_str) > 0 and not context_str.startswith('Doc '):
            context_str = 'Documents:\n' + context_str
    else:
        # 没空间，放弃文档
        context_str = code_attempt_str

    return context_str
```

### 截断示例

**场景**：经过5轮后，上下文非常长

**原始长度**：
```python
doc_str:      15000 tokens (3个文档)
code_str:     12000 tokens (2段代码 + 输出)
attempt_str:  10000 tokens (3次答案尝试)
total:        37000 tokens  # 超过预算 24000
```

**截断过程**：

```
Step 1: 截断 attempt_str 到 8000 tokens
  原始: 10000 tokens
  结果: 8000 tokens (保留最新的2次尝试)

Step 2: 截断 code_str + attempt_str 到 16000 tokens
  原始: 12000 + 8000 = 20000 tokens
  结果: 16000 tokens (保留最新的代码 + 最新的尝试)

Step 3: 决定文档空间
  剩余预算: 24000 - 2000 (问题) = 22000 tokens
  已使用: 16000 tokens
  文档空间: 22000 - 16000 = 6000 tokens

Step 4: 截断 doc_str + code_attempt_str 到 22000 tokens
  原始: 15000 + 16000 = 31000 tokens
  结果: 22000 tokens
    - doc_str: 6000 tokens (只保留最新的1-2个文档)
    - code_attempt_str: 16000 tokens (完整保留)
```

**最终结果**：
```python
context_str = """Doc 3: 在Python中可以使用math.factorial()函数...

```python
# 最新的代码
import math
result = math.factorial(15)
...
```

```output
15! = 1307674368000
```

Attempt2 answer by answer-math-1: 1307674368000
Attempt3 answer by answer-1: 1307674368000
"""

total_length: 22000 tokens < 24000 (预算内) ✓
```

---

### 对话历史的中间截断

对于 Function Call 任务，对话历史可能包含几十轮人机交互。

**函数**：`cut_middle_turns()` (`generation_quick3.py:108-130`)

**策略**：保留开头和结尾，删除中间

**示例**：

**原始对话**（10轮，每轮1000 tokens，共10000 tokens）：
```python
messages = [
    {"role": "user", "content": "帮我查询天气"},           # Turn 1
    {"role": "assistant", "content": "好的，请问哪个城市"},  # Turn 2
    {"role": "user", "content": "北京"},                   # Turn 3
    {"role": "assistant", "content": "正在查询..."},       # Turn 4
    {"role": "user", "content": "顺便查一下上海"},          # Turn 5
    {"role": "assistant", "content": "好的"},             # Turn 6
    {"role": "user", "content": "还要深圳"},              # Turn 7
    {"role": "assistant", "content": "稍等"},             # Turn 8
    {"role": "user", "content": "结果呢"},                # Turn 9
    {"role": "assistant", "content": "北京晴..."}         # Turn 10
]
```

**截断到 4000 tokens**：
```python
cut_messages = cut_middle_turns(tokenizer, messages, max_length=4000)

# 结果 (保留前2000 + 后2000)
cut_messages = [
    {"role": "user", "content": "帮我查询天气"},           # Turn 1 - 保留
    {"role": "assistant", "content": "好的，请问哪个城市"},  # Turn 2 - 保留
    # ... Turn 3-8 删除 ...
    {"role": "user", "content": "结果呢"},                # Turn 9 - 保留
    {"role": "assistant", "content": "北京晴..."}         # Turn 10 - 保留
]
```

**可视化**：
```
原始:
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ T1 │ T2 │ T3 │ T4 │ T5 │ T6 │ T7 │ T8 │ T9 │T10 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 1000 1000 1000 1000 1000 1000 1000 1000 1000 1000  (tokens)

截断后:
┌────┬────┐       删除中间       ┌────┬────┐
│ T1 │ T2 │ ................... │ T9 │T10 │
└────┴────┘                      └────┴────┘
 1000 1000                        1000 1000
 └─ 前2000 ─┘                    └─ 后2000 ─┘
```

**为什么这样做？**
1. **开头重要**：包含任务描述、初始指令、系统提示
2. **结尾重要**：包含最新状态、最新用户输入、最新上下文
3. **中间相对不重要**：历史对话的过渡部分，信息密度低

---

## 上下文传递路径

### 完整数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    Step N 结束                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ 工具执行结果
                         ▼
        ┌────────────────────────────────────┐
        │ 更新应用层上下文                    │
        │                                    │
        │ retrieved_documents[i] += new_docs │
        │ code_snippets[i] += new_code       │
        │ attempts[i] += new_attempt         │
        └────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Step N+1 开始                             │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 格式化应用层上下文                  │
        │                                    │
        │ doc_str = format_documents(...)    │
        │ code_str = format_code(...)        │
        │ attempt_str = format_attempts(...) │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 截断到 token 预算                   │
        │                                    │
        │ context_str = cut_seq(             │
        │     doc_str + code_str + ...,      │
        │     l=24000                        │
        │ )                                  │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 构建 chat 消息                      │
        │                                    │
        │ chat = [                           │
        │   {"role": "system", ...},         │
        │   {"role": "user",                 │
        │    "content": f"Problem: {problem} │
        │               \n\n{context_str}"}  │
        │ ]                                  │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 应用 Chat Template                  │
        │                                    │
        │ prompt = tokenizer.apply_chat_     │
        │          template(chat, tools=...) │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ Tokenize                           │
        │                                    │
        │ input_ids = tokenizer(prompt)      │
        │ attention_mask = ...               │
        │ position_ids = ...                 │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 左侧 Padding                        │
        │                                    │
        │ padded_input_ids = cat([           │
        │     padding,                       │
        │     input_ids                      │
        │ ])                                 │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 模型生成                            │
        │                                    │
        │ gen_output = actor_rollout_wg.     │
        │              generate_sequences()  │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 后处理 & 解析                       │
        │                                    │
        │ responses_str = tokenizer.decode() │
        │ tool_calls = postprocess_...()     │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 执行工具                            │
        │                                    │
        │ results = execute_predictions()    │
        └────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │ 保存训练数据                        │
        │                                    │
        │ all_turn_input_ids.append(...)     │
        │ all_turn_responses.append(...)     │
        │ all_turn_tools.append(...)         │
        └────────────────────────────────────┘
                         │
                         │ 回到顶部 (Step N 结束)
                         ▼
```

---

## 两种任务类型对比

### QA 任务

**上下文管理**：完全在内存中

**示例**：
```python
# 初始化
retrieved_documents[0] = []
code_snippets[0] = []
attempts[0] = []

# 第一轮：搜索
retrieved_documents[0] = [doc1, doc2]

# 第二轮：生成代码
code_snippets[0] = [{"code": "...", "output": "..."}]

# 第三轮：答案
attempts[0] = [{"answer": "42", "model": "answer-1"}]

# 所有上下文都在内存中，可以随时访问
```

**优点**：
- ✅ 简单、可控
- ✅ 容易调试和重现
- ✅ 不依赖外部系统

**缺点**：
- ❌ 工具调用是模拟的
- ❌ 无法真正与外部 API 交互

---

### Function Call 任务

**上下文管理**：通过文件系统与外部环境交互

**示例**：

```python
# 目录结构
/tmp/transfer/{example_id}_{repeat_id}/
├── task.json              # 任务描述
├── input_0.json           # 第1轮输入
├── output_0.json          # 第1轮输出
├── input_1.json           # 第2轮输入
├── output_1.json          # 第2轮输出
├── ...
├── done                   # 完成信号
└── output/                # 最终结果
    └── result.json
```

**交互流程**：

```
训练进程 (ToolOrchestra)          外部进程 (环境)
      │                              │
      ├──── 启动外部进程 ─────────────>│
      │                              │
      │<───── 写入 input_0.json ──────┤
      │     (包含对话历史 + 工具)       │
      │                              │
      ├─ 读取 input_0.json           │
      ├─ 模型生成 tool_call           │
      ├──── 写入 output_0.json ──────>│
      │                              │
      │                              ├─ 执行工具调用
      │                              ├─ 更新对话历史
      │<───── 写入 input_1.json ──────┤
      │                              │
      ├─ 读取 input_1.json           │
      ├─ 模型生成 tool_call           │
      ├──── 写入 output_1.json ──────>│
      │                              │
      │                              ├─ 执行工具调用
      │                              ├─ 任务完成
      │<───── 写入 done ──────────────┤
      │                              │
      ├─ 检测到 done                 │
      ├─ 标记样本完成                 │
      │                              │
```

**input_N.json 格式**：
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "查询北京的天气"},
    {"role": "assistant", "content": "<tool_call>{...}</tool_call>"},
    {"role": "user", "content": "北京今天晴天，气温25°C。还需要什么帮助？"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_weather",
        "description": "查询天气信息",
        "parameters": {...}
      }
    }
  ],
  "original_messages": [...],  # 未截断的完整历史
  "original_tools": [...]       # 所有可用工具
}
```

**优点**：
- ✅ 可以真正调用外部 API
- ✅ 更接近真实应用场景
- ✅ 可以与任意外部系统集成

**缺点**：
- ❌ 依赖外部进程（需要处理超时、错误）
- ❌ 调试困难（需要检查文件系统）
- ❌ 不易重现（外部状态可能变化）

---

## 关键技巧与最佳实践

### 技巧 1：文档去重与排序

**问题**：多轮搜索可能返回重复的文档

**解决方案**：`merge_documents()` 函数

**实现** (`generation_quick3.py:58-78`)：
```python
def merge_documents(main_list, sub_list):
    """
    智能合并文档列表：
    1. 交错插入新旧文档（新文档优先）
    2. 自动去重
    3. 保持相对顺序
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
        # 添加新文档（如果不存在）
        if sub_list[idx_sub] not in merged_list:
            merged_list.append(sub_list[idx_sub])

        # 添加对应的旧文档
        for iter_idx in range(idx_main, idx_main + multiple):
            if main_list[iter_idx] not in merged_list:
                merged_list.append(main_list[iter_idx])

        idx_main += multiple
        idx_sub += 1

    # 添加剩余的旧文档
    merged_list += main_list[multiple * len(sub_list):]

    return merged_list
```

**示例**：
```python
main_list = ["Doc A", "Doc B", "Doc C", "Doc D", "Doc E", "Doc F"]
sub_list = ["Doc X", "Doc B", "Doc Y"]  # Doc B 重复

result = merge_documents(main_list, sub_list)
# 结果: ["Doc X", "Doc A", "Doc B", "Doc C", "Doc Y", "Doc D", "Doc E", "Doc F"]
#
# 策略:
# - Doc X (新) → Doc A, Doc B (旧, 2个)
# - Doc B (重复, 跳过) → Doc C, Doc D (旧, 2个)
# - Doc Y (新) → Doc E, Doc F (旧, 2个)
#
# 比例: 每1个新文档后面跟2个旧文档 (6/3=2)
```

---

### 技巧 2：代码片段累积（不去重）

**原因**：不同轮次的代码可能相关但不相同

**示例**：
```python
# 第一轮：初步探索
code_snippets[0] = [
    {
        'code': "import numpy as np\nx = np.array([1,2,3])\nprint(x.mean())",
        'output': "2.0"
    }
]

# 第二轮：进一步计算
code_snippets[0] += [
    {
        'code': "import numpy as np\nx = np.array([1,2,3])\nprint(x.std())",
        'output': "0.816496580927726"
    }
]

# 构建 prompt 时，两段代码都显示
# 这样模型可以看到完整的推理链条
```

---

### 技巧 3：答案尝试的历史记录

**目的**：让模型"从错误中学习"

**示例**：
```python
# 第一次尝试（可能错误）
attempts[0] = [
    {"answer": "41", "model": "answer-math-1"}
]

# 构建下一轮 prompt 时，模型会看到:
# "Attempt1 answer by answer-math-1: 41"
# 模型可能思考：这个答案好像不对...

# 第二次尝试（修正）
attempts[0] += [
    {"answer": "42", "model": "answer-1"}
]

# 现在模型看到:
# "Attempt1 answer by answer-math-1: 41"
# "Attempt2 answer by answer-1: 42"
# 模型可以对比两个答案，做出更好的判断
```

---

### 技巧 4：Tensor 的高效拼接

**问题**：多轮中需要频繁拼接 tensor

**解决方案**：使用 `TensorHelper` 类

**示例**：
```python
# 不好的做法：手动处理 padding
# ❌ 容易出错，代码冗长
input_ids = torch.cat([prompt_ids, response_ids], dim=1)
# 还需要手动处理 padding、attention_mask、position_ids...

# 好的做法：使用 TensorHelper
# ✅ 自动处理所有细节
tensor_fn = TensorHelper(config)

# 拼接并自动处理 padding
concatenated = tensor_fn.concatenate_with_padding(
    [prompt_ids, response_ids, next_obs_ids],
    pad_to_left=True
)

# 自动创建 attention_mask 和 position_ids
attention_mask = tensor_fn.create_attention_mask(concatenated)
position_ids = tensor_fn.create_position_ids(attention_mask)
```

---

### 技巧 5：Active Mask 管理

**目的**：高效处理不同样本的完成时间

**示例**：
```python
# 初始化：所有样本都活跃
active_mask = torch.ones(batch_size, dtype=torch.bool)
# [True, True, True, True]

# 第一轮结束：样本 2 完成了
dones = [False, False, True, False]
curr_active_mask = torch.tensor([not done for done in dones])
active_mask = active_mask * curr_active_mask
# [True, True, False, True]

# 第二轮：只对活跃样本生成
rollings_active = DataProto.from_dict({
    k: v[active_mask] for k, v in rollings.batch.items()
})
# 现在 batch_size=3（跳过样本 2）

# 第二轮结束：样本 0 也完成了
dones = [True, False, False]  # 相对于活跃样本的索引
curr_active_mask = torch.tensor([not done for done in dones])
# 更新时需要映射回原始索引
active_indices = torch.where(active_mask)[0]  # [0, 1, 3]
active_mask[active_indices] = active_mask[active_indices] * curr_active_mask
# [False, True, False, True]

# 继续迭代，直到所有样本完成
```

---

### 技巧 6：GPU Padding 对齐

**问题**：分布式训练要求每个 GPU 的 batch_size 相同

**解决方案**：用第一个样本 padding

**实现** (`generation_quick3.py:945-994`)：
```python
def _generate_with_gpu_padding(self, active_batch):
    num_gpus = self.config.num_gpus  # 例如: 4
    batch_size = active_batch.batch['input_ids'].shape[0]  # 例如: 10

    remainder = batch_size % num_gpus  # 10 % 4 = 2

    if remainder == 0:
        # 刚好整除，直接生成
        return self.actor_rollout_wg.generate_sequences(active_batch)

    # 需要 padding
    padding_size = num_gpus - remainder  # 4 - 2 = 2

    padded_batch = {}
    for k, v in active_batch.batch.items():
        # 用第一个样本 padding
        pad_sequence = v[0:1].repeat(padding_size, *[1] * (len(v.shape) - 1))
        padded_batch[k] = torch.cat([v, pad_sequence], dim=0)

    # 现在 batch_size = 10 + 2 = 12 (能被4整除)
    padded_active_batch = DataProto.from_dict(padded_batch)

    # 生成
    padded_output = self.actor_rollout_wg.generate_sequences(padded_active_batch)

    # 移除 padding
    trimmed_batch = {
        k: v[:-padding_size] for k, v in padded_output.batch.items()
    }

    padded_output.batch = trimmed_batch
    return padded_output
```

**可视化**：
```
原始 batch (10个样本):
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

Padding 后 (12个样本):
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 0*│ 0*│
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
                                          └─ padding ─┘

分配到 4个 GPU:
GPU 0: [0, 1, 2]
GPU 1: [3, 4, 5]
GPU 2: [6, 7, 8]
GPU 3: [9, 0*, 0*]  ← GPU 3 也有3个样本

生成后，移除 padding:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

---

## 总结

ToolOrchestra 的上下文维护机制是一个**分层、累积、动态截断**的精巧系统：

### 三大特点

1. **分层设计**
   - 应用层：人类可读的完整历史
   - 提示层：模型可见的格式化文本
   - 张量层：计算图中的高效表示

2. **累积策略**
   - 只增不减，像滚雪球
   - 每轮在前面的基础上继续
   - 完整保留推理链条

3. **动态截断**
   - 基于优先级分级截断
   - Token 级精确控制
   - 自适应分配空间

### 关键优势

- ✅ **完整性**: 应用层保留所有历史
- ✅ **可控性**: 提示层智能截断
- ✅ **高效性**: 张量层优化计算
- ✅ **灵活性**: 支持两种任务类型
- ✅ **扩展性**: 易于添加新工具

### 设计哲学

> 在应用层维护完整状态，在提示层进行截断和格式化。
>
> 既保证了信息的完整性，又满足了模型的长度限制。

---

**文档版本**: 1.0
**最后更新**: 2026-01-08
**作者**: Claude Code (基于代码深度分析)
**相关文档**: `toolorchestra_multiturn_implementation.md`
