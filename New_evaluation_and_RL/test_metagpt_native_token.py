"""
测试MetaGPT原生Token追踪功能
使用MetaGPT内置的CostManager来追踪每个workflow的token使用情况
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import importlib

# 设置路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MetaGPT imports
from metagpt.context import Context
from metagpt.utils.cost_manager import CostManager, Costs
from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.llm_provider_registry import create_llm_instance


class MetaGPTNativeTokenTracker:
    """
    使用MetaGPT原生功能的Token追踪器
    为每个workflow创建独立的Context和CostManager
    """
    
    def __init__(self):
        """初始化追踪器"""
        self.workflow_contexts = {}  # workflow_id -> Context
        self.workflow_results = {}   # workflow_id -> execution result
        self.total_stats = {
            'total_workflows': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_cost': 0.0,
            'workflows': []
        }
        logger.info("MetaGPT Native Token Tracker initialized")
    
    def create_workflow_context(self, workflow_id: str) -> Context:
        """
        为workflow创建独立的Context和CostManager
        
        Args:
            workflow_id: workflow的唯一标识
        
        Returns:
            配置好的Context实例
        """
        # 创建新的Context
        context = Context()
        
        # 创建独立的CostManager
        cost_manager = CostManager()
        cost_manager.max_budget = 100.0  # 设置预算上限
        
        # 关联到context
        context.cost_manager = cost_manager
        
        # 保存到字典
        self.workflow_contexts[workflow_id] = context
        
        logger.info(f"Created context for workflow: {workflow_id}")
        return context
    
    def get_workflow_stats(self, workflow_id: str) -> Dict:
        """
        获取指定workflow的token统计
        
        Args:
            workflow_id: workflow标识
        
        Returns:
            包含token统计信息的字典
        """
        context = self.workflow_contexts.get(workflow_id)
        if not context:
            logger.warning(f"No context found for workflow: {workflow_id}")
            return {}
        
        # 获取costs信息
        costs = context.cost_manager.get_costs()
        
        return {
            'workflow_id': workflow_id,
            'prompt_tokens': costs.total_prompt_tokens,
            'completion_tokens': costs.total_completion_tokens,
            'total_tokens': costs.total_prompt_tokens + costs.total_completion_tokens,
            'total_cost': costs.total_cost,
            'budget': costs.total_budget
        }
    
    def print_workflow_stats(self, workflow_id: str):
        """
        打印workflow的详细token统计
        
        Args:
            workflow_id: workflow标识
        """
        stats = self.get_workflow_stats(workflow_id)
        
        if not stats:
            print(f"\n❌ No statistics found for workflow: {workflow_id}")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 Token统计 - Workflow: {workflow_id}")
        print(f"{'='*80}")
        print(f"  📝 输入Token (Prompt):     {stats['prompt_tokens']:,}")
        print(f"  💬 输出Token (Completion): {stats['completion_tokens']:,}")
        print(f"  📈 总计Token:              {stats['total_tokens']:,}")
        print(f"  💰 估算成本:               ${stats['total_cost']:.6f}")
        print(f"  💳 预算限制:               ${stats['budget']:.2f}")
        print(f"{'='*80}\n")
    
    def update_total_stats(self, workflow_id: str):
        """
        更新总体统计信息
        
        Args:
            workflow_id: workflow标识
        """
        stats = self.get_workflow_stats(workflow_id)
        if stats and stats.get('total_tokens', 0) > 0:
            self.total_stats['total_workflows'] += 1
            self.total_stats['total_prompt_tokens'] += stats['prompt_tokens']
            self.total_stats['total_completion_tokens'] += stats['completion_tokens']
            self.total_stats['total_cost'] += stats['total_cost']
            self.total_stats['workflows'].append(stats)
    
    def print_total_stats(self):
        """打印所有workflow的汇总统计"""
        print(f"\n{'⭐'*40}")
        print(f"{'='*80}")
        print(f"🏆 总体Token统计汇总 (MetaGPT Native)")
        print(f"{'='*80}")
        print(f"  📊 处理的Workflows数:      {self.total_stats['total_workflows']}")
        print(f"  📝 总输入Token:            {self.total_stats['total_prompt_tokens']:,}")
        print(f"  💬 总输出Token:            {self.total_stats['total_completion_tokens']:,}")
        print(f"  🎯 总计Token:              {(self.total_stats['total_prompt_tokens'] + self.total_stats['total_completion_tokens']):,}")
        print(f"  💰 总估算成本:             ${self.total_stats['total_cost']:.6f}")
        
        if self.total_stats['total_workflows'] > 0:
            avg_tokens = (self.total_stats['total_prompt_tokens'] + 
                         self.total_stats['total_completion_tokens']) / self.total_stats['total_workflows']
            print(f"  📈 平均每个Workflow:       {avg_tokens:.0f} tokens")
        
        print(f"{'='*80}")
        print(f"{'⭐'*40}\n")


class WorkflowExecutor:
    """
    Workflow执行器，集成MetaGPT原生token追踪
    """
    
    def __init__(self, tracker: MetaGPTNativeTokenTracker):
        """
        初始化执行器
        
        Args:
            tracker: Token追踪器实例
        """
        self.tracker = tracker
        self.llm_config = self._get_default_llm_config()
        
    def _get_default_llm_config(self) -> Dict:
        """获取默认的LLM配置"""
        return {
            'provider': 'openai',
            'model': 'qwen-turbo',
            'api_key': 'sk-test-key',
            'base_url': 'http://localhost:5009',
            'temperature': 0.7,
            'calc_usage': True  # 重要：启用token计算
        }
    
    async def execute_workflow_with_tracking(self, 
                                            workflow_code: str,
                                            workflow_id: str,
                                            problem_text: str) -> Dict:
        """
        执行workflow并追踪token使用
        
        Args:
            workflow_code: workflow的Python代码
            workflow_id: workflow标识
            problem_text: 问题描述
        
        Returns:
            包含执行结果和token统计的字典
        """
        try:
            # 1. 创建workflow的独立context
            context = self.tracker.create_workflow_context(workflow_id)
            
            # 2. 创建LLM配置（启用calc_usage）
            llm_config = LLMConfig(
                api_type=LLMType.OPENAI,
                model=self.llm_config['model'],
                api_key=self.llm_config['api_key'],
                base_url=self.llm_config['base_url'],
                temperature=self.llm_config['temperature'],
                calc_usage=True  # 启用token计算
            )
            
            # 3. 创建LLM实例并关联cost_manager
            llm = create_llm_instance(llm_config)
            llm.cost_manager = context.cost_manager  # 关键：关联cost_manager
            
            # 4. 准备执行环境
            exec_globals = {
                'asyncio': asyncio,
                'create': lambda config: llm,  # 使用已配置的llm
                'operator': self._get_operator_module(),
                'List': list,
                'Literal': type(None)  # 简化
            }
            
            # 5. 执行workflow代码获取类
            exec_namespace = {}
            exec(workflow_code, exec_globals, exec_namespace)
            
            # 获取Workflow类
            WorkflowClass = exec_namespace.get('Workflow') or exec_namespace.get('InternBootcampWorkflow')
            if not WorkflowClass:
                raise ValueError(f"No Workflow class found in code for {workflow_id}")
            
            # 6. 实例化workflow（传入已配置好的llm_config）
            workflow_instance = WorkflowClass(config=llm_config, problem=problem_text)
            
            # 7. 确保workflow使用的llm关联了cost_manager
            if hasattr(workflow_instance, 'llm') and workflow_instance.llm:
                workflow_instance.llm.cost_manager = context.cost_manager
            
            # 8. 执行workflow
            logger.info(f"Executing workflow: {workflow_id}")
            start_time = datetime.now()
            
            if hasattr(workflow_instance, 'run_workflow'):
                result = await workflow_instance.run_workflow()
            else:
                result = await workflow_instance()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 9. 获取token统计
            stats = self.tracker.get_workflow_stats(workflow_id)
            
            # 10. 打印统计信息
            self.tracker.print_workflow_stats(workflow_id)
            
            # 11. 更新总体统计
            self.tracker.update_total_stats(workflow_id)
            
            return {
                'workflow_id': workflow_id,
                'result': str(result),
                'execution_time': execution_time,
                'token_stats': stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'workflow_id': workflow_id,
                'error': str(e),
                'success': False
            }
    
    def _get_operator_module(self):
        """获取operator模块（模拟）"""
        # 创建一个mock operator模块
        class MockOperator:
            class Generate:
                def __init__(self, llm, problem):
                    self.llm = llm
                    self.problem = problem
                
                async def __call__(self, instruction: str, context: str = "") -> str:
                    # 模拟生成
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{instruction}\n\nContext: {context or self.problem}"}
                    ]
                    response = await self.llm.aask("\n".join([m["content"] for m in messages]))
                    return response
            
            class Revise:
                def __init__(self, llm, problem):
                    self.llm = llm
                    self.problem = problem
                
                async def __call__(self, instruction: str, context: str) -> str:
                    messages = [
                        {"role": "system", "content": "You are a helpful editor."},
                        {"role": "user", "content": f"{instruction}\n\nText to revise: {context}"}
                    ]
                    response = await self.llm.aask("\n".join([m["content"] for m in messages]))
                    return response
            
            class Summarize:
                def __init__(self, llm, problem):
                    self.llm = llm
                    self.problem = problem
                
                async def __call__(self, instruction: str, context: str) -> str:
                    messages = [
                        {"role": "user", "content": f"Summarize: {context}\nInstruction: {instruction}"}
                    ]
                    response = await self.llm.aask("\n".join([m["content"] for m in messages]))
                    return response
            
            class Ensemble:
                def __init__(self, llm, problem):
                    self.llm = llm
                    self.problem = problem
                
                async def __call__(self, instruction: str, contexts: List[str]) -> str:
                    combined = "\n---\n".join(contexts)
                    messages = [
                        {"role": "user", "content": f"{instruction}\n\nOptions:\n{combined}"}
                    ]
                    response = await self.llm.aask("\n".join([m["content"] for m in messages]))
                    return response
        
        return MockOperator()


async def test_single_workflow():
    """测试单个workflow的token追踪"""
    print("\n" + "="*80)
    print("🧪 测试单个Workflow的Token追踪 (MetaGPT Native)")
    print("="*80)
    
    # 创建追踪器和执行器
    tracker = MetaGPTNativeTokenTracker()
    executor = WorkflowExecutor(tracker)
    
    # 简单的测试workflow
    test_workflow_code = """
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        
        # 测试生成
        result1 = await self.generate(
            instruction="Analyze the problem and provide a solution approach",
            context=""
        )
        
        # 测试修订
        result2 = await self.revise(
            instruction="Improve the solution with more detail",
            context=result1
        )
        
        # 测试总结
        final = await self.summarize(
            instruction="Provide the final answer",
            context=result2
        )
        
        return final
