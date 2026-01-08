# Project TODO

> 和合作者共同维护的任务清单

**参考文档**: [新任务 RL 训练接入完整指南](verl_api/new_task_integration_guide.md)

---

## 🔥 P0 - 紧急（阻塞开发/严重bug）

### 1. 数据准备【阻塞】
- [ ] **1.1 设计数据格式**
  - [ ] 确定 prompt 字段结构（初始对话 + 工具调用历史）
  - [ ] 确定 reward_model 字段内容（ground_truth + 工具使用标注）
  - [ ] 确定 data_source 命名规范
  - [ ] 设计工具调用标注格式

- [ ] **1.2 数据预处理脚本**
  - [ ] 编写 `examples/data_preprocess/workflow_task.py`
  - [ ] 实现原始数据加载逻辑
  - [ ] 实现格式转换逻辑（转 verl 格式）
  - [ ] 实现数据验证逻辑

- [ ] **1.3 生成测试数据**
  - [ ] 准备 10-20 个小规模样本
  - [ ] 生成 `data/workflow_task/train.parquet`
  - [ ] 生成 `data/workflow_task/valid.parquet`
  - [ ] 运行验证脚本确认格式正确

### 2. Reward 系统基础【阻塞】
- [ ] **2.1 实现 Reward 函数**
  - [ ] 创建 `verl/utils/reward_score/workflow_task.py`
  - [ ] 实现 `compute_score()` 函数
  - [ ] 实现答案提取逻辑
  - [ ] 实现工具调用正确性判断
  - [ ] 添加调试输出（num_examine）

- [ ] **2.2 注册 Reward**
  - [ ] 在 `verl/trainer/ppo/reward.py` 中添加导入
  - [ ] 添加 reward_type 路由逻辑
  - [ ] 测试 Reward 加载

- [ ] **2.3 测试 Reward 计算**
  - [ ] 编写单元测试脚本
  - [ ] 测试 5-10 个样本
  - [ ] 验证 Reward 分数正确性

---

## 🎯 P1 - 重要（新功能/重构/优化）

### 3. Tool 实现【核心功能】
- [ ] **3.1 设计 Tool 架构**
  - [ ] 确定需要哪些工具（搜索/执行/验证等）
  - [ ] 设计每个工具的输入输出格式
  - [ ] 设计工具的依赖关系

- [ ] **3.2 实现核心工具**
  - [ ] 创建 `verl/tools/workflow_tools.py`
  - [ ] 实现工具 1（如：搜索工具）
  - [ ] 实现工具 2（如：代码执行工具）
  - [ ] 实现工具 3（如：答案工具）
  - [ ] 每个工具实现 `execute()` 和 `format_result()` 方法

- [ ] **3.3 Tool 注册和配置**
  - [ ] 在 `verl/tools/__init__.py` 中注册工具
  - [ ] 创建 `config/tool_config/workflow_tools.yaml`
  - [ ] 定义工具的 Schema（参数、描述等）
  - [ ] （可选）创建 `tools.json` 配置文件

- [ ] **3.4 测试工具调用**
  - [ ] 单独测试每个工具的执行
  - [ ] 测试工具的错误处理
  - [ ] 测试工具的超时机制

### 4. Multi-turn 训练配置【核心功能】
- [ ] **4.1 编写主配置文件**
  - [ ] 创建 `config/workflow_task_grpo.yaml`
  - [ ] 配置数据路径（train_files, val_files）
  - [ ] 配置 Reward Manager（reward_type）
  - [ ] 配置 multi_turn 参数（enable: true, max_turns）
  - [ ] 配置 tool_config_path
  - [ ] 配置模型和训练参数

- [ ] **4.2 Multi-turn 参数调优**
  - [ ] 确定 max_turns（建议 5-10）
  - [ ] 确定 max_prompt_length（建议 4096）
  - [ ] 确定 max_response_length（建议 2048）
  - [ ] 确定生成参数（temperature, top_p）

### 5. Generation Manager【如需自定义】
- [ ] **5.1 评估是否需要自定义**
  - [ ] 测试默认 Generation Manager 是否满足需求
  - [ ] 如需自定义，继续 5.2-5.4
  - [ ] 如不需要，跳到第 6 节

- [ ] **5.2 实现自定义 Generation Manager**
  - [ ] 创建 `verl/workers/rollout/workflow_generation_manager.py`
  - [ ] 实现 `run_multi_turn_generation()` 方法
  - [ ] 实现上下文初始化逻辑
  - [ ] 实现 prompt 构建逻辑
  - [ ] 实现工具调用解析逻辑
  - [ ] 实现工具执行逻辑
  - [ ] 实现终止判断逻辑

