"""
VERL支持工具模块 - 严格复用现有系统组件
"""
import os
import sys
import json
import random
import importlib
import logging
from typing import List, Dict, Any, Tuple

# 添加ScoreFlow路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# ScoreFlow在Test_FILE目录下
SCOREFLOW_PATH = os.path.dirname(os.path.dirname(CURRENT_DIR))  # 上一级目录
SCRIPTS_PATH = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts")
if SCOREFLOW_PATH not in sys.path:
    sys.path.append(SCOREFLOW_PATH)
if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

# 直接导入base_handler模块
try:
    sys.path.append(os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts"))
    from base_handler import BenchmarkHandler
except ImportError:
    # 如果上面失败，尝试绝对路径导入
    import importlib.util
    base_handler_path = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts", "base_handler.py")
    spec = importlib.util.spec_from_file_location("base_handler", base_handler_path)
    base_handler_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_handler_module)
    BenchmarkHandler = base_handler_module.BenchmarkHandler

def get_benchmark_handler(benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
    """
    与 workflow_generator.py 和 workflow_executor.py 完全相同的函数
    动态导入并实例化指定 benchmark 的处理器
    """
    try:
        # 直接导入handler模块
        handler_path = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts", benchmark_name.upper(), "handler.py")
        
        if not os.path.exists(handler_path):
            # 尝试小写目录名
            handler_path = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts", benchmark_name.lower(), "handler.py")
            
        if not os.path.exists(handler_path):
            raise FileNotFoundError(f"Handler文件未找到: {handler_path}")
            
        # 使用importlib直接加载
        spec = importlib.util.spec_from_file_location(f"{benchmark_name}_handler", handler_path)
        handler_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler_module)
        
        # 约定 Handler 类名为 BenchmarkNameHandler (例如 Gsm8kHandler)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        
        return handler_class(dataset_path=dataset_path)
    except (ModuleNotFoundError, AttributeError, ValueError, FileNotFoundError) as e:
        logging.error(f"无法为 benchmark '{benchmark_name}' 加载处理器: {e}")
        raise

def create_generation_tasks(total_problems: int, min_sample: int, max_sample: int) -> List[List[int]]:
    """
    与 master_runner.py 完全相同的函数
    从总问题数中创建随机抽样任务列表
    """
    print(f"正在从 {total_problems} 个问题中创建随机抽样任务...")
    indices = list(range(total_problems))
    random.shuffle(indices)
    
    tasks = []
    i = 0
    while i < len(indices):
        chunk_size = random.randint(min_sample, max_sample)
        chunk = indices[i:i + chunk_size]
        if not chunk:
            continue
        tasks.append(chunk)
        i += chunk_size
        
    print(f"成功创建 {len(tasks)} 个生成任务。")
    return tasks

def create_train_test_split(total_problems: int, train_ratio: float = 0.8, 
                          min_sample: int = 2, max_sample: int = 4) -> Tuple[List[List[int]], List[int]]:
    """
    严格按照 master_runner.py 的逻辑进行训练/测试集分割
    确保训练集和测试集完全不重叠
    """
    # 1. 使用相同的随机打乱逻辑
    indices = list(range(total_problems))
    random.shuffle(indices)
    
    # 2. 按比例分割
    split_point = int(total_problems * train_ratio)
    train_indices = indices[:split_point]
    test_indices = indices[split_point:]
    
    # 3. 为训练集创建任务组 (复用master_runner逻辑)
    train_tasks = []
    i = 0
    while i < len(train_indices):
        chunk_size = random.randint(min_sample, max_sample)
        chunk = train_indices[i:i + chunk_size]
        if not chunk:
            continue
        train_tasks.append(chunk)
        i += chunk_size
    
    logging.info(f"训练/测试集分割完成: {len(train_tasks)} 个训练任务, {len(test_indices)} 个测试样本")
    return train_tasks, test_indices

def load_prompt_templates(benchmark_name: str) -> Tuple[str, str, str, List[str]]:
    """
    与 workflow_generator.py 完全相同的函数
    从 benchmark 的 conditions 模块加载 Prompt 模板
    """
    try:
        # 直接加载conditions模块
        conditions_path = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts", benchmark_name.upper(), "conditions.py")
        
        if not os.path.exists(conditions_path):
            conditions_path = os.path.join(SCOREFLOW_PATH, "ScoreFlow", "scripts", benchmark_name.lower(), "conditions.py")
            
        if not os.path.exists(conditions_path):
            raise FileNotFoundError(f"Conditions文件未找到: {conditions_path}")
            
        spec = importlib.util.spec_from_file_location(f"{benchmark_name}_conditions", conditions_path)
        conditions_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conditions_module)
        
        return (
            getattr(conditions_module, "START_PROMPT", ""), 
            getattr(conditions_module, "END_PROMPT", ""),
            getattr(conditions_module, "SYSTEM_PROMPT", "You are a helpful AI assistant."),
            getattr(conditions_module, "META_PROMPTS", [])
        )
    except (ModuleNotFoundError, AttributeError, FileNotFoundError) as e:
        logging.error(f"无法为 benchmark '{benchmark_name}' 加载脚本模板: {e}")
        raise e

def construct_generation_prompt(handler: BenchmarkHandler, data_indices: List[int], 
                              benchmark_name: str) -> Tuple[List[Dict], str]:
    """
    与 workflow_generator.py 完全相同的函数
    使用 Handler 构建生成请求的 Prompt
    """
    start_prompt, end_prompt, system_prompt, meta_prompts = load_prompt_templates(benchmark_name)
    
    # 1. 使用 handler 获取问题文本
    problem_text = handler.get_prompt_text(data_indices)
    
    # 2. 构建 Prompt
    selected_meta_prompt = random.choice(meta_prompts) if meta_prompts else ""
    final_end_prompt = f"\n**CRITICAL INSTRUCTION FOR THIS SPECIFIC TASK:**\n{selected_meta_prompt}\n\n" + end_prompt
    user_prompt_str = start_prompt + f"{problem_text}" + final_end_prompt

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt_str}
    ]
    
    return messages, problem_text

def format_chat_template(messages: List[Dict]) -> str:
    """
    将messages格式化为HuggingFace chat_template格式
    """
    formatted_parts = []
    for msg in messages:
        role = msg['role']
        content = msg['content']
        if role == 'system':
            formatted_parts.append(f"<|system|>\n{content}")
        elif role == 'user':
            formatted_parts.append(f"<|user|>\n{content}")
        elif role == 'assistant':
            formatted_parts.append(f"<|assistant|>\n{content}")
    
    return "\n".join(formatted_parts) + "<|end|>"

def load_config(config_path: str = None) -> Dict:
    """加载配置文件"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_dir_exists(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True) 