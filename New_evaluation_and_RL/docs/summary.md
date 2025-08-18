# New_evaluation_and_RL 项目总结

## 📖 项目概述

New_evaluation_and_RL 是 Flow_RL 项目的重构版本，专注于 workflow 生成、执行和评估的完整流程。项目采用微服务架构，通过统一配置管理和模块化设计，提供了一个高效、可扩展的 workflow 评估系统。

### 🎯 核心功能

1. **Workflow 生成与执行**: 使用 MetaGPT 框架执行复杂的 workflow
2. **多模型支持**: 支持本地模型、API 代理和评估专用 API 三种模式
3. **评分计算**: 提供 REST API 接口计算 workflow 执行分数
4. **数据生成**: 支持 VERL 训练数据的 parquet 格式生成
5. **服务编排**: 完整的服务启动和依赖管理流程

## 🏗️ 架构设计

### 服务组件架构

```
New_evaluation_and_RL/
├── config.yaml              # 统一配置文件
├── metagpt_api_key_proxy/   # API 代理服务
├── reward_server/           # 评分计算服务
├── evaluation_server/       # 评估服务管理
├── generate_parquet_and_jsonl/ # 数据生成工具
├── servers_and_proxy/       # 服务启动脚本
├── tests/                   # 测试工具
└── docs/                    # 文档目录
```

### 配置管理

所有服务共享 `config.yaml` 统一配置文件，包含：

- **服务配置**: 端口、主机、速率限制等
- **模型配置**: 本地/API 模式切换
- **路径配置**: 数据集、工作目录等绝对路径
- **评测参数**: 批处理大小、超时设置等

## 🔧 核心组件详解

### 1. API 代理服务 (metagpt_api_key_proxy)

**功能**: 提供 OpenAI 兼容的 API 代理，支持速率限制和请求转发

**组件**:
- `api_key_proxy_enhanced.py`: MetaGPT 专用代理 (端口 5009)
- `api_key_proxy_enhanced_for_evaluation.py`: 评估专用代理 (端口 5010)

**特性**:
- 速率限制控制 (可配置 req/s)
- 实时进度显示和调试模式
- 代理绕过设置 (避免 Clash 干扰)
- 流式响应支持

### 2. 评分服务器 (reward_server)

**功能**: 提供 workflow 评分计算的 REST API 服务

**核心文件**:
- `scoreflow_reward_server.py`: Flask 服务器主程序
- `scoreflow_reward_utils.py`: 评分计算核心逻辑

**API 端点**:
- `GET /health`: 健康检查
- `POST /compute_score`: 单次评分计算
- `POST /batch_compute`: 批量评分计算
- `GET /config`: 获取服务配置

**执行特性**:
- 并行执行模式 (parallel_safe)
- 独立日志文件管理
- All-Reduce 结果汇总
- MetaGPT workflow 执行

### 3. 数据生成工具 (generate_parquet_and_jsonl)

**功能**: 生成 VERL 训练数据的 parquet 和 jsonl 格式

**核心文件**:
- `generate_verl_training_data.py`: 主要数据生成脚本
- `generate_data.sh`: 硬编码配置的便捷启动脚本

**支持的基准测试**:
- gsm8k, mbpp, drop, hotpotqa, humaneval, high_level_math

**生成特性**:
- 支持训练/测试数据分割
- 可配置测试用例数量
- 自动数据验证和保护性检查
- HuggingFace chat 格式支持

### 4. 评估服务管理 (evaluation_server)

**功能**: 管理本地模型服务 (SGLang)

**当前状态**: 
- `sglang_manager.py`: 占位实现，暂未完全实现本地模式
- 推荐使用 API 模式进行评估

## 🚀 服务启动流程

### 标准启动顺序

1. **启动 MetaGPT API 代理**
   ```bash
   bash New_evaluation_and_RL/servers_and_proxy/start_api_proxy.sh
   ```

2. **启动 ScoreFlow 评分服务器**
   ```bash
   bash New_evaluation_and_RL/servers_and_proxy/start_scoreflow_reward.sh
   ```

3. **启动评估服务** (可选)
   ```bash
   bash New_evaluation_and_RL/servers_and_proxy/start_evaluation_server.sh
   ```

