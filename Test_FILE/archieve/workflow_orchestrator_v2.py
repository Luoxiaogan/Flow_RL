import os
import sys
import asyncio
import aiohttp
import json
import importlib
from typing import Dict, List, Any
from dataclasses import dataclass, field
import logging
import time

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- 设置Python路径 ---
# 不需要检查，我是本地安装的
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# # 假设 ScoreFlow 和 metagpt 位于 Test_FILE/ 目录下
# sys.path.append(CURRENT_DIR) 
# # 如果它们在父目录，使用 sys.path.append(os.path.dirname(CURRENT_DIR))

# # 尝试导入 metagpt 的关键模块，以确保路径正确
# try:
#     from metagpt.provider.llm_provider_registry import create_llm_instance
# except ImportError as e:
#     logging.error(f"无法导入 metagpt 模块: {e}")
#     logging.error("请确保 'metagpt' 库在您的Python环境中，并且 sys.path 设置正确。")
#     sys.exit(1)


# --- 数据模型 ---
@dataclass
class Workflow:
    """用于存储工作流信息的标准结构"""
    id: str
    benchmark: str
    prompt: str  # 这是用户最初的高级prompt
    code: str = ""
    status: str = "new"  # new -> generated -> verified_correct / verified_incorrect / execution_failed
    execution_result: Any = None
    error: str = ""

# --- 核心编排器 ---

