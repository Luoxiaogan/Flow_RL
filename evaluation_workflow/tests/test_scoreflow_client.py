#!/usr/bin/env python3
"""
测试 ScoreFlow HTTP 客户端
验证不需要 MetaGPT 环境即可调用评分服务
"""

import sys
import logging
from pathlib import Path

# 添加项目路径
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_without_metagpt():
    """测试在没有 MetaGPT 的环境中使用 ScoreFlow"""
    print("\n=== 测试 ScoreFlow HTTP 客户端 ===\n")
    
    # 1. 测试导入（不应该需要 MetaGPT）
    print("1. 测试导入 scoreflow_client...")
    try:
        from evaluation.scoreflow_client import (
            compute_score_via_api,
            test_connection,
            ScoreFlowClient
        )
        print("   ✓ 成功导入 scoreflow_client（不需要 MetaGPT）")
    except ImportError as e:
        print(f"   ✗ 导入失败: {e}")
        return False
    
    # 2. 测试连接
    print("\n2. 测试 ScoreFlow 服务连接...")
    if test_connection():
        print("   ✓ ScoreFlow 服务正在运行")
    else:
        print("   ✗ ScoreFlow 服务未运行")
        print("   请在另一个终端（有 MetaGPT 的环境）中启动：")
        print("     cd services && ./start_scoreflow_reward.sh")
        return False
    
    # 3. 测试客户端类
    print("\n3. 测试 ScoreFlowClient 类...")
    try:
        client = ScoreFlowClient()
        print("   ✓ 客户端初始化成功")
        
        # 获取配置
        config = client.get_config()
        if config:
            print(f"   ✓ 获取服务配置成功")
        else:
            print("   ⚠ 无法获取服务配置")
    except Exception as e:
        print(f"   ✗ 客户端初始化失败: {e}")
        return False
    
    # 4. 测试评分功能
    print("\n4. 测试评分功能...")
    try:
        test_code = """
class Workflow:
    def __init__(self):
        pass
        
    def execute(self):
        return "test"
"""
        score = compute_score_via_api(
            data_source="gsm8k",
            solution_str=test_code,
            extra_info={"test_mode": True}
        )
        print(f"   ✓ 评分调用成功，返回分数: {score}")
    except Exception as e:
        print(f"   ✗ 评分调用失败: {e}")
        return False
    
    # 5. 测试 evaluate_model.py 的导入
    print("\n5. 测试 evaluate_model.py 导入...")
    try:
        # 模拟 evaluate_model.py 的导入逻辑
        from evaluation.scoreflow_client import compute_score_via_api as scoreflow_compute_score
        print("   ✓ 使用 HTTP API 方式导入成功")
        
        # 测试函数是否可调用
        if callable(scoreflow_compute_score):
            print("   ✓ 评分函数可调用")
        else:
            print("   ✗ 评分函数不可调用")
            return False
            
    except ImportError as e:
        print(f"   ✗ 导入失败: {e}")
        return False
    
    return True


def test_metagpt_not_needed():
    """验证不需要 MetaGPT"""
    print("\n=== 验证 MetaGPT 依赖 ===\n")
    
    # 尝试导入 MetaGPT（应该失败）
    print("1. 检查 MetaGPT 是否存在...")
    try:
        import metagpt
        print("   ⚠ MetaGPT 已安装（但不是必需的）")
    except ImportError:
        print("   ✓ MetaGPT 未安装（这是正常的）")
    
    # 确认 scoreflow_client 不需要 MetaGPT
    print("\n2. 确认 scoreflow_client 不依赖 MetaGPT...")
    import ast
    client_file = PROJECT_ROOT / "evaluation" / "scoreflow_client.py"
    with open(client_file, 'r') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    if 'metagpt' in imports:
        print("   ✗ scoreflow_client 导入了 MetaGPT（不应该）")
        return False
    else:
        print("   ✓ scoreflow_client 不依赖 MetaGPT")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ScoreFlow HTTP 客户端测试")
    print("=" * 60)
    
    # 测试不需要 MetaGPT
    metagpt_test = test_metagpt_not_needed()
    
    # 测试客户端功能
    client_test = test_without_metagpt()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if metagpt_test:
        print("✓ 不依赖 MetaGPT")
    else:
        print("✗ 存在 MetaGPT 依赖")
    
    if client_test:
        print("✓ HTTP 客户端工作正常")
    else:
        print("✗ HTTP 客户端有问题")
    
    if metagpt_test and client_test:
        print("\n🎉 所有测试通过！可以在不同环境中运行：")
        print("  Terminal 1 (MetaGPT): 运行 scoreflow_reward_server")
        print("  Terminal 2 (SGLang): 运行 evaluate_model")
    else:
        print("\n⚠️ 有测试失败，请检查配置")
    
    sys.exit(0 if (metagpt_test and client_test) else 1)