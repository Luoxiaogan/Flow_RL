#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Local test script for evaluation system
Can run without GPU or actual models
"""
import os
import sys
import json
import asyncio
import random
from pathlib import Path
from datetime import datetime
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("本地评估系统测试")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python: {sys.version}")
print(f"工作目录: {os.getcwd()}")
print("="*60)


class SimpleModelSimulator:
    """简单的模型模拟器"""
    
    def __init__(self, name="mock-model"):
        self.name = name
        print(f"\n[模拟] 创建模型: {name}")
    
    def generate(self, prompt_text):
        """生成模拟的 workflow 代码"""
        # 模拟不同质量的代码生成
        quality = random.choice(['good', 'medium', 'poor'])
        
        if quality == 'good':
            code = """<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
    
    async def run_workflow(self):
        # High quality workflow
        analysis = await self.generate(
            instruction="Analyze the problem thoroughly",
            context=self.problem_text
        )
        solution = await self.generate(
            instruction=f"Based on analysis: {analysis}, solve the problem",
            context=self.problem_text
        )
        refined = await self.revise(
            instruction="Verify and improve the solution",
            context=solution
        )
        return refined
</code>"""
        elif quality == 'medium':
            code = """<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
    
    async def run_workflow(self):
        # Medium quality workflow
        result = await self.generate(
            instruction="Solve the problem",
            context=self.problem_text
        )
        return result
</code>"""
        else:
            code = """<code>
class Workflow:
    def __init__(self, config, problem):
        self.problem_text = problem
    
    async def run_workflow(self):
        # Poor quality workflow
        return "42"