"""
    
    # 执行workflow
    result = await executor.execute_workflow_with_tracking(
        workflow_code=test_workflow_code,
        workflow_id="test_workflow_001",
        problem_text="What is 2 + 2?"
    )
    
    print(f"\n✅ Workflow执行{'成功' if result['success'] else '失败'}")
    if result['success']:
        print(f"   执行时间: {result['execution_time']:.2f}秒")
        print(f"   结果预览: {result['result'][:100]}...")


async def test_multiple_workflows():
    """测试多个workflow的token追踪"""
    print("\n" + "="*80)
    print("🧪 测试多个Workflows的Token追踪 (MetaGPT Native)")
    print("="*80)
    
    # 创建追踪器和执行器
    tracker = MetaGPTNativeTokenTracker()
    executor = WorkflowExecutor(tracker)
    
    # 从train.jsonl加载测试数据
    train_file = Path("generate_parquet_and_jsonl/internbootcamp_data_test/train.jsonl")
    
    if not train_file.exists():
        print(f"❌ 测试文件不存在: {train_file}")
        return
    
    # 读取前3条数据
    test_cases = []
    with open(train_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 3:  # 只测试前3个
                break
            data = json.loads(line)
            test_cases.append(data)
    
    print(f"📚 加载了 {len(test_cases)} 个测试用例")
    
    # 执行每个测试用例
    for i, test_case in enumerate(test_cases):
        workflow_id = f"workflow_{i:03d}"
        print(f"\n▶️  执行 {workflow_id}...")
        
        # 提取prompt（简化处理）
        user_prompt = test_case['prompt'][1]['content'] if len(test_case['prompt']) > 1 else "Test problem"
        
        # 创建简单的测试workflow
        workflow_code = f"""
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
    
    async def run_workflow(self):
        result = await self.generate(
            instruction="Solve this problem step by step",
            context=""
        )
        return f"[answer]{i}[/answer]"  # 模拟答案
