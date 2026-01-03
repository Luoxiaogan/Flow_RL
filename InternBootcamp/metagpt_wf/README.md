# MetaGPT Workflow Executor

这是一个改进版的工作流执行器，将原来的system_prompt生成改为MetaGPT workflow模板生成，并执行MetaGPT风格的工作流。

## 主要改进

### 1. 从System Prompt到MetaGPT Workflow Template
- **原版本**: 上游模型生成system_prompt，下游模型基于system_prompt解决问题
- **新版本**: 上游模型生成MetaGPT workflow模板，下游模型执行MetaGPT workflow

### 2. MetaGPT Workflow结构
生成的workflow遵循MetaGPT的标准结构：
```python
class Workflow:
    def __init__(self, config, problem):
        self.problem = problem
        self.agent = create(config)
        # 初始化operators
        self.custom = operator.Custom(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        
    async def run_workflow(self):
        # 工作流逻辑
        solution = await self.custom(instruction="...")
        return solution
```

### 3. 支持的Operators
- **Custom**: 基于自定义指令生成解答
- **Review**: 审查和改进先前的解答  
- **Programmer**: 编写和执行Python代码
- **ScEnsemble**: 从多个解答中选择最佳方案

## 文件结构
```
metagpt_wf/
├── metagpt_workflow_executor.py  # 主执行脚本
├── README.md                     # 说明文档
└── metagpt_workflow_results.jsonl  # 输出结果（运行后生成）
```

## 使用方法

1. 确保已安装依赖：
```bash
pip install openai asyncio
```

2. 运行脚本：
```bash
cd Flow_RL/InternBootcamp/metagpt_wf
python metagpt_workflow_executor.py
```

3. 结果会保存在 `metagpt_workflow_results.jsonl` 中

## 输出格式

每个任务的结果包含：
- `task_id`: 任务ID
- `task_name`: 任务名称  
- `task_description`: 任务描述
- `workflow_template`: 生成的MetaGPT workflow模板
- `test_results`: 测试用例结果列表
- `accuracy`: 准确率
- `correct_count`: 正确数量
- `total_count`: 总测试数量

## 设计特点

1. **简洁实现**: 相比于完整的workflow_orchestrator_v5.py，这个实现更加简洁，专注于核心功能
2. **Mock Operators**: 使用模拟的operators来执行workflow，避免复杂的依赖
3. **异步执行**: 支持并行处理多个任务和测试用例
4. **错误容错**: 当workflow执行失败时，回退到直接LLM调用

## 与原版对比

| 特性 | 原版 (system_prompt) | 新版 (MetaGPT workflow) |
|------|---------------------|------------------------|
| 上游输出 | System prompt文本 | MetaGPT workflow类代码 |
| 下游执行 | 基于prompt的对话 | 执行workflow的run_workflow方法 |
| 灵活性 | 固定的prompt-response模式 | 可组合的operator流水线 |
| 扩展性 | 限制于prompt工程 | 可添加新的operators |
| 复用性 | prompt特定于任务 | workflow可跨任务复用 | 