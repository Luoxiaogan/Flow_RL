# workflow_executor.py

import os
import sys
import asyncio
import importlib
import argparse
import json
import logging
import csv
import re
import random  # 新增：用于随机选择测试index
from typing import Dict, Any, List # 增加 List 导入

# --- 设置Python路径 (如果需要) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOREFLOW_PATH = os.path.dirname(CURRENT_DIR)
if SCOREFLOW_PATH not in sys.path:
    sys.path.append(SCOREFLOW_PATH)

# 这两个导入对于执行工作流至关重要
from metagpt.provider.llm_provider_registry import create_llm_instance, LLMType
from metagpt.configs.llm_config import LLMConfig

from ScoreFlow.scripts.base_handler import BenchmarkHandler

# --- 配置解析 ---
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='工作流执行与验证器 (V2 - 修复版)')
    
    # === 核心输入 ===
    parser.add_argument('--workflow-path', type=str, required=True, help='要执行的工作流 .py 文件的路径')
    parser.add_argument('--exec-llm', type=str, required=True, help='执行LLM配置 (JSON string)')
    parser.add_argument('--workspace-path', type=str, required=True, help='主工作空间路径，用于保存CSV结果')
    
    # === 其他配置 ===
    parser.add_argument('--workflow-timeout', type=int, default=120, help='单个工作流的执行超时时间(秒)')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='日志级别')

    return parser.parse_args()

def parse_exec_llm(exec_llm_str: str) -> Dict:
    try:
        return json.loads(exec_llm_str)
    except json.JSONDecodeError as e:
        logging.error(f"执行LLM配置解析失败: {e}")
        sys.exit(1)

def get_benchmark_handler(benchmark_name: str, dataset_path: str, config=None) -> BenchmarkHandler:
    """与 generator 中相同的函数，用于动态加载处理器。"""
    try:
        handler_module_path = f"ScoreFlow.scripts.{benchmark_name.lower()}.handler"
        handler_module = importlib.import_module(handler_module_path)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        return handler_class(dataset_path=dataset_path, config=config)
    except (ModuleNotFoundError, AttributeError, ValueError) as e:
        logging.error(f"无法为 benchmark '{benchmark_name}' 加载处理器: {e}")
        raise

def convert_config_for_metagpt(config_dict: Dict) -> LLMConfig:
    """将字典格式的LLM配置转换为metagpt的LLMConfig对象。"""
    provider = config_dict.get('provider', 'openai')
    api_type_map = {
        'openai': LLMType.OPENAI, 'azure': LLMType.AZURE, 'gemini': LLMType.GEMINI,
        'claude': LLMType.CLAUDE, 'moonshot': LLMType.MOONSHOT,
        'zhipuai': LLMType.ZHIPUAI, 'qianfan': LLMType.QIANFAN,
        # ... 可以添加更多映射
    }
    api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
    
    return LLMConfig(
        api_type=api_type,
        model=config_dict.get('model'),
        api_key=config_dict.get('api_key'),
        base_url=config_dict.get('base_url')
    )

def save_result_to_csv(workspace_path: str, result_data: Dict[str, Any]):
    """以线程安全的方式将单条执行结果追加到CSV文件。"""
    csv_file = os.path.join(workspace_path, "execution_results.csv")
    file_exists = os.path.exists(csv_file)
    
    # 确保主工作区目录存在
    os.makedirs(workspace_path, exist_ok=True)
    
    # 使用 'a' 模式追加写入
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 如果文件是新创建的，则写入表头
        if not file_exists:
            writer.writerow([
                "ID", 
                "Benchmark", 
                "Data_Indices",       # 训练时使用的indices
                "Test_Data_Indice",   # 新增：实际测试使用的index
                "Status", 
                "Error_Type",
                "Ground_Truth",       # 标准答案
                "Model_Output"        # 模型输出
            ])
        
        writer.writerow([
            result_data["id"],
            result_data["benchmark"],
            '_'.join(map(str, result_data["data_indices"])),
            str(result_data.get("test_index", "")),  # 新增：测试index
            result_data["status"],
            result_data["error"].split(':')[0] if result_data.get("error") else "",
            result_data.get("ground_truth", ""),
            result_data.get("model_output", "")
        ])
    logging.info(f"结果已记录到: {csv_file}")

