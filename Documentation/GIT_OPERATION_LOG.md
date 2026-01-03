# Git操作记录

## 2025-01-24 代码回退与选择性应用

### 操作背景
需要回退到稳定版本，但保留部分新功能，放弃有问题的更改。

### 操作内容

#### 1. 回退基准
- **目标commit**: `c86235db` - 回退到稳定的Qwen2.5-7B-Instruct配置
- **原因**: 这是最后一个确认稳定运行的版本

#### 2. 保留的更改
- **Cherry-pick commit**: `87f44441` - token count功能
- **包含内容**:
  - Token使用量统计功能
  - API费用惩罚机制
  - 相关测试和文档

#### 3. 放弃的更改
- **丢弃commit**: `6333d9be` - 实现debug模式控制
- **原因**: 该功能在非debug模式下禁用了必要的日志保存和operator输出，影响系统正常运行

### 操作步骤
```bash
# 1. 硬重置到稳定版本
git reset --hard c86235db

# 2. Cherry-pick需要的功能
git cherry-pick 87f44441

# 3. 解决合并冲突（internbootcamp_reward_utils.py）
# 保留token统计相关代码

# 4. 修改commit消息为中文
git commit --amend -m "添加Token使用量统计和费用惩罚功能"
```

### 最终状态
- 基于稳定版本 `c86235db`
- 集成了token统计和费用惩罚功能
- 移除了有问题的debug模式控制
- 代码处于稳定可用状态

### 注意事项
- 该操作导致本地分支与远程分支diverge
- 需要使用 `git push --force-with-lease` 强制推送
- 确保其他协作者知晓此次强制推送