- [ ] **5.3 实现上下文管理**
  - [ ] 实现上下文累积策略（文档/代码/答案）
  - [ ] 实现长度控制逻辑（优先级截断）
  - [ ] 实现 `_build_prompt_with_context_control()`
  - [ ] 实现 `merge_documents()` 等辅助函数

- [ ] **5.4 注册 Generation Manager**
  - [ ] 在配置中指定自定义 Generation Manager
  - [ ] 测试 Generation Manager 加载

### 6. 启动脚本和测试【核心功能】
- [ ] **6.1 创建启动脚本**
  - [ ] 创建 `scripts/train_workflow.sh`
  - [ ] 配置环境变量
  - [ ] 配置训练参数
  - [ ] 添加日志和监控

- [ ] **6.2 端到端测试**
  - [ ] 使用 4 个样本测试完整流程
  - [ ] 验证数据加载
  - [ ] 验证 Reward 计算
  - [ ] 验证工具调用
  - [ ] 验证 multi-turn 循环
  - [ ] 检查是否有报错

- [ ] **6.3 小规模训练**
  - [ ] 使用 100 个样本训练 10 步
  - [ ] 监控 loss 和 reward
  - [ ] 检查模型是否学习
  - [ ] 记录训练日志

---

## 📋 P2 - 常规（代码清理/文档补充）

### 7. 优化和调试【性能优化】
- [ ] **7.1 性能优化**
  - [ ] 优化数据加载速度
  - [ ] 优化 Reward 计算（批处理）
  - [ ] 优化工具调用（并行执行）
  - [ ] 优化 GPU 内存使用

- [ ] **7.2 调试工具**
  - [ ] 添加详细日志输出
  - [ ] 实现可视化工具（查看工具调用）
  - [ ] 实现采样检查工具

- [ ] **7.3 监控和日志**
  - [ ] 集成 Wandb 监控
  - [ ] 记录工具使用统计
  - [ ] 记录 Reward 分布
  - [ ] 记录 multi-turn 轮次统计

### 8. 高级功能【可选】
- [ ] **8.1 自定义 RewardManager**
  - [ ] 评估是否需要（批量处理/模型推理）
  - [ ] 创建 `verl/workers/reward_manager/workflow_manager.py`
  - [ ] 实现 `compute_rewards()` 方法
  - [ ] 注册 RewardManager

- [ ] **8.2 自定义 Trainer**
  - [ ] 评估是否需要（GRPO 变体/特殊筛选）
  - [ ] 创建 `verl/trainer/ppo/workflow_trainer.py`
  - [ ] 实现自定义归一化逻辑
  - [ ] 实现自定义样本筛选

- [ ] **8.3 评估脚本**
  - [ ] 创建 `scripts/eval_workflow.sh`
  - [ ] 实现评估指标计算
  - [ ] 生成评估报告

### 9. 文档和测试【质量保证】
- [ ] **9.1 补充文档**
  - [ ] 编写任务说明文档
  - [ ] 编写数据格式文档
  - [ ] 编写工具使用说明
  - [ ] 编写训练配置说明

- [ ] **9.2 单元测试**
  - [ ] Reward 函数测试
  - [ ] Tool 执行测试
  - [ ] 数据加载测试
  - [ ] 上下文管理测试

- [ ] **9.3 集成测试**
  - [ ] 端到端训练测试
  - [ ] 多 GPU 训练测试
  - [ ] 长时间训练稳定性测试

---

## ✅ 已完成（本周）

- [x] 创建 verl API 文档系统（9篇文档）
- [x] 创建新任务接入完整指南
- [x] 更新 README.md 导读文档

---

## 📝 开发顺序建议

**阶段 1: 基础搭建（P0，预计 1-2 天）**
```
数据准备 → Reward 实现 → 基础测试
```

**阶段 2: 核心功能（P1.3-6，预计 2-3 天）**
```
Tool 实现 → 配置编写 → 端到端测试
```

**阶段 3: 高级功能（P1.5 + P2，预计 3-5 天）**
```
自定义 Generation Manager → 优化调试 → 完整训练
```

**阶段 4: 优化完善（P2，持续）**
```
性能优化 → 文档补充 → 测试覆盖
```

---

## 🔗 相关资源

- **主要参考**: [新任务 RL 训练接入完整指南](verl_api/new_task_integration_guide.md)
- **数据准备**: [数据接口规范](verl_api/data_interface.md)
- **Reward 实现**: [Reward 接口规范](verl_api/reward_interface.md)
- **Tool 实现**: [配置与加载机制](verl_api/config_and_loading.md)
- **Multi-turn**: [Multi-Turn 逻辑实现](verl_api/toolorchestra_multiturn_implementation.md)
- **上下文管理**: [上下文维护机制](verl_api/context_maintenance_mechanism.md)

---

*最后更新: 2026-01-08*
*项目: Flow_RL_refactor - Workflow 工具调用系统*