async def execute_and_verify(args: argparse.Namespace):
    """主执行和验证逻辑。"""
    workflow_id, benchmark_name, status, error_msg = "unknown", "unknown", "initialization_failed", ""
    data_indices = []
    verification_index = None  # 初始化verification_index，确保在作用域内可访问

    try:
        # 1. 加载元数据
        meta_path = args.workflow_path.replace('.py', '.meta.json')
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"元数据文件未找到: {meta_path}")
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        workflow_id = meta['id']
        benchmark_name = meta['benchmark']
        dataset_path = meta['dataset_path']
        data_indices = meta['data_indices']

        logging.info(f"开始处理工作流 {workflow_id} (Benchmark: {benchmark_name})...")
        
        # 获取执行配置，用于传递给handler
        exec_llm_config_dict = parse_exec_llm(args.exec_llm)
        metagpt_llm_config = convert_config_for_metagpt(exec_llm_config_dict)

        # 2. 初始化 Handler 并获取验证所需数据（传入config）
        handler = get_benchmark_handler(benchmark_name, dataset_path, metagpt_llm_config)
        
        # 新增：从训练集外随机选择测试index
        # 获取数据集的总大小
        total_dataset_size = len(handler.data)
        
        # 计算所有可用的indices
        all_indices = set(range(total_dataset_size))
        
        # 排除训练时使用的indices
        available_test_indices = all_indices - set(data_indices)
        
        # 随机选择一个测试index
        if available_test_indices:
            verification_index = random.choice(list(available_test_indices))
            logging.info(f"从 {len(available_test_indices)} 个未使用的indices中随机选择了测试index: {verification_index}")
            logging.info(f"训练indices: {data_indices}, 测试index: {verification_index}")
        else:
            # 边界情况：如果所有indices都被使用了，则回退到原逻辑
            verification_index = data_indices[0]
            logging.warning(f"所有indices都已被使用，回退到使用训练index: {verification_index}")
        verification_data = handler.get_verification_data(verification_index)
        
        # 3. 加载工作流代码
        with open(args.workflow_path, 'r', encoding='utf-8') as f:
            workflow_code = f.read()
        
        # 4. 使用 Handler 构建完整的可执行脚本
        # full_script_code = handler.build_executable_script(workflow_code, args.workflow_timeout)
        script_parts = handler.build_executable_script(workflow_code, args.workflow_timeout)
        # 将各个部分拼接成完整的脚本
        full_script_code = (
            script_parts["python_start"] + "\n" +
            script_parts["workflow_code"] + "\n" +
            script_parts["python_end"]
        )
        
        # 调试：打印脚本的前500个字符
        logging.info(f"[{workflow_id}] 拼接后的脚本代码前500字符:\n{full_script_code[:500]}...")
        
        # 5. 准备执行环境并执行脚本
        execution_namespace = {}
        
        ### --- 修改点：重构执行环境的准备过程 --- ###

        # 动态加载主 operator 模块
        # DROP使用common operators，其他benchmark使用自己的operators
        # if benchmark_name == "drop":
        #     operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
        # else:
        #     operator_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name}.operator")
        operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
        
        # 准备一个基础的全局命名空间
        exec_globals = {
            'asyncio': asyncio,
            'create': create_llm_instance,
            'operator': operator_module,
            'Literal': getattr(__import__('typing'), 'Literal'),
            'List': List, # 明确提供 List 类型，因为模板中会用到
        }

        # 动态检查并注入可选的 operator_an 模块及其内容
        # 这是为了支持像 MBPP 这样有额外 Pydantic 模型的 benchmark
        try:
            an_module_path = f"ScoreFlow.scripts.{benchmark_name}.operator_an"
            operator_an_module = importlib.import_module(an_module_path)
            
            # 遍历 operator_an 模块中的所有公共成员 (如 CodeRunnerResult 类)
            for attr_name in dir(operator_an_module):
                if not attr_name.startswith('_'):
                    # 将其直接注入到全局命名空间中
                    # 这使得工作流代码可以直接使用 `CodeRunnerResult` 而无需导入
                    exec_globals[attr_name] = getattr(operator_an_module, attr_name)
            logging.debug(f"成功注入模块 '{an_module_path}' 的内容到执行环境。")
            
        except ModuleNotFoundError:
            # 如果 benchmark 没有 operator_an.py 文件，则静默处理
            logging.debug(f"未找到可选的 'operator_an.py' 模块，跳过注入。")
            pass

        exec(full_script_code, exec_globals, execution_namespace)
        
        WorkflowClass = execution_namespace.get('Workflow')
        if not WorkflowClass:
            raise ValueError("在执行的脚本中未找到 'Workflow' 类。")
        
        # 将verification_data转换为格式化的问题文本
        # 使用handler的get_prompt_text方法，复用已有的格式化逻辑
        problem_index = verification_data.get('index', verification_index)
        problem_text = handler.get_prompt_text([problem_index])
        
        # 实例化并运行工作流，传入格式化的字符串
        workflow_instance = WorkflowClass(config=metagpt_llm_config, problem=problem_text)
        
        # 调试：确认workflow实例创建成功
        logging.info(f"[{workflow_id}] Workflow实例创建成功: {type(workflow_instance)}")

        # 关键：使用 handler 提供的、正确的调用签名来执行工作流
        # 根据 call_signature 的内容决定如何调用
        if "timeout=" in script_parts["call_signature"]:
            # 从 call_signature 中提取 timeout 值
            timeout_match = re.search(r'timeout=(\d+)', script_parts["call_signature"])
            if timeout_match:
                timeout_value = int(timeout_match.group(1))
                execution_result = await workflow_instance(timeout=timeout_value)
            else:
                # 如果无法提取，使用默认超时
                execution_result = await workflow_instance(timeout=args.workflow_timeout)
        else:
            # 旧版格式，不需要传入 timeout
            execution_result = await workflow_instance()
        
        # 调试：打印执行结果
        logging.info(f"[{workflow_id}] 执行结果: {execution_result}")
        logging.info(f"[{workflow_id}] 执行结果类型: {type(execution_result)}")
        
        # 6. 使用 Handler 进行验证
        logging.info(f"[{workflow_id}] 执行完毕，开始验证...")
        # 检查judge是否是协程函数，支持向后兼容
        import inspect
        if inspect.iscoroutinefunction(handler.judge):
            is_correct = await handler.judge(execution_result, verification_data)
        else:
            is_correct = handler.judge(execution_result, verification_data)
        
        # 调试：打印judge结果
        logging.info(f"[{workflow_id}] Judge结果: {is_correct}")
        logging.info(f"[{workflow_id}] 标准答案: {verification_data.get('answer', verification_data.get('all_answers', 'N/A'))}")
        status = "verified_correct" if is_correct else "verified_incorrect"
        logging.info(f"工作流 {workflow_id} 验证结果: {status}")
        
    except Exception as e:
        status = "execution_failed"
        error_msg = f"{type(e).__name__}: {e}"
        logging.error(f"处理工作流 {workflow_id} 时出错: {e}", exc_info=True)

    # 7. 无论成功与否，都记录结果
    # 处理model_output为JSON单行格式
    if 'execution_result' in locals() and execution_result:
        # 将输出转换为JSON格式，替换所有换行符为空格，确保CSV每条数据占一行
        model_output_json = json.dumps({"output": str(execution_result)}, ensure_ascii=False)
        # 替换所有换行符和回车符为空格
        model_output_json = model_output_json.replace('\n', ' ').replace('\r', ' ')
    else:
        model_output_json = '{}'
    
    # 处理ground_truth为JSON单行格式（与model_output保持一致）
    if 'verification_data' in locals() and verification_data:
        ground_truth_value = verification_data.get('answer', verification_data.get('all_answers', 'N/A'))
        ground_truth_json = json.dumps({"answer": str(ground_truth_value)}, ensure_ascii=False)
        # 替换所有换行符和回车符为空格
        ground_truth_json = ground_truth_json.replace('\n', ' ').replace('\r', ' ')
    else:
        ground_truth_json = '{}'
    
    result_data = {
        "id": workflow_id,
        "benchmark": benchmark_name,
        "data_indices": data_indices,
        "test_index": verification_index if 'verification_index' in locals() else None,  # 新增：记录实际测试的index
        "status": status,
        "error": error_msg,
        "ground_truth": ground_truth_json,  # 使用JSON格式的单行字符串
        "model_output": model_output_json  # 使用JSON格式的单行字符串
    }
    save_result_to_csv(args.workspace_path, result_data)

async def main():
    args = parse_arguments()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s')

    try:
        await execute_and_verify(args)
    except Exception as e:
        logging.critical(f"执行器发生无法恢复的严重错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())