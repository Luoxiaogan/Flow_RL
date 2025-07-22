# InternBootcamp Benchmark集成说明文档

## 概述

InternBootcamp是一个包含数百种不同任务类型的复杂训练场系统，与ScoreFlow中其他benchmark（如GSM8K、MBPP等）有着显著的结构差异。本文档详细说明了InternBootcamp的特殊性以及集成方案的设计思路。

## 核心差异

### 1. 任务多样性 vs 单一任务类型

**传统Benchmark（如GSM8K）**：
- 单一任务类型：数学应用题
- 固定的输入输出格式
- 统一的验证逻辑

**InternBootcamp**：
- 数百种不同的任务类型：数独、扫雷、Kakuro、算法问题、图论等
- 每种任务有独特的输入格式和验证逻辑
- 动态的任务集合，可能随时增加新任务类型

### 2. 验证机制的差异

**传统Benchmark**：
- 简单的答案比对（如数值比较、字符串匹配）
- 验证逻辑写在handler中

**InternBootcamp**：
- 每个任务类型有独立的验证器（bootcamp类）
- 复杂的验证逻辑（如数独的行列区域约束、扫雷的逻辑推理）
- 验证器已经在InternBootcamp系统中实现

### 3. 数据结构的差异

**传统Benchmark数据格式**：
```json
{
  "question": "John has 5 apples...",
  "answer": "15"
}
```

**InternBootcamp数据格式**：
```json
{
  "id": 0,
  "task_name": "sudoku",
  "task_type": "logic_puzzle", 
  "task_description": "详细的任务说明...",
  "test_cases": [
    {
      "case": {
        "puzzle": [[0, 4, 2, ...], ...],
        "size": 9,
        "region_rows": 3,
        "region_cols": 3
      },
      "prompt": "实际给模型的提示..."
    }
  ]
}
```

## 集成设计方案

### 1. 通用Handler设计

我们创建了一个**通用Handler**，而不是为每种任务类型创建独立的handler：

```python
class InternBootcampHandler(BenchmarkHandler):
    def _load_bootcamp_class(self, task_name: str):
        """动态加载对应的bootcamp类"""
        module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
        module = importlib.import_module(module_path)
        return getattr(module, f"{task_name.capitalize()}bootcamp")
```

**优势**：
- 自动支持所有现有和未来的任务类型
- 无需手动维护任务类型列表
- 利用Python的动态特性实现扩展性

### 2. 统一接口封装

所有InternBootcamp任务都实现了`Basebootcamp`接口：

```python
class Basebootcamp:
    @staticmethod
    def prompt_func(question_ori) -> str:
        """将任务数据转换为提示"""
        
    @staticmethod
    def extract_output(output):
        """从模型输出中提取答案"""
        
    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        """验证答案正确性"""
        
    @classmethod
    def verify_score(cls, model_output, identity, ...) -> float:
        """计算得分"""
```

我们的集成方案直接调用这些接口，无需重新实现验证逻辑。

### 3. 工作流生成策略

由于任务类型众多，我们设计了通用的操作符：

```python
# 通用操作符，适用于所有任务类型
- TaskAnalyzer      # 分析任务类型和要求
- StrategyPlanner   # 制定解题策略
- ProblemSolver     # 执行解题逻辑
- FormatExtractor   # 提取格式化答案
- SolutionValidator # 验证解决方案
```

这些操作符可以根据具体任务动态调整行为，而不是为每种任务创建专门的操作符。

## 使用方法

### 1. 数据准备

InternBootcamp数据集位于：
```
InternBootcamp/workflow_test_v2/bootcamp_dataset.jsonl
```

每行是一个JSON对象，包含任务信息和测试用例。

### 2. 运行工作流生成

```bash
cd Test_FILE/
python workflow_generator.py \
    --benchmark internbootcamp \
    --num_workflows 100 \
    --api_model "your-model"
```

### 3. 执行和验证

```bash
python workflow_executor.py \
    --benchmark internbootcamp \
    --workspace_dir "./workspace_internbootcamp"
```

系统会：
1. 加载生成的工作流
2. 对每个测试用例执行工作流
3. 使用对应的bootcamp类验证结果
4. 记录成功的工作流

### 4. 查看结果

成功的工作流会保存在：
```
training_data/internbootcamp_successful_workflows.jsonl
```

## 技术细节

### 动态类加载机制

```python
# 根据task_name动态加载验证器
def judge(self, model_output, ground_truth_data):
    task_name = ground_truth_data.get('task_name')
    bootcamp_class = self._load_bootcamp_class(task_name)
    
    # 使用bootcamp的验证方法
    score = bootcamp_class.verify_score(
        model_output=str(model_output),
        identity=case_data,
        format_score=0.1
    )
    
    return score >= 0.9  # 阈值可调
```

### 错误处理

- 如果某个bootcamp类加载失败，会记录错误但不会中断整个流程
- 每个测试用例独立验证，一个失败不影响其他
- 详细的错误日志帮助调试

### 性能优化

- 使用缓存避免重复加载bootcamp类
- 支持并发执行多个工作流
- 批量处理测试用例

## 扩展性

### 添加新任务类型

1. 在InternBootcamp中实现新的bootcamp类
2. 确保实现了`Basebootcamp`接口
3. 无需修改ScoreFlow集成代码，自动支持

### 自定义验证逻辑

如果需要特殊的验证逻辑，可以在handler中添加特殊处理：

```python
if task_name == "special_task":
    # 特殊处理逻辑
    pass
else:
    # 通用处理逻辑
    pass
```

## 常见问题

### Q: 为什么不像其他benchmark一样为每种任务创建独立的handler？

A: InternBootcamp包含数百种任务类型，为每种创建handler会导致：
- 大量重复代码
- 难以维护
- 无法自动支持新任务类型

通用handler通过动态加载机制，实现了"一次编写，处处运行"。

### Q: 如何调试特定任务类型的问题？

A: 可以通过以下方式调试：
1. 查看日志中的错误信息
2. 单独测试bootcamp类的验证逻辑
3. 使用小批量数据测试特定任务类型

### Q: 性能是否会受影响？

A: 动态加载有轻微的性能开销，但通过缓存机制已经最小化。实际使用中，验证逻辑的执行时间远大于类加载时间。

## 总结

InternBootcamp的集成展示了ScoreFlow系统的灵活性和扩展性。通过巧妙的设计，我们用一套通用代码支持了数百种不同的任务类型，这种方法可以为未来集成其他复杂benchmark提供参考。

关键成功因素：
1. **统一接口**：利用InternBootcamp已有的接口规范
2. **动态加载**：使用Python的反射机制实现灵活性
3. **通用设计**：操作符和工作流模板的通用性
4. **错误容忍**：优雅处理各种异常情况

这种设计理念可以推广到其他需要处理多样化任务的场景中。