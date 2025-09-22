# Workflow DAG 分析项目

本项目提供了从 Python 代码块中提取、分析和可视化工作流拓扑结构的工具集。

## 📂 项目结构

```
workflow_dag_analysis/
├── scripts/                    # 分析和可视化脚本
│   ├── extract_python_code.py          # 从工作流中提取Python代码
│   ├── extract_workflow_dag.py         # 使用Graphviz的DAG提取
│   ├── extract_workflow_dag_simple.py  # 简化版DAG提取（matplotlib）
│   ├── extract_workflow_summary.py     # 工作流统计分析
│   └── sample_workflow.py              # 用于测试的示例工作流
├── data/                       # 输入数据文件
│   └── extracted_python_code.jsonl     # 提取的工作流代码块
├── results/                    # 生成的可视化和报告
│   ├── *.png                           # DAG可视化图像
│   ├── *.json                          # 分析报告
│   └── *.csv                           # 汇总数据
└── docs/                       # 文档
    └── README.md                        # 项目说明
```

## 🚀 快速开始

### 1. 从工作流中提取Python代码
```bash
cd scripts/
python extract_python_code.py ../../../Test_FILE/training_data/workflow_dataset.json
```

### 2. 提取并可视化DAG
```bash
# 简化版本（使用matplotlib，无需外部依赖）
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --output-dir ../results/ --limit 10

# 高级版本（需要Graphviz）
python extract_workflow_dag.py --input ../data/extracted_python_code.jsonl --output-dir ../results/ --limit 10
```

### 3. 生成统计分析
```bash
python extract_workflow_summary.py --input ../data/extracted_python_code.jsonl --output-dir ../results/
```

## 📊 脚本说明

### `extract_python_code.py`
从工作流JSON文件中提取Python代码块。
- **输入**：工作流数据集JSON文件
- **输出**：包含提取代码块的JSONL文件
- **用途**：分析流程的第一步

### `extract_workflow_dag_simple.py`
使用NetworkX和matplotlib的简化DAG提取和可视化。
- **特性**：
  - 提取算子依赖关系
  - 包含INPUT/OUTPUT节点
  - 识别并行执行模式
  - 无需外部依赖
- **输出**：PNG可视化图像和JSON指标

### `extract_workflow_dag.py`
使用Graphviz可视化的高级DAG提取。
- **特性**：
  - 高质量图形渲染
  - 分层布局
  - 详细的依赖跟踪
- **要求**：必须安装Graphviz可执行文件

### `extract_workflow_summary.py`
统计分析和模式提取。
- **特性**：
  - 算子分布分析
  - 工作流模式识别
  - 基准测试统计
  - CSV和JSON报告
- **输出**：综合分析报告

## 📈 分析指标

工具提取和分析以下指标：

1. **拓扑指标**：
   - 算子数量
   - 依赖关系数量
   - DAG验证
   - 最长执行路径
   - 最大并行度

2. **算子统计**：
   - 类型分布（Generate、Revise、Summarize、Ensemble）
   - 使用频率
   - 常见组合

3. **工作流模式**：
   - 并行执行（asyncio.gather）
   - 多步骤工作流
   - 集成聚合
   - 上下文依赖

## 🎨 可视化

DAG可视化使用颜色编码不同的节点类型：
- 🟢 **绿色**：输入节点
- 🌸 **粉色**：输出节点
- 🔵 **蓝色**：Generate算子
- 🟣 **紫色**：Revise算子
- 🟡 **黄色**：Summarize算子
- 🟠 **橙色**：Ensemble算子

## 📝 数据格式

### 输入格式（extracted_python_code.jsonl）
```json
{
  "workflow_id": "humaneval_8_0",
  "benchmark": "humaneval",
  "data_indices": [23, 137],
  "python_code_blocks": ["..."],
  "num_code_blocks": 1
}
```

### 输出格式（DAG分析）
```json
{
  "workflow_id": "humaneval_8_0",
  "num_operators": 5,
  "longest_path": 4,
  "parallel_operations": 2,
  "operator_types": {
    "generate": 3,
    "ensemble": 1,
    "revise": 1
  }
}
```

## 🛠️ 依赖项

### 必需的Python包
```bash
pip install networkx matplotlib pandas tabulate
```

### 可选（用于高级可视化）
```bash
pip install graphviz pyvis
# 还需要Graphviz可执行文件：https://graphviz.org/download/
```

## 📊 示例结果

基于50个工作流的分析：
- **每个工作流平均算子数**：6.7
- **最常见的算子**：Generate（100%）、Revise（100%）、Ensemble（100%）
- **常见模式**：并行执行（96%）、多步骤（74%）
- **典型组合**：Generate → Revise → Ensemble

## 🔍 使用示例

### 分析特定工作流
```bash
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --workflow-id humaneval_8_0
```

### 生成汇总报告
```bash
python extract_workflow_summary.py --input ../data/extracted_python_code.jsonl --limit 100
```

### 显示详细指标的详细输出
```bash
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --verbose
```

## 📄 许可

本项目是Flow_RL工作流分析系统的一部分。