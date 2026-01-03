# Workflow评估系统

一个用于测试和评估任意workflow的完整框架，支持从JSONL文件批量测试workflow，并生成详细的分类统计报告。

## 📁 目录结构

```
workflow_evaluator/
├── config.yaml              # 配置文件
├── data_processor.py        # 数据处理器 - 解析JSONL，提取workflow代码
├── workflow_executor.py     # 执行器 - 调用reward server执行测试
├── result_analyzer.py       # 分析器 - 统计分析测试结果
├── report_generator.py      # 报告生成器 - 生成Markdown报告
├── utils.py                 # 工具函数
├── main.py                  # 主程序入口
└── results/                 # 结果输出目录
    ├── gsm8k/               # 按data_source分类
    │   ├── generate_revise/ # 按operators组合分类
    │   └── ...
    ├── raw/                 # 原始结果
    └── summaries/          # 汇总报告
```

## 🚀 快速开始

### 1. 基本使用

```bash
# 完整测试流程（从JSONL文件）
python main.py test --input ../baseline/test_IMO_0922_QZH_with_responses.jsonl

# 分析现有结果
python main.py analyze

# 测试单个workflow
python main.py single --workflow-file my_workflow.py --data-source gsm8k
```

### 2. 高级选项

```bash
# 只测试特定data_source
python main.py test --data-source gsm8k

# 只测试特定operators组合
python main.py test --operators generate,revise,summarize

# 限制测试数量
python main.py test --limit 10

# 自定义并发数
python main.py test --concurrency 10
```

## 📊 功能特性

### 1. 数据处理
- **自动提取workflow代码**: 从response字段中智能提取Python代码
- **分类管理**: 按data_source和operators_group自动分类
- **数据验证**: 验证workflow代码的基本结构

### 2. 执行测试
- **分组执行策略**: 先按data_source分组，再按operators_group分组执行
- **即时保存结果**: 每完成一组立即保存，防止数据丢失
- **并发执行**: 支持配置并发数（concurrency）控制执行速度
- **自动重试**: 失败时自动重试（可配置）
- **超时控制**: 防止单个测试占用过长时间
- **实时进度**: 显示执行进度和分组状态

### 3. 结果分析
- **多维度统计**:
  - 按data_source分析（benchmark维度）
  - 按operators分析（方法维度）
  - 交叉分析（组合维度）
- **性能指标**:
  - 成功率
  - 平均分数
  - 执行时间
  - 错误分类

### 4. 报告生成
- **分层报告结构**:
  - 整体摘要
  - 按data_source详细报告
  - 按operators详细报告
  - 最佳/最差表现排名
- **Markdown格式**: 易于阅读和分享
- **自动保存**: 按分类保存到对应目录

## ⚙️ 配置说明

编辑 `config.yaml` 文件来自定义系统行为：

```yaml
# Reward Server配置
reward_server:
  url: 'http://localhost:8899'
  timeout: 300
  max_retries: 3

# 测试配置
test:
  concurrency: 8  # 并发执行数量（替代原batch_size）
  save_intermediate: true  # 每组完成后立即保存

  # 测试用例配置
  num_test_cases: 200  # 每个workflow测试的样本数量
  random_seed: 42  # 随机种子，确保可重复性
  benchmark_mapping_file: '../benchmark_mapping_test.jsonl'  # benchmark映射文件

# 分析配置
analysis:
  generate_charts: true
  include_failed_details: true
```

### 📌 新功能说明

#### 1. 分组执行策略
系统采用两级分组执行策略，确保测试有序且结果安全：

```
执行顺序：
├── Data Source 1 (如: gsm8k)
│   ├── Operator Group 1 (如: generate_revise)
│   │   └── [并发执行workflows] → 立即保存
│   ├── Operator Group 2 (如: generate_ensemble)
│   │   └── [并发执行workflows] → 立即保存
│   └── ...
├── Data Source 2 (如: mbpp)
│   └── ...
```

**优势**：
- ✅ 每组完成立即保存，防止意外中断导致数据丢失
- ✅ 清晰的执行进度，易于追踪
- ✅ 生成每组的statistics.json统计文件

#### 2. 测试用例自动配置

系统会自动处理测试用例的选择和路径配置：

1. **自动加载benchmark映射**：从`benchmark_mapping_test.jsonl`读取每个benchmark的测试数据路径
2. **随机选择测试用例**：根据配置的`num_test_cases`随机选择测试样本
3. **传递完整路径**：将`data_path`和`test_cases`自动添加到请求的`extra_info`中

这确保了reward server能够找到正确的测试数据文件并执行测试。

## 📈 输出示例

### 测试结果分类
```
results/
├── gsm8k/
│   ├── generate_revise_summarize/
│   │   ├── test_results.jsonl      # 测试结果
│   │   ├── failed_cases.jsonl      # 失败案例
│   │   └── summary.md              # 摘要报告
│   └── generate_ensemble_decompose/
│       └── ...
└── summaries/
    └── complete_analysis.md        # 完整分析报告
```

### 报告内容
- 整体成功率和平均分数
- 每个benchmark的详细表现
- 不同operator组合的对比
- 错误类型分析
- 性能统计（执行时间等）

## 🔍 使用场景

1. **批量测试新生成的workflow**: 测试大量自动生成的workflow
2. **对比不同方法**: 比较不同operator组合的效果
3. **Benchmark评估**: 评估在不同benchmark上的表现
4. **错误分析**: 找出常见的失败模式
5. **性能优化**: 识别执行慢的workflow

## 📝 注意事项

1. **确保Reward Server运行**: 在执行测试前启动reward server
2. **输入格式**: JSONL文件需包含response字段（含workflow代码）
3. **分类依据**: 自动根据data_source和operators_group分类
4. **结果累积**: 多次运行会累积结果，可用于长期跟踪

## 🛠️ 依赖要求

```bash
pip install pyyaml pandas matplotlib seaborn aiohttp
```

## 📞 问题反馈

如有问题或建议，请查看生成的日志文件 `workflow_evaluator.log` 或报告中的错误分析部分。