import os
import sys
import asyncio
import aiohttp
import json
import importlib
from typing import Dict, List, Any, Type
from dataclasses import dataclass
import logging
import time

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 数据模型 ---
@dataclass
class Workflow:
    """用于存储工作流信息的标准结构"""
    id: str
    benchmark: str
    prompt: str
    code: str = ""
    status: str = "new"  # new -> generated -> verified_correct / verified_incorrect / execution_failed
    execution_result: Any = None
    error: str = ""

# --- 核心编排器 ---
class WorkflowOrchestrator:
    """
    一个通用的、由配置驱动的AI工作流编排引擎。
    """
    def __init__(self, generation_api_pool: List[str], execution_llm_config: Dict, workspace_path: str):
        """
        generation_api_pool: 用于生成workflow的api pool.
        execution_llm_config: 用于执行workflow的llm配置
        workspace_path: 用于保存workflow的文件夹路径
        """
        if not generation_api_pool:
            raise ValueError("生成API池不能为空。")
        if not execution_llm_config:
            raise ValueError("执行LLM配置不能为空。")
        
        self.generation_api_pool = generation_api_pool
        self.execution_llm_config = execution_llm_config
        self.workspace_path = workspace_path
        self.workflows: List[Workflow] = []
        
        os.makedirs(os.path.join(self.workspace_path, "generated_workflows"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_path, "logs"), exist_ok=True)

    def _get_generation_prompt_template(self, benchmark_name: str) -> str:
        """从对应benchmark的scripts目录动态加载生成prompt模板"""
        try:
            # e.g., import ScoreFlow.scripts.GSM8K.conditions
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.conditions")
            # 假设模板变量固定为 START_PORMPT
            return getattr(conditions_module, "START_PORMPT")
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载prompt模板。请确保 'ScoreFlow/scripts/{benchmark_name}/conditions.py' 文件存在且包含 'START_PORMPT' 变量。")
            raise e

    async def _call_generation_api(self, session: aiohttp.ClientSession, workflow: Workflow, api_endpoint: str):
        """异步调用单个生成API"""
        try:
            # 1. 动态获取该benchmark的prompt模板
            prompt_template = self._get_generation_prompt_template(workflow.benchmark)
            # 2. 将用户的高级prompt格式化进模板
            # (注意：这里的格式化逻辑取决于您的START_PORMPT内容，您可能需要调整)
            # 假设模板本身已足够，用户prompt仅作记录
            full_prompt = prompt_template # 在您的例子中，START_PORMPT已经很完整，可能不需要再插入用户prompt
            
            logging.info(f"向 {api_endpoint} 发送生成请求 (ID: {workflow.id})")
            
            async with session.post(api_endpoint, json={"prompt": full_prompt}, timeout=300) as response:
                response.raise_for_status()
                data = await response.json()
                
                raw_code = data.get("workflow_code", "")
                if "<graph>" in raw_code: # 您的conditions.py模板中包含<graph>标签
                    code = raw_code.split('<graph>')[1].split('</graph>')[0].strip()
                else:
                    code = raw_code

                if code:
                    workflow.code = code
                    workflow.status = "generated"
                    logging.info(f"成功生成工作流: {workflow.id}")
                    self._save_workflow_to_file(workflow)
                else:
                    raise ValueError("API响应中缺少有效的 'workflow_code' 或 '<graph>' 标签")

        except Exception as e:
            workflow.status = "generation_failed"
            workflow.error = str(e)
            logging.error(f"调用生成API时出错 {workflow.id}: {e}")
    
    async def generate_workflows(self, prompts_by_benchmark: Dict[str, List[str]]):
        """根据给定的Prompt并行生成工作流。"""
        logging.info("开始并行生成工作流...")
        api_index = 0
        tasks = []
        for benchmark, prompts in prompts_by_benchmark.items():
            for i, prompt_text in enumerate(prompts):
                wf = Workflow(id=f"{benchmark.lower()}_{i}", benchmark=benchmark, prompt=prompt_text)
                self.workflows.append(wf)
                api_endpoint = self.generation_api_pool[api_index % len(self.generation_api_pool)]
                api_index += 1
                tasks.append((wf, api_endpoint))
        
        async with aiohttp.ClientSession() as session:
            generation_tasks = [self._call_generation_api(session, wf, api) for wf, api in tasks]
            await asyncio.gather(*generation_tasks)
        logging.info("工作流生成阶段完成。")

    def _get_benchmark_class(self, benchmark_name: str): # -> Type[BaseBenchmark]
        """动态加载并返回Benchmark类"""
        try:
            module_name = benchmark_name.lower()
            class_name = f"{benchmark_name.upper()}Benchmark"
            # e.g., from ScoreFlow.benchmark.gsm8k import GSM8KBenchmark
            benchmark_module = importlib.import_module(f"ScoreFlow.benchmark.{module_name}")
            return getattr(benchmark_module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载Benchmark类。请确保 'ScoreFlow/benchmark/{module_name}.py' 文件存在且包含 '{class_name}' 类。")
            raise e

    async def _execute_and_verify_one_workflow(self, workflow: Workflow):
        """执行并验证单个工作流"""
        if workflow.status != "generated":
            return

        try:
            benchmark_name = workflow.benchmark
            logging.info(f"开始处理工作流 {workflow.id} (Benchmark: {benchmark_name})...")

            # 1. 动态加载Benchmark类并获取数据
            BenchmarkClass = self._get_benchmark_class(benchmark_name)
            # 实例化benchmark，传入文件路径等（此处路径需要您根据项目实际情况配置或硬编码）
            # 假设数据集都在 'ScoreFlow/benchmark/datasets/' 目录下
            dataset_path = os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets', f'{benchmark_name.lower()}.jsonl')
            log_path = os.path.join(self.workspace_path, 'logs')
            benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path=log_path)
            
            dataset = await benchmark_instance.load_data()
            if not dataset:
                raise ValueError(f"数据集 '{dataset_path}' 为空或加载失败。")
            problem_data = dataset[0] # 使用第一个问题进行验证
            question = benchmark_instance.get_input_text(problem_data)
            ground_truth_answer = problem_data["answer"] # 假设字段名为 "answer"

            # 2. 动态实例化并运行生成的工作流
            logging.info(f"[{workflow.id}] 正在实例化和运行...")
            execution_namespace = {}
            exec(workflow.code, globals(), execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError("在生成的工作流代码中未找到 'Workflow' 类。")

            workflow_instance = WorkflowClass(config=self.execution_llm_config, problem=question)
            
            if hasattr(workflow_instance, '__call__'):
                execution_result = await workflow_instance()
            else:
                raise ValueError("工作流类中缺少 `__call__` 方法。")

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
    GENERATION_API_POOL = ["http://127.0.0.1:8000/generate_workflow"]
    
    EXECUTION_LLM_CONFIG = {
        "provider": "openai", 
        "model": "gpt-4-turbo",
        # "api_key": os.environ.get("OPENAI_API_KEY"),
        # "base_url": "...",
    }

    WORKSPACE_PATH = os.path.join(CURRENT_DIR, "workspace_v3")

    # 现在，我们只需要提供benchmark的名称和解决该benchmark的高级目标描述
    PROMPTS_TO_RUN = {
        "GSM8K": [
            "Solve a math word problem by breaking it down into simple steps.",
        ],
        "MBPP": [
            "Write a Python function based on a textual description.",
        ],
        # 添加更多benchmark...
        # "HotpotQA": ["Find supporting facts to answer a multi-hop question."],
    }

    # --- 执行 ---
    orchestrator = WorkflowOrchestrator(
        generation_api_pool=GENERATION_API_POOL,
        execution_llm_config=EXECUTION_LLM_CONFIG,
        workspace_path=WORKSPACE_PATH
    )
    
    await orchestrator.run(PROMPTS_TO_RUN)


if __name__ == "__main__":
    asyncio.run(main())