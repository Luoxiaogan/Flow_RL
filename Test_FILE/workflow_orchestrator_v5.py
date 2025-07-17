import os
import sys
import asyncio
import importlib
import argparse
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging
import time
from openai import AsyncOpenAI

# --- 设置Python路径 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOREFLOW_PATH = os.path.join(os.path.dirname(CURRENT_DIR))
sys.path.append(SCOREFLOW_PATH)

try:
    from metagpt.provider.llm_provider_registry import create_llm_instance
except ImportError as e:
    logging.error(f"无法导入 metagpt 模块: {e}。请确保 'metagpt' 和 'ScoreFlow' 在Python路径中。")
    sys.exit(1)

# --- 配置解析 ---
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='工作流编排器 V5')
    
    # API池配置
    parser.add_argument('--api-pool', type=str, required=True,
                       help='API配置池，JSON格式的字符串，例如: \'[{"provider":"openai","model":"gpt-4","api_key":"sk-xxx","base_url":"https://api.openai.com/v1"}]\'')
    
    # 执行LLM配置
    parser.add_argument('--exec-llm', type=str, required=True,
                       help='执行LLM配置，JSON格式，例如: \'{"provider":"openai","model":"gpt-4","api_key":"sk-xxx","base_url":"https://api.openai.com/v1"}\'')
    
    # 路径配置
    parser.add_argument('--workspace-path', type=str, default=os.path.join(CURRENT_DIR, "workspace_v5"),
                       help='工作空间路径')
    parser.add_argument('--dataset-base-path', type=str, default=os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets'),
                       help='数据集基础路径')
    parser.add_argument('--gsm8k-dataset-path', type=str,
                       help='GSM8K数据集路径（如果不指定，使用dataset-base-path/gsm8k.jsonl）')
    
    # 任务配置
    parser.add_argument('--generation-tasks', type=str, default='GSM8K:0,5,10-11',
                       help='生成任务配置，格式: BENCHMARK1:task1,task2;BENCHMARK2:task1,task2')
    
    # 系统配置
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    parser.add_argument('--max-concurrent-tasks', type=int, default=10,
                       help='最大并发任务数')
    parser.add_argument('--workflow-timeout', type=int, default=120,
                       help='工作流超时时间(秒)')
    
    return parser.parse_args()

def parse_api_pool(api_pool_str: str) -> List[Dict]:
    """解析API池字符串"""
    try:
        return json.loads(api_pool_str)
    except json.JSONDecodeError as e:
        logging.error(f"API池配置解析失败: {e}")
        sys.exit(1)

def parse_exec_llm(exec_llm_str: str) -> Dict:
    """解析执行LLM配置字符串"""
    try:
        return json.loads(exec_llm_str)
    except json.JSONDecodeError as e:
        logging.error(f"执行LLM配置解析失败: {e}")
        sys.exit(1)

def parse_generation_tasks(tasks_str: str) -> Dict[str, List[List[int]]]:
    """解析生成任务配置"""
    tasks = {}
    for benchmark_task in tasks_str.split(';'):
        if ':' in benchmark_task:
            benchmark, indices_str = benchmark_task.split(':', 1)
            benchmark = benchmark.strip()
            indices_list = []
            
            for task in indices_str.split(','):
                task = task.strip()
                if '-' in task:
                    # 处理范围，如 "10-11"
                    start, end = map(int, task.split('-'))
                    indices_list.append(list(range(start, end + 1)))
                else:
                    # 单个索引
                    indices_list.append([int(task)])
            
            tasks[benchmark] = indices_list
    return tasks

def get_dataset_path(benchmark_name: str, dataset_base_path: str, custom_paths: Dict[str, str]) -> str:
    """获取数据集路径"""
    # 优先使用自定义路径
    if benchmark_name.upper() in custom_paths:
        return custom_paths[benchmark_name.upper()]
    
    # 使用默认路径
    return os.path.join(dataset_base_path, f'{benchmark_name.lower()}.jsonl')