</code>"""
        
        return code


class SimpleRewardCalculator:
    """简单的奖励计算器"""
    
    def __init__(self):
        self.evaluation_count = 0
        print("\n[模拟] 创建奖励计算器")
    
    def calculate_score(self, code, benchmark):
        """计算模拟分数"""
        self.evaluation_count += 1
        
        # 基于代码长度和 benchmark 类型给分
        base_score = len(code) / 2000.0  # 代码越长分数越高（简单模拟）
        base_score = min(base_score, 0.8)  # 最高 0.8
        
        # 根据 benchmark 调整
        if 'gsm8k' in benchmark:
            score = base_score + random.uniform(0.1, 0.2)
        elif 'drop' in benchmark:
            score = base_score + random.uniform(0.05, 0.15)
        else:
            score = base_score + random.uniform(0.0, 0.1)
        
        # 10% 概率失败
        if random.random() < 0.1:
            return {'success': False, 'score': 0.0, 'error': '模拟超时'}
        
        return {
            'success': True,
            'score': min(score, 1.0),
            'message': f'评估 #{self.evaluation_count}'
        }


async def run_local_test():
    """运行本地测试"""
    
    print("\n" + "="*60)
    print("开始本地测试")
    print("="*60)
    
    # 1. 创建测试数据
    print("\n[步骤 1] 创建测试数据")
    
    test_samples = []
    benchmarks = ['workflow_gsm8k', 'workflow_drop', 'workflow_high_level_math']
    
    for i in range(10):
        sample = {
            'data_source': random.choice(benchmarks),
            'prompt': [
                {'role': 'system', 'content': 'You are a workflow generator.'},
                {'role': 'user', 'content': f'Problem {i}: Calculate something...'}
            ],
            'reward_model': {'ground_truth': 'default'},
            'extra_info': {
                'test_cases': [i*10, i*10+1, i*10+2],
                'data_path': 'local_test.jsonl'
            }
        }
        test_samples.append(sample)
    
    print(f"[OK] 创建了 {len(test_samples)} 个测试样本")
    
    # 分布统计
    for benchmark in benchmarks:
        count = sum(1 for s in test_samples if benchmark in s['data_source'])
        print(f"  - {benchmark}: {count} 个")
    
    # 2. 模拟模型生成
    print("\n[步骤 2] 模拟模型生成")
    
    model = SimpleModelSimulator("llama-3-8b-mock")
    solutions = []
    
    for i, sample in enumerate(test_samples):
        print(f"  生成 {i+1}/{len(test_samples)}...", end='\r')
        code = model.generate(str(sample['prompt']))
        solutions.append(code)
        await asyncio.sleep(0.1)  # 模拟延迟
    
    print(f"✓ 生成了 {len(solutions)} 个解决方案")
    
    # 3. 计算分数
    print("\n[步骤 3] 计算评估分数")
    
    calculator = SimpleRewardCalculator()
    scores = []
    
    for i, (sample, solution) in enumerate(zip(test_samples, solutions)):
        print(f"  评估 {i+1}/{len(test_samples)}...", end='\r')
        score = calculator.calculate_score(solution, sample['data_source'])
        scores.append(score)
        await asyncio.sleep(0.05)  # 模拟延迟
    
    print(f"✓ 完成 {len(scores)} 个评估")
    
    # 4. 生成报告
    print("\n[步骤 4] 生成评估报告")
    
    # 导入真实的报告生成器
    from evaluation.report_generator import ReportGenerator
    
    report_dir = Path('local_test_reports')
    report_dir.mkdir(exist_ok=True)
    
    generator = ReportGenerator(str(report_dir))
    
    checkpoint_info = {
        'step': 1000,
        'path': './local-test-checkpoint',
        'output_dir': './local-test-output'
    }
    
    report = await generator.generate_report(scores, checkpoint_info, test_samples)
    
    # 5. 显示结果
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    
    print(f"\n📊 总体统计:")
    print(f"  总样本数: {report['total_samples']}")
    print(f"  总体得分: {report['overall_score']:.2%}")
    print(f"  成功率: {report['success_rate']:.2%}")
    
    print(f"\n📈 各 Benchmark 成绩:")
    for benchmark, stats in report['benchmark_scores'].items():
        benchmark_name = benchmark.replace('workflow_', '')
        print(f"\n  {benchmark_name}:")
        print(f"    样本数: {stats['num_samples']}")
        print(f"    成功率: {stats['success_rate']:.1%}")
        print(f"    平均分: {stats['mean_score']:.3f}")
        print(f"    最高分: {stats['max_score']:.3f}")
        print(f"    最低分: {stats['min_score']:.3f}")
    
    print(f"\n📁 报告已保存到: {report_dir}/")
    print(f"  - JSON: eval_checkpoint_1000.json")
    print(f"  - Markdown: eval_checkpoint_1000.md")
    print(f"  - CSV: eval_checkpoint_1000_details.csv")
    
    # 6. 测试评估回调
    print("\n[步骤 5] 测试评估回调集成")
    
    # 保存测试数据文件
    test_file = Path('local_test_data.jsonl')
    with open(test_file, 'w', encoding='utf-8') as f:
        for sample in test_samples[:5]:  # 只用5个样本测试
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # 测试回调初始化
    from evaluation.evaluation_callback import EvaluationCallback
    
    eval_config = {
        'test_data_path': str(test_file),
        'reward_server_url': 'http://localhost:8899',
        'eval_batch_size': 2,
        'async_eval': False,
        'eval_interval': 1,
        'output_dir': 'local_callback_test',
        'max_samples': 5
    }
    
    try:
        callback = EvaluationCallback(eval_config)
        print("✓ EvaluationCallback 初始化成功")
        
        # 测试数据加载
        loaded_data = callback._load_test_data()
        print(f"✓ 成功加载 {len(loaded_data)} 个测试样本")
        
    except Exception as e:
        print(f"✗ EvaluationCallback 测试失败: {e}")
    
    # 清理
    test_file.unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("✅ 本地测试完成！")
    print("="*60)
    
    print("\n💡 提示:")
    print("1. 这是一个完全本地的模拟测试")
    print("2. 不需要 GPU 或实际模型")
    print("3. 分数是随机生成的，仅用于测试流程")
    print("4. 真实使用时需要:")
    print("   - 启动 reward server")
    print("   - 有训练好的模型 checkpoint")
    print("   - 真实的测试数据集")
    
    return True


def main():
    """主函数"""
    try:
        # 运行异步测试
        success = asyncio.run(run_local_test())
        
        if success:
            print("\n✅ 所有测试通过！")
            return 0
        else:
            print("\n❌ 测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return 1
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)