### 服务验证

使用 curl 命令验证服务状态：
```bash
# 健康检查
curl http://localhost:8899/health

# API 代理测试
curl http://localhost:5009/

# 评估服务测试
curl http://localhost:5010/
```

## ⚙️ 配置模式

### 模型执行模式

1. **evaluation_api** (推荐)
   - 使用评估专用 API 代理 (端口 5010)
   - 支持立即兼容 SGLang 本地模型
   - 更高的速率限制 (3 req/s)

2. **api**
   - 使用 MetaGPT API 代理 (端口 5009)
   - 标准 API 转发模式

3. **local** (暂未实现)
   - SGLang 本地服务器模式
   - 需要额外实现

### 关键配置项

```yaml
# 服务配置
services:
  metagpt_api_proxy:
    port: 5009
    rate_per_second: 3
  
  evaluation_api_proxy:
    port: 5010
    rate_per_second: 3
  
  scoreflow_reward:
    port: 8899
    timeout: 300

# 模型配置
model:
  mode: "evaluation_api"  # 推荐设置
```

## 🧪 测试和调试

### 测试工具

1. **API 测试脚本**
   - `tests/test_api.sh`: 完整的 API 功能测试
   - `tests/test_scoreflow_request.py`: Python 客户端测试
   - `tests/curl.txt`: curl 命令示例

2. **调试功能**
   - ScoreFlow 服务器支持 `--debug` 模式
   - 生成详细的执行日志和性能统计
   - 独立的 workflow 执行日志文件

### 测试示例

```bash
# 运行完整测试
bash New_evaluation_and_RL/tests/test_api.sh

# Python 客户端测试
python New_evaluation_and_RL/tests/test_scoreflow_request.py
```

## 📊 数据生成和评估

### VERL 数据生成

```bash
# 使用便捷脚本 (硬编码配置)
bash New_evaluation_and_RL/generate_parquet_and_jsonl/generate_data.sh

# 使用完整脚本 (命令行参数)
python New_evaluation_and_RL/generate_parquet_and_jsonl/generate_verl_training_data.py \
  --benchmarks gsm8k mbpp \
  --num-test-entries 10 \
  --output-dir data
```

### 评估流程

1. 生成测试数据 (parquet 格式)
2. 启动所有必需服务
3. 运行评估脚本进行 workflow 测试
4. 查看结果和日志

## 🔍 关键特性

### 性能优化

- **并行执行**: 支持多个 test case 并行处理
- **速率限制**: 可配置的 API 请求频率控制
- **资源管理**: 独立的日志文件和工作目录管理

### 错误处理

- **服务健康检查**: 自动检测依赖服务状态
- **代理绕过**: 智能处理系统代理干扰
- **超时控制**: 可配置的执行超时机制

### 日志和监控

- **分层日志**: 服务级别和 workflow 级别日志分离
- **实时进度**: 进度条和状态显示
- **调试支持**: 详细的执行轨迹和性能统计

## 🛠️ 开发指南

### 环境准备

```bash
# 激活 conda 环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate workflow
```

### 配置修改

1. 编辑 `config.yaml` 调整服务配置
2. 修改绝对路径以适应本地环境
3. 根据需要调整端口和速率限制

### 扩展开发

- 添加新的基准测试支持
- 实现 SGLang 本地模式
- 扩展评分算法
- 优化并行执行策略

## 📋 使用最佳实践

1. **服务启动**: 严格按照依赖顺序启动服务
2. **配置管理**: 统一使用 config.yaml，避免硬编码路径
3. **测试验证**: 每次修改后运行完整测试套件
4. **日志监控**: 定期检查服务日志，及时发现问题
5. **资源清理**: 适时清理工作目录和日志文件

## 🔮 未来规划

- [ ] 完善 SGLang 本地模式实现
- [ ] 添加更多基准测试支持
- [ ] 优化并行执行性能
- [ ] 实现分布式评估
- [ ] 添加 Web UI 管理界面

---

**项目状态**: 生产就绪  
**最后更新**: 2024年8月18日  
**维护者**: 项目团队

本文档提供了 New_evaluation_and_RL 项目的完整概览。如需详细的 API 文档，请参考 `docs/reward_server.md`。