#!/usr/bin/env python3
"""
测试debug模式的功能
"""
import os
import sys
import yaml
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 从scoreflow_reward_utils导入compute_score函数
from reward_server.scoreflow_reward_utils import compute_score

def test_debug_mode(debug_enabled: bool):
    """测试debug模式"""
    print(f"\n{'='*60}")
    print(f"测试Debug模式: {'开启' if debug_enabled else '关闭'}")
    print(f"{'='*60}\n")
    
    # 临时修改配置文件
    config_file = PROJECT_ROOT / "config.yaml"
    
    # 读取原始配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 备份原始debug设置
    original_debug = config['services']['scoreflow_reward']['debug']
    
    # 设置新的debug值
    config['services']['scoreflow_reward']['debug'] = debug_enabled
    
    # 写回配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    try:
        # 测试workflow代码
        test_solution = """
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the math problem step by step.")
        return solution
</code>
"""
        
        # 测试参数
        test_extra_info = {
            'data_path': 'gsm8k/test.jsonl',
            'test_cases': [0, 1, 2],  # 使用前3个测试用例
        }
        
        # 执行测试
        print("开始执行测试...")
        score = compute_score('gsm8k', test_solution, "default", test_extra_info)
        
        print(f"\n最终得分: {score:.3f}")
        
        # 检查是否创建了workspace目录
        workspace_path = PROJECT_ROOT / "workspace"
        if workspace_path.exists():
            # 列出workspace中的内容
            gsm8k_dir = workspace_path / "gsm8k"
            if gsm8k_dir.exists():
                workflow_dirs = list(gsm8k_dir.iterdir())
                if workflow_dirs:
                    print(f"\n📁 创建了 {len(workflow_dirs)} 个workflow目录:")
                    for d in workflow_dirs[:3]:  # 只显示前3个
                        print(f"   - {d.name}")
                        # 列出目录中的文件
                        files = list(d.iterdir())
                        if files:
                            print(f"     包含 {len(files)} 个文件")
                else:
                    print("\n✅ 没有创建workflow目录（符合预期）")
            else:
                print("\n✅ 没有创建gsm8k目录（符合预期）")
        else:
            print("\n✅ 没有创建workspace目录（符合预期）")
        
    finally:
        # 恢复原始配置
        config['services']['scoreflow_reward']['debug'] = original_debug
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print(f"\n✅ 已恢复原始debug配置: {original_debug}")

def main():
    """主函数"""
    print("\n" + "="*80)
    print("开始测试Debug模式功能")
    print("="*80)
    
    # 测试debug=false
    print("\n1. 测试 debug=false（最小化输出，不保存文件）")
    test_debug_mode(False)
    
    print("\n" + "-"*80)
    
    # 测试debug=true
    print("\n2. 测试 debug=true（完整输出，保存所有文件）")
    test_debug_mode(True)
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

if __name__ == "__main__":
    main()