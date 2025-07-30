import os
import sys
import asyncio
import importlib
import argparse
import json
import logging
import time
import random
from typing import Dict, List, Any, Tuple
from openai import AsyncOpenAI

# --- 设置Python路径 (如果需要) ---
# 这部分可以根据您的项目结构调整或保留
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 假设 ScoreFlow 在上一级目录
SCOREFLOW_PATH = os.path.dirname(CURRENT_DIR) 
if SCOREFLOW_PATH not in sys.path:
    sys.path.append(SCOREFLOW_PATH)

from ScoreFlow.scripts.base_handler import BenchmarkHandler

# --- 配置解析 ---
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='工作流生成器 (V6 - 仅生成)')
    
    # === 参数简化和修改 ===
    parser.add_argument('--api-pool', type=str, required=True, help='API配置池 (JSON string)')
    parser.add_argument('--workspace-path', type=str, default=os.path.join(CURRENT_DIR, "workspace_v6"), help='工作空间路径')
    parser.add_argument('--benchmark', type=str, required=True, help='要处理的基准测试名称 (例如: gsm8k)')
    # 合并后的数据集路径参数
    parser.add_argument('--dataset-path', type=str, required=True, help='数据集文件的完整路径 (例如: /path/to/gsm8k.jsonl)')
    parser.add_argument('--generation-tasks', type=str, required=True, help='生成任务配置, e.g., "1_2_3,4_5"')
    parser.add_argument('--training-data-output', type=str, help='训练数据输出文件路径 (JSONL)')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='日志级别')
    parser.add_argument('--max-concurrent-tasks', type=int, default=10, help='最大并发任务数')
    
    ### 修改点 1: 增加新的命令行参数 --id-start-index ###
    parser.add_argument('--id-start-index', type=int, default=0, help='生成工作流ID的起始索引')
    parser.add_argument('--parallelism', type=int, default=2, help='每个数据组合生成的工作流并行度')
    parser.add_argument('--max-concurrent-groups', type=int, default=5, help='最大并发组数')
    
    return parser.parse_args()

def parse_api_pool(api_pool_str: str) -> List[Dict]:
    try:
        return json.loads(api_pool_str)
    except json.JSONDecodeError as e:
        logging.error(f"API池配置解析失败: {e}")
        sys.exit(1)

def parse_generation_tasks_for_benchmark(tasks_str: str) -> List[List[int]]:
    """
    解析单个 benchmark 的生成任务配置。
    支持新格式：用'_'连接的非连续索引组，如 "1_5_8"。
    与旧版不同，这里只处理一个benchmark的字符串，例如 "1_2,5_8_9"
    """
    indices_list = []
    if not tasks_str:
        return indices_list
        
    for task_group in tasks_str.split(','):
        task_group = task_group.strip()
        if '_' in task_group:
            indices_list.append([int(i) for i in task_group.split('_')])
        elif '-' in task_group:
            start, end = map(int, task_group.split('-'))
            indices_list.append(list(range(start, end + 1)))
        else:
            indices_list.append([int(task_group)])
            
    return indices_list

def get_benchmark_handler(benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
    """动态导入并实例化指定 benchmark 的处理器。"""
    try:
        handler_module_path = f"ScoreFlow.scripts.{benchmark_name.lower()}.handler"
        handler_module = importlib.import_module(handler_module_path)
        
        # 约定 Handler 类名为 BenchmarkNameHandler (例如 Gsm8kHandler)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        
        return handler_class(dataset_path=dataset_path)
    except (ModuleNotFoundError, AttributeError, ValueError) as e:
        logging.error(f"无法为 benchmark '{benchmark_name}' 加载处理器: {e}")
        raise

async def call_openai_compatible_api(api_config: Dict, messages: List[Dict]) -> str:
    # 这个函数保持不变
    try:
        client = AsyncOpenAI(api_key=api_config.get("api_key"), base_url=api_config.get("base_url"))
        completion = await client.chat.completions.create(model=api_config.get("model"), messages=messages)
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"调用API时出错 (model: {api_config.get('model')}): {e}")
        raise e


