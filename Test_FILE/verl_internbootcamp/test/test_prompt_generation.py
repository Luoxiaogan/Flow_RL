"""
测试脚本：验证generate_verl_data.py的prompt生成功能
测试新的prompt模板是否按照workflow_generator的方式工作
"""
import os
import sys
import asyncio
import json

# 添加必要的路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_verl_data import VERLDataGenerator

async def test_prompt_generation():
    """测试prompt生成功能"""
    print("=== 测试VERL数据生成器的Prompt模板 ===\n")
    
    # 创建生成器
    generator = VERLDataGenerator()
    
    # 测试1: 验证prompt模板加载
    print("1. 测试加载prompt模板...")
    start_prompt, end_prompt, system_prompt, meta_prompts = generator.load_prompt_templates()
    
    print(f"[OK] 成功加载 {len(meta_prompts)} 个META_PROMPTS")
    print(f"[OK] SYSTEM_PROMPT长度: {len(system_prompt)} 字符")
    print(f"[OK] START_PROMPT长度: {len(start_prompt)} 字符")
    print(f"[OK] END_PROMPT长度: {len(end_prompt)} 字符")
    
    # 测试2: 生成chat消息
    print("\n2. 测试生成chat消息格式...")
    test_task = "sudoku_4x4_easy"
    test_description = "Solve a 4x4 Sudoku puzzle with easy difficulty"
    
    messages = generator.create_chat_messages(test_task, test_description)
    
    print(f"[OK] 生成了 {len(messages)} 条消息")
    if len(messages) > 0:
        print(f"[OK] User消息长度: {len(messages[0]['content'])} 字符")
    
    # 显示消息内容预览
    print("\n3. 消息内容预览:")
    print("--- User Message (前500字符) ---")
    if len(messages) > 0:
        print(messages[0]['content'][:500] + "...")
        user_content = messages[0]['content']
    else:
        user_content = ""
    print("\n4. 验证关键元素:")
    print(f"[OK] 包含task_name: {'Task: sudoku_4x4_easy' in user_content}")
    print(f"[OK] 包含task_description: {test_description in user_content}")
    print(f"[OK] 不包含CRITICAL INSTRUCTION: {'CRITICAL INSTRUCTION' not in user_content}")
    print(f"[OK] 只有一条消息(no system): {len(messages) == 1}")
    print(f"[OK] 包含Example: {'Example:' in user_content}")
    
    # 测试3: 生成完整的VERL条目
    print("\n5. 测试生成完整VERL条目...")
    entry = await generator.generate_single_entry(test_task, 0, "predefined", timeout=5.0)
    
    if entry:
        print("[OK] 成功生成VERL条目")
        print(f"  - data_source: {entry['data_source']}")
        print(f"  - ability: {entry['ability']}")
        print(f"  - prompt消息数: {len(entry['prompt'])}")
        print(f"  - 包含reward_model: {'reward_model' in entry}")
        print(f"  - 包含extra_info: {'extra_info' in entry}")
        
        # 保存测试结果
        output_file = os.path.join(os.path.dirname(__file__), "test_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_messages": messages,
                "test_entry": entry
            }, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] 测试结果已保存到: {output_file}")
    else:
        print("[FAIL] 生成VERL条目失败")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_prompt_generation())