#!/usr/bin/env python3
"""
测试generation_config处理逻辑
验证模型配置和evaluation配置的合并是否正确
"""
import yaml
import json
from pathlib import Path
from typing import Dict

def load_evaluation_config(config_path: str) -> Dict:
    """加载evaluation_config.yaml"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def simulate_model_generation_config(model_type: str) -> Dict:
    """模拟模型自带的generation_config.json"""
    configs = {
        'llama': {
            "bos_token_id": 128000,
            "do_sample": True,
            "eos_token_id": [128001, 128008, 128009],
            "temperature": 0.6,
            "top_p": 0.9,
            "transformers_version": "4.42.3"
        },
        'qwen': {
            "bos_token_id": 151643,
            "pad_token_id": 151643,
            "do_sample": True,
            "eos_token_id": [151645, 151643],
            "repetition_penalty": 1.05,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "transformers_version": "4.37.0"
        }
    }
    return configs.get(model_type, {})

def merge_configs(model_config: Dict, eval_config: Dict) -> Dict:
    """模拟配置合并逻辑"""
    # Step 1: 使用模型配置作为基础
    final_config = model_config.copy()
    
    # Step 2: 从evaluation_config.yaml的generation部分覆盖
    generation_params = eval_config.get('generation', {})
    
    override_params = {
        'max_new_tokens': generation_params.get('max_new_tokens', 2048),
        'temperature': generation_params.get('temperature', 0.7),
        'top_p': generation_params.get('top_p', 0.95),
        'do_sample': generation_params.get('do_sample', True),
    }
    
    # 添加可选参数
    if 'top_k' in generation_params:
        override_params['top_k'] = generation_params['top_k']
    if 'repetition_penalty' in generation_params:
        override_params['repetition_penalty'] = generation_params['repetition_penalty']
    if 'num_beams' in generation_params:
        override_params['num_beams'] = generation_params['num_beams']
    if 'early_stopping' in generation_params:
        override_params['early_stopping'] = generation_params['early_stopping']
    
    # 覆盖
    final_config.update(override_params)
    
    return final_config

def main():
    print("=" * 60)
    print("Generation Config 合并测试")
    print("=" * 60)
    
    # 加载evaluation_config.yaml
    config_path = Path(__file__).parent / "configs" / "evaluation_config.yaml"
    eval_config = load_evaluation_config(config_path)
    
    print("\n📄 Evaluation Config (generation部分):")
    print(json.dumps(eval_config.get('generation', {}), indent=2))
    
    # 测试两种模型
    for model_type in ['llama', 'qwen']:
        print(f"\n\n{'='*60}")
        print(f"测试 {model_type.upper()} 模型")
        print('='*60)
        
        # 获取模型配置
        model_config = simulate_model_generation_config(model_type)
        print(f"\n📦 模型自带的generation_config.json:")
        print(json.dumps(model_config, indent=2))
        
        # 合并配置
        final_config = merge_configs(model_config, eval_config)
        print(f"\n✅ 最终合并后的配置:")
        print(json.dumps(final_config, indent=2))
        
        # 分析变化
        print(f"\n🔍 配置变化分析:")
        for key in final_config:
            if key in model_config:
                if final_config[key] != model_config[key]:
                    print(f"  ✏️  {key}: {model_config[key]} → {final_config[key]} (被覆盖)")
                else:
                    print(f"  ✓  {key}: {final_config[key]} (保持不变)")
            else:
                print(f"  ➕ {key}: {final_config[key]} (新增)")
    
    print("\n" + "="*60)
    print("📝 优先级说明:")
    print("  1. 最高：evaluation_config.yaml中的参数")
    print("  2. 中等：模型自带的generation_config.json")
    print("  3. 最低：代码中的默认值")
    print("="*60)

if __name__ == "__main__":
    main()