def convert_config_for_metagpt(config_dict: Dict) -> object:
    """将我们的配置字典转换为 MetaGPT 期望的配置对象"""
    from metagpt.provider.llm_provider_registry import LLMType
    from metagpt.configs.llm_config import LLMConfig
    
    # 将 provider 映射到 api_type (使用LLMType枚举)
    provider = config_dict.get('provider', 'openai')
    if provider in ['openai', 'dashscope']:
        # 通义千问API使用OpenAI兼容格式，所以使用OPENAI类型
        api_type = LLMType.OPENAI
    elif provider == 'dashscope_native':
        # 如果需要原生dashscope支持
        api_type = LLMType.DASHSCOPE
    else:
        # 尝试匹配其他提供商
        provider_mapping = {
            'anthropic': LLMType.ANTHROPIC,
            'claude': LLMType.CLAUDE,
            'azure': LLMType.AZURE,
            'gemini': LLMType.GEMINI,
            'moonshot': LLMType.MOONSHOT,
            'qianfan': LLMType.QIANFAN,
            'zhipuai': LLMType.ZHIPUAI,
        }
        api_type = provider_mapping.get(provider, LLMType.OPENAI)
    
    # 创建 LLMConfig 实例
    llm_config = LLMConfig(
        api_type=api_type,
        model=config_dict.get('model'),
        api_key=config_dict.get('api_key'),
        base_url=config_dict.get('base_url'),
        # 可选属性
        temperature=config_dict.get('temperature', 0.7),
        max_token=config_dict.get('max_tokens', 4096),
        timeout=config_dict.get('timeout', 60),
        calc_usage=config_dict.get('calc_usage', True),
        use_system_prompt=config_dict.get('use_system_prompt', True),
        proxy=config_dict.get('proxy', None),
        pricing_plan=config_dict.get('pricing_plan', None),
    )
    
    return llm_config

def print_config(args, api_pool, exec_llm_config, generation_tasks):
    """打印当前配置"""
    print("=== 当前工作流配置 ===")
    print(f"工作空间路径: {args.workspace_path}")
    print(f"数据集基础路径: {args.dataset_base_path}")
    print(f"日志级别: {args.log_level}")
    print(f"最大并发任务数: {args.max_concurrent_tasks}")
    print(f"工作流超时时间: {args.workflow_timeout}秒")
    
    print(f"\nAPI配置池 ({len(api_pool)} 个API):")
    for i, api in enumerate(api_pool):
        print(f"  API {i+1}: {api['provider']} - {api['model']}")
        print(f"    Base URL: {api['base_url']}")
        print(f"    API Key: {'***' + api['api_key'][-4:] if api['api_key'] else 'Not Set'}")
    
    print(f"\n执行LLM配置:")
    print(f"  Provider: {exec_llm_config['provider']}")
    print(f"  Model: {exec_llm_config['model']}")
    
    print(f"\n生成任务配置:")
    for benchmark, tasks in generation_tasks.items():
        print(f"  {benchmark}: {tasks}")
    
    print("=" * 50)

# --- 数据模型 (V5) ---
@dataclass
class Workflow:
    """
    用于存储工作流信息的标准结构。
    V5版本使用 data_indices 替代了 prompt 来追踪数据来源。
    """
    id: str
    benchmark: str
    data_indices: List[int]  # 新增：记录生成此工作流所用的数据索引
    code: str = ""
    status: str = "new"
    execution_result: Any = None
    error: str = ""

# --- API 调用抽象 ---
async def call_openai_compatible_api(api_config: Dict, messages: List[Dict]) -> str:
    """
    一个通用的函数，用于调用任何与OpenAI API兼容的端点。
    """
    try:
        client = AsyncOpenAI(
            api_key=api_config.get("api_key"),
            base_url=api_config.get("base_url"),
        )
        completion = await client.chat.completions.create(
            model=api_config.get("model"),
            messages=messages,
            # 您可能希望增加温度以获得更多样化的工作流
            # temperature=0.7, 
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"调用API时出错 (model: {api_config.get('model')}): {e}")
        raise e

