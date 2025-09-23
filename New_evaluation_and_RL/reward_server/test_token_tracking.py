"""
测试脚本：利用MetaGPT内置的Token统计机制
演示如何在不修改原脚本的情况下获取workflow执行的token消耗
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加必要的路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入必要的模块
from scoreflow_reward_utils import ScoreFlowRewardCalculator
from metagpt.utils.cost_manager import CostManager
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.configs.llm_config import LLMConfig, LLMType


class TokenTrackingCalculator(ScoreFlowRewardCalculator):
    """
    扩展的计算器，添加token追踪功能
    """
    
    def __init__(self, config_path: str = None):
        """初始化并启用token追踪"""
        super().__init__(config_path)
        
        # 存储token统计信息
        self.token_stats = {}
        self.current_workflow_tokens = {
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'api_calls': []
        }
    
    async def execute_workflow_with_token_tracking(self, workflow_code: str, benchmark_name: str, 
                                                   test_case_index: int, dataset_path: str):
        """
        执行workflow并追踪token使用
        
        这个方法演示如何：
        1. 在执行前设置token追踪
        2. 执行workflow
        3. 从workflow实例中提取token统计
        """
        
        print(f"\n{'='*60}")
        print(f"开始执行Workflow - 启用Token追踪")
        print(f"Benchmark: {benchmark_name}, Test Case: {test_case_index}")
        print(f"{'='*60}\n")
        
        try:
            # 1. 加载handler
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                raise ValueError(f"无法加载 {benchmark_name} 的handler")
            
            # 2. 构建可执行脚本
            script_parts = handler.build_executable_script(workflow_code, timeout=self.timeout)
            full_script_code = (
                script_parts["python_start"] + "\n" +
                script_parts["workflow_code"] + "\n" +
                script_parts["python_end"]
            )
            
            # 3. 准备执行环境（与原脚本相同）
            import importlib
            execution_namespace = {}
            
            operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
            
            exec_globals = {
                'asyncio': asyncio,
                'create': create_llm_instance,
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': list,
            }
            
            # 加载operator_an模块
            try:
                common_an_module = importlib.import_module("ScoreFlow.scripts.common.operator_an")
                for attr_name in dir(common_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(common_an_module, attr_name)
            except ModuleNotFoundError:
                pass
            
            # 4. 执行脚本获取Workflow类
            exec(full_script_code, exec_globals, execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            
            if not WorkflowClass:
                raise ValueError("未找到Workflow类")
            
            # 5. 创建启用token追踪的LLM配置
            # 关键点：确保LLM配置包含cost tracking
            provider = self.llm_config.get('provider', 'openai')
            api_type_map = {
                'openai': LLMType.OPENAI, 'azure': LLMType.AZURE,
                'gemini': LLMType.GEMINI, 'claude': LLMType.CLAUDE,
            }
            api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
            
            # 创建带有cost manager的配置
            metagpt_config = LLMConfig(
                api_type=api_type,
                model=self.llm_config.get('model'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url'),
                # 如果MetaGPT版本支持，可以添加额外的cost tracking参数
            )
            
            # 6. 获取问题文本
            problem_text = handler.get_prompt_text([test_case_index])
            
            # 7. 创建workflow实例
            workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            # 8. 尝试访问或创建cost manager
            # MetaGPT的workflow（Role）通常有context属性
            if hasattr(workflow_instance, 'context'):
                context = workflow_instance.context
                
                # 检查是否有cost_manager
                if hasattr(context, 'cost_manager'):
                    print("✅ 找到context.cost_manager")
                    cost_manager = context.cost_manager
                elif hasattr(context, '_cost_manager'):
                    print("✅ 找到context._cost_manager")
                    cost_manager = context._cost_manager
                else:
                    print("⚠️ Context中未找到cost_manager，尝试创建")
                    # 某些版本可能需要手动创建
                    cost_manager = CostManager()
                    context.cost_manager = cost_manager
            else:
                print("⚠️ Workflow实例没有context属性")
                cost_manager = None
            
            # 9. 执行workflow
            print("\n开始执行workflow...")
            
            # 根据签名执行
            if "timeout=" in script_parts.get("call_signature", ""):
                result = await asyncio.wait_for(
                    workflow_instance(timeout=self.timeout),
                    timeout=self.timeout + 10
                )
            else:
                result = await asyncio.wait_for(
                    workflow_instance(),
                    timeout=self.timeout + 10
                )
            
            print(f"\n执行结果: {str(result)[:200]}...")
            
            # 10. 提取token统计信息
            print("\n" + "="*60)
            print("Token使用统计:")
            print("="*60)
            
            token_info = {
                'benchmark': benchmark_name,
                'test_case': test_case_index,
                'timestamp': datetime.now().isoformat()
            }
            
            # 方法1：从cost_manager获取
            if cost_manager:
                try:
                    # MetaGPT的CostManager通常有这些方法
                    if hasattr(cost_manager, 'total_prompt_tokens'):
                        token_info['prompt_tokens'] = cost_manager.total_prompt_tokens
                        print(f"Prompt Tokens: {cost_manager.total_prompt_tokens}")
                    
                    if hasattr(cost_manager, 'total_completion_tokens'):
                        token_info['completion_tokens'] = cost_manager.total_completion_tokens
                        print(f"Completion Tokens: {cost_manager.total_completion_tokens}")
                    
                    if hasattr(cost_manager, 'total_tokens'):
                        token_info['total_tokens'] = cost_manager.total_tokens
                        print(f"Total Tokens: {cost_manager.total_tokens}")
                    
                    if hasattr(cost_manager, 'total_cost'):
                        token_info['total_cost'] = cost_manager.total_cost
                        print(f"Total Cost: ${cost_manager.total_cost:.4f}")
                    
                    # 获取详细的API调用记录
                    if hasattr(cost_manager, 'costs'):
                        token_info['api_calls'] = len(cost_manager.costs)
                        print(f"API调用次数: {len(cost_manager.costs)}")
                        
                        # 打印每次调用的详情
                        for i, cost_record in enumerate(cost_manager.costs[:3]):  # 只显示前3个
                            print(f"\n  调用 {i+1}:")
                            if isinstance(cost_record, dict):
                                for key, value in cost_record.items():
                                    print(f"    {key}: {value}")
                except Exception as e:
                    print(f"⚠️ 从cost_manager提取信息失败: {e}")
            
            # 方法2：从workflow实例的其他属性获取
            if hasattr(workflow_instance, '_llm'):
                llm_instance = workflow_instance._llm
                if hasattr(llm_instance, 'completion_tokens'):
                    print(f"\n从LLM实例获取的tokens: {llm_instance.completion_tokens}")
            
            # 方法3：检查workflow的actions
            if hasattr(workflow_instance, 'actions'):
                total_action_tokens = 0
                for action in workflow_instance.actions:
                    if hasattr(action, 'token_count'):
                        total_action_tokens += action.token_count
                if total_action_tokens > 0:
                    print(f"\n从Actions累计的tokens: {total_action_tokens}")
            
            # 方法4：检查是否有rc (role context)
            if hasattr(workflow_instance, 'rc'):
                rc = workflow_instance.rc
                if hasattr(rc, 'cost_manager'):
                    print("\n从Role Context获取cost_manager")
                    # 提取信息...
            
            print("\n" + "="*60)
            
            return result, token_info
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return None, {}


async def test_token_tracking():
    """
    测试token追踪功能
    """
    print("\n" + "="*80)
    print("MetaGPT Token追踪测试")
    print("="*80)
    
    # 1. 创建带token追踪的计算器
    calculator = TokenTrackingCalculator()
    
    # 2. 准备测试workflow
    test_workflow = """
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def __call__(self, timeout=180):
        # 简单的workflow，调用一次LLM
        solution = await self.custom(
            instruction="Solve this step by step. Be concise."
        )
        return solution
