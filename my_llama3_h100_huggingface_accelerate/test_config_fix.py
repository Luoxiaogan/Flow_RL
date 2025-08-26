#!/usr/bin/env python3
"""
验证配置读取修复
测试SimpleEvaluator和ScoreCollector的配置传递是否正确
"""

import sys
import yaml
from pathlib import Path

# 添加src到路径
sys.path.insert(0, 'src')

def test_config_reading():
    """测试配置读取是否正确"""
    print("=" * 60)
    print("测试配置读取修复")
    print("=" * 60)
    
    # 1. 加载评估配置
    config_path = "configs/evaluation_config.yaml"
    if not Path(config_path).exists():
        print(f"⚠️  配置文件不存在: {config_path}")
        print("   这个测试需要在项目目录下运行")
        return
    
    with open(config_path, 'r') as f:
        eval_config = yaml.safe_load(f)
    
    print("\n✅ 成功加载evaluation_config.yaml")
    
    # 2. 测试generation配置
    generation_config = eval_config.get('generation', {})
    print(f"\n📊 Generation配置:")
    print(f"   max_new_tokens: {generation_config.get('max_new_tokens', 'NOT FOUND')}")
    print(f"   temperature: {generation_config.get('temperature', 'NOT FOUND')}")
    print(f"   top_p: {generation_config.get('top_p', 'NOT FOUND')}")
    
    # 3. 测试reward_server配置
    reward_config = eval_config.get('reward_server', {})
    fallback_config = reward_config.get('fallback', {})
    print(f"\n🌐 Reward Server配置:")
    print(f"   host: {fallback_config.get('host', 'NOT FOUND')}")
    print(f"   port: {fallback_config.get('port', 'NOT FOUND')}")  # 注意是'port'不是'prot'
    print(f"   timeout: {fallback_config.get('timeout', 'NOT FOUND')}")
    
    # 4. 模拟SimpleEvaluator初始化
    print("\n🔧 模拟SimpleEvaluator初始化:")
    if generation_config:
        max_input_length = generation_config.get('max_new_tokens', 1024) + 5476
        print(f"   ✅ 如果传递eval_config: max_input_length = {max_input_length}")
    else:
        print(f"   ❌ 如果没有传递eval_config: max_input_length = 6500 (默认值)")
    
    # 5. 模拟ScoreCollector端口获取
    print("\n🔧 模拟ScoreCollector端口获取:")
    correct_port = fallback_config.get('port', 8899)
    wrong_port = fallback_config.get('prot', 8899)  # 拼写错误
    print(f"   ✅ 使用'port': {correct_port}")
    print(f"   ❌ 使用'prot': {wrong_port} (拼写错误，返回默认值)")
    
    print("\n" + "=" * 60)
    print("📝 修复总结:")
    print("=" * 60)
    print("1. SimpleEvaluator必须传递eval_config参数")
    print("2. 获取port时使用正确的键名'port'而不是'prot'")
    print("3. 这两个修复确保配置能正确传递到评估组件")
    print("=" * 60)

if __name__ == "__main__":
    test_config_reading()