#!/usr/bin/env python3
"""
简单的Workflow测试工具
直接修改配置区的参数，然后运行即可测试workflow
"""

import os
import sys
import asyncio
import json
import importlib
from typing import Dict, Any
import logging

# 添加项目路径
sys.path.append('/Users/luogan/Code/workflow_generation/Flow_RL')
os.chdir('/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE')

# ========================================
#           配 置 区
# ========================================

# Workflow文件路径
WORKFLOW_PATH = "/Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/workspace_mbpp_COT/generated_workflows/mbpp/mbpp_0_0.py"

# Benchmark名称（可以从workflow路径自动推断）
BENCHMARK = "mbpp"  # gsm8k, mbpp, drop, etc.

# 数据集路径
DATASET_PATH = "/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/mbpp/train.jsonl"

# 测试数据的索引
TEST_INDEX = 5

# LLM配置
LLM_CONFIG = {
    "provider": "openai",
    "model": "qwen-turbo",
    "api_key": "956c41bd0f31beaf68b871d4987af4bb",
    "base_url": "https://idealab.alibaba-inc.com/api/openai/v1"
}

# 工作流执行超时（秒）
WORKFLOW_TIMEOUT = 360

# 日志级别
LOG_LEVEL = "INFO"

# ========================================
#           主 程 序
# ========================================

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.configs.llm_config import LLMConfig, LLMType
from ScoreFlow.scripts.base_handler import BenchmarkHandler


def get_benchmark_handler(benchmark_name: str, dataset_path: str, config=None) -> BenchmarkHandler:
    """动态加载benchmark handler"""
    try:
        handler_module_path = f"ScoreFlow.scripts.{benchmark_name.lower()}.handler"
        handler_module = importlib.import_module(handler_module_path)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        return handler_class(dataset_path=dataset_path, config=config)
    except Exception as e:
        logging.error(f"无法加载 {benchmark_name} 的handler: {e}")
        raise


def convert_config_for_metagpt(config_dict: Dict) -> LLMConfig:
    """将配置字典转换为MetaGPT的LLMConfig"""
    provider = config_dict.get('provider', 'openai')
    api_type_map = {
        'openai': LLMType.OPENAI,
        'azure': LLMType.AZURE,
        'gemini': LLMType.GEMINI,
        'claude': LLMType.CLAUDE,
    }
    api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
    
    return LLMConfig(
        api_type=api_type,
        model=config_dict.get('model'),
        api_key=config_dict.get('api_key'),
        base_url=config_dict.get('base_url')
    )


async def test_workflow():
    """主测试函数"""
    print("=" * 60)
    print("Workflow 测试工具")
    print("=" * 60)
    
    # 自动推断benchmark（如果需要）
    if not BENCHMARK:
        # 从路径推断：.../generated_workflows/xxx/...
        parts = WORKFLOW_PATH.split('/')
        if 'generated_workflows' in parts:
            idx = parts.index('generated_workflows')
            benchmark = parts[idx + 1] if idx + 1 < len(parts) else None
        else:
            benchmark = None
    else:
        benchmark = BENCHMARK
    
    if not benchmark:
        print("❌ 无法确定benchmark名称，请在配置区设置BENCHMARK")
        return
    
    print(f"📋 Benchmark: {benchmark}")
    print(f"📄 Workflow: {os.path.basename(WORKFLOW_PATH)}")
    print(f"📊 Dataset: {os.path.basename(DATASET_PATH)}")
    print(f"🔢 Test Index: {TEST_INDEX}")
    print(f"⏱️  Timeout: {WORKFLOW_TIMEOUT}秒")
    print("-" * 60)
    
    # 1. 准备LLM配置
    metagpt_config = convert_config_for_metagpt(LLM_CONFIG)
    
    # 2. 加载Handler
    print("📚 加载Handler...")
    handler = get_benchmark_handler(benchmark, DATASET_PATH, metagpt_config)
    
    # 3. 获取测试数据
    print(f"📖 获取索引 {TEST_INDEX} 的数据...")
    verification_data = handler.get_verification_data(TEST_INDEX)
    problem_text = handler.get_prompt_text([TEST_INDEX])
    
    print("\n🔍 问题预览:")
    print("-" * 40)
    # 只显示前500个字符
    preview = problem_text[:500] + "..." if len(problem_text) > 500 else problem_text
    print(preview)
    print("-" * 40)
    
    # 4. 加载workflow代码
    print("\n🔧 加载Workflow代码...")
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow_code = f.read()
    
    # 5. 构建可执行脚本
    print("🏗️  构建可执行脚本...")
    script_parts = handler.build_executable_script(workflow_code, WORKFLOW_TIMEOUT)
    
    # 拼接完整脚本
    full_script = (
        script_parts["python_start"] + "\n" +
        script_parts["workflow_code"] + "\n" +
        script_parts["python_end"]
    )
    
    # 6. 准备执行环境
    print("⚙️  准备执行环境...")
    
    # 导入必要的模块
    # if benchmark == "drop":
    #     operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
    # else:
    #     operator_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark}.operator")
    operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
    
    # 准备全局命名空间
    exec_globals = {
        'asyncio': asyncio,
        'create': create_llm_instance,
        'operator': operator_module,
        'Literal': getattr(__import__('typing'), 'Literal'),
        'List': list,
        'Dict': dict,
        'Any': Any,
        'Union': getattr(__import__('typing'), 'Union'),
    }
    
    # 7. 执行workflow
    print("\n🚀 执行Workflow...")
    print("=" * 60)
    
    try:
        # 执行脚本创建Workflow类
        execution_namespace = {}
        exec(full_script, exec_globals, execution_namespace)
        
        WorkflowClass = execution_namespace.get('Workflow')
        if not WorkflowClass:
            raise ValueError("未找到Workflow类")
        
        # 创建workflow实例
        workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
        
        # 执行workflow
        import time
        start_time = time.time()
        
        # 根据call_signature决定如何调用
        if "timeout=" in script_parts["call_signature"]:
            result = await asyncio.wait_for(
                workflow_instance(timeout=WORKFLOW_TIMEOUT),
                timeout=WORKFLOW_TIMEOUT + 10
            )
        else:
            result = await asyncio.wait_for(
                workflow_instance(),
                timeout=WORKFLOW_TIMEOUT
            )
        
        execution_time = time.time() - start_time
        
        print("=" * 60)
        print(f"\n✅ 执行成功！耗时: {execution_time:.2f}秒")
        
        # 8. 显示结果
        print("\n📝 Workflow输出:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # 9. 验证结果
        print("\n🎯 验证结果...")
        
        # 获取标准答案
        if 'answer' in verification_data:
            ground_truth = verification_data['answer']
        elif 'all_answers' in verification_data:
            ground_truth = verification_data['all_answers']
        else:
            ground_truth = "未找到标准答案"
        
        print(f"📌 标准答案: {ground_truth}")
        
        # 使用handler的judge方法
        import inspect
        if inspect.iscoroutinefunction(handler.judge):
            is_correct = await handler.judge(result, verification_data)
        else:
            is_correct = handler.judge(result, verification_data)
        
        if is_correct:
            print("✅ 答案正确！")
        else:
            print("❌ 答案错误")
        
    except asyncio.TimeoutError:
        print(f"\n⏱️ 执行超时（超过{WORKFLOW_TIMEOUT}秒）")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


async def main():
    """主入口"""
    try:
        await test_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())