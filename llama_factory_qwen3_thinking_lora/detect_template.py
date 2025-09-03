#!/usr/bin/env python
"""
检测 LLaMA-Factory 训练时实际使用的 template
"""

import sys
import yaml
import json
import os
from pathlib import Path

def detect_template(config_file):
    """检测配置文件中的 template 设置和模型实际的 chat_template"""
    
    print("=" * 70)
    print("🔍 检测实际使用的 Chat Template")
    print("=" * 70)
    
    # 1. 读取配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    model_path = config.get('model_name_or_path', '')
    template_setting = config.get('template', None)
    enable_thinking = config.get('enable_thinking', None)
    
    print(f"\n📋 配置文件: {config_file}")
    print(f"📦 模型路径: {model_path}")
    print(f"⚙️  template 参数: {template_setting if template_setting else '未设置（将使用模型自带）'}")
    print(f"🧠 enable_thinking: {enable_thinking if enable_thinking is not None else '未设置'}")
    
    # 2. 检查模型的 tokenizer_config.json
    if os.path.exists(model_path):
        tokenizer_config_path = os.path.join(model_path, "tokenizer_config.json")
        if os.path.exists(tokenizer_config_path):
            with open(tokenizer_config_path, 'r', encoding='utf-8') as f:
                tokenizer_config = json.load(f)
            
            has_chat_template = 'chat_template' in tokenizer_config
            
            print(f"\n📄 Tokenizer 配置:")
            print(f"   - 文件路径: {tokenizer_config_path}")
            print(f"   - chat_template 存在: {'✅ 是' if has_chat_template else '❌ 否'}")
            
            if has_chat_template:
                template_str = tokenizer_config['chat_template']
                print(f"\n📝 Chat Template 内容预览:")
                print("-" * 50)
                # 显示前500字符
                print(template_str[:500])
                if len(template_str) > 500:
                    print("... [内容过长，已截断]")
                print("-" * 50)
                
                # 检测 thinking 相关关键词
                thinking_keywords = ['thinking', 'Thinking', 'THINKING', 'think', 'thought']
                has_thinking = any(keyword in template_str for keyword in thinking_keywords)
                print(f"\n🧠 Thinking 模式检测: {'✅ 模板包含 thinking 支持' if has_thinking else '❌ 模板未检测到 thinking 关键词'}")
    else:
        print(f"\n⚠️  注意: 模型路径 {model_path} 在本地不存在")
        print("   训练时将尝试从 Hugging Face 下载")
    
    # 3. 判断实际使用的 template
    print("\n" + "=" * 70)
    print("📊 结论：实际使用的 Template")
    print("=" * 70)
    
    if template_setting:
        if template_setting in ['default', 'empty']:
            print(f"✅ 将使用: 模型自带的 tokenizer_config.json 中的 chat_template")
            print(f"   原因: template 设置为 '{template_setting}'")
        else:
            print(f"✅ 将使用: LLaMA-Factory 内置的 '{template_setting}' 模板")
            print(f"   原因: 明确指定了 template 参数")
    else:
        print(f"✅ 将使用: 模型自带的 tokenizer_config.json 中的 chat_template")
        print(f"   原因: template 参数未设置或被注释")
    
    if enable_thinking is None:
        print(f"\n💡 Thinking 模式: 由 chat_template 自动决定")
    else:
        print(f"\n💡 Thinking 模式: {'启用' if enable_thinking else '禁用'}")
    
    print("\n" + "=" * 70)
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python detect_template.py <config_file.yaml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在: {config_file}")
        sys.exit(1)
    
    sys.exit(detect_template(config_file))