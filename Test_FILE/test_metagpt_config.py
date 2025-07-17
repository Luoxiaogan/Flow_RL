#!/usr/bin/env python3
"""
测试 MetaGPT LLM 配置的正确格式
"""

import sys
import os

# 添加 ScoreFlow 路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOREFLOW_PATH = os.path.join(os.path.dirname(CURRENT_DIR))
sys.path.append(SCOREFLOW_PATH)

def test_metagpt_config():
    """测试 MetaGPT 的配置格式"""
    print("=== 测试 MetaGPT LLM 配置 ===")
    
    try:
        from metagpt.provider.llm_provider_registry import create_llm_instance, LLMType
        from metagpt.configs.llm_config import LLMConfig
        from metagpt.llm import LLM
        
        print("✓ 成功导入 MetaGPT 模块")
        
        # 测试 1: 查看 LLMConfig 的结构
        print("\n1. 查看 LLMConfig 类的属性:")
        config_attrs = [attr for attr in dir(LLMConfig) if not attr.startswith('_')]
        print("LLMConfig 属性:", config_attrs)
        
        # 测试 2: 创建一个 LLMConfig 实例
        print("\n2. 创建 LLMConfig 实例:")
        try:
            llm_config = LLMConfig(
                api_type=LLMType.OPENAI,
                model="qwen-turbo",
                api_key="test-key",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            print("✓ LLMConfig 创建成功")
            print("LLMConfig 实例属性:", [attr for attr in dir(llm_config) if not attr.startswith('_')])
            
            # 检查关键属性
            print("api_type:", getattr(llm_config, 'api_type', 'NOT_FOUND'))
            print("use_system_prompt:", getattr(llm_config, 'use_system_prompt', 'NOT_FOUND'))
            print("proxy:", getattr(llm_config, 'proxy', 'NOT_FOUND'))
            print("pricing_plan:", getattr(llm_config, 'pricing_plan', 'NOT_FOUND'))
            
        except Exception as e:
            print("✗ LLMConfig 创建失败:", e)
            import traceback
            traceback.print_exc()
        
        # 测试 3: 使用 LLM 函数
        print("\n3. 测试 LLM 函数:")
        try:
            llm = LLM(llm_config)
            print("✓ LLM 创建成功:", type(llm))
        except Exception as e:
            print("✗ LLM 创建失败:", e)
            import traceback
            traceback.print_exc()
            
        # 测试 4: 直接使用 create_llm_instance
        print("\n4. 测试 create_llm_instance:")
        try:
            llm = create_llm_instance(llm_config)
            print("✓ create_llm_instance 成功:", type(llm))
        except Exception as e:
            print("✗ create_llm_instance 失败:", e)
            import traceback
            traceback.print_exc()
        
    except ImportError as e:
        print("✗ 导入 MetaGPT 模块失败:", e)
        import traceback
        traceback.print_exc()

def test_alternative_config():
    """测试替代配置方法"""
    print("\n=== 测试替代配置方法 ===")
    
    try:
        from metagpt.config2 import Config
        print("✓ 导入 Config 成功")
        
        # 创建 Config 实例
        config = Config()
        print("Config 属性:", [attr for attr in dir(config) if not attr.startswith('_')][:20])  # 只显示前20个
        
        # 查看 llm 相关属性
        if hasattr(config, 'llm'):
            print("config.llm 属性:", [attr for attr in dir(config.llm) if not attr.startswith('_')][:20])
        
    except Exception as e:
        print("✗ Config 测试失败:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metagpt_config()
    test_alternative_config()
