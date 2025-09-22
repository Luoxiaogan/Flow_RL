"""
极简Workflow执行器
基于reward_server的执行流程，使用Gemini API作为LLM后端
"""

import asyncio
import sys
import os
import json
import yaml
import traceback
import random
import string
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 设置环境变量和路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载配置
CONFIG_FILE = Path(__file__).parent / "gemini_config.yaml"

class SimpleWorkflowExecutor:
    """
    极简workflow执行器
    模仿reward_server的execute_workflow_metagpt方法
    """

    def __init__(self, config_file: str = None):
        """
        初始化执行器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file) if config_file else CONFIG_FILE
        self.config = self._load_config()
        self._setup_environment()

    def _load_config(self) -> Dict:
        """加载Gemini API配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"[OK] Loaded config file: {self.config_file}")
                return config
        else:
            # 默认配置
            default_config = {
                'llm': {
                    'api_type': 'openai',
                    'base_url': 'http://39.96.211.155:8000/proxy/api/openai/v1',
                    'api_key': '8cf060f9e1f444858609730176542253',
                    'model': 'gemini-2.5-pro',
                    'max_tokens': 2000,
                    'temperature': 0.7
                },
                'paths': {
                    'project_root': str(PROJECT_ROOT),
                    'scoreflow_handlers': '.',
                    'metagpt_root': 'metagpt_root'
                },
                'execution': {
                    'timeout': 1800,
                    'silent': False
                }
            }
            print(f"[WARNING] Config file not found, using default config")
            return default_config

    def _setup_environment(self):
        """设置环境（模仿reward_server）"""
        paths = self.config.get('paths', {})
        project_root = Path(paths.get('project_root', PROJECT_ROOT))

        # 设置ScoreFlow路径
        scoreflow_handlers = paths.get('scoreflow_handlers', '.')
        if scoreflow_handlers == '.':
            scoreflow_path = project_root
        else:
            scoreflow_path = project_root / scoreflow_handlers

        if scoreflow_path.exists():
            sys.path.insert(0, str(scoreflow_path))
            print(f"[OK] Added ScoreFlow path: {scoreflow_path}")

        # 设置MetaGPT路径
        metagpt_root = project_root / paths.get('metagpt_root', 'metagpt_root')
        if metagpt_root.exists():
            sys.path.append(str(metagpt_root))
            os.environ["METAGPT_PROJECT_ROOT"] = str(metagpt_root)
            print(f"[OK] Set MetaGPT path: {metagpt_root}")

        # 创建必要目录
        workspace = metagpt_root / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        # 设置静默模式
        if self.config.get('execution', {}).get('silent', False):
            os.environ['SCOREFLOW_SILENT'] = 'true'
            print("[INFO] Silent mode enabled")

    async def execute_workflow(self, workflow_code: str, problem_text: str,
                              benchmark_name: str = "imo", test_case: int = 0) -> Dict[str, Any]:
        """
        执行workflow代码（模仿execute_workflow_metagpt）

        Args:
            workflow_code: 完整的workflow Python代码
            problem_text: 要解决的问题文本
            benchmark_name: benchmark名称（默认imo）
            test_case: 测试案例编号

        Returns:
            包含结果和执行信息的字典
        """
        exec_start = datetime.now()

        # 生成workflow标识
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        workflow_id = f"exec_{benchmark_name}_{test_case}_{timestamp}_{random_id}"

        print(f"\n{'='*60}")
        print(f"[START] Executing Workflow: {workflow_id}")
        print(f"[INFO] Benchmark: {benchmark_name}, Test Case: {test_case}")
        print(f"[INFO] Timeout: {self.config['execution']['timeout']} seconds")
        print(f"{'='*60}\n")

        try:
            # 1. 准备执行环境
            namespace = self._prepare_namespace()

            # 2. 动态执行workflow代码
            print("[LOAD] Loading Workflow code...")
            exec(workflow_code, namespace)

            # 3. 获取Workflow类
            Workflow = namespace.get('Workflow')
            if not Workflow:
                raise ValueError("Workflow类未在代码中找到")

            # 4. 准备LLM配置（转换为LLMConfig对象）
            llm_config = self._prepare_llm_config()

            # 5. 创建workflow实例
            print("[CREATE] Creating Workflow instance...")
            workflow_instance = Workflow(llm_config, problem_text)

            # 5. 执行workflow（带超时控制）
            print("[EXECUTE] Running Workflow...")
            timeout = self.config['execution']['timeout']

            result = await asyncio.wait_for(
                workflow_instance(),
                timeout=timeout
            )

            # 6. 处理结果
            exec_end = datetime.now()
            execution_time = (exec_end - exec_start).total_seconds()

            print(f"\n{'='*60}")
            print(f"[SUCCESS] Workflow execution completed!")
            print(f"[TIME] Execution time: {execution_time:.2f} seconds")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'workflow_id': workflow_id,
                'result': result,
                'execution_time': execution_time,
                'benchmark': benchmark_name,
                'test_case': test_case
            }

        except asyncio.TimeoutError:
            print(f"\n[ERROR] Workflow execution timeout ({self.config['execution']['timeout']} seconds)")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': 'Execution timeout',
                'benchmark': benchmark_name,
                'test_case': test_case
            }

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()

            print(f"\n[ERROR] {error_msg}")
            print(f"详细信息:\n{error_trace}")

            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': error_msg,
                'error_trace': error_trace,
                'benchmark': benchmark_name,
                'test_case': test_case
            }

    def _prepare_llm_config(self):
        """准备LLM配置，转换为LLMConfig对象"""
        try:
            # 尝试导入MetaGPT的配置类
            from metagpt.configs.llm_config import LLMConfig

            # 从字典创建LLMConfig对象
            llm_dict = self.config.get('llm', {})

            # 创建LLMConfig实例
            llm_config = LLMConfig(
                api_type=llm_dict.get('api_type', 'openai'),
                base_url=llm_dict.get('base_url'),
                api_key=llm_dict.get('api_key'),
                model=llm_dict.get('model', 'gemini-2.5-pro'),
                max_tokens=llm_dict.get('max_tokens', 2000),
                temperature=llm_dict.get('temperature', 0.7)
            )

            print("[OK] LLMConfig created successfully")
            return llm_config

        except ImportError as e:
            print(f"[WARNING] Cannot import LLMConfig, returning dict config: {e}")
            # 如果无法导入，返回原始字典配置
            return self.config.get('llm', {})

    def _prepare_namespace(self) -> Dict:
        """准备workflow执行的命名空间"""
        # 导入必要的模块
        try:
            # 尝试导入MetaGPT的LLM创建函数
            from metagpt.provider.llm_provider_registry import create_llm_instance as create

            # 尝试导入ScoreFlow的operator
            import ScoreFlow.scripts.common.operator as operator

            print("[OK] Successfully imported MetaGPT and ScoreFlow modules")

        except ImportError as e:
            print(f"[WARNING] Import failed, using mock version: {e}")

            # 如果导入失败，提供模拟版本
            class MockLLM:
                """模拟LLM，使用Gemini API"""
                def __init__(self, config):
                    self.config = config

                async def aask(self, prompt: str, system_prompt: str = ""):
                    """调用Gemini API"""
                    import aiohttp

                    url = f"{self.config['base_url']}/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {self.config['api_key']}",
                        "Content-Type": "application/json"
                    }

                    data = {
                        "model": self.config.get('model', 'gemini-2.5-pro'),
                        "messages": [
                            {"role": "system", "content": system_prompt or "You are a helpful AI assistant"},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": self.config.get('max_tokens', 2000),
                        "temperature": self.config.get('temperature', 0.7)
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, json=data) as response:
                            result = await response.json()
                            return result['choices'][0]['message']['content']

            def create(config):
                """创建模拟LLM实例"""
                return MockLLM(config)

            # 模拟operator模块
            class operator:
                pass

        # 返回命名空间
        namespace = {
            'asyncio': asyncio,
            'create': create,
            'operator': operator,
            '__name__': '__main__',
            'List': list,
            'Dict': dict,
            'Any': Any,
            'Optional': Optional
        }

        return namespace

async def main():
    """主函数示例"""
    # 创建执行器
    executor = SimpleWorkflowExecutor()

    # 示例workflow代码
    workflow_code = '''
import asyncio
from typing import List, Dict, Any

class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        # 初始化算子（如果有operator模块）
        try:
            self.generate = operator.Generate(self.llm, self.problem_text)
            self.verifier = operator.Verifier(self.llm, self.problem_text)
            self.refiner = operator.Refiner(self.llm, self.problem_text)
            print("✅ 算子初始化成功")
        except:
            print("⚠️ 算子初始化失败，使用简化版本")

    async def run_workflow(self):
        """执行workflow逻辑"""
        # 这里是您的workflow逻辑
        result = f"处理问题: {self.problem_text[:50]}..."

        # 如果有LLM，尝试调用
        try:
            if hasattr(self, 'generate'):
                result = await self.generate(
                    instruction="Solve this problem step by step",
                    context=""
                )
        except:
            pass

        return result

    async def __call__(self):
        """主入口"""
        return await self.run_workflow()
'''

    # 测试问题
    problem = "Prove that for any positive integer n, the sum 1 + 2 + ... + n equals n(n+1)/2."

    # 执行workflow
    result = await executor.execute_workflow(
        workflow_code=workflow_code,
        problem_text=problem,
        benchmark_name="imo",
        test_case=1
    )

    # 输出结果
    print("\n📊 执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())