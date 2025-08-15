#!/usr/bin/env python
"""
SGLang 服务器调试脚本
用于诊断SGLang启动问题
"""
import sys
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sglang_server import ModelConfig, InferenceManager
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_sglang_server():
    """测试SGLang服务器启动"""
    
    # 配置 - 请根据实际情况修改
    model_path = "/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft_new/checkpoint-200"
    port = 30000
    
    print("=" * 60)
    print("SGLang 服务器调试模式")
    print("=" * 60)
    print(f"模型路径: {model_path}")
    print(f"端口: {port}")
    print("=" * 60)
    
    # 检查模型路径是否存在
    model_dir = Path(model_path)
    if not model_dir.exists():
        print(f"❌ 错误: 模型路径不存在: {model_path}")
        return
    
    print(f"✓ 模型路径存在")
    
    # 检查模型文件
    important_files = [
        "config.json",
        "tokenizer_config.json",
        "model.safetensors",  # 或者其他模型文件格式
        "pytorch_model.bin",
        "model-00001-of-*.safetensors"  # 分片模型
    ]
    
    print("\n检查模型文件:")
    found_any = False
    for pattern in important_files:
        if pattern.endswith("*"):
            # 处理通配符模式
            base_pattern = pattern.replace("*", "")
            files = list(model_dir.glob(pattern))
            if files:
                print(f"  ✓ 找到: {pattern} ({len(files)} 个文件)")
                found_any = True
        else:
            file_path = model_dir / pattern
            if file_path.exists():
                print(f"  ✓ 找到: {pattern}")
                found_any = True
            else:
                # 不一定所有文件都必须存在
                pass
    
    if not found_any:
        print("  ⚠ 警告: 未找到常见的模型文件，请检查模型格式")
    
    # 创建配置
    config = ModelConfig(
        model_type="local",
        model_path=model_path,
        port=port,
        tensor_parallel=1,
        temperature=0.7,
        max_tokens=4096
    )
    
    # 创建管理器（启用调试模式）
    print("\n启动SGLang服务器（调试模式）...")
    print("-" * 60)
    
    manager = InferenceManager(config, debug=True)
    
    # 尝试初始化（增加超时时间）
    success = manager.initialize(timeout=180)  # 3分钟超时
    
    if success:
        print("-" * 60)
        print("✓ 服务器启动成功！")
        
        # 测试推理
        print("\n测试推理...")
        try:
            response = await manager.generate("你好，请问1+1等于几？")
            print(f"响应: {response}")
            print("✓ 推理测试成功！")
        except Exception as e:
            print(f"❌ 推理测试失败: {e}")
        
        # 关闭服务器
        print("\n关闭服务器...")
        manager.close()
        print("✓ 服务器已关闭")
    else:
        print("-" * 60)
        print("❌ 服务器启动失败")
        print("\n可能的原因:")
        print("1. 模型格式不兼容")
        print("2. GPU内存不足")
        print("3. SGLang版本问题")
        print("4. 缺少必要的依赖")
        print("\n建议:")
        print("1. 检查GPU状态: nvidia-smi")
        print("2. 检查SGLang版本: pip show sglang")
        print("3. 尝试直接运行SGLang命令查看错误:")
        print(f"   python -m sglang.launch_server --model-path {model_path} --port {port} --tp 1")

if __name__ == "__main__":
    asyncio.run(test_sglang_server())