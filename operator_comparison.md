# Operator对比分析

## GSM8K原始版本（default组）
包含4个基础operators：
1. **Generate** - CREATE new information
2. **Revise** - IMPROVE existing information  
3. **Summarize** - COMPRESS information
4. **Ensemble** - DECIDE between or synthesize options

## GSM8K_REASONING增强版本（reasoning_heavy组）
包含6个operators，新增了2个：
1. **Generate** - 创建新的信息或分析
2. **Decompose** - 分解复杂问题 ✨**新增**
3. **Revise** - 改进和优化现有内容
4. **Summarize** - 压缩和提取关键信息
5. **Ensemble** - 整合多个候选方案
6. **FormatAnswer** - 格式化最终答案 ✨**新增**

## 关键差异

### 新增的Operator功能：

**Decompose（分解）**：
- 签名：`await self.decompose(instruction: str, context: str) -> str`
- 作用：将复杂问题分解为更小的子问题
- 适用场景：处理需要多步推理的复杂数学问题

**FormatAnswer（格式化答案）**：
- 签名：`await self.formatanswer(instruction: str, context: str) -> str`
- 作用：按照指定要求格式化最终答案
- 适用场景：确保答案符合特定格式要求

## 结论
系统**确实成功**添加了新的operator！gsm8k_reasoning版本比原始gsm8k多了2个专门用于推理增强的operator（Decompose和FormatAnswer），这正是reasoning_heavy组的特点。