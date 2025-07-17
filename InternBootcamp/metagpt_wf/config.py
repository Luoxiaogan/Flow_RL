"""
配置文件 - MetaGPT Workflow Executor
"""

# LLM配置
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# 文件路径配置
PATHS = {
    "dataset_file": "multi_task_dataset.jsonl",
    "output_file": "metagpt_workflow_results.jsonl",
    "test_output_file": "test_results.json"
}

# 执行配置
EXECUTION_CONFIG = {
    "temperature_generation": 0.7,  # 生成workflow模板时的temperature
    "temperature_execution": 0.3,   # 执行任务时的temperature
    "max_concurrent_tasks": 4,       # 最大并发任务数
    "timeout_seconds": 120           # 单个任务超时时间
}

# MetaGPT Workflow模板配置
WORKFLOW_TEMPLATE_CONFIG = {
    "available_operators": [
        "Custom",
        "Review", 
        "Programmer",
        "ScEnsemble"
    ],
    "default_operators": ["Custom", "Review"],  # 默认使用的operators
    "require_graph_tags": True,  # 是否要求<graph>标签
}

# 验证配置
VERIFICATION_CONFIG = {
    "answer_tags": ["[answer]", "[/answer]"],  # 答案标签
    "enable_verification": True,  # 是否启用验证
    "fallback_on_error": True     # 错误时是否回退到直接LLM调用
} 