"""
    
    # 3. 测试参数
    benchmark = 'gsm8k'
    test_case = 0
    dataset_path = str(PROJECT_ROOT / 'Processed_dataset' / 'gsm8k' / 'test.jsonl')
    
    # 4. 执行并追踪
    result, token_info = await calculator.execute_workflow_with_token_tracking(
        test_workflow, benchmark, test_case, dataset_path
    )
    
    # 5. 保存统计结果
    output_file = CURRENT_DIR / f"token_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(token_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Token统计已保存到: {output_file}")
    
    # 6. 尝试其他获取token信息的方法
    print("\n" + "="*60)
    print("其他可能的Token获取方法:")
    print("="*60)
    
    # 检查MetaGPT全局统计
    try:
        from metagpt.context import Context
        global_context = Context()
        if hasattr(global_context, 'cost_manager'):
            print("找到全局Context的cost_manager")
    except:
        pass
    
    # 检查环境变量
    if 'METAGPT_COST_TRACKING' in os.environ:
        print(f"METAGPT_COST_TRACKING: {os.environ['METAGPT_COST_TRACKING']}")
    
    print("\n测试完成！")


def explore_metagpt_token_api():
    """
    探索MetaGPT的token统计API
    打印可用的方法和属性
    """
    print("\n" + "="*60)
    print("探索MetaGPT Token统计API")
    print("="*60)
    
    try:
        # 1. 检查CostManager类
        from metagpt.utils.cost_manager import CostManager
        cost_mgr = CostManager()
        
        print("\nCostManager可用方法和属性:")
        for attr in dir(cost_mgr):
            if not attr.startswith('_'):
                print(f"  - {attr}")
                
        # 2. 检查Context类
        from metagpt.context import Context
        ctx = Context()
        
        print("\nContext中与cost相关的属性:")
        for attr in dir(ctx):
            if 'cost' in attr.lower() or 'token' in attr.lower():
                print(f"  - {attr}")
                
    except ImportError as e:
        print(f"导入失败: {e}")
        print("可能需要检查MetaGPT版本")


if __name__ == "__main__":
    # 先探索API
    explore_metagpt_token_api()
    
    # 然后运行测试
    asyncio.run(test_token_tracking())