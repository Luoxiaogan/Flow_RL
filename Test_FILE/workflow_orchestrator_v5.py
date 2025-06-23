import os
import sys
import asyncio
import importlib
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging
import time
from openai import AsyncOpenAI

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 设置Python路径 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 假设 ScoreFlow 位于项目根目录，如果不是，请调整此路径
SCOREFLOW_PATH = os.path.join(os.path.dirname(CURRENT_DIR))
sys.path.append(SCOREFLOW_PATH)

try:
    from metagpt.provider.llm_provider_registry import create_llm_instance
except ImportError as e:
    logging.error(f"无法导入 metagpt 模块: {e}。请确保 'metagpt' 和 'ScoreFlow' 在Python路径中。")
    sys.exit(1)

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
    def __init__(self, generation_api_configs: List[Dict], execution_llm_config: Dict, workspace_path: str):
        if not generation_api_configs:
            raise ValueError("生成API配置列表不能为空。")
        self.generation_api_configs = generation_api_configs
        self.execution_llm_config = execution_llm_config
        self.workspace_path = workspace_path
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
        # 假设数据集路径，您可能需要根据实际情况调整
        dataset_path = os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets', f'{benchmark_name.lower()}.jsonl')
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
            dataset_path = os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets', f'{benchmark_name.lower()}.jsonl')
            benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path="")
            
            # 使用data_indices中的第一个索引来获取验证用的问题
            verification_index = workflow.data_indices[0]
            problem_data = (await benchmark_instance.load_data(specific_indices=[verification_index]))[0]
            question = benchmark_instance.get_input_text(problem_data)
            ground_truth_answer = problem_data["answer"]

            # 2. 包装并执行代码
            logging.info(f"[{workflow.id}] 正在包装并执行 (验证问题索引: {verification_index})...")
            full_script_code = python_start + "\n" + workflow.code + "\n" + python_end.format(time=120)

            execution_namespace = {}
            exec(full_script_code, globals(), execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass: raise ValueError("在执行的代码中未找到 'Workflow' 类。")

            workflow_instance = WorkflowClass(config=self.execution_llm_config, problem=question)
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
        await asyncio.gather(*verification_tasks)
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
    # --- 配置区域 ---
    GENERATION_API_CONFIGS = [
        {
            "provider": "aliyun_dashscope",
            "model": "qwen-plus",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
    ]
    
    EXECUTION_LLM_CONFIG = { "provider": "openai", "model": "gpt-4-turbo" }

    WORKSPACE_PATH = os.path.join(CURRENT_DIR, "workspace_v5")

    # V5: 定义生成任务，基于数据索引
    GENERATION_TASKS_BY_BENCHMARK = {
        "GSM8K": [
            [0],          # 任务1: 基于gsm8k.jsonl的第0行问题生成一个工作流
            [5],          # 任务2: 基于gsm8k.jsonl的第5行问题生成一个工作流
            [10, 11],     # 任务3: 基于第10和11行问题共同生成一个工作流
        ],
        # "MBPP": [ [0], [1] ], # 也可以为其他benchmark定义任务
    }

    # --- 执行 ---
    orchestrator = WorkflowOrchestrator(
        generation_api_configs=GENERATION_API_CONFIGS,
        execution_llm_config=EXECUTION_LLM_CONFIG,
        workspace_path=WORKSPACE_PATH
    )
    
    # 调用run方法时传入新的任务定义
    await orchestrator.run(GENERATION_TASKS_BY_BENCHMARK)

if __name__ == "__main__":
    # ... (确保环境变量和路径设置正确)
    asyncio.run(main())