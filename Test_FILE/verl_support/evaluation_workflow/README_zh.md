# 📊 模型评测工作流系统

一个模块化的模型评测系统，支持本地模型和API模型的全面评测，具有清晰的服务管理架构和统一配置系统。

## 🎯 系统特点

- **服务分离架构**：API代理、评分服务和评测执行相互独立
- **统一配置管理**：一个YAML文件管理所有配置
- **灵活的模型支持**：支持本地SGLang部署和外部API调用
- **完整的评测流程**：推理、评分、报告生成一体化
- **便捷的调试工具**：内置多种调试和监控脚本

## 🚀 快速开始指南

### 第一步：配置系统

编辑 `config.yaml` 文件，根据你的需求配置参数：

```yaml
# 选择评测模式
model:
  mode: "local"  # 本地模型模式
  # mode: "api"  # API模型模式
  
  # 本地模型配置
  local:
    model_path: "/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft_new/checkpoint-200"
    port: 30000
    tensor_parallel: 1
```

### 第二步：启动必要服务

在**独立的终端窗口**中分别启动服务：

#### Terminal 1 - API代理服务（仅API模式需要）
```bash
cd evaluation_workflow/services
./start_api_proxy.sh
```
> 📌 该服务将API请求代理到配置的目标服务器，支持速率限制和并发控制

#### Terminal 2 - ScoreFlow评分服务
```bash
cd evaluation_workflow/services
./start_reward_server.sh
```
> 📌 该服务负责执行生成的workflow并计算准确率分数

### 第三步：执行评测

#### Terminal 3 - 运行主评测
```bash
cd evaluation_workflow/scripts
./run_evaluation.sh
```
> 📌 系统会自动检查服务状态，确认无误后开始评测

## 📁 项目结构详解

```
evaluation_workflow/
│
├── 📄 config.yaml              # 🔧 统一配置文件（核心）
├── 📄 README_zh.md             # 📖 中文说明文档
├── 📄 README.md                # 📖 英文说明文档
│
├── 📂 services/                # 🚀 服务管理目录
│   ├── start_api_proxy.sh        # 启动API代理服务脚本
│   ├── start_reward_server.sh    # 启动评分服务脚本
│   ├── stop_all_services.sh      # 一键停止所有服务
│   └── api_key_proxy.py          # API代理服务实现
│
├── 📂 evaluation/              # 💡 评测核心模块
│   ├── evaluate_model.py         # 主评测程序
│   ├── sglang_server.py          # SGLang服务器管理
│   ├── batch_inference.py        # 批量推理引擎
│   ├── report_generator.py       # 评测报告生成器
│   └── utils.py                  # 工具函数库
│
├── 📂 scripts/                 # 🎮 执行脚本目录
│   ├── run_evaluation.sh         # 主评测执行脚本
│   ├── debug_sglang.sh          # SGLang调试工具
│   └── results/                  # 评测结果输出目录
│
└── 📂 logs/                    # 📝 日志文件目录（自动创建）
    ├── api_proxy_*.log           # API代理服务日志
    ├── reward_server_*.log       # 评分服务日志
    └── *.pid                     # 服务进程ID文件
```

## ⚙️ 详细配置说明

### 1. 服务配置部分

```yaml
services:
  # API代理服务配置
  api_proxy:
    enabled: true                  # 是否启用
    host: "localhost"             # 监听地址
    port: 5009                    # 监听端口
    target_url: "https://..."     # 目标API地址
    rate_per_second: 3            # 每秒请求限制
    max_concurrency: 6            # 最大并发数
    queue_type: "default"         # 队列类型：default/random
    
  # ScoreFlow评分服务配置
  scoreflow_reward:
    enabled: true                 # 是否启用
    host: "0.0.0.0"              # 监听地址
    port: 8899                    # 监听端口
    timeout: 300                  # 超时时间（秒）
    debug: false                  # 调试模式
```

### 2. 模型配置部分

#### 本地模型模式配置
```yaml
model:
  mode: "local"                   # 使用本地模型
  local:
    model_path: "/path/to/model"  # 模型checkpoint路径
    port: 30000                   # SGLang服务端口
    tensor_parallel: 1            # 张量并行GPU数
    data_parallel: 1              # 数据并行副本数
    mem_fraction_static: 0.85     # GPU内存分配比例
    startup_timeout: 180          # 启动超时（秒）
    debug_mode: false             # 是否显示详细输出
```

#### API模型模式配置
```yaml
model:
  mode: "api"                     # 使用API模型
  api:
    url: "http://localhost:5009/v1/chat/completions"  # API端点
    key: "your-api-key"           # API密钥
    model: "gpt-4"                # 模型名称
```

### 3. 评测参数配置

```yaml
evaluation:
  # 数据配置
  test_data: "../data/test_new/test.parquet"  # 测试数据路径
  output_dir: "./results"                     # 结果输出目录
  
  # 推理参数
  max_inference_workers: 10      # 最大推理并发数
  max_scoring_workers: 5         # 最大评分并发数
  batch_size: 50                 # 批处理大小
  temperature: 0.7               # 生成温度参数
  max_tokens: 8192               # 最大生成token数
  
  # 可选参数
  limit: null                    # 样本数限制（null=全部）
  skip_scoring: false            # 是否跳过评分阶段
  save_intermediate: true        # 是否保存中间结果
```

