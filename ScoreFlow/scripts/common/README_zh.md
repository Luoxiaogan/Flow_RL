# ScoreFlow 通用算子文档

## 概述

ScoreFlow 通用算子提供了一套可重用的原子操作，用于构建复杂的 AI 工作流。这些算子采用模块化架构设计，能够灵活组合成高级问题求解管道。

## 架构设计

### 核心组件

1. **operator.py**: 包含算子的具体实现
2. **operator_an.py**: 定义用于结构化输入输出验证的 Pydantic 模型
3. **conditions.py**: 包含算子执行的提示词和条件配置

### 设计原则

- **模块化**: 每个算子执行单一、明确的功能
- **类型安全**: Pydantic 模型确保结构化和验证的输入输出
- **异步执行**: 所有算子支持异步操作
- **错误处理**: 具备重试机制的健壮错误恢复
- **安全第一**: 代码执行在沙箱环境中，基于 AST 的安全检查

## 可用算子列表

### 1. Generate（生成器）
**用途**: 根据指令和上下文创建新的非结构化文本

**类**: `Generate(Operator)`

**Pydantic 模型**: `GenerateOp`

**使用示例**:
```python
gen = Generate(llm, problem_text)
response = await gen(instruction="编写解决方案", context="之前的分析")
```

**核心特性**:
- 灵活的文本生成
- 上下文感知响应
- 自动整合问题文本

---

### 2. Revise（修订器）
**用途**: 根据特定指令审查和改进现有文本

**类**: `Revise(Operator)`

**Pydantic 模型**: `ReviseOp`

**使用示例**:
```python
rev = Revise(llm, problem_text)
improved_text = await rev(instruction="使语气更正式", context="草稿文本")
```

**核心特性**:
- 结构化 XML 输出，包含推理过程
- 在提升质量的同时保留原始含义
- 包含逐步修订过程

---

### 3. Summarize（摘要器）
**用途**: 将长文本压缩为关键要点

**类**: `Summarize(Operator)`

**Pydantic 模型**: 复用 `GenerateOp`

**使用示例**:
```python
summ = Summarize(llm, problem_text)
summary = await summ(instruction="聚焦主要论点", context="长文本")
```

**核心特性**:
- 提取相关信息
- 问题感知的摘要生成
- 通过指令自定义关注点

---

### 4. Ensemble（集成器）
**用途**: 根据策略指令从多个选项中选择或综合

**类**: `Ensemble(Operator)`

**Pydantic 模型**: `EnsembleOp`

**使用示例**:
```python
ens = Ensemble(llm, problem_text)
result = await ens(instruction="选择最准确的", contexts_list=[选项1, 选项2, 选项3])
```

**核心特性**:
- 多选项评估
- 可选择现有方案或综合新方案
- 透明的决策过程

---

### 5. Programmer（编程器）
**用途**: 生成并执行 Python 代码来解决问题

**类**: `Programmer(Operator)`

**Pydantic 模型**: `CodeGenerateOp`

**使用示例**:
```python
prog = Programmer(llm, problem_text)
result = await prog(instruction="用数学方法求解", context="分析", max_retries=3)
```

**核心特性**:
- 带重试机制的自动代码生成
- 沙箱执行环境
- 基于 AST 的安全检查
- 进程级隔离和超时保护
- 禁止危险导入（os、sys、subprocess 等）

**安全限制**:
- 禁止系统操作
- 禁止网络访问
- 禁止文件 I/O
- 禁止 GUI/绘图库
- 必须定义 `solve()` 函数

---

### 6. Decompose（分解器）
**用途**: 将复杂问题分解为可管理的子问题

**类**: `Decompose(Operator)`

**Pydantic 模型**: `DecomposeOp`

**使用示例**:
```python
dec = Decompose(llm, problem_text)
subproblems = await dec(instruction="分解为逻辑步骤", context="复杂问题")
```

**核心特性**:
- 层次化问题分解
- 子问题间的依赖追踪
- 返回带 ID 和依赖关系的结构化列表

**输出格式**:
```json
[
  {"id": "sub1", "description": "第一步", "dependencies": ""},
  {"id": "sub2", "description": "第二步", "dependencies": "sub1"}
]
```

---

### 7. Verifier（验证器）
**用途**: 使用 IMO 级别标准严格验证解答正确性

**类**: `Verifier(Operator)`

**Pydantic 模型**: `VerifierOp`

**使用示例**:
```python
ver = Verifier(llm, problem_text)
verification = await ver(instruction="检查数学严谨性", context="解答文本")
```

