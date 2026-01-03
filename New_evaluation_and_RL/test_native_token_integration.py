"""
测试集成后的MetaGPT原生Token追踪功能
验证internbootcamp_reward_utils.py中的token统计是否正常工作
"""

import asyncio
import json
from pathlib import Path

# 导入修改后的模块
from internbootcamp_reward_server.internbootcamp_reward_utils import (
    compute_score,
    _compute_score_async,
    GLOBAL_TOKEN_TRACKER
)


async def test_single_workflow():
    """测试单个workflow的token追踪"""
    print("\n" + "="*80)
    print("🧪 测试单个Workflow的Token追踪")
    print("="*80)
    
    # 准备测试数据
    test_solution = """
<code>
class InternBootcampWorkflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        
        # 生成初步解决方案
        solution = await self.generate(
            instruction="Analyze the problem and provide a solution",
            context=""
        )
        
        # 改进解决方案
        improved = await self.revise(
            instruction="Improve the solution with more details",
            context=solution
        )
        
        return improved
</code>
"""
    
    test_extra_info = {
        'task_name': 'adidyoumean',
        'test_cases': ["{'input': 'hello'}"]  # 单个测试用例
    }
    
    print("📝 执行workflow...")
    score = await _compute_score_async(test_solution, "default", test_extra_info)
    
    print(f"\n✅ 测试完成")
    print(f"   得分: {score:.3f}")
    
    # 验证token统计
    print("\n🔍 验证Token统计:")
    stats = GLOBAL_TOKEN_TRACKER.get_summary()
    print(f"   总Workflows数: {stats['workflows_processed']}")
    print(f"   总Tokens: {stats['total_tokens']}")


async def test_multiple_workflows():
    """测试多个workflow的token追踪"""
    print("\n" + "="*80)
    print("🧪 测试多个Workflows的Token追踪")
    print("="*80)
    
    # 从train.jsonl加载测试数据
    train_file = Path("generate_parquet_and_jsonl/internbootcamp_data_test/train.jsonl")
    
    if not train_file.exists():
        print(f"⚠️  测试文件不存在: {train_file}")
        print("   使用模拟数据...")
        
        # 使用模拟数据
        test_cases = [
            {
                'task_name': 'aalmostarithmeticalprogression',
                'test_cases': ["{'n': 2, 'b': [3, 5], 'ans': 2}"]
            },
            {
                'task_name': 'adidyoumean',
                'test_cases': ["{'input': 'hellno'}"]
            }
        ]
    else:
        # 读取真实数据
        test_cases = []
        with open(train_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 2:  # 只测试前2个
                    break
                data = json.loads(line)
                extra_info = data.get('extra_info', {})
                if extra_info:
                    test_cases.append({
                        'task_name': extra_info.get('task_name', 'unknown'),
                        'test_cases': extra_info.get('test_cases', [])[:1]  # 只取第一个test case
                    })
    
    print(f"📚 准备测试 {len(test_cases)} 个workflows")
    
    # 执行每个测试
    for i, test_case in enumerate(test_cases):
        print(f"\n▶️  执行Workflow {i+1}/{len(test_cases)}: {test_case['task_name']}")
        
        # 创建简单的workflow代码
        workflow_solution = f"""
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
    
    async def run_workflow(self):
        result = await self.generate(
            instruction="Solve this {test_case['task_name']} problem step by step",
            context=""
        )
        return "[answer]test_answer[/answer]"
</code>
"""
        
        extra_info = {
            'task_name': test_case['task_name'],
            'test_cases': test_case['test_cases']
        }
        
        try:
            score = await _compute_score_async(workflow_solution, "default", extra_info)
            print(f"   ✅ 完成 - 得分: {score:.3f}")
        except Exception as e:
            print(f"   ❌ 失败 - {str(e)[:100]}")
    
    print("\n" + "="*80)
    print("📊 最终统计验证")
    print("="*80)
    
    # 获取最终统计
    final_stats = GLOBAL_TOKEN_TRACKER.get_summary()
    print(f"✅ 总计处理Workflows: {final_stats['workflows_processed']}")
    print(f"✅ 总输入Tokens: {final_stats['total_prompt_tokens']:,}")
    print(f"✅ 总输出Tokens: {final_stats['total_completion_tokens']:,}")
    print(f"✅ 总Tokens: {final_stats['total_tokens']:,}")


async def main():
    """主测试函数"""
    print("\n" + "🚀"*40)
    print("测试MetaGPT原生Token追踪集成")
    print("验证internbootcamp_reward_utils.py的修改")
    print("🚀"*40)
    
    # 测试1：单个workflow
    await test_single_workflow()
    
    # 测试2：多个workflows
    await test_multiple_workflows()
    
    print("\n" + "✨"*40)
    print("所有测试完成！")
    print("✨"*40)
    
    # 打印最终汇总
    print("\n📊 最终汇总:")
    GLOBAL_TOKEN_TRACKER.print_total_stats()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())