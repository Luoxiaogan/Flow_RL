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
sys.path.append(CURRENT_DIR)

try:
    from metagpt.provider.llm_provider_registry import create_llm_instance
except ImportError as e:
    logging.error(f"无法导入 metagpt 模块: {e}。请确保 'metagpt' 和 'ScoreFlow' 在Python路径中。")
    sys.exit(1)

# --- 数据模型 ---
@dataclass
class Workflow:
    """用于存储工作流信息的标准结构"""
    id: str
    benchmark: str
    prompt: str
    code: str = ""
    status: str = "new"
    execution_result: Any = None
    error: str = ""

# --- API 调用抽象 ---
async def call_openai_compatible_api(api_config: Dict, messages: List[Dict]) -> str:
    """
    一个通用的函数，用于调用任何与OpenAI API兼容的端点。

    Args:
        api_config (Dict): 包含 'model', 'api_key', 'base_url' 的配置字典。
        messages (List[Dict]): 发送给模型的聊天消息列表。

    Returns:
        str: 模型返回的内容。
    """
    try:
        client = AsyncOpenAI(
            api_key=api_config.get("api_key"),
            base_url=api_config.get("base_url"),
        )
        completion = await client.chat.completions.create(
            model=api_config.get("model"),
            messages=messages,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"调用API时出错 (model: {api_config.get('model')}): {e}")
        # 在实际应用中，您可能希望抛出异常而不是返回空字符串
        raise e

