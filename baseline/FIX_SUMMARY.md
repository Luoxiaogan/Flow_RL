# 🔧 Workflow模板修复总结

## 问题诊断
错误信息：`Workflow.__init__() got an unexpected keyword argument 'config'`

### 根本原因
- Workflow类的初始化参数不正确
- 原模板使用`__init__(self, llm)`，但reward_server期望`__init__(self, config, problem)`

## 修复内容

### 1. 正确的Workflow格式
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        # 初始化需要的operator
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        # 实现workflow逻辑
        ...
```

### 2. 关键修改点

#### ✅ 初始化参数
- ❌ 错误：`__init__(self, llm)`
- ✅ 正确：`__init__(self, config, problem)`

#### ✅ 运行方法
- ❌ 错误：`async def run(self, problem)`
- ✅ 正确：`async def run_workflow(self)`

#### ✅ Operator初始化
- ❌ 错误：`Generate(llm=self.llm, problem=problem)`
- ✅ 正确：`operator.Generate(self.llm, self.problem_text)`

#### ✅ 代码包装
- 必须用\`\`\`python和\`\`\`包裹整个workflow代码
- 这是reward_server解析代码的必要格式

### 3. 已更新的文件
- `workflow_templates.py` - CoT和Self-consistency模板
- `minimal_test.py` - 极简测试脚本

## CoT Workflow实现

```python
async def run_workflow(self):
    # Step 1: 使用CoT prompt引导逐步思考
    cot_instruction = (
        "Let's solve this problem step by step. "
        "First, carefully read and understand what the problem is asking. "
        "Then, break down the problem into logical steps. "
        "Work through each step methodically, showing your reasoning. "
        "Finally, arrive at the answer and clearly state it."
    )
    solution = await self.generate(cot_instruction, "")

    # Step 2: 使用ensemble提取最终答案
    ensemble_instruction = (
        "Review the solution above and extract the final answer. "
        "Make sure the answer is clear and directly addresses what was asked."
    )
    final_answer = await self.ensemble(ensemble_instruction, [solution])

    return final_answer
```

## Self-Consistency Workflow实现

```python
async def run_workflow(self):
    solutions = []

    # 生成3个不同方法的解决方案
    # 1. 数学/代数方法
    solution1 = await self.generate(instruction1, "")
    solutions.append(solution1)

    # 2. 逻辑推理方法
    solution2 = await self.generate(instruction2, "")
    solutions.append(solution2)

    # 3. 分步解析方法
    solution3 = await self.generate(instruction3, "")
    solutions.append(solution3)

    # 使用ensemble选择最佳答案
    final_answer = await self.ensemble(ensemble_instruction, solutions)

    return final_answer
```

## 测试方法

### 极简测试（单样例）
```bash
python minimal_test.py
```
- 只测试1个GSM8K样例
- 快速验证系统是否能运行

### 快速测试（5个样例）
```bash
python quick_test.py
```
- 测试GSM8K的5个样例
- 验证基本功能

### 完整测试（50个样例/benchmark）
```bash
python test_workflows.py
```
- 测试所有3个benchmark
- 每个benchmark 50个样例

## 注意事项

1. **确保Reward Server运行**
   ```bash
   cd ../New_evaluation_and_RL/reward_server
   python scoreflow_reward_server.py --port 7788
   ```

2. **Workflow代码格式要求**
   - 必须包含```python标记
   - 严格遵循__init__和run_workflow的签名
   - 只使用Generate和Ensemble算子

3. **常见错误**
   - 如果仍然报config错误，检查workflow代码是否被正确包装
   - 如果timeout，增加请求超时时间或减少样例数

## 总结

通过修正Workflow类的初始化参数和方法签名，系统现在应该能够正常运行。主要修改是将原本面向简单LLM调用的接口改为符合MetaGPT/ScoreFlow框架的标准格式。