"""
        
        # 执行
        result = await executor.execute_workflow_with_tracking(
            workflow_code=workflow_code,
            workflow_id=workflow_id,
            problem_text=user_prompt[:500]  # 截断过长的prompt
        )
        
        if result['success']:
            print(f"   ✅ 成功 - Tokens: {result['token_stats'].get('total_tokens', 0)}")
        else:
            print(f"   ❌ 失败 - {result.get('error', 'Unknown error')}")
    
    # 打印总体统计
    tracker.print_total_stats()


async def test_with_real_api():
    """测试与真实API的集成（需要配置正确的API）"""
    print("\n" + "="*80)
    print("🧪 测试真实API集成的Token追踪")
    print("="*80)
    
    # 检查是否有真实的API配置
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "sk-test-key":
        print("⚠️  未配置真实的API密钥，跳过此测试")
        print("   设置环境变量 OPENAI_API_KEY 以启用真实API测试")
        return
    
    tracker = MetaGPTNativeTokenTracker()
    executor = WorkflowExecutor(tracker)
    
    # 更新为真实的API配置
    executor.llm_config = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'api_key': api_key,
        'base_url': 'https://api.openai.com/v1',
        'temperature': 0.7,
        'calc_usage': True
    }
    
    # 执行测试
    result = await executor.execute_workflow_with_tracking(
        workflow_code="""
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
    
    async def run_workflow(self):
        response = await self.llm.aask("What is the capital of France?")
        return response
""",
        workflow_id="real_api_test",
        problem_text="Test with real API"
    )
    
    if result['success']:
        print(f"✅ 真实API测试成功!")
        print(f"   使用的Tokens: {result['token_stats'].get('total_tokens', 0)}")
        print(f"   估算成本: ${result['token_stats'].get('total_cost', 0):.6f}")


async def main():
    """主测试函数"""
    print("\n" + "🚀"*40)
    print("MetaGPT原生Token追踪功能测试")
    print("🚀"*40)
    
    # 测试1：单个workflow
    await test_single_workflow()
    
    # 测试2：多个workflows
    await test_multiple_workflows()
    
    # 测试3：真实API（可选）
    await test_with_real_api()
    
    print("\n" + "✨"*40)
    print("测试完成！")
    print("✨"*40)


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())