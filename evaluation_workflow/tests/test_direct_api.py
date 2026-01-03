#!/usr/bin/env python3
"""
测试直接使用 Alibaba API (不经过 proxy) 的 MetaGPT 配置
"""

import sys
import os
import asyncio
from pathlib import Path

# 设置路径
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
SCOREFLOW_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCOREFLOW_ROOT))

# 设置 MetaGPT 环境
os.environ['METAGPT_PROJECT_ROOT'] = str(SCOREFLOW_ROOT / "Test_FILE")
os.environ['METAGPT_CONFIG'] = str(SCOREFLOW_ROOT / "Test_FILE" / "config" / "config2.yaml")

def colored_print(text: str, color: str = "green"):
    """彩色输出"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

async def test_direct_api_workflow():
    """测试直接使用 API 的完整工作流"""
    print("\n" + "="*60)
    colored_print("测试直接 API 调用 (不使用 proxy)", "cyan")
    print("="*60 + "\n")
    
    try:
        # 1. 导入必要的模块
        from metagpt.configs.llm_config import LLMConfig, LLMType
        from metagpt.provider.llm_provider_registry import create_llm_instance as create
        import ScoreFlow.scripts.common.operator as operator
        
        colored_print("✓ 成功导入 MetaGPT 和 ScoreFlow 模块", "green")
        
        # 2. 创建直接的 API 配置（不经过 proxy）
        config = LLMConfig(
            api_type=LLMType.OPENAI,
            model="qwen-turbo",
            api_key="956c41bd0f31beaf68b871d4987af4bb",
            base_url="https://idealab.alibaba-inc.com/api/openai/v1"
        )
        
        colored_print("✓ 创建直接 API 配置:", "green")
        print(f"  - Base URL: {config.base_url}")
        print(f"  - Model: {config.model}")
        print(f"  - API Type: {config.api_type}")
        
        # 3. 创建 LLM 实例
        print("\n正在创建 LLM 实例...")
        llm = create(config)
        colored_print("✓ 成功创建 LLM 实例", "green")
        
        # 4. 测试简单的 LLM 调用
        print("\n测试 LLM 调用...")
        test_prompt = "请回答：1+1等于几？只回答数字。"
        
        response = await llm.aask(test_prompt)
        colored_print(f"✓ LLM 响应成功: {response}", "green")
        
        # 5. 测试 operator（模拟 Workflow 中的使用）
        print("\n测试 ScoreFlow Operator...")
        problem_text = "计算 15 + 27 的结果"
        
        # 创建 Generate operator（模拟 Workflow 的初始化）
        generate_op = operator.Generate(llm, problem_text)
        colored_print("✓ 成功创建 Generate operator", "green")
        
        # 执行 operator
        instruction = "请计算这个数学问题并给出答案"
        result = await generate_op(instruction=instruction, context="")
        
        colored_print(f"✓ Operator 执行成功", "green")
        print(f"  结果: {result[:100]}..." if len(result) > 100 else f"  结果: {result}")
        
        # 6. 模拟完整的 Workflow 类
        print("\n测试完整的 Workflow 模拟...")
        
        class TestWorkflow:
            def __init__(self, config, problem):
                self.config = config
                self.problem_text = problem
                self.llm = create(config)  # 关键：直接使用 LLMConfig
                
                # 初始化 operators
                self.generate = operator.Generate(self.llm, self.problem_text)
                self.revise = operator.Revise(self.llm, self.problem_text)
                
            async def run_workflow(self):
                # 生成初始解决方案
                solution = await self.generate(
                    instruction="解决这个数学问题，给出详细步骤",
                    context=""
                )
                
                # 修订解决方案
                refined = await self.revise(
                    instruction="检查计算是否正确，如有错误请修正",
                    context=solution
                )
                
                return refined
            
            async def __call__(self):
                return await self.run_workflow()
        
        # 实例化并运行工作流
        workflow = TestWorkflow(config=config, problem="计算 45 * 3 + 12")
        colored_print("✓ 成功创建 Workflow 实例", "green")
        
        workflow_result = await workflow()
        colored_print("✓ Workflow 执行成功", "green")
        print(f"  结果预览: {workflow_result[:150]}..." if len(workflow_result) > 150 else f"  结果: {workflow_result}")
        
        return True
        
    except Exception as e:
        colored_print(f"✗ 测试失败: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

async def test_scoreflow_with_direct_api():
    """测试 ScoreFlow reward 计算器使用直接 API"""
    print("\n" + "="*60)
    colored_print("测试 ScoreFlow Reward 计算器（直接 API）", "cyan")
    print("="*60 + "\n")
    
    try:
        # 临时修改配置以使用直接 API
        import yaml
        
        config_path = PROJECT_ROOT / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 模拟直接 API 配置
        from scoreflow.scoreflow_reward_utils import ScoreFlowRewardCalculator
        
        # 创建计算器实例（它会从 config.yaml 读取配置）
        calculator = ScoreFlowRewardCalculator()
        
        # 临时修改其配置以使用直接 API
        calculator.llm_config = {
            'provider': 'openai',
            'model': 'qwen-turbo',
            'api_key': '956c41bd0f31beaf68b871d4987af4bb',
            'base_url': 'https://idealab.alibaba-inc.com/api/openai/v1',
            'temperature': 0.3
        }
        
        colored_print("✓ 配置 ScoreFlow 使用直接 API", "green")
        print(f"  - Base URL: {calculator.llm_config['base_url']}")
        print(f"  - Model: {calculator.llm_config['model']}")
        
        # 测试简单的工作流代码
        test_workflow = """
class Workflow:
    async def run_workflow(self):
        result = await self.generate(
            instruction="Calculate 25 + 17 and provide the answer",
            context=""
        )
        return f"Final Answer: 42"
"""
        
        print("\n测试工作流执行...")
        score = await calculator.compute_score(
            solution_str=test_workflow,
            data_source="gsm8k",
            ground_truth=None,
            extra_info={
                "test_cases": [0],
                "data_path": "Processed_dataset/gsm8k/test.jsonl"
            }
        )
        
        colored_print(f"✓ ScoreFlow 执行成功，得分: {score}", "green")
        
        return True
        
    except Exception as e:
        colored_print(f"✗ ScoreFlow 测试失败: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """运行所有测试"""
    print("="*60)
    colored_print("直接 API 测试套件", "blue")
    colored_print("（绕过 api_proxy，直接连接 Alibaba API）", "blue")
    print("="*60)
    
    results = []
    
    # 测试1：基础工作流
    test1_result = await test_direct_api_workflow()
    results.append(("直接 API 工作流", test1_result))
    
    # 测试2：ScoreFlow 集成
    # 注意：这可能需要实际的数据文件
    # test2_result = await test_scoreflow_with_direct_api()
    # results.append(("ScoreFlow 集成", test2_result))
    
    # 总结
    print("\n" + "="*60)
    colored_print("测试总结", "blue")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        color = "green" if result else "red"
        colored_print(f"{status} - {name}", color)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        colored_print("\n🎉 所有测试通过！直接 API 配置工作正常。", "green")
        colored_print("这证明了 LLMConfig 可以直接使用，无需 Config 包装。", "yellow")
    
    return passed == total

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)