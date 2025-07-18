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
import random
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
    
    parser.add_argument('--api-pool', type=str, required=True, help='API配置池 (JSON string)')
    parser.add_argument('--exec-llm', type=str, required=True, help='执行LLM配置 (JSON string)')
    parser.add_argument('--workspace-path', type=str, default=os.path.join(CURRENT_DIR, "workspace_v5"), help='工作空间路径')
    parser.add_argument('--dataset-base-path', type=str, default=os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets'), help='数据集基础路径')
    parser.add_argument('--gsm8k-dataset-path', type=str, help='GSM8K数据集路径')
    parser.add_argument('--generation-tasks', type=str, default='GSM8K:0,5,10-11', help='生成任务配置')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='日志级别')
    parser.add_argument('--max-concurrent-tasks', type=int, default=10, help='最大并发任务数')
    parser.add_argument('--workflow-timeout', type=int, default=120, help='工作流超时时间(秒)')
    parser.add_argument('--training-data-output', type=str, help='训练数据输出文件路径 (JSONL)')
    # <--- 新增参数 --->
    parser.add_argument('--no-save-workflows', action='store_true', help='禁用保存单个工作流.py文件')
    
    return parser.parse_args()

def parse_api_pool(api_pool_str: str) -> List[Dict]:
    try:
        return json.loads(api_pool_str)
    except json.JSONDecodeError as e:
        logging.error(f"API池配置解析失败: {e}")
        sys.exit(1)

def parse_exec_llm(exec_llm_str: str) -> Dict:
    try:
        return json.loads(exec_llm_str)
    except json.JSONDecodeError as e:
        logging.error(f"执行LLM配置解析失败: {e}")
        sys.exit(1)

def parse_generation_tasks(tasks_str: str) -> Dict[str, List[List[int]]]:
    """
    解析生成任务配置。
    支持新格式：用'_'连接的非连续索引组，如 "1_5_8"。
    """
    tasks = {}
    for benchmark_task in tasks_str.split(';'):
        if ':' in benchmark_task:
            benchmark, indices_str = benchmark_task.split(':', 1)
            benchmark = benchmark.strip()
            indices_list = []
            
            for task_group in indices_str.split(','):
                task_group = task_group.strip()
                if '_' in task_group: # <--- 新增：处理非连续组
                    indices_list.append([int(i) for i in task_group.split('_')])
                elif '-' in task_group:
                    start, end = map(int, task_group.split('-'))
                    indices_list.append(list(range(start, end + 1)))
                else:
                    indices_list.append([int(task_group)])
            
            tasks[benchmark] = indices_list
    return tasks

def get_dataset_path(benchmark_name: str, dataset_base_path: str, custom_paths: Dict[str, str]) -> str:
    if benchmark_name.upper() in custom_paths:
        return custom_paths[benchmark_name.upper()]
    return os.path.join(dataset_base_path, f'{benchmark_name.lower()}.jsonl')

def convert_config_for_metagpt(config_dict: Dict) -> object:
    from metagpt.provider.llm_provider_registry import LLMType
    from metagpt.configs.llm_config import LLMConfig
    
    provider = config_dict.get('provider', 'openai')
    api_type_map = {'openai': LLMType.OPENAI, 'dashscope': LLMType.OPENAI, 'anthropic': LLMType.ANTHROPIC, 'claude': LLMType.CLAUDE, 'azure': LLMType.AZURE, 'gemini': LLMType.GEMINI, 'moonshot': LLMType.MOONSHOT, 'qianfan': LLMType.QIANFAN, 'zhipuai': LLMType.ZHIPUAI}
    api_type = api_type_map.get(provider, LLMType.OPENAI)
    
    return LLMConfig(api_type=api_type, model=config_dict.get('model'), api_key=config_dict.get('api_key'), base_url=config_dict.get('base_url'))

def print_config(args, api_pool, exec_llm_config, generation_tasks):
    print("=== 当前工作流配置 ===")
    print(f"工作空间路径: {args.workspace_path}")
    print(f"日志级别: {args.log_level}")
    print(f"最大并发任务数: {args.max_concurrent_tasks}")
    
    print("\nAPI配置池:")
    for i, api in enumerate(api_pool):
        print(f"  API {i+1}: {api['provider']} - {api['model']}")
    
    print(f"\n执行LLM配置: {exec_llm_config['provider']} - {exec_llm_config['model']}")
    print(f"\n生成任务配置:")
    for benchmark, tasks in generation_tasks.items():
        print(f"  {benchmark}: {len(tasks)} 个任务组")
    print("=" * 50)