**核心特性**:
- IMO（国际数学奥林匹克）评分标准
- 识别关键错误和论证缺陷
- 详细的逐步验证日志
- 不尝试修复错误（纯验证）

**错误分类**:
- **关键错误（Critical Error）**: 破坏逻辑链（如计算错误、逻辑谬误）
- **论证缺陷（Justification Gap）**: 缺乏严谨性但可能正确（如缺少证明、含糊解释）

---

### 8. Refiner（改进器）
**用途**: 基于验证反馈改进解答

**类**: `Refiner(Operator)`

**Pydantic 模型**: `RefinerOp`

**使用示例**:
```python
ref = Refiner(llm, problem_text)
improved = await ref(
    instruction="解决所有问题",
    context="原始解答",
    verification_feedback="验证结果"
)
```

**核心特性**:
- 解决验证中发现的所有问题
- 维持数学严谨性
- 提供完整的改进解答
- 包含改进分析

---

## 基础算子类

所有算子都继承自基础 `Operator` 类：

```python
class Operator:
    def __init__(self, llm, problem_text: str = ""):
        self.llm = llm
        self.problem_text = str(problem_text)
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
```

### 通用方法

- `_fill_node()`: 通用的 LLM 调用和 Pydantic 模型填充
- 支持 XML 和单字段填充模式
- 自动错误处理和日志记录

## Pydantic 模型

每个算子都有对应的 Pydantic 模型进行类型验证：

| 算子 | 模型 | 关键字段 |
|------|------|----------|
| Generate | GenerateOp | response |
| Revise | ReviseOp | think, revised_context |
| Ensemble | EnsembleOp | think, result |
| Programmer | CodeGenerateOp | think, code |
| Decompose | DecomposeOp | think, subproblems |
| Verifier | VerifierOp | verdict, findings, verification_log |
| Refiner | RefinerOp | analysis, refined_solution |

## 执行模式

### 静默模式
设置环境变量以抑制算子执行日志：
```bash
export SCOREFLOW_SILENT=true
```

### XML 填充模式
用于具有多个字段的结构化输出：
```python
response = await self._fill_node(OpClass, prompt, mode="xml_fill")
```

### 单字段填充模式
用于简单的单字段响应：
```python
response = await self._fill_node(OpClass, prompt, mode="single_fill")
```

## 安全特性

### 代码执行安全

`Programmer` 算子包含多层安全保护：

1. **AST 分析**: 执行前的代码分析
2. **导入限制**: 阻止危险库
3. **进程隔离**: 在独立进程中运行
4. **超时保护**: 可配置的执行超时
5. **命名空间隔离**: 干净的执行环境

### 禁止的导入
- 系统操作: os, sys, subprocess, multiprocessing
- GUI/绘图: matplotlib, seaborn, plotly, tkinter
- 网络操作: 直接网络访问被阻止

## 最佳实践

1. **始终提供 problem_text**: 确保上下文感知操作
2. **使用合适的算子**: 为每个任务选择正确的工具
3. **链式组合算子**: 组合形成复杂工作流
4. **优雅处理错误**: 所有算子返回结构化错误
5. **利用重试机制**: 特别是对于 Programmer 算子
6. **先验证后改进**: 使用 Verifier → Refiner 管道提升质量

## 与 MetaGPT 集成

所有算子都与 MetaGPT 的 ActionNode 框架兼容：
- 使用 MetaGPT 的 LLM 接口
- 支持异步执行
- 集成到 MetaGPT 的工作流系统

## 工作流示例

```python
# 复杂问题求解管道
decomposer = Decompose(llm, problem_text)
subproblems = await decomposer(instruction="系统化分解")

solutions = []
for subproblem in subproblems:
    generator = Generate(llm, problem_text)
    solution = await generator(instruction=f"求解: {subproblem['description']}")
    
    verifier = Verifier(llm, problem_text)
    verification = await verifier(context=solution)
    
    if "关键错误" in verification["verdict"].lower():
        refiner = Refiner(llm, problem_text)
        solution = await refiner(
            context=solution,
            verification_feedback=str(verification)
        )
    
    solutions.append(solution)

ensemble = Ensemble(llm, problem_text)
final_answer = await ensemble(
    instruction="综合完整解答",
    contexts_list=solutions
)
```

## 性能考虑

- **异步操作**: 所有算子都是异步优先
- **进程池**: Programmer 使用 ProcessPoolExecutor 进行隔离
- **超时控制**: 可配置的代码执行超时
- **重试逻辑**: 内置重试机制确保健壮性

## 未来增强

- 为特定领域添加更多算子
- 增强验证策略
- 改进代码生成能力
- 扩展安全特性
- 性能优化