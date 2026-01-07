#!/usr/bin/env python3
"""
测试workflow执行日志保存系统
"""

import os
import sys
import json
import csv
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_workflow_logging():
    """测试workflow日志保存功能"""
    
    print("="*60)
    print("测试Workflow执行日志保存系统")
    print("="*60)
    
    # 准备测试数据
    test_workflow = """
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.generate = operator.Generate(self.config, self.problem)
    
    async def run_workflow(self):
        print("开始执行workflow...")
        solution = await self.generate(instruction="Solve the problem step by step.")
        print(f"生成的解决方案: {solution[:100]}...")
        return solution
    
    async def __call__(self, timeout=300):
        return await self.run_workflow()
"""
    
    # 准备测试请求
    test_data = {
        "data_source": "gsm8k",
        "solution_str": f"<code>\n{test_workflow}\n</code>",
        "ground_truth": "default",
        "extra_info": {
            "test_cases": [0, 1, 2],  # 测试前3个案例
            "data_path": "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k/test.jsonl"
        }
    }
    
    print("\n📝 测试数据准备完成")
    print(f"   Benchmark: {test_data['data_source']}")
    print(f"   Test Cases: {test_data['extra_info']['test_cases']}")
    
    # 发送请求到ScoreFlow Reward服务
    import requests
    
    url = "http://localhost:8899/compute_score"
    
    print(f"\n🚀 发送请求到: {url}")
    
    try:
        response = requests.post(url, json=test_data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 请求成功!")
            print(f"   分数: {result.get('score', 0):.3f}")
            print(f"   消息: {result.get('message', '')}")
            
            # 检查workspace目录
            workspace_path = Path("/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/workspace")
            gsm8k_dir = workspace_path / "gsm8k"
            
            if gsm8k_dir.exists():
                # 找到最新的workflow目录
                workflow_dirs = sorted([d for d in gsm8k_dir.iterdir() if d.is_dir()], 
                                     key=lambda x: x.stat().st_mtime, reverse=True)
                
                if workflow_dirs:
                    latest_dir = workflow_dirs[0]
                    print(f"\n📁 检查日志目录: {latest_dir}")
                    
                    # 列出所有文件
                    files = list(latest_dir.iterdir())
                    print(f"\n📄 生成的文件:")
                    for file in sorted(files):
                        print(f"   - {file.name}")
                    
                    # 检查必要文件是否存在
                    required_files = [
                        "workflow.py",
                        "metadata.json",
                        "results.csv",
                        "summary.json"
                    ]
                    
                    for test_case in test_data['extra_info']['test_cases']:
                        required_files.append(f"test_case_{test_case}.log")
                    
                    missing_files = []
                    for required_file in required_files:
                        if not (latest_dir / required_file).exists():
                            missing_files.append(required_file)
                    
                    if missing_files:
                        print(f"\n⚠️ 缺少文件: {missing_files}")
                    else:
                        print(f"\n✅ 所有必要文件都已生成!")
                        
                        # 读取并显示summary.json
                        summary_file = latest_dir / "summary.json"
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary = json.load(f)
                        
                        print(f"\n📊 执行汇总:")
                        print(f"   Workflow ID: {summary['workflow_id']}")
                        print(f"   总测试案例: {summary['total_test_cases']}")
                        print(f"   成功案例: {summary['successful_cases']}")
                        print(f"   失败案例: {summary['failed_cases']}")
                        print(f"   平均分数: {summary['average_score']:.3f}")
                        print(f"   总耗时: {summary['total_duration']:.2f}秒")
                        
                        # 读取并显示results.csv的前几行
                        results_file = latest_dir / "results.csv"
                        print(f"\n📋 结果CSV内容:")
                        with open(results_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                print(f"   Test Case {row['test_case']}: "
                                    f"成功={row['success']}, "
                                    f"分数={float(row['score']):.1f}, "
                                    f"耗时={float(row['duration']):.2f}秒")
                                if row['error']:
                                    print(f"     错误: {row['error'][:50]}...")
                        
                        # 显示一个test case日志的前几行
                        test_log = latest_dir / f"test_case_{test_data['extra_info']['test_cases'][0]}.log"
                        if test_log.exists():
                            print(f"\n📝 Test Case {test_data['extra_info']['test_cases'][0]} 日志预览:")
                            with open(test_log, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:20]  # 只显示前20行
                                for line in lines:
                                    print(f"   {line.rstrip()}")
                                if len(f.readlines()) > 20:
                                    print("   ...")
                else:
                    print(f"\n⚠️ 没有找到workflow目录")
            else:
                print(f"\n⚠️ workspace目录不存在: {gsm8k_dir}")
                
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(f"   错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到ScoreFlow Reward服务")
        print("   请确保服务正在运行: bash servers_and_proxy/start_scoreflow_reward.sh")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    test_workflow_logging()