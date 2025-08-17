# Workflow执行日志系统

## 系统概述

Workflow执行日志系统为ScoreFlow Reward服务中的所有workflow执行提供全面的日志记录和结果追踪。每次workflow执行都会创建一个专属目录，包含详细的日志、结果和元数据。

## 核心功能

- **结构化目录组织**：按benchmark/data_source组织workflow
- **双向输出**：所有日志同时显示在终端并保存到文件
- **CSV结果记录**：测试案例结果以CSV格式保存，便于分析
- **执行元数据**：完整保存workflow上下文和配置信息
- **错误信息清理**：错误消息经过清理以兼容CSV格式

## 目录结构

```
workspace/
├── gsm8k/                              # GSM8K基准测试
│   ├── workflow_20250117_143025_abc123/   # 单个workflow执行记录
│   │   ├── workflow.py                 # 原始workflow代码
│   │   ├── metadata.json              # 执行元数据
│   │   ├── test_case_0.log           # 测试案例0的执行日志
│   │   ├── test_case_1.log           # 测试案例1的执行日志
│   │   ├── test_case_2.log           # 测试案例2的执行日志
│   │   ├── results.csv                # 所有测试案例结果
│   │   └── summary.json               # 执行汇总
│   └── workflow_20250117_143125_def456/
│       └── ...
├── mbpp/                               # MBPP基准测试
│   └── ...
└── high_level_math/                   # 高级数学基准测试
    └── ...
```

## 配置说明

在`config.yaml`中添加workspace路径：

```yaml
scoreflow_reward:
  workspace: "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/workspace"  # workflow执行日志保存目录
```

## 文件说明

### workflow.py
提交执行的原始workflow代码。

### metadata.json
包含内容：
- workflow_id: 唯一标识符
- data_source: 基准测试名称
- test_cases: 测试案例索引列表
- timestamp: 执行开始时间
- extra_info: 请求中的额外上下文信息

### test_case_X.log
测试案例X的完整执行日志，包括：
- workflow中的所有print输出
- MetaGPT operator的输出
- 错误消息和堆栈跟踪
- 时间信息

### results.csv
CSV文件，包含列：
- test_case: 测试案例索引
- success: 成功/失败（true/false）
- score: 分数（0.0到1.0）
- duration: 执行时间（秒）
- error: 清理后的错误信息（如果失败）
- timestamp: 完成时间

### summary.json
汇总统计信息：
- workflow_id: 唯一标识符
- total_test_cases: 测试案例总数
- successful_cases: 成功执行数量
- failed_cases: 失败执行数量
- average_score: 所有测试案例的平均分数
- total_duration: 总执行时间
- timestamp: 汇总生成时间

## 使用方法

### 测试系统

运行测试脚本：
```bash
bash test_logging_system.sh
```

或手动测试：
```bash
# 启动服务
bash servers_and_proxy/start_api_proxy.sh
bash servers_and_proxy/start_scoreflow_reward.sh

# 运行测试
python tests/test_workflow_logging.py
```

### 查看结果

执行后，检查workspace目录：
```bash
# 查找最新的workflow
ls -lt workspace/gsm8k/ | head -5

# 查看汇总信息
cat workspace/gsm8k/workflow_*/summary.json | jq .

# 查看结果CSV
cat workspace/gsm8k/workflow_*/results.csv

# 查看特定测试案例日志
less workspace/gsm8k/workflow_*/test_case_0.log
```

### 使用Python分析结果

```python
import pandas as pd
import json
from pathlib import Path

# 加载结果
workspace = Path("workspace/gsm8k")
latest_workflow = sorted(workspace.glob("workflow_*"))[-1]

# 读取CSV结果
df = pd.read_csv(latest_workflow / "results.csv")
print(f"平均分数: {df['score'].mean():.3f}")
print(f"成功率: {df['success'].mean():.1%}")

# 读取汇总
with open(latest_workflow / "summary.json", encoding='utf-8') as f:
    summary = json.load(f)
print(f"总耗时: {summary['total_duration']:.2f}秒")
```

## 实现细节

### 日志捕获机制

系统使用`TeeOutput`类来复制所有stdout/stderr输出：
- 终端输出保持实时可见
- 所有输出同时写入日志文件
- 禁用缓冲以确保立即可见

### 错误处理

错误消息经过清理以适合CSV存储：
- 换行符替换为" | "
- 逗号替换为分号
- 双引号替换为单引号
- 长度限制为500字符

### 并发控制

测试案例以受控并发方式执行：
- 最大并发执行数在config.yaml中配置
- 批处理以防止资源耗尽
- 失败执行的异常处理

## 故障排除

### 没有日志出现
- 检查服务是否运行：`curl http://localhost:8899/health`
- 验证workspace目录权限
- 检查config.yaml中的workspace路径是否正确

### 日志不完整
- 增加config.yaml中的timeout设置
- 检查系统资源（内存/CPU）
- 验证MetaGPT配置

### CSV解析错误
- 检查错误消息中的特殊字符
- 验证CSV文件编码（UTF-8）
- 使用pandas时设置error_bad_lines=False

## 系统优势

1. **调试便利**：完整的执行跟踪用于故障排查
2. **性能分析**：持续时间跟踪用于优化
3. **质量指标**：成功率和分数用于评估
4. **可重现性**：保存完整的workflow代码和上下文
5. **批量分析**：CSV格式支持统计分析

## 常见使用场景

### 场景1：调试失败的workflow
```bash
# 找到失败的测试案例
grep "false" workspace/gsm8k/workflow_*/results.csv

# 查看具体错误
cat workspace/gsm8k/workflow_*/test_case_X.log | grep -A 10 "错误"
```

### 场景2：性能优化
```python
# 分析执行时间分布
import pandas as pd
df = pd.read_csv("workspace/gsm8k/workflow_*/results.csv")
print(f"最慢执行: {df['duration'].max():.2f}秒")
print(f"最快执行: {df['duration'].min():.2f}秒")
print(f"平均执行: {df['duration'].mean():.2f}秒")
```

### 场景3：批量统计
```bash
# 统计所有workflow的成功率
for dir in workspace/gsm8k/workflow_*; do
    echo -n "$dir: "
    jq -r '.average_score' "$dir/summary.json"
done | sort -t: -k2 -nr
```

## 注意事项

- 日志文件可能很大，定期清理旧的workflow目录
- 敏感信息可能出现在日志中，注意安全
- CSV文件使用UTF-8编码，确保工具兼容
- 并发执行可能影响性能，根据需要调整max_concurrent设置