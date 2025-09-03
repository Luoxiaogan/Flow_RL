#!/usr/bin/env python
"""
计算 LoRA 参数量及占比
"""

def calculate_lora_params(
    model_name="Qwen3-8B",
    lora_rank=8,
    lora_target="all",
    hidden_size=4096,
    intermediate_size=11008,
    num_layers=32,
    num_heads=32
):
    """计算 LoRA 参数量"""
    
    print("=" * 60)
    print(f"📊 LoRA 参数量计算 - {model_name}")
    print("=" * 60)
    
    # 原始模型参数（近似值）
    if "8B" in model_name:
        total_params = 8_000_000_000  # 80亿
    elif "7B" in model_name:
        total_params = 7_000_000_000  # 70亿
    else:
        total_params = 8_000_000_000  # 默认
    
    print(f"\n📦 模型配置:")
    print(f"  • Hidden Size: {hidden_size}")
    print(f"  • Intermediate Size: {intermediate_size}")
    print(f"  • Number of Layers: {num_layers}")
    print(f"  • LoRA Rank: {lora_rank}")
    print(f"  • LoRA Target: {lora_target}")
    
    # 计算每种模块的 LoRA 参数
    lora_params = 0
    details = []
    
    if lora_target == "all" or "q_proj" in lora_target:
        # Attention 模块
        # Q, K, V, O projections
        attention_params_per_layer = 4 * (hidden_size * lora_rank * 2)
        total_attention = attention_params_per_layer * num_layers
        lora_params += total_attention
        details.append(("Attention (Q,K,V,O)", total_attention))
    
    if lora_target == "all" or "gate_proj" in lora_target:
        # FFN 模块
        # gate_proj + up_proj: hidden_size -> intermediate_size
        ffn_up_params = 2 * (hidden_size * lora_rank + lora_rank * intermediate_size)
        # down_proj: intermediate_size -> hidden_size
        ffn_down_params = intermediate_size * lora_rank + lora_rank * hidden_size
        
        ffn_params_per_layer = ffn_up_params + ffn_down_params
        total_ffn = ffn_params_per_layer * num_layers
        lora_params += total_ffn
        details.append(("FFN (gate,up,down)", total_ffn))
    
    # 打印详细信息
    print(f"\n🔍 LoRA 参数分布:")
    for name, params in details:
        print(f"  • {name}: {params:,} ({params/1e6:.2f}M)")
    
    print(f"\n📊 统计结果:")
    print(f"  • LoRA 总参数: {lora_params:,} ({lora_params/1e6:.2f}M)")
    print(f"  • 原始模型参数: {total_params:,} ({total_params/1e9:.1f}B)")
    print(f"  • LoRA 占比: {lora_params/total_params*100:.3f}%")
    print(f"  • 参数缩减: {total_params/lora_params:.1f}x")
    
    # 显存估算
    param_memory = lora_params * 2 / 1e9  # FP16, 2 bytes per param
    optimizer_memory = lora_params * 4 / 1e9  # Adam states
    total_memory = param_memory + optimizer_memory
    
    print(f"\n💾 显存估算 (仅 LoRA 部分):")
    print(f"  • 参数显存 (FP16): {param_memory:.3f} GB")
    print(f"  • 优化器状态: {optimizer_memory:.3f} GB")
    print(f"  • 总计: {total_memory:.3f} GB")
    
    # 不同 rank 对比
    print(f"\n📈 不同 Rank 的参数量对比:")
    for r in [4, 8, 16, 32, 64, 128]:
        params_r = calculate_params_for_rank(r, hidden_size, intermediate_size, num_layers, lora_target)
        percentage = params_r / total_params * 100
        print(f"  • Rank {r:3d}: {params_r/1e6:6.1f}M ({percentage:.3f}%)")
    
    return lora_params

def calculate_params_for_rank(rank, hidden_size, intermediate_size, num_layers, lora_target):
    """计算特定 rank 的参数量"""
    params = 0
    if lora_target == "all":
        # Attention
        params += 4 * (hidden_size * rank * 2) * num_layers
        # FFN
        params += (2 * (hidden_size * rank + rank * intermediate_size) + 
                  intermediate_size * rank + rank * hidden_size) * num_layers
    return params

if __name__ == "__main__":
    # Qwen3-8B 配置
    calculate_lora_params(
        model_name="Qwen3-8B",
        lora_rank=8,
        lora_target="all",
        hidden_size=4096,
        intermediate_size=11008,
        num_layers=32,
        num_heads=32
    )
    
    print("\n" + "=" * 60)
    print("💡 建议:")
    print("  • Rank 8: 适合大多数任务，平衡效果和效率")
    print("  • Rank 16: 复杂任务，需要更强表达能力")
    print("  • Rank 32+: 接近全量微调效果，但失去效率优势")
    print("  • Alpha = 2×Rank: 常用设置，提供稳定的学习率缩放")
    print("=" * 60)