#!/usr/bin/env python3
"""
比较不同处理方法的chat template结果
展示原始数据、处理后数据、以及tokenizer应用后的差异
"""

import json
import yaml
import os
from pathlib import Path
from transformers import AutoTokenizer

def get_project_root():
    """从root.yaml获取项目根路径"""
    try:
        script_dir = Path(__file__).parent
        root_config_path = script_dir / "configs" / "root.yaml"
        
        with open(root_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config.get('root', '/nas/ganluo/Flow_RL')
    except Exception:
        return '/nas/ganluo/Flow_RL'

def load_first_record(filepath):
    """加载JSONL文件的第一条记录"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            return json.loads(first_line)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_to_file(content, filepath):
    """保存内容到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Saved to: {filepath}")

def truncate_content(text, max_chars=1000):
    """截断过长的内容用于显示"""
    if len(text) > max_chars:
        return text[:max_chars] + f"\n... (truncated, total {len(text)} chars) ..."
    return text

def main():
    print("=" * 80)
    print("Chat Template Comparison Tool")
    print("=" * 80)
    
    # 文件路径
    project_root = get_project_root()
    base_dir = os.path.join(project_root, "training_data")
    original_file = os.path.join(base_dir, "0813_workspace_drop_COT_qwen_max/filtered_training_data.jsonl")
    llama_file = os.path.join(base_dir, "0813_filter之后的COT_SFT数据/merged_training_data_llama.jsonl")
    qwen_file = os.path.join(base_dir, "0813_filter之后的COT_SFT数据/merged_training_data_qwen.jsonl")
    
    # 检查文件是否存在
    for filepath in [original_file, llama_file, qwen_file]:
        if not Path(filepath).exists():
            print(f"❌ File not found: {filepath}")
            return
    
    # 1. 加载原始数据
    print("\n📁 Loading original data...")
    original_record = load_first_record(original_file)
    if not original_record:
        return
    
    messages = original_record.get("messages", [])
    print(f"✅ Original record loaded: {len(messages)} messages")
    
    # 显示messages结构
    print("\n📋 Messages structure:")
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content_length = len(msg.get('content', ''))
        print(f"  Message {i}: role='{role}', content_length={content_length}")
    
    # 2. 加载处理后的数据
    print("\n📁 Loading processed data...")
    llama_record = load_first_record(llama_file)
    qwen_record = load_first_record(qwen_file)
    
    # 显示处理后数据的差异
    print("\n🔍 Processed data differences:")
    print("LLaMA format keys:", list(llama_record.keys()) if llama_record else "N/A")
    print("Qwen format keys:", list(qwen_record.keys()) if qwen_record else "N/A")
    
    # 3. 加载tokenizers（使用本地路径模拟）
    print("\n🤖 Loading tokenizers...")
    
    # 注意：这里使用模拟路径，实际服务器上应该使用：
    # qwen_model_path = "/nas/models/Qwen2.5-7B-Instruct"
    # llama_model_path = "/nas/models/Meta-Llama-3.1-8B-Instruct"
    
    # 为了演示，我们使用Hugging Face model IDs（需要网络）
    # 在服务器上请替换为实际路径
    try:
        print("Loading Qwen tokenizer...")
        qwen_tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen2.5-7B-Instruct",
            trust_remote_code=True
        )
        print("✅ Qwen tokenizer loaded")
    except Exception as e:
        print(f"⚠️ Could not load Qwen tokenizer: {e}")
        print("Using fallback tokenizer...")
        qwen_tokenizer = None
    
    try:
        print("Loading LLaMA tokenizer...")
        llama_tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            trust_remote_code=True
        )
        print("✅ LLaMA tokenizer loaded")
    except Exception as e:
        print(f"⚠️ Could not load LLaMA tokenizer: {e}")
        print("Using fallback tokenizer...")
        llama_tokenizer = None
    
    # 4. 应用chat templates
    print("\n🔄 Applying chat templates...")
    
    results = {}
    
    # 4.1 Qwen处理
    if qwen_tokenizer:
        print("\n--- Qwen Chat Template ---")
        qwen_formatted = qwen_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        results['qwen_formatted'] = qwen_formatted
        
        # 显示格式化后的文本（截断显示）
        print("Formatted text preview:")
        print(truncate_content(qwen_formatted, 800))
        
        # 保存完整版本
        save_to_file(qwen_formatted, "output_qwen_formatted.txt")
        
        # Tokenize示例（只处理前500字符以避免太长）
        print("\n🔢 Qwen Tokenization example:")
        tokens = qwen_tokenizer(
            qwen_formatted[:500],
            truncation=True,
            max_length=100,
            return_tensors=None
        )
        print(f"Token IDs (first 20): {tokens['input_ids'][:20]}")
        print(f"Total tokens: {len(tokens['input_ids'])}")
    
    # 4.2 LLaMA处理
    if llama_tokenizer:
        print("\n--- LLaMA Chat Template ---")
        llama_formatted = llama_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        results['llama_formatted'] = llama_formatted
        
        # 显示格式化后的文本（截断显示）
        print("Formatted text preview:")
        print(truncate_content(llama_formatted, 800))
        
        # 保存完整版本
        save_to_file(llama_formatted, "output_llama_formatted.txt")
        
        # Tokenize示例
        print("\n🔢 LLaMA Tokenization example:")
        tokens = llama_tokenizer(
            llama_formatted[:500],
            truncation=True,
            max_length=100,
            return_tensors=None
        )
        print(f"Token IDs (first 20): {tokens['input_ids'][:20]}")
        print(f"Total tokens: {len(tokens['input_ids'])}")
    
    # 5. 训练流程说明
    print("\n" + "=" * 80)
    print("📚 Training Pipeline Explanation:")
    print("=" * 80)
    print("""
    1️⃣ Raw Data: {"messages": [...]} format
       ↓
    2️⃣ Apply Chat Template: tokenizer.apply_chat_template(messages)
       - Qwen: Uses ChatML format with <|im_start|> and <|im_end|>
       - LLaMA: Uses special tokens like <|begin_of_text|> and <|start_header_id|>
       ↓
    3️⃣ Formatted Text: String with special tokens
       ↓
    4️⃣ Tokenization: tokenizer(formatted_text)
       ↓
    5️⃣ Token IDs: List of integers for model input
    """)
    
    # 6. generation_config.json说明
    print("\n📝 About generation_config.json:")
    print("-" * 40)
    print("""
    generation_config.json is used ONLY during inference/generation, NOT training:
    
    - Contains default parameters like:
      * temperature, top_p, top_k
      * max_length, min_length
      * repetition_penalty
      * eos_token_id, pad_token_id
    
    - Used when calling model.generate() or pipeline("text-generation")
    - Training ignores this file completely
    - Each model can have different default generation settings
    """)
    
    # 7. 关键差异总结
    if qwen_tokenizer and llama_tokenizer:
        print("\n🎯 Key Differences Summary:")
        print("-" * 40)
        
        # 比较长度
        if 'qwen_formatted' in results and 'llama_formatted' in results:
            qwen_len = len(results['qwen_formatted'])
            llama_len = len(results['llama_formatted'])
            print(f"Qwen formatted length: {qwen_len} chars")
            print(f"LLaMA formatted length: {llama_len} chars")
            print(f"Difference: {abs(qwen_len - llama_len)} chars")
        
        print("""
        Main differences:
        1. Special tokens format (Qwen: <|im_start|>, LLaMA: <|start_header_id|>)
        2. Token vocabulary (different tokenizer.json)
        3. Default chat template structure
        4. Metadata handling in processed files
        """)
    
    print("\n✅ Comparison complete! Check the output files for full formatted texts.")
    print("   - output_qwen_formatted.txt")
    print("   - output_llama_formatted.txt")

if __name__ == "__main__":
    main()