class WorkflowGenerator:
    def __init__(self, api_configs: List[Dict], workspace_path: str, handler: BenchmarkHandler,
                 training_data_output: str = None, max_concurrent_groups: int = 5):
        if not api_configs:
            raise ValueError("生成API配置不能为空。")
        self.api_configs = api_configs
        self.workspace_path = workspace_path
        self.handler = handler
        self.benchmark_name = handler.benchmark_name
        self.training_data_output = training_data_output
        self.max_concurrent_groups = max_concurrent_groups

        # 创建工作流保存目录
        self.workflows_output_dir = os.path.join(self.workspace_path, "generated_workflows", self.benchmark_name)
        os.makedirs(self.workflows_output_dir, exist_ok=True)

    def _load_prompt_templates(self) -> Tuple[str, str, str, List[str]]:
        """从 benchmark 的 conditions 模块加载 Prompt 模板。"""
        try:
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{self.benchmark_name}.conditions")
            return (
                getattr(conditions_module, "START_PROMPT", ""), 
                getattr(conditions_module, "END_PROMPT", ""),
                getattr(conditions_module, "SYSTEM_PROMPT", "You are a helpful AI assistant."),
                getattr(conditions_module, "META_PROMPTS", [])
            )
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"无法为 benchmark '{self.benchmark_name}' 加载脚本模板: {e}")
            raise e

    def _construct_generation_prompt(self, data_indices: List[int], existing_workflow: str = None) -> Tuple[List[Dict], str]:
        """使用 Handler 构建生成请求的 Prompt。"""
        start_prompt, end_prompt, system_prompt, meta_prompts = self._load_prompt_templates()
        
        # 1. 使用 handler 获取问题文本
        problem_text = self.handler.get_prompt_text(data_indices)
        
        # 2. 构建 Prompt
        selected_meta_prompt = random.choice(meta_prompts) if meta_prompts else ""
        final_end_prompt = f"\n**CRITICAL INSTRUCTION FOR THIS SPECIFIC TASK:**\n{selected_meta_prompt}\n\n" + end_prompt
        
        # 3. 如果有已存在的工作流，添加指示生成不同逻辑的工作流
        if existing_workflow:
            diversity_prompt = f"\n\n**CRITICAL REQUIREMENT - DIFFERENT LOGIC**: \n<existing_workflow>\n{existing_workflow}\n</existing_workflow>\n\n**You MUST generate a workflow with FUNDAMENTALLY DIFFERENT LOGIC from the above workflow.**\n\nDO NOT just change variable names (solution vs solution1) or formatting!\n\nInstead, you MUST use at least TWO of the following strategies to ensure different logic:\n1. **Different operator sequence**: Use operators in a different order (e.g., if existing uses generate->fix->review, try generate->review->ensemble)\n2. **Different control flow**: Use different conditional logic or loop structures (e.g., if existing checks result once, try multiple attempts with different strategies)\n3. **Different parallel/serial execution**: If existing runs operators serially, try parallel execution, or vice versa\n4. **Different ensemble strategy**: If existing uses ScEnsemble on all solutions, try selecting the best one first\n5. **Different error handling**: Use different approaches when solutions fail (e.g., retry with different prompts vs fix existing)\n6. **Different operator combinations**: Use operators that the existing workflow doesn't use at all\n\n**REMEMBER: The goal is LOGICAL DIFFERENCE, not cosmetic changes!**\n\n"
            user_prompt_str = start_prompt + f"{problem_text}" + diversity_prompt + final_end_prompt
        else:
            user_prompt_str = start_prompt + f"{problem_text}" + final_end_prompt

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt_str}
        ]
        
        return messages, problem_text

    async def _generate_one_workflow(self, workflow_id: str, data_indices: List[int], api_config: Dict, existing_workflow: str = None):
        """生成单个工作流并保存文件。"""
        try:
            # 1. 构建 Prompt
            messages, problem_text = self._construct_generation_prompt(data_indices, existing_workflow)
            
            # 2. 调用 API
            logging.info(f"向 {api_config.get('provider', 'api')} 发送生成请求 (ID: {workflow_id}, Indices: {data_indices})")
            response_content = await call_openai_compatible_api(api_config, messages)
            
            # 3. 提取代码
            # 优先提取 <graph> 标签内的内容，否则剥离 ```python ```
            if "<graph>" in response_content:
                code = response_content.split('<graph>')[1].split('</graph>')[0].strip()
            else:
                code = response_content.strip().strip('```python').strip('```').strip()

            # 4. 保存结果
            if code:
                self._save_workflow_files(workflow_id, code, data_indices)
                logging.info(f"成功生成并保存工作流: {workflow_id}")
                # 立即保存训练数据（而不是暂存）
                if self.training_data_output:
                    _, _, system_prompt, _ = self._load_prompt_templates()
                    training_record = {
                        "workflow_id": workflow_id,  # 添加工作流ID以便后续匹配
                        "benchmark": self.benchmark_name,
                        "data_indices": data_indices,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": problem_text},
                            {"role": "assistant", "content": code}
                        ]
                    }
                    self._save_single_training_record(training_record)
                return code  # 返回生成的代码供后续使用
            else:
                raise ValueError("API响应中未能提取有效代码。")

        except Exception as e:
            logging.error(f"生成工作流 {workflow_id} 时失败: {e}")
            return None

    def _save_workflow_files(self, workflow_id: str, code: str, indices: List[int]):
        """保存 .py 代码和 .meta.json 元数据文件。"""
        # 保存纯代码 .py 文件
        py_path = os.path.join(self.workflows_output_dir, f"{workflow_id}.py")
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(f"# Workflow ID: {workflow_id}\n# Benchmark: {self.benchmark_name}\n# Data Indices: {indices}\n\n{code}")
        
        # 保存元数据 .meta.json 文件
        meta_path = os.path.join(self.workflows_output_dir, f"{workflow_id}.meta.json")
        meta_data = {
            "id": workflow_id,
            "benchmark": self.benchmark_name,
            "data_indices": indices,
            "dataset_path": self.handler.dataset_path, # 保存数据集路径供执行器使用
            "generation_timestamp": time.time()
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=4)

    def _save_single_training_record(self, record: Dict):
        """立即保存单条训练数据到文件（线程安全）。"""
        if not self.training_data_output:
            return
        
        output_dir = os.path.dirname(self.training_data_output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # 使用追加模式，每次写入一条记录
        with open(self.training_data_output, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        logging.debug(f"训练数据已保存: {record['workflow_id']}")

    ### 修改点 2: 修改 run 方法的签名，接收 start_index 和 parallelism ###
    async def run(self, data_indices_list: List[List[int]], start_index: int, parallelism: int = 2):
        """主运行逻辑，创建并执行所有生成任务。"""
        # 修改日志，显示ID起始点和并行度
        total_workflows = len(data_indices_list) * parallelism
        logging.info(f"开始为 Benchmark '{self.benchmark_name}' 生成 {total_workflows} 个工作流 ({len(data_indices_list)} 组 × {parallelism} 并行度)，ID 从 {start_index} 开始...")
        
        # 创建信号量限制并发组数
        semaphore = asyncio.Semaphore(self.max_concurrent_groups)
        api_index_counter = 0
        
        # 创建所有组的任务，组间并行执行，组内串行执行
        group_tasks = []
        
        async def generate_group_with_semaphore(indices, group_index, parallelism, api_start_index):
            async with semaphore:
                await self._generate_group_workflows(indices, group_index, parallelism, api_start_index)
        
        for i, indices in enumerate(data_indices_list):
            # 为每个组创建一个异步任务
            group_task = generate_group_with_semaphore(
                indices, 
                start_index + i, 
                parallelism, 
                api_index_counter
            )
            group_tasks.append(group_task)
            api_index_counter += parallelism  # 预分配API索引
        
        # 并行执行所有组的任务（受信号量限制）
        await asyncio.gather(*group_tasks)
        
        if self.training_data_output:
            # 统计已保存的训练数据条数
            total_workflows = len(data_indices_list) * parallelism
            logging.info(f"工作流生成阶段完成。已生成 {total_workflows} 个工作流，训练数据已保存到: {self.training_data_output}")
        else:
            logging.info("工作流生成阶段完成。")
    
    async def _generate_group_workflows(self, indices: List[int], group_index: int, parallelism: int, api_start_index: int):
        """为一个数据组生成多个工作流，组内串行执行以便后续工作流参考前面的工作流"""
        generated_workflows = []  # 存储已生成的工作流代码
        
        for j in range(parallelism):
            workflow_id = f"{self.benchmark_name}_{group_index}_{j}"
            api_config = self.api_configs[(api_start_index + j) % len(self.api_configs)]
            
            # 第一个工作流不需要参考已有工作流
            if j == 0:
                generated_code = await self._generate_one_workflow(workflow_id, indices, api_config)
            else:
                # 后续工作流需要参考第一个生成的工作流
                existing_workflow = generated_workflows[0] if generated_workflows else None
                generated_code = await self._generate_one_workflow(workflow_id, indices, api_config, existing_workflow)
            
            if generated_code:
                generated_workflows.append(generated_code)


async def main():
    args = parse_arguments()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')

    start_time = time.time()
    
    api_pool = parse_api_pool(args.api_pool)
    if not api_pool:
        logging.error("错误: API配置池为空！")
        return
        
    generation_indices_list = parse_generation_tasks_for_benchmark(args.generation_tasks)
    
    try:
        # 使用新的 Handler 模式
        handler = get_benchmark_handler(args.benchmark, args.dataset_path)
        
        generator = WorkflowGenerator(
            api_configs=api_pool,
            workspace_path=args.workspace_path,
            handler=handler,
            training_data_output=args.training_data_output,
            max_concurrent_groups=args.max_concurrent_groups
        )
        
        ### 修改点 4: 将从命令行解析出的 id_start_index 和 parallelism 传递给 run 方法 ###
        await generator.run(generation_indices_list, args.id_start_index, args.parallelism)
        
    except (ImportError, FileNotFoundError, ValueError) as e:
        logging.error(f"初始化或运行生成器时发生严重错误: {e}")
        sys.exit(1)

    logging.info(f"\n整个生成流程耗时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())

      