# --- 核心编排器 V4 ---
class WorkflowOrchestrator:
    """
    一个通用的、由配置驱动的AI工作流编排引擎 (V4)。
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
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.conditions")
            python_start = getattr(conditions_module, "PYTHON_START", "")
            python_end = getattr(conditions_module, "PYTHON_END", "")
            start_prompt = getattr(conditions_module, "START_PORMPT", "")
            end_prompt = getattr(conditions_module, "END_PROMPT", "")
            return python_start, python_end, start_prompt, end_prompt
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载脚本模板: {e}")
            raise e

    async def _construct_generation_prompt(self, workflow: Workflow) -> List[Dict]:
        """根据模板和样本数据构造最终的生成Prompt。"""
        benchmark_name = workflow.benchmark
        _py_start, _py_end, start_prompt_template, end_prompt_template = self._load_script_parts(benchmark_name)
        
        # 根据您的要求，我们将一个数据样本融入到Prompt中，作为上下文或示例
        BenchmarkClass = self._get_benchmark_class(benchmark_name)
        # 假设数据集路径，您可能需要根据实际情况调整
        dataset_path = os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets', f'{benchmark_name.lower()}.jsonl')
        log_path = os.path.join(self.workspace_path, 'logs')
        benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path=log_path)
        dataset = await benchmark_instance.load_data()
        sample_problem = benchmark_instance.get_input_text(dataset[0])
        
        # 将样本问题添加到START_PORMPT中。这是一种可能的实现方式，您可能需要根据
        # 您的START_PORMPT模板的具体格式进行调整。
        # 这里我们简单地将问题附加在后面，作为一个清晰的任务描述。
        final_prompt_str = start_prompt_template + f"{sample_problem}"+ end_prompt_template

        return [
            {'role': 'system', 'content': 'You are an expert in creating AI workflows.'},
            {'role': 'user', 'content': final_prompt_str}
        ]

    async def _call_generation_api(self, workflow: Workflow, api_config: Dict):
        """使用抽象的API调用函数来生成工作流。"""
        try:
            messages = await self._construct_generation_prompt(workflow)
            logging.info(f"向 {api_config.get('base_url')} 发送生成请求 (ID: {workflow.id})")
            
            response_content = await call_openai_compatible_api(api_config, messages)
            
            # 提取代码
            if "<graph>" in response_content:
                code = response_content.split('<graph>')[1].split('</graph>')[0].strip()
            else: # 如果没有graph标签，就假定整个返回都是代码
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

    async def generate_workflows(self, prompts_by_benchmark: Dict[str, List[str]]):
        """并行生成工作流。"""
        logging.info("开始并行生成工作流...")
        api_index = 0
        tasks = []
        for benchmark, prompts in prompts_by_benchmark.items():
            for i, prompt_text in enumerate(prompts):
                wf = Workflow(id=f"{benchmark.lower()}_{i}", benchmark=benchmark, prompt=prompt_text)
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
        """执行并验证单个工作流，使用完整的 PYTHON_START 和 PYTHON_END 包装。"""
        if workflow.status != "generated":
            return

        try:
            benchmark_name = workflow.benchmark
            logging.info(f"开始处理工作流 {workflow.id} (Benchmark: {benchmark_name})...")

            # 1. 动态加载脚本模板和数据集
            python_start, python_end, start_prompt, end_prompt = self._load_script_parts(benchmark_name)
            BenchmarkClass = self._get_benchmark_class(benchmark_name)
            dataset_path = os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets', f'{benchmark_name.lower()}.jsonl')
            log_path = os.path.join(self.workspace_path, 'logs')
            benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path=log_path)
            dataset = await benchmark_instance.load_data()
            problem_data = dataset[0]
            question = benchmark_instance.get_input_text(problem_data)
            ground_truth_answer = problem_data["answer"]

            # 2. 使用 START/END 模板包装代码并执行
            logging.info(f"[{workflow.id}] 正在包装并执行代码...")
            # 使用默认超时时间，或从conditions.py动态加载
            full_script_code = python_start + "\n" + workflow.code + "\n" + python_end.format(time=120)

            execution_namespace = {}
            exec(full_script_code, globals(), execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError("在执行的代码中未找到 'Workflow' 类.")

            workflow_instance = WorkflowClass(config=self.execution_llm_config, problem=question)
            execution_result = await workflow_instance()
            workflow.execution_result = execution_result
            logging.info(f"[{workflow.id}] 执行完毕，结果: {str(execution_result)[:100]}...")

            # 3. 动态调用Judger进行验证
            logging.info(f"[{workflow.id}] 开始验证...")
            judger_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.judger")
            JudgerClass = getattr(judger_module, 'Workflow') # judger也被命名为Workflow
            judger_instance = JudgerClass(llm_config=self.execution_llm_config)
            
            judgement_str = await judger_instance(
                question=question, 
                model_answer=str(execution_result), 
                right_answer=ground_truth_answer
            )
            
            if judgement_str.strip() == '1':
                workflow.status = "verified_correct"
                logging.info(f"工作流 {workflow.id} 验证通过！")
            else:
                workflow.status = "verified_incorrect"
                logging.warning(f"工作流 {workflow.id} 验证失败 (Judger返回: {judgement_str})")

        except Exception as e:
            workflow.status = "execution_failed"
            workflow.error = f"{type(e).__name__}: {e}"
            logging.error(f"处理工作流 {workflow.id} 时出错: {e}", exc_info=True)

    async def execute_and_verify_workflows(self):
        """并行地执行和验证所有已生成的工作流。"""
        logging.info("开始并行执行和验证所有工作流...")
        verification_tasks = [self._execute_and_verify_one_workflow(wf) for wf in self.workflows if wf.status == 'generated']
        await asyncio.gather(*verification_tasks)
        logging.info("工作流执行和验证阶段完成。")

    # _save_workflow_to_file 和 print_summary 方法与V2版本相同，此处省略以保持简洁
    def _save_workflow_to_file(self, workflow: Workflow):
        benchmark_path = os.path.join(self.workspace_path, "generated_workflows", workflow.benchmark)
        os.makedirs(benchmark_path, exist_ok=True)
        file_path = os.path.join(benchmark_path, f"{workflow.id}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Benchmark: {workflow.benchmark}\n")
            f.write(f"# User Prompt: {workflow.prompt}\n\n")
            f.write(workflow.code)
    
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
    # 1. 配置生成API，现在是字典列表
    GENERATION_API_CONFIGS = [
        {
            "provider": "aliyun_dashscope",
            "model": "qwen-plus",
            "api_key": os.getenv("DASHSCOPE_API_KEY"), # 请确保设置了环境变量
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        },
        # 您可以添加更多API配置
        # {
        #     "provider": "openai",
        #     "model": "gpt-4-turbo-preview",
        #     "api_key": os.getenv("OPENAI_API_KEY"),
        #     "base_url": "https://api.openai.com/v1",
        # },
    ]
    
    # 2. 配置执行工作流时内部使用的LLM
    EXECUTION_LLM_CONFIG = {
        "provider": "openai",
        "model": "gpt-4-turbo",
        # ... 其他配置
    }

    WORKSPACE_PATH = os.path.join(CURRENT_DIR, "workspace_v4")

    # 3. 配置要运行的benchmark和高级目标描述
    PROMPTS_TO_RUN = {
        "GSM8K": [
            "Solve a math word problem by breaking it down into simple steps.",
        ],
    }

    # --- 执行 ---
    orchestrator = WorkflowOrchestrator(
        generation_api_configs=GENERATION_API_CONFIGS,
        execution_llm_config=EXECUTION_LLM_CONFIG,
        workspace_path=WORKSPACE_PATH
    )
    
    await orchestrator.run(PROMPTS_TO_RUN)


if __name__ == "__main__":
    # 在运行前，请确保：
    # 1. `openai` 库已安装 (`pip install openai`)。
    # 2. 您的环境变量 (如 DASHSCOPE_API_KEY) 已正确设置。
    # 3. ScoreFlow 和 metagpt 的项目结构正确，可供导入。
    asyncio.run(main())