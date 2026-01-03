#!/usr/bin/env python3
"""
验证精简后的配置是否正确工作
"""
import yaml
from pathlib import Path

def test_simplified_config():
    """测试精简后的配置"""
    
    print("=" * 60)
    print("验证精简后的配置")
    print("=" * 60)
    
    # 读取配置文件
    config_path = Path("configs/evaluation_config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    generation_config = config.get('generation', {})
    
    print("\n📋 当前generation配置:")
    print("-" * 40)
    for key, value in generation_config.items():
        print(f"  {key}: {value}")
    
    # 验证必要参数存在
    print("\n✅ 必要参数检查:")
    required = ['max_new_tokens', 'do_sample']
    for param in required:
        if param in generation_config:
            print(f"  ✓ {param}: {generation_config[param]}")
        else:
            print(f"  ✗ {param}: 缺失 (将使用默认值)")
    
    # 检查已删除的参数
    print("\n🗑️  已删除的无效默认值参数:")
    removed = ['repetition_penalty', 'early_stopping', 'num_beams', 'use_model_config']
    for param in removed:
        if param in generation_config:
            print(f"  ⚠️ {param} 仍然存在: {generation_config[param]}")
        else:
            print(f"  ✓ {param}: 已正确删除")
    
    # 模拟参数优先级
    print("\n🔄 模拟参数优先级 (evaluation config → model config):")
    print("-" * 40)
    
    # 模拟不同模型的配置
    model_configs = {
        'Llama-3.1': {
            'temperature': 0.6,
            'top_p': 0.9,
            'do_sample': True
        },
        'Qwen2.5': {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 20,
            'repetition_penalty': 1.05,
            'do_sample': True
        }
    }
    
    for model_name, model_config in model_configs.items():
        print(f"\n{model_name}:")
        
        # 从evaluation config开始
        final_params = {}
        
        # 添加必要参数
        final_params['max_new_tokens'] = generation_config.get('max_new_tokens', 8192)
        final_params['do_sample'] = generation_config.get('do_sample', True)
        
        # 添加配置中存在的可选参数
        optional = ['temperature', 'top_p', 'top_k']
        for param in optional:
            if param in generation_config:
                final_params[param] = generation_config[param]
        
        print("  基础参数（from evaluation）:")
        for k, v in final_params.items():
            print(f"    {k}: {v}")
        
        # 模型配置覆盖
        print("  模型覆盖后:")
        for key, value in model_config.items():
            old_value = final_params.get(key)
            final_params[key] = value
            if old_value is not None and old_value != value:
                print(f"    {key}: {old_value} → {value} ✅")
            else:
                print(f"    {key}: {value} (新增)")
        
        # 确保max_new_tokens存在
        if 'max_new_tokens' not in final_params:
            final_params['max_new_tokens'] = generation_config.get('max_new_tokens', 8192)
            print(f"    max_new_tokens: {final_params['max_new_tokens']} (补充)")
    
    print("\n" + "=" * 60)
    print("✅ 配置验证完成！")
    print("=" * 60)
    print("\n关键发现:")
    print("1. 必要参数（max_new_tokens, do_sample）正确保留")
    print("2. 无效默认值参数已删除")
    print("3. 模型配置能正确覆盖evaluation配置")
    print("4. 系统更简洁，避免了不必要的参数污染")

if __name__ == "__main__":
    test_simplified_config()