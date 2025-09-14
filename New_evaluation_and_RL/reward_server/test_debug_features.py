#!/usr/bin/env python
"""
测试ScoreFlow Reward Server的Debug功能
验证新增的debug机制是否正常工作
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加必要的路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoreflow_reward_utils import compute_score, _compute_score_async

# 测试数据
test_workflow = """
```python
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def __call__(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
```
"""

test_extra_info = {
    'data_path': 'Processed_dataset/gsm8k/test.jsonl',
    'test_cases': [0, 1, 2],  # 使用前3个测试用例
    'raw_data': 0,
    'answer': 'test_answer'
}

async def test_debug_features():
    """测试debug功能"""
    print("="*60)
    print("测试ScoreFlow Reward Server Debug功能")
    print("="*60)
    
    # 临时修改配置文件以启用debug
    config_file = Path(__file__).parent.parent / "config.yaml"
    if config_file.exists():
        import yaml
        
        # 读取当前配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 保存原始debug设置
        original_debug = config.get('services', {}).get('scoreflow_reward', {}).get('debug', False)
        
        # 启用debug
        if 'services' not in config:
            config['services'] = {}
        if 'scoreflow_reward' not in config['services']:
            config['services']['scoreflow_reward'] = {}
        config['services']['scoreflow_reward']['debug'] = True
        
        # 写回配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        
        print("✅ 已启用debug模式")
    else:
        print("⚠️ 配置文件不存在，使用默认设置")
        original_debug = False
    
    try:
        # 执行测试
        print("\n开始执行测试workflow...")
        score = await _compute_score_async('gsm8k', test_workflow, "default", test_extra_info)
        print(f"\n测试完成，得分: {score:.3f}")
        
        # 检查生成的debug文件
        workspace_dir = Path("workspace") if Path("workspace").exists() else Path("New_evaluation_and_RL/workspace")
        if workspace_dir.exists():
            print("\n检查生成的debug文件:")
            
            # 查找最新的workflow目录
            gsm8k_dir = workspace_dir / "gsm8k"
            if gsm8k_dir.exists():
                workflow_dirs = sorted([d for d in gsm8k_dir.iterdir() if d.is_dir()], 
                                     key=lambda x: x.stat().st_mtime, reverse=True)
                
                if workflow_dirs:
                    latest_workflow = workflow_dirs[0]
                    print(f"\n最新的workflow目录: {latest_workflow.name}")
                    
                    # 列出所有debug文件
                    debug_files = [
                        "execution_timeline.jsonl",
                        "execution_timeline_complete.json",
                        "error_analysis.json",
                        "performance_metrics.json",
                        "metagpt_traces"
                    ]
                    
                    for debug_file in debug_files:
                        file_path = latest_workflow / debug_file
                        if file_path.exists():
                            if file_path.is_file():
                                size = file_path.stat().st_size
                                print(f"  ✅ {debug_file} ({size} bytes)")
                                
                                # 显示部分内容
                                if debug_file.endswith('.json'):
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = json.load(f)
                                        if 'execution_stats' in content:
                                            print(f"     - 执行统计: {content['execution_stats']}")
                                        elif 'total_errors' in content:
                                            print(f"     - 错误总数: {content['total_errors']}")
                                        elif 'total_events' in content:
                                            print(f"     - 事件总数: {content['total_events']}")
                            else:
                                # 目录
                                trace_files = list(file_path.glob("*.json"))
                                print(f"  ✅ {debug_file}/ ({len(trace_files)} trace files)")
                                for trace_file in trace_files[:3]:  # 只显示前3个
                                    print(f"     - {trace_file.name}")
                        else:
                            print(f"  ❌ {debug_file} (未生成)")
                else:
                    print("未找到workflow目录")
            else:
                print(f"未找到gsm8k目录: {gsm8k_dir}")
        else:
            print(f"未找到workspace目录: {workspace_dir}")
            
    finally:
        # 恢复原始debug设置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            config['services']['scoreflow_reward']['debug'] = original_debug
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            
            print(f"\n✅ 已恢复debug设置为: {original_debug}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_debug_features())
    print("\n测试完成！")