#!/usr/bin/env python3
"""
测试生成参数优先级逻辑
验证模型配置优先于evaluation配置
"""

def simulate_parameter_priority():
    """模拟参数优先级逻辑"""
    print("=" * 60)
    print("生成参数优先级测试")
    print("=" * 60)
    
    # 模拟evaluation_config.yaml的配置
    eval_config = {
        'max_new_tokens': 2048,
        'temperature': 0.6,
        'top_p': 0.95,
        'top_k': 20,
        'do_sample': True,
        'repetition_penalty': 1.0
    }
    
    # 模拟不同模型的generation_config.json
    models = {
        'Llama-3.1': {
            'temperature': 0.6,
            'top_p': 0.9,
            'do_sample': True,
            # 注意：没有max_new_tokens
        },
        'Qwen2.5': {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 20,
            'repetition_penalty': 1.05,
            'do_sample': True,
            # 注意：没有max_new_tokens
        },
        'Qwen3': {
            'temperature': 0.6,
            'top_p': 0.95,
            'top_k': 20,
            'do_sample': True,
            # 注意：没有max_new_tokens
        }
    }
    
    for model_name, model_config in models.items():
        print(f"\n### {model_name} 模型")
        print("-" * 40)
        
        # Step 1: 从evaluation config开始
        final_config = eval_config.copy()
        print(f"基础配置（evaluation_config）:")
        for k, v in eval_config.items():
            print(f"  {k}: {v}")
        
        # Step 2: 用模型配置覆盖
        print(f"\n模型配置覆盖:")
        for key, value in model_config.items():
            if key != 'transformers_version':
                old_value = final_config.get(key)
                final_config[key] = value
                if old_value != value:
                    print(f"  {key}: {old_value} → {value} ✅ (使用模型的值)")
                else:
                    print(f"  {key}: {value} (相同)")
        
        # Step 3: 检查max_new_tokens
        if 'max_new_tokens' not in model_config:
            print(f"  max_new_tokens: {final_config['max_new_tokens']} (模型没有，使用evaluation的)")
        
        print(f"\n最终配置:")
        important_keys = ['temperature', 'top_p', 'top_k', 'repetition_penalty', 'max_new_tokens']
        for key in important_keys:
            if key in final_config:
                source = "模型" if key in model_config else "evaluation"
                print(f"  {key}: {final_config[key]} (来自{source})")
    
    print("\n" + "=" * 60)
    print("📝 优先级总结:")
    print("=" * 60)
    print("1. 模型generation_config.json中有的参数 → 使用模型的值（优先）")
    print("2. 模型没有但evaluation_config.yaml有的参数 → 使用evaluation的值")
    print("3. 特别注意：max_new_tokens通常只在evaluation配置中")
    print("=" * 60)

if __name__ == "__main__":
    simulate_parameter_priority()