class WorkflowOrchestrator:
    """
    一个用于生成、执行和验证AI工作流的编排器。
    它使用异步操作来最大化效率，并深度集成ScoreFlow项目结构。
    """
    def __init__(self, generation_api_pool: List[str], execution_llm_config: Dict, workspace_path: str):
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

    def _get_generation_prompt(self, user_prompt: str) -> str:
        """根据用户prompt和ScoreFlow/scripts/GSM8K/conditions.py中的模板构建详细的生成prompt"""
        # 这个模板基于 conditions.py 中的 START_PORMPT，但更通用
        return f"""You are an expert in creating AI workflows. Your objective is to output a Python workflow class based on the following template structure.
This workflow will be used to solve a problem described by a user.

The user's problem description is: "{user_prompt}"

You must generate a Python class named `Workflow`.
This class must have:
1. An `__init__` method that accepts `config` and `problem` arguments. It should initialize all necessary operators from `ScoreFlow.scripts.GSM8K.operator` (like `Custom`, `Review`, `Programmer`) using the provided `config` and `problem`.
2. An `async def run_workflow(self)` method that contains the logic to solve the problem by calling the operators. It should finally return the solution.

Do not include any specific information from the user's problem in the generated code. The code should be a general-purpose workflow, where the specific problem is passed in during runtime via the `problem` argument.

Only output the complete Python code for the class, enclosed in ```python ... ```.

Example Template:
```python
import asyncio
from typing import Literal
# Make sure to import the correct operators for the benchmark
import ScoreFlow.scripts.GSM8K.operator as operator 
from metagpt.provider.llm_provider_registry import create_llm_instance as create

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.llm = create(config)
        # Initialize operators here
        self.custom_op = operator.Custom(self.llm, self.problem)
        # self.review_op = operator.Review(self.llm, self.problem)
        
    async def run_workflow(self):
        # Implement your workflow logic here
        # For example:
        step1_result = await self.custom_op(instruction="First, think step by step.")
        # ... more steps ...
        return step1_result

    async def __call__(self):
        # A standard entry point to run the workflow with a timeout
        TIMEOUT = 120 
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)"""
    
    async def _call_generation_api(self, session: aiohttp.ClientSession, workflow: Workflow, api_endpoint: str):
        """异步调用单个生成API"""
        try:
            full_prompt = self._get_generation_prompt(workflow.prompt)
            logging.info(f"向 {api_endpoint} 发送生成请求 (ID: {workflow.id})")
            
            async with session.post(api_endpoint, json={"prompt": full_prompt}, timeout=300) as response:
                response.raise_for_status()
                data = await response.json()
                
                # 从API响应中提取Python代码
                raw_code = data.get("workflow_code", "")
                if "```python" in raw_code:
                    code = raw_code.split("```python")[1].split("```")[0].strip()
                else:
                    code = raw_code
                
                if code:
                    workflow.code = code
                    workflow.status = "generated"
                    logging.info(f"成功生成工作流: {workflow.id}")
                    self._save_workflow_to_file(workflow)
                else:
                    workflow.status = "generation_failed"
                    workflow.error = "API响应中缺少有效的 'workflow_code'"
                    logging.error(f"生成失败 {workflow.id}: {workflow.error}")

        except Exception as e:
            workflow.status = "generation_failed"
            workflow.error = str(e)
            logging.error(f"调用生成API时出错 {workflow.id}: {e}")

    def _save_workflow_to_file(self, workflow: Workflow):
        """将工作流代码保存到文件"""
        benchmark_path = os.path.join(self.workspace_path, "generated_workflows", workflow.benchmark)
        os.makedirs(benchmark_path, exist_ok=True)
        file_path = os.path.join(benchmark_path, f"{workflow.id}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Benchmark: {workflow.benchmark}\n")
            f.write(f"# User Prompt: {workflow.prompt}\n\n")
            f.write(workflow.code)

    async def generate_workflows(self, prompts_by_benchmark: Dict[str, List[str]]):
        """根据给定的Prompt并行生成工作流。"""
        logging.info("开始并行生成工作流...")
        tasks_to_create = []
        for benchmark, prompts in prompts_by_benchmark.items():
            for i, prompt in enumerate(prompts):
                wf = Workflow(id=f"{benchmark.lower()}_{i}", benchmark=benchmark, prompt=prompt)
                self.workflows.append(wf)
                api_endpoint = self.generation_api_pool[len(tasks_to_create) % len(self.generation_api_pool)]
                tasks_to_create.append((wf, api_endpoint))
        
        async with aiohttp.ClientSession() as session:
            generation_tasks = [self._call_generation_api(session, wf, api) for wf, api in tasks_to_create]
            await asyncio.gather(*generation_tasks)
        
        logging.info("工作流生成阶段完成。")

    async def _execute_and_verify_one_workflow(self, workflow: Workflow):
        """执行并验证单个工作流"""
        if workflow.status != "generated":
            return

        try:
            benchmark_name = workflow.benchmark
            logging.info(f"开始处理工作流 {workflow.id} for benchmark {benchmark_name}...")

            # --- 1. 加载Benchmark数据集以获取问题和答案 ---
            # 动态导入benchmark的数据加载器
            benchmark_module = importlib.import_module(f"ScoreFlow.benchmark.{benchmark_name.lower()}")
            dataset = benchmark_module.load_dataset()
            
            # 为了演示，我们只使用数据集中的第一个问题
            if not dataset:
                raise ValueError(f"Benchmark '{benchmark_name}' 的数据集为空或加载失败。")
            problem_data = dataset[0]
            question = problem_data["question"]
            ground_truth_answer = problem_data["answer"]

            # --- 2. 动态实例化并运行生成的工作流 ---
            logging.info(f"[{workflow.id}] 正在实例化和运行...")
            
            execution_namespace = {}
            # 在一个独立的命名空间中执行代码，以定义Workflow类
            exec(workflow.code, globals(), execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError("在生成的工作流代码中未找到 'Workflow' 类。")

            # 实例化工作流，传入LLM配置和具体问题
            workflow_instance = WorkflowClass(config=self.execution_llm_config, problem=question)
            
            # 执行 __call__ 或者 run_workflow
            if hasattr(workflow_instance, '__call__'):
                execution_result = await workflow_instance()
            elif hasattr(workflow_instance, 'run_workflow'):
                execution_result = await workflow_instance.run_workflow()
            else:
                raise ValueError("工作流类中缺少 `__call__` 或 `run_workflow` 方法。")

            workflow.execution_result = execution_result
            logging.info(f"[{workflow.id}] 执行完毕，结果: {str(execution_result)[:100]}...")

            # --- 3. 调用Judger进行验证 ---
            logging.info(f"[{workflow.id}] 开始验证...")
            
            # 动态导入该benchmark的judger
            judger_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.judger")
            JudgerClass = getattr(judger_module, 'Workflow') # judger也被命名为Workflow
            judger_instance = JudgerClass(llm_config=self.execution_llm_config)

            # 调用judger的 __call__ 方法
            # 注意：这里的签名需要和您实际的judger匹配
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
                logging.warning(f"工作流 {workflow.id} 验证失败。Judger返回: {judgement_str}")

        except Exception as e:
            workflow.status = "execution_failed"
            workflow.error = f"{type(e).__name__}: {e}"
            logging.error(f"执行或验证工作流 {workflow.id} 时出错: {e}", exc_info=True)

    async def execute_and_verify_workflows(self):
        """并行地执行和验证所有已生成的工作流。"""
        logging.info("开始并行执行和验证所有工作流...")
        
        verification_tasks = [self._execute_and_verify_one_workflow(wf) for wf in self.workflows if wf.status == 'generated']
        await asyncio.gather(*verification_tasks)
        
        logging.info("工作流执行和验证阶段完成。")

    def print_summary(self):
        """打印最终的执行摘要"""
        # (此函数与V1版本相同，保持不变)
        logging.info("\n--- 最终执行摘要 ---\n")
        summary_by_benchmark = {}
        
        for wf in self.workflows:
            bm = wf.benchmark
            if bm not in summary_by_benchmark:
                summary_by_benchmark[bm] = {"correct": 0, "incorrect": 0, "failed": 0, "total": 0}
            
            summary_by_benchmark[bm]["total"] += 1
            if wf.status == "verified_correct":
                summary_by_benchmark[bm]["correct"] += 1
            elif wf.status == "verified_incorrect":
                summary_by_benchmark[bm]["incorrect"] += 1
            else:
                summary_by_benchmark[bm]["failed"] += 1
            
            logging.info(f"  - ID: {wf.id}, Benchmark: {wf.benchmark}, 状态: {wf.status}")
            if wf.error:
                logging.info(f"    错误: {wf.error}")

        logging.info("\n--- 统计 ---\n")
        for bm, stats in summary_by_benchmark.items():
            total_verified = stats['correct'] + stats['incorrect']
            accuracy = (stats['correct'] / total_verified * 100) if total_verified > 0 else 0
            logging.info(f"Benchmark: {bm}")
            logging.info(f"  总数: {stats['total']}, 验证通过: {stats['correct']}, 验证失败: {stats['incorrect']}, 执行出错: {stats['failed']}")
            logging.info(f"  准确率 (正确数 / (正确数 + 错误数)): {accuracy:.2f}%")
        
    async def run(self, prompts_by_benchmark: Dict[str, List[str]]):
        """异步执行整个工作流生成和验证的流程。"""
        start_time = time.time()
        
        await self.generate_workflows(prompts_by_benchmark)
        await self.execute_and_verify_workflows()
        self.print_summary()
        
        end_time = time.time()
        logging.info(f"\n整个流程耗时: {end_time - start_time:.2f} 秒")