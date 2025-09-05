#!/usr/bin/env python
"""
检查 Qwen3-8B 模型的 tokenizer_config.json 中的 chat_template
"""

import json
import os
from transformers import AutoTokenizer

def check_tokenizer_template(model_path):
    """检查模型的 tokenizer 配置"""
    print(f"检查模型: {model_path}\n")
    
    # 1. 检查 tokenizer_config.json 文件
    config_path = os.path.join(model_path, "tokenizer_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print("=" * 60)
        print("tokenizer_config.json 内容:")
        print("=" * 60)
        
        # 检查是否有 chat_template
        if 'chat_template' in config:
            print("\n✅ 找到 chat_template 字段!")
            print("\nChat Template 内容:")
            print("-" * 40)
            print(config['chat_template'][:500])  # 只显示前500字符
            if len(config['chat_template']) > 500:
                print("... (内容过长，已截断)")
            print("-" * 40)
        else:
            print("\n❌ 未找到 chat_template 字段")
            
        # 显示其他相关字段
        print("\n其他相关字段:")
        for key in ['eos_token', 'bos_token', 'pad_token', 'unk_token', 'sep_token']:
            if key in config:
                print(f"  - {key}: {config[key]}")
    else:
        print(f"❌ 文件不存在: {config_path}")
    
    # 2. 尝试加载 tokenizer 并测试
    print("\n" + "=" * 60)
    print("使用 Transformers 加载 tokenizer:")
    print("=" * 60)
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        
        print("✅ Tokenizer 加载成功")
        
        # 检查 tokenizer 的 chat_template 属性
        if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template:
            print("\n✅ tokenizer.chat_template 存在")
            print(f"类型: {type(tokenizer.chat_template)}")
        else:
            print("\n❌ tokenizer.chat_template 不存在或为空")
            
        # 测试 apply_chat_template
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ]
        
        print("\n测试 apply_chat_template:")
        print("-" * 40)
        try:
            # 尝试应用 chat template
            formatted = tokenizer.apply_chat_template(
                test_messages,
                tokenize=False,
                add_generation_prompt=False
            )
            print("✅ apply_chat_template 成功!")
            print("\n格式化后的文本:")
            print(formatted[:500])  # 只显示前500字符
            if len(formatted) > 500:
                print("... (内容过长，已截断)")
        except Exception as e:
            print(f"❌ apply_chat_template 失败: {e}")
            
    except Exception as e:
        print(f"❌ 加载 tokenizer 失败: {e}")

def main():
    # 检查本地路径
    local_model_path = "/nas/models/Qwen3-8B"
    
    if os.path.exists(local_model_path):
        check_tokenizer_template(local_model_path)
    else:
        print(f"❌ 模型路径不存在: {local_model_path}")
        print("\n尝试使用 Hugging Face 模型名称...")
        check_tokenizer_template("Qwen/Qwen3-8B")

if __name__ == "__main__":
    main()