# --- 核心编排器 V5 ---
class WorkflowOrchestrator:
    """
    一个通用的、由配置驱动的AI工作流编排引擎 (V5).
    """
    def __init__(self, generation_api_configs: List[Dict], execution_llm_config: Dict, workspace_path: str,
                 max_concurrent_tasks: int = 10, workflow_timeout: int = 120,
                 dataset_base_path: str = None, custom_dataset_paths: Dict[str, str] = None):
        if not generation_api_configs:
            raise ValueError("生成API配置列表不能为空。")
        self.generation_api_configs = generation_api_configs
        self.execution_llm_config = execution_llm_config
        self.workspace_path = workspace_path
        self.max_concurrent_tasks = max_concurrent_tasks
        self.workflow_timeout = workflow_timeout
        self.dataset_base_path = dataset_base_path or os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets')
        self.custom_dataset_paths = custom_dataset_paths or {}
        self.workflows: List[Workflow] = []
        os.makedirs(os.path.join(self.workspace_path, "generated_workflows"), exist_ok=True)

    def _load_script_parts(self, benchmark_name: str) -> Tuple[str, str, str, str]:
        """从对应benchmark的scripts目录动态加载脚本的各个部分。"""
        try:
            # e.g., import ScoreFlow.scripts.GSM8K.conditions
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.conditions")
            python_start = getattr(conditions_module, "PYTHON_START", "")
            python_end = getattr(conditions_module, "PYTHON_END", "")
            start_prompt = getattr(conditions_module, "START_PORMPT", "")
            end_prompt = getattr(conditions_module, "END_PORMPT", "")
            return python_start, python_end, start_prompt, end_prompt
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载脚本模板: {e}")
            raise e

    async def _construct_generation_prompt(self, workflow: Workflow) -> List[Dict]:
        """根据模板和指定索引的数据构造最终的生成Prompt。"""
        benchmark_name = workflow.benchmark
        _, _, start_prompt_template, end_prompt_template = self._load_script_parts(benchmark_name)
        
        # 1. 加载Benchmark类以获取数据
        BenchmarkClass = self._get_benchmark_class(benchmark_name)
        # 使用配置中的数据集路径
        dataset_path = get_dataset_path(benchmark_name, self.dataset_base_path, self.custom_dataset_paths)
        benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path="")
        
        # 2. 根据data_indices加载一个或多个问题
        problems = await benchmark_instance.load_data(specific_indices=workflow.data_indices)
        if not problems:
            raise ValueError(f"无法从数据集加载索引为 {workflow.data_indices} 的问题。")
        
        # 3. 将问题格式化为字符串
        problem_text = ""
        for i, p in enumerate(problems):
            input_text = benchmark_instance.get_input_text(p)
            problem_text += f"Problem {i+1}:\n{input_text}\n\n"
        
        # 4. 组合成最终的prompt
        final_prompt_str = start_prompt_template + f"{problem_text.strip()}" + end_prompt_template

        return [
            {'role': 'system', 'content': 'You are an expert in creating generalized AI workflows.'},
            {'role': 'user', 'content': final_prompt_str}
        ]

    async def _call_generation_api(self, workflow: Workflow, api_config: Dict):
        """使用抽象的API调用函数来生成工作流。"""
        try:
            messages = await self._construct_generation_prompt(workflow)
            logging.info(f"向 {api_config.get('base_url')} 发送生成请求 (ID: {workflow.id}, Indices: {workflow.data_indices})")
            
            response_content = await call_openai_compatible_api(api_config, messages)
            
            if "<graph>" in response_content:
                code = response_content.split('<graph>')[1].split('</graph>')[0].strip()
            else:
                code = response_content.strip().strip('```python').strip('```').strip()

            if code:
                workflow.code = code
                workflow.status = "generated"
                logging.info(f"成功生成工作流: {workflow.id}")
                self._save_workflow_to_file(workflow)
            else:
                raise ValueError("API响应中未能提取有效代码。")
        except Exception as e:
            workflow.status = "generation_failed"
            workflow.error = str(e)
            logging.error(f"调用生成API时出错 {workflow.id}: {e}")

    async def generate_workflows(self, tasks_by_benchmark: Dict[str, List[List[int]]]):
        """根据指定的数据索引并行生成工作流。"""
        logging.info("开始并行生成工作流...")
        api_index = 0
        tasks = []
        for benchmark, data_indices_list in tasks_by_benchmark.items():
            for i, indices in enumerate(data_indices_list):
                wf = Workflow(id=f"{benchmark.lower()}_{i}", benchmark=benchmark, data_indices=indices)
                self.workflows.append(wf)
                api_config = self.generation_api_configs[api_index % len(self.generation_api_configs)]
                api_index += 1
                tasks.append(self._call_generation_api(wf, api_config))
        
        await asyncio.gather(*tasks)
        logging.info("工作流生成阶段完成。")

    def _get_benchmark_class(self, benchmark_name: str):
        """动态加载并返回Benchmark类"""
        try:
            module_name = benchmark_name.lower()
            class_name = f"{benchmark_name.upper()}Benchmark"
            benchmark_module = importlib.import_module(f"ScoreFlow.benchmark.{module_name}")
            return getattr(benchmark_module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载Benchmark类。")
            raise e

    async def _execute_and_verify_one_workflow(self, workflow: Workflow):
        """执行并验证单个工作流"""
        if workflow.status != "generated":
            return

        try:
            benchmark_name = workflow.benchmark
            logging.info(f"开始处理工作流 {workflow.id} (Benchmark: {benchmark_name})...")

            # 1. 动态加载模板和数据
            python_start, python_end, start_prompt, end_prompt = self._load_script_parts(benchmark_name)
            BenchmarkClass = self._get_benchmark_class(benchmark_name)
            dataset_path = get_dataset_path(benchmark_name, self.dataset_base_path, self.custom_dataset_paths)
            benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path="")
            
            # 使用data_indices中的第一个索引来获取验证用的问题
            verification_index = workflow.data_indices[0]
            problem_data = (await benchmark_instance.load_data(specific_indices=[verification_index]))[0]
            question = benchmark_instance.get_input_text(problem_data)
            ground_truth_answer = problem_data["answer"]

            # 2. 包装并执行代码
            logging.info(f"[{workflow.id}] 正在包装并执行 (验证问题索引: {verification_index})...")
            full_script_code = python_start + "\n" + workflow.code + "\n" + python_end.format(time=self.workflow_timeout)

            # 创建执行命名空间，包含必要的导入和模块
            execution_globals = dict(globals())
            
            # 预先导入必要的模块到执行环境
            try:
                # 导入 asyncio 和 typing
                execution_globals['asyncio'] = asyncio
                
                # 导入 operator 模块
                operator_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.operator")
                execution_globals['operator'] = operator_module
                
                # 导入 create 函数
                execution_globals['create'] = create_llm_instance
                
                # 添加其他可能需要的模块
                from typing import Literal
                execution_globals['Literal'] = Literal
                
            except ImportError as e:
                logging.warning(f"导入模块时警告: {e}")
            
            execution_namespace = {}
            
            # 执行完整的脚本代码（包含所有导入）
            exec(full_script_code, execution_globals, execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass: raise ValueError("在执行的代码中未找到 'Workflow' 类。")

            workflow_instance = WorkflowClass(config=convert_config_for_metagpt(self.execution_llm_config), problem=question)
            workflow.execution_result = await workflow_instance()
            logging.info(f"[{workflow.id}] 执行完毕")

            # 3. 验证...
            # ... (此部分逻辑与v4一致)

        except Exception as e:
            workflow.status = "execution_failed"
            workflow.error = f"{type(e).__name__}: {e}"
            logging.error(f"处理工作流 {workflow.id} 时出错: {e}", exc_info=True)

    def _save_workflow_to_file(self, workflow: Workflow):
        """将工作流代码保存到文件，并记录数据索引"""
        benchmark_path = os.path.join(self.workspace_path, "generated_workflows", workflow.benchmark)
        os.makedirs(benchmark_path, exist_ok=True)
        file_path = os.path.join(benchmark_path, f"{workflow.id}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Benchmark: {workflow.benchmark}\n")
            f.write(f"# Generated from data indices: {workflow.data_indices}\n\n")
            f.write(workflow.code)
    
    async def execute_and_verify_workflows(self):
        """并行地执行和验证所有已生成的工作流。"""
        logging.info("开始并行执行和验证所有工作流...")
        verification_tasks = [self._execute_and_verify_one_workflow(wf) for wf in self.workflows if wf.status == 'generated']
        
        # 使用配置的并发限制
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        async def sem_execute(task):
            async with semaphore:
                return await task
        
        tasks_with_semaphore = [sem_execute(task) for task in verification_tasks]
        await asyncio.gather(*tasks_with_semaphore)
        logging.info("工作流执行和验证阶段完成。")

    def print_summary(self):
        # ... (同 V2)
        pass


    async def run(self, prompts_by_benchmark: Dict[str, List[str]]):
        """异步执行整个工作流生成和验证的流程。"""
        start_time = time.time()
        
        await self.generate_workflows(prompts_by_benchmark)
        await self.execute_and_verify_workflows()
        self.print_summary() # 您可以取消这行的注释来查看摘要
        
        end_time = time.time()
        logging.info(f"\n整个流程耗时: {end_time - start_time:.2f} 秒")

async def main():
    """主函数入口"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置日志
    logging.basicConfig(level=getattr(logging, args.log_level), format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 解析配置
    api_pool = parse_api_pool(args.api_pool)
    exec_llm_config = parse_exec_llm(args.exec_llm)
    generation_tasks = parse_generation_tasks(args.generation_tasks)
    
    # 创建自定义路径字典
    custom_dataset_paths = {}
    if args.gsm8k_dataset_path:
        custom_dataset_paths['GSM8K'] = args.gsm8k_dataset_path
    
    # 打印当前配置
    print_config(args, api_pool, exec_llm_config, generation_tasks)
    
    # 检查必要的API配置
    if not api_pool:
        logging.error("错误: 未找到任何可用的API配置！请检查环境变量。")
        return
    
    # --- 执行 ---
    orchestrator = WorkflowOrchestrator(
        generation_api_configs=api_pool,
        execution_llm_config=exec_llm_config,
        workspace_path=args.workspace_path,
        max_concurrent_tasks=args.max_concurrent_tasks,
        workflow_timeout=args.workflow_timeout,
        dataset_base_path=args.dataset_base_path,
        custom_dataset_paths=custom_dataset_paths
    )
    
    # 调用run方法时传入配置中的任务定义
    await orchestrator.run(generation_tasks)

if __name__ == "__main__":
    # 确保环境变量和路径设置正确
    asyncio.run(main())