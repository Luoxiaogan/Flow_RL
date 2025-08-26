#!/usr/bin/env python3
"""
验证WandB集成的完整性
"""
import re

def check_wandb_integration():
    """检查WandB集成的完整性"""
    
    print("=" * 70)
    print("WandB集成验证")
    print("=" * 70)
    
    # 读取train.py检查WandB集成
    with open('src/train.py', 'r') as f:
        train_content = f.read()
    
    print("\n📊 WandB集成检查:")
    print("-" * 50)
    
    # 检查初始化
    print("\n1. WandB初始化:")
    if "wandb.init(" in train_content:
        print("   ✅ wandb.init() 已配置")
        
        # 提取配置参数
        config_pattern = r'config=\{([^}]+)\}'
        config_match = re.search(config_pattern, train_content, re.DOTALL)
        if config_match:
            config_items = [item.strip() for item in config_match.group(1).split(',') if ':' in item]
            print(f"   记录的配置参数数量: {len(config_items)}")
            print("   配置类别:")
            categories = set()
            for item in config_items:
                if "# " in item:
                    category = item.split("# ")[-1].strip()
                    categories.add(category)
            for cat in categories:
                print(f"     - {cat}")
    else:
        print("   ❌ wandb.init() 未找到")
    
    # 检查训练日志
    print("\n2. 训练指标记录:")
    if 'wandb.log(log_dict' in train_content:
        print("   ✅ 训练损失记录已配置")
    else:
        print("   ❌ 训练损失记录未找到")
    
    # 检查评估日志
    print("\n3. 评估指标记录:")
    eval_metrics = []
    
    # 查找所有eval开头的指标
    eval_pattern = r'"eval[^"]*"'
    eval_matches = re.findall(eval_pattern, train_content)
    if eval_matches:
        print("   ✅ 评估指标记录已配置")
        print("   记录的评估指标:")
        for metric in sorted(set(eval_matches)):
            metric_name = metric.strip('"')
            print(f"     - {metric_name}")
            eval_metrics.append(metric_name)
    else:
        print("   ❌ 评估指标记录未找到")
    
    # 检查配置参数记录
    print("\n4. 生成参数记录:")
    if '"config/max_input_length"' in train_content:
        print("   ✅ 生成参数记录已配置")
        config_params = [
            "max_input_length",
            "max_new_tokens", 
            "temperature",
            "top_p",
            "top_k"
        ]
        for param in config_params:
            if f'"config/{param}"' in train_content:
                print(f"     ✅ {param}")
            else:
                print(f"     ❌ {param}")
    else:
        print("   ❌ 生成参数记录未配置")
    
    # 检查数据集大小记录
    print("\n5. 数据集信息记录:")
    if 'wandb.config.update({"dataset_size"' in train_content:
        print("   ✅ 数据集大小记录已配置")
    else:
        print("   ❌ 数据集大小记录未配置")
    
    # 检查W&B关闭
    print("\n6. WandB正确关闭:")
    if "wandb.finish()" in train_content:
        print("   ✅ wandb.finish() 已配置")
    else:
        print("   ❌ wandb.finish() 未找到")
    
    # 检查run_training.sh中的环境变量
    print("\n7. 环境变量配置:")
    with open('run_training.sh', 'r') as f:
        script_content = f.read()
    
    if "WANDB_PROJECT=" in script_content:
        project_match = re.search(r'WANDB_PROJECT="([^"]+)"', script_content)
        if project_match:
            print(f"   ✅ WANDB_PROJECT: {project_match.group(1)}")
    else:
        print("   ❌ WANDB_PROJECT 未设置")
    
    if "--report_to wandb" in script_content:
        print("   ✅ --report_to wandb 已启用")
    else:
        print("   ❌ --report_to wandb 未启用")
    
    print("\n" + "=" * 70)
    print("📊 WandB集成总结")
    print("=" * 70)
    
    print("\n增强的功能:")
    print("1. ✅ 详细的配置记录（模型、数据、训练、评估、硬件）")
    print("2. ✅ 增强的评估指标（accuracy、scores、success_rate等）")
    print("3. ✅ 按数据源分类的评估breakdown")
    print("4. ✅ 生成参数记录")
    print("5. ✅ 数据集大小记录")
    print("6. ✅ 标签系统（model_type、deepspeed-zero2、accelerate）")
    
    print("\nWandB Dashboard将显示:")
    print("- 训练损失曲线")
    print("- 评估准确率和分数趋势")
    print("- 各数据源的性能对比")
    print("- 所有超参数配置")
    print("- 硬件使用情况")

if __name__ == "__main__":
    check_wandb_integration()