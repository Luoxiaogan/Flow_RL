# 📊 模型评测工作流系统

一个模块化的模型评测系统，支持本地模型和API模型的评测，具有清晰的服务管理和配置系统。

## 🚀 快速开始

### 1. 配置系统

编辑 `config.yaml` 文件，设置你的评测参数：

```yaml
model:
  mode: "local"  # 或 "api"
  local:
    model_path: "/path/to/your/model"
```

### 2. 启动必要服务

在独立的终端中启动服务：

**Terminal 1 - API代理服务（如果使用API模式）：**
```bash
cd services
./start_api_proxy.sh
```

**Terminal 2 - ScoreFlow Reward服务：**
```bash
cd services
./start_reward_server.sh
```

### 3. 运行评测

**Terminal 3 - 执行评测：**
```bash
cd scripts
./run_evaluation.sh
```

## 📁 目录结构

```
evaluation_workflow/
├── config.yaml              # 统一配置文件
├── services/               # 服务管理
│   ├── start_api_proxy.sh     # 启动API代理
│   ├── start_reward_server.sh # 启动Reward服务
│   ├── stop_all_services.sh   # 停止所有服务
│   └── api_key_proxy.py       # API代理服务
├── evaluation/             # 评测核心模块
│   ├── evaluate_model.py      # 主评测程序
│   ├── sglang_server.py       # SGLang服务管理
│   ├── batch_inference.py     # 批量推理引擎
│   ├── report_generator.py    # 报告生成器
│   └── utils.py              # 工具函数
├── scripts/                # 执行脚本
│   ├── run_evaluation.sh      # 主评测脚本
│   └── debug_sglang.sh        # SGLang调试脚本
└── logs/                   # 日志目录（自动创建）
```

## ⚙️ 配置说明

### 服务配置

```yaml
services:
  api_proxy:
    port: 5009              # API代理端口
    rate_per_second: 3      # 速率限制
    max_concurrency: 6      # 最大并发数
    
  scoreflow_reward:
    port: 8899              # Reward服务端口
    timeout: 300            # 超时时间
```

### 模型配置

#### 本地模型模式
```yaml
model:
  mode: "local"
  local:
    model_path: "/nas/models/your-model"
    port: 30000
    tensor_parallel: 1
```

#### API模型模式
```yaml
model:
  mode: "api"
  api:
    url: "http://localhost:5009/v1/chat/completions"
    key: "your-api-key"
    model: "gpt-4"
```

### 评测参数

```yaml
evaluation:
  test_data: "../data/test_new/test.parquet"
  output_dir: "./results"
  max_inference_workers: 10
  max_scoring_workers: 5
  temperature: 0.7
  max_tokens: 8192
  skip_scoring: false       # 跳过评分（调试用）
  limit: null              # 限制样本数（null为全部）
```

## 🔧 常用操作

### 停止所有服务
```bash
cd services
./stop_all_services.sh
```

### 调试SGLang
```bash
cd scripts
./debug_sglang.sh
```

### 查看日志
```bash
# API代理日志
tail -f logs/api_proxy_*.log

# Reward服务日志
tail -f logs/reward_server_*.log
```

## 📊 输出结果

评测结果保存在 `scripts/results/` 目录下，包括：

- `summary_report.md` - 评测总结报告
- `*_results.jsonl` - 详细评测结果
- `*.png` - 可视化图表
- `results.csv` - CSV格式结果

## 🐛 故障排查

### 服务无法启动

1. 检查端口是否被占用：
```bash
lsof -i :5009   # API代理端口
lsof -i :8899   # Reward服务端口
lsof -i :30000  # SGLang端口
```

2. 查看服务日志：
```bash
ls -lt logs/*.log
```

### SGLang启动失败

1. 使用调试模式：
```bash
cd scripts
./debug_sglang.sh
```

2. 检查GPU状态：
```bash
nvidia-smi
```

3. 增加启动超时时间：
编辑 `config.yaml`：
```yaml
model:
  local:
    startup_timeout: 300  # 增加到5分钟
```

### 评分服务连接失败

确保ScoreFlow Reward服务正在运行：
```bash
curl http://localhost:8899/health
```

## 💡 提示

1. **服务独立管理**：每个服务在独立终端中运行，便于监控和调试
2. **统一配置**：所有参数在 `config.yaml` 中管理
3. **日志追踪**：所有服务日志保存在 `logs/` 目录
4. **灵活控制**：可以独立启停各个服务

## 📝 注意事项

- ScoreFlow Reward服务器保持在原位置 (`../scoreflow_reward_server.py`)
- 通过相对路径访问，无需移动原文件
- 首次运行会自动创建必要的目录
- 服务PID保存在 `logs/` 目录中，用于服务管理

## 🔄 工作流程

1. **配置阶段**：编辑 `config.yaml`
2. **服务启动**：在独立终端启动必要服务
3. **评测执行**：运行 `run_evaluation.sh`
4. **结果查看**：检查 `results/` 目录
5. **服务停止**：运行 `stop_all_services.sh`

## 📞 支持

如有问题，请检查：
1. 配置文件是否正确
2. 服务是否正常运行
3. 日志文件中的错误信息