@dataclass
class Workflow:
    id: str
    benchmark: str
    data_indices: List[int]
    generation_prompt: str = ""
    problem_text: str = ""
    code: str = ""
    status: str = "new"
    execution_result: Any = None
    error: str = ""

async def call_openai_compatible_api(api_config: Dict, messages: List[Dict]) -> str:
    try:
        client = AsyncOpenAI(api_key=api_config.get("api_key"), base_url=api_config.get("base_url"))
        completion = await client.chat.completions.create(model=api_config.get("model"), messages=messages)
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"调用API时出错 (model: {api_config.get('model')}): {e}")
        raise e

class WorkflowOrchestrator:
    def __init__(self, generation_api_configs: List[Dict], execution_llm_config: Dict, workspace_path: str,
                 max_concurrent_tasks: int = 10, workflow_timeout: int = 120,
                 dataset_base_path: str = None, custom_dataset_paths: Dict[str, str] = None,
                 training_data_output: str = None, no_save_workflows: bool = False):
        if not generation_api_configs:
            raise ValueError("生成API配置不能为空。")
        self.generation_api_configs = generation_api_configs
        self.execution_llm_config = execution_llm_config
        self.workspace_path = workspace_path
        self.max_concurrent_tasks = max_concurrent_tasks
        self.workflow_timeout = workflow_timeout
        self.dataset_base_path = dataset_base_path or os.path.join(CURRENT_DIR, 'ScoreFlow', 'benchmark', 'datasets')
        self.custom_dataset_paths = custom_dataset_paths or {}
        self.training_data_output = training_data_output
        self.no_save_workflows = no_save_workflows # <--- 保存标志
        self.workflows: List[Workflow] = []

        # 无条件地创建主工作区目录，因为它需要存放CSV等摘要文件。
        os.makedirs(self.workspace_path, exist_ok=True) 
        # 仅在需要保存单个 .py 文件时，才创建子目录
        if not self.no_save_workflows:
            os.makedirs(os.path.join(self.workspace_path, "generated_workflows"), exist_ok=True)
        # if not self.no_save_workflows:
        #      os.makedirs(os.path.join(self.workspace_path, "generated_workflows"), exist_ok=True)

    def _load_script_parts(self, benchmark_name: str) -> Tuple[str, str, str, str, List[str]]:
        try:
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.conditions")
            return (
                getattr(conditions_module, "PYTHON_START", ""),
                getattr(conditions_module, "PYTHON_END", ""),
                getattr(conditions_module, "START_PORMPT", ""),
                getattr(conditions_module, "END_PROMPT", ""),
                getattr(conditions_module, "META_PROMPTS", [])
            )
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载脚本模板: {e}")
            raise e

    async def _construct_generation_prompt(self, workflow: Workflow) -> List[Dict]:
        benchmark_name = workflow.benchmark
        _, _, start_prompt_template, end_prompt_template, meta_prompts = self._load_script_parts(benchmark_name)
        
        BenchmarkClass = self._get_benchmark_class(benchmark_name)
        dataset_path = get_dataset_path(benchmark_name, self.dataset_base_path, self.custom_dataset_paths)
        benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path="")
        
        problems = await benchmark_instance.load_data(specific_indices=workflow.data_indices)
        if not problems:
            raise ValueError(f"无法从数据集加载索引为 {workflow.data_indices} 的问题。")
        
        problem_text = "\n\n".join([f"Problem {i+1}:\n{benchmark_instance.get_input_text(p)}" for i, p in enumerate(problems)])
        workflow.problem_text = problem_text
        
        selected_meta_prompt = random.choice(meta_prompts) if meta_prompts else ""
        final_end_prompt = f"\n**CRITICAL INSTRUCTION FOR THIS SPECIFIC TASK:**\n{selected_meta_prompt}\n\n" + end_prompt_template
        final_prompt_str = start_prompt_template + f"{problem_text}" + final_end_prompt

        return [{'role': 'system', 'content': 'You are an expert in creating generalized AI workflows.'}, {'role': 'user', 'content': final_prompt_str}]

    async def _call_generation_api(self, workflow: Workflow, api_config: Dict):
        try:
            messages = await self._construct_generation_prompt(workflow)
            workflow.generation_prompt = messages[-1]['content']
            
            logging.info(f"向 {api_config.get('base_url')} 发送生成请求 (ID: {workflow.id}, Indices: {workflow.data_indices})")
            response_content = await call_openai_compatible_api(api_config, messages)
            
            code = response_content.split('<graph>')[1].split('</graph>')[0].strip() if "<graph>" in response_content else response_content.strip().strip('```python').strip('```').strip()

            if code:
                workflow.code = code
                workflow.status = "generated"
                logging.info(f"成功生成工作流: {workflow.id}")
                if not self.no_save_workflows: # <--- 检查标志
                    self._save_workflow_to_file(workflow)
            else:
                raise ValueError("API响应中未能提取有效代码。")
        except Exception as e:
            workflow.status = "generation_failed"
            workflow.error = str(e)
            logging.error(f"调用生成API时出错 {workflow.id}: {e}")

    async def generate_workflows(self, tasks_by_benchmark: Dict[str, List[List[int]]]):
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
        try:
            return getattr(importlib.import_module(f"ScoreFlow.benchmark.{benchmark_name.lower()}"), f"{benchmark_name.upper()}Benchmark")
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为benchmark '{benchmark_name}' 加载Benchmark类。")
            raise e

    def _extract_final_answer(self, result_str: str, benchmark_name: str) -> str:
        try:
            if benchmark_name.upper() == "GSM8K":
                import re
                answer_match = re.search(r'####\s*(\d+(?:\.\d+)?)', result_str)
                if answer_match: return answer_match.group(1)
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', result_str)
                if numbers: return numbers[-1]
            return result_str[:200]
        except Exception as e:
            logging.warning(f"答案提取失败: {e}")
            return result_str[:200]

    async def _execute_and_verify_one_workflow(self, workflow: Workflow):
        if workflow.status != "generated": return
        try:
            benchmark_name = workflow.benchmark
            logging.info(f"开始处理工作流 {workflow.id} (Benchmark: {benchmark_name})...")
            python_start, python_end, _, _, _ = self._load_script_parts(benchmark_name)
            BenchmarkClass = self._get_benchmark_class(benchmark_name)
            dataset_path = get_dataset_path(benchmark_name, self.dataset_base_path, self.custom_dataset_paths)
            benchmark_instance = BenchmarkClass(name=benchmark_name, file_path=dataset_path, log_path="")
            problem_data = (await benchmark_instance.load_data(specific_indices=[workflow.data_indices[0]]))[0]
            question, ground_truth_answer = benchmark_instance.get_input_text(problem_data), problem_data["answer"]
            full_script_code = f"{python_start}\n{workflow.code}\n{python_end.format(time=self.workflow_timeout)}"
            execution_namespace = {}
            exec(full_script_code, {'asyncio': asyncio, 'create': create_llm_instance, 'operator': importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.operator"), 'Literal': __import__('typing').Literal}, execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass: raise ValueError("未找到 'Workflow' 类。")
            workflow.execution_result = await WorkflowClass(config=convert_config_for_metagpt(self.execution_llm_config), problem=question)()
            logging.info(f"[{workflow.id}] 执行完毕...")
            model_answer = self._extract_final_answer(str(workflow.execution_result), benchmark_name)
            JudgerClass = getattr(importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.judger"), 'Workflow')
            judgement = await JudgerClass(llm_config=convert_config_for_metagpt(self.execution_llm_config))(question=question, model_answer=model_answer, right_answer=ground_truth_answer)
            workflow.status = "verified_correct" if judgement.strip() == '1' else "verified_incorrect"
            logging.info(f"工作流 {workflow.id} 验证: {workflow.status}")
        except Exception as e:
            workflow.status = "execution_failed"
            workflow.error = f"{type(e).__name__}: {e}"
            logging.error(f"处理工作流 {workflow.id} 时出错: {e}", exc_info=True)

    def _save_workflow_to_file(self, workflow: Workflow):
        benchmark_path = os.path.join(self.workspace_path, "generated_workflows", workflow.benchmark)
        os.makedirs(benchmark_path, exist_ok=True)
        file_path = os.path.join(benchmark_path, f"{workflow.id}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Benchmark: {workflow.benchmark}\n# Workflow ID: {workflow.id}\n# Data Indices: {workflow.data_indices}\n\n{workflow.code}")
        logging.info(f"工作流代码已保存到: {file_path}")

    async def execute_and_verify_workflows(self):
        logging.info("开始并行执行和验证所有工作流...")
        tasks = [self._execute_and_verify_one_workflow(wf) for wf in self.workflows if wf.status == 'generated']
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        async def sem_task(task):
            async with semaphore: return await task
        await asyncio.gather(*[sem_task(t) for t in tasks])
        logging.info("工作流执行和验证阶段完成。")

    def print_summary(self):
        print("\n" + "="*60 + "\n工作流执行摘要\n" + "="*60)
        summary = {}
        for wf in self.workflows: summary[wf.status] = summary.get(wf.status, 0) + 1
        for status, count in summary.items(): print(f"  {status}: {count}")
        print("="*60)

    def _save_results_to_json(self):
        # 此函数可以保留用于调试，但主要输出转为CSV
        pass

    def _save_results_to_csv(self):
        """以流式追加方式将执行结果保存为CSV文件。"""
        import csv
        csv_file = os.path.join(self.workspace_path, "execution_results.csv")
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ID", "Benchmark", "Data_Indices", "Status", "Has_Result", "Error_Type"])
            
            for wf in self.workflows:
                writer.writerow([wf.id, wf.benchmark, '_'.join(map(str, wf.data_indices)), wf.status, bool(wf.execution_result), wf.error.split(':')[0] if wf.error else ""])
        logging.info(f"执行结果CSV已追加到: {csv_file}")

    def _save_training_data(self):
        if not self.training_data_output: return
        training_records, cache = [], {}
        default_prompt = "You are a helpful AI assistant."
        for wf in self.workflows:
            if wf.code and wf.problem_text:
                if wf.benchmark not in cache:
                    try:
                        cache[wf.benchmark] = getattr(importlib.import_module(f"ScoreFlow.scripts.{wf.benchmark}.conditions"), "SYSTEM_PROMPT", default_prompt)
                    except:
                        cache[wf.benchmark] = default_prompt
                training_records.append({"messages": [{"role": "system", "content": cache[wf.benchmark]}, {"role": "user", "content": wf.problem_text}, {"role": "assistant", "content": wf.code}]})
        
        if training_records:
            output_dir = os.path.dirname(self.training_data_output)
            if output_dir: os.makedirs(output_dir, exist_ok=True)
            with open(self.training_data_output, 'a', encoding='utf-8') as f:
                for record in training_records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            logging.info(f"训练数据已追加到: {self.training_data_output}")

    async def run(self, tasks_by_benchmark: Dict[str, List[List[int]]]):
        start_time = time.time()
        await self.generate_workflows(tasks_by_benchmark)
        await self.execute_and_verify_workflows()
        self.print_summary()
        self._save_results_to_csv() # 移到主逻辑中
        self._save_training_data()
        logging.info(f"\n整个流程耗时: {time.time() - start_time:.2f} 秒")

async def main():
    args = parse_arguments()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')
    
    api_pool = parse_api_pool(args.api_pool)
    exec_llm_config = parse_exec_llm(args.exec_llm)
    generation_tasks = parse_generation_tasks(args.generation_tasks)
    
    custom_paths = {'GSM8K': args.gsm8k_dataset_path} if args.gsm8k_dataset_path else {}
    print_config(args, api_pool, exec_llm_config, generation_tasks)
    
    if not api_pool:
        logging.error("错误: API配置池为空！")
        return
    
    orchestrator = WorkflowOrchestrator(
        generation_api_configs=api_pool, execution_llm_config=exec_llm_config,
        workspace_path=args.workspace_path, max_concurrent_tasks=args.max_concurrent_tasks,
        workflow_timeout=args.workflow_timeout, dataset_base_path=args.dataset_base_path,
        custom_dataset_paths=custom_paths, training_data_output=args.training_data_output,
        no_save_workflows=args.no_save_workflows # <--- 传递参数
    )
    await orchestrator.run(generation_tasks)

if __name__ == "__main__":
    asyncio.run(main())