## 🔧 常用操作指南

### 服务管理

#### 一键停止所有服务
```bash
cd services
./stop_all_services.sh
```

#### 查看服务状态
```bash
# 查看API代理服务
ps aux | grep api_key_proxy

# 查看评分服务
ps aux | grep scoreflow_reward

# 查看端口占用
lsof -i :5009   # API代理
lsof -i :8899   # 评分服务
lsof -i :30000  # SGLang
```

### 调试工具

#### SGLang调试模式
```bash
cd scripts
./debug_sglang.sh
```
> 直接显示SGLang的所有输出，便于诊断启动问题

#### 查看实时日志
```bash
# API代理日志
tail -f logs/api_proxy_*.log

# 评分服务日志
tail -f logs/reward_server_*.log

# 查看最新日志
ls -lt logs/*.log | head -5
```

### 测试服务连接

```bash
# 测试API代理
curl http://localhost:5009

# 测试评分服务
curl http://localhost:8899/health

# 测试SGLang（如果运行中）
curl http://localhost:30000/health
```

## 📊 评测结果说明

评测完成后，结果保存在 `scripts/results/` 目录：

```
results/
└── 20250115_140000_model_name/
    ├── 📄 summary_report.md      # 总体评测报告
    ├── 📄 results.csv            # CSV格式完整结果
    ├── 📄 gsm8k_results.jsonl    # GSM8K详细结果
    ├── 📄 mbpp_results.jsonl     # MBPP详细结果
    ├── 📊 score_distribution.png  # 分数分布图
    ├── 📊 average_scores.png     # 平均分数图表
    └── 📊 success_rates.png      # 成功率统计图
```

### 结果文件格式

**JSONL格式**（每行一个JSON对象）：
```json
{
  "prompt": "用户输入的问题",
  "response": "模型生成的完整回复",
  "workflow": "提取的workflow代码",
  "score": 0.85,
  "success": true,
  "inference_time": 2.3,
  "scoring_time": 1.5,
  "metadata": {...}
}
```

## 🐛 常见问题解决

### 1. SGLang服务启动失败

**问题表现**：超时或立即退出

**解决方案**：
1. 检查GPU内存：`nvidia-smi`
2. 使用调试模式查看详细错误：`./debug_sglang.sh`
3. 减少内存分配：编辑config.yaml，设置 `mem_fraction_static: 0.6`
4. 增加启动超时：设置 `startup_timeout: 300`

### 2. 评分服务连接失败

**问题表现**：`ScoreFlow Reward服务未运行`

**解决方案**：
1. 确认服务已启动：`./start_reward_server.sh`
2. 检查健康状态：`curl http://localhost:8899/health`
3. 查看服务日志：`tail -f logs/reward_server_*.log`
4. 或设置跳过评分：`skip_scoring: true`

### 3. API代理速率限制

**问题表现**：请求被拒绝或超时

**解决方案**：
1. 调整速率限制：`rate_per_second: 5`
2. 增加并发数：`max_concurrency: 10`
3. 检查目标API状态

### 4. 端口被占用

**问题表现**：`Port already in use`

**解决方案**：
```bash
# 查找占用进程
lsof -i :端口号

# 终止进程
kill -9 进程ID

# 或使用停止脚本
./stop_all_services.sh
```

## 💡 最佳实践

### 1. 评测前准备
- ✅ 确认GPU可用性和内存充足
- ✅ 检查测试数据路径正确
- ✅ 验证模型路径或API密钥有效
- ✅ 创建独立的screen/tmux会话运行服务

### 2. 服务启动顺序
1. 先启动API代理（如需要）
2. 再启动评分服务
3. 最后运行评测

### 3. 监控和日志
- 使用 `tail -f` 实时监控日志
- 定期清理旧日志文件
- 保留重要评测结果的备份

### 4. 性能优化
- 根据GPU内存调整 `tensor_parallel`
- 根据任务复杂度调整 `max_inference_workers`
- 批量处理时注意 `batch_size` 设置

## 🔄 完整工作流程

```mermaid
graph LR
    A[编辑config.yaml] --> B[启动API代理]
    B --> C[启动评分服务]
    C --> D[运行评测脚本]
    D --> E[生成评测报告]
    E --> F[查看结果]
    F --> G[停止所有服务]
```

## 📝 注意事项

1. **路径说明**：
   - ScoreFlow服务器文件保持在 `../scoreflow_reward_server.py`
   - 通过相对路径访问，无需移动原始文件
   
2. **服务独立性**：
   - 每个服务独立运行，可单独启停
   - 服务间通过HTTP API通信
   
3. **配置优先级**：
   - `config.yaml` 是唯一的配置来源
   - 所有脚本都从此文件读取配置
   
4. **日志管理**：
   - 日志自动按时间戳命名
   - PID文件用于服务管理

## 🆘 获取帮助

遇到问题时，请按以下步骤排查：

1. **查看README文档**：确认操作步骤正确
2. **检查配置文件**：验证参数设置合理
3. **查看服务日志**：分析具体错误信息
4. **使用调试工具**：运行调试脚本诊断问题
5. **检查系统资源**：确认GPU/内存/端口可用

---

*最后更新：2025年1月*