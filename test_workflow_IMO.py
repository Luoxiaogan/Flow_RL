#!/usr/bin/env python3
"""
IMO Workflow测试工具 - 命令行版本
支持流式输出和灵活的参数配置
"""

import os
import sys
import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, Any
import importlib
import time
import traceback

# 添加项目路径
sys.path.append('/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT')
os.chdir('/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/Test_FILE')

# ========================================
#           命令行参数解析
# ========================================

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='IMO Workflow测试工具')

    # 数据索引参数
    parser.add_argument('--index', type=int, default=0,
                        help='workflow响应的索引 (默认: 0)')
    parser.add_argument('--problem-index', type=int, default=0,
                        help='IMO问题的索引 (默认: 0)')

    # 文件路径参数
    parser.add_argument('--imo-problem', required=True,
                        help='IMO问题文件路径 (JSONL格式)')
    parser.add_argument('--imo-response', required=True,
                        help='IMO响应文件路径 (JSONL格式)')

    # LLM配置参数
    parser.add_argument('--llm-model', default='qwen-turbo',
                        help='LLM模型名称 (默认: qwen-turbo)')
    parser.add_argument('--api-key', required=True,
                        help='API密钥')
    parser.add_argument('--base-url', required=True,
                        help='API基础URL')
    parser.add_argument('--provider', default='openai',
                        help='API提供商 (默认: openai)')

    # 执行配置
    parser.add_argument('--timeout', type=int, default=360,
                        help='workflow执行超时秒数 (默认: 360)')
    parser.add_argument('--stream', action='store_true',
                        help='启用流式输出')

    return parser.parse_args()

# ========================================
#           辅助函数
# ========================================

def load_problem(problem_file, problem_index):
    """从imo_problems.jsonl读取问题"""
    with open(problem_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == problem_index:
                try:
                    # 尝试用eval解析（对于有LaTeX的文件更宽松）
                    data = eval(line.strip())
                except:
                    # 如果失败，尝试JSON
                    data = json.loads(line.strip())

                return f"---\n**PROBLEM:**\n{data['problem']}\n---"

    raise ValueError(f"Problem index {problem_index} not found")

def load_workflow_code(response_file, index):
    """从响应文件读取workflow代码"""
    with open(response_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == index:
                data = json.loads(line.strip())
                content = data['response']['content']

                # 提取```python和```之间的代码
                start = content.find('```python')
                if start == -1:
                    raise ValueError(f"No Python code found in response {index}")

                end = content.find('```', start + 9)
                if end == -1:
                    raise ValueError(f"Python code block not properly closed in response {index}")

                return content[start + 9:end].strip()
    raise ValueError(f"Response index {index} not found")

def convert_config_for_metagpt(config_dict: Dict):
    """将配置字典转换为MetaGPT的LLMConfig"""
    from metagpt.configs.llm_config import LLMConfig, LLMType

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

# ========================================
#           流式输出支持
# ========================================

def get_streaming_wrapper(enable_stream=False):
    """返回流式输出包装代码（如果启用）"""
    if not enable_stream:
        return ""

    return '''
# 简单的流式输出提示
import sys

original_llm_aask = None

def wrap_streaming(llm):
    """为LLM添加流式输出提示"""
    global original_llm_aask
    if original_llm_aask is None:
        original_llm_aask = llm.aask

        async def streaming_aask(prompt, **kwargs):
            print("\\n" + "="*60)
            print("🤖 LLM正在生成响应...")
            print("="*60)
            response = await original_llm_aask(prompt, **kwargs)
            print("\\n" + "="*60 + "\\n")
            return response

        llm.aask = streaming_aask
    return llm
'''

# ========================================
#           主执行函数
# ========================================

async def test_workflow(args):
    """主测试函数，执行workflow"""

    print("=" * 60)
    print("IMO Workflow 测试工具")
    print("=" * 60)
    print(f"📋 Workflow索引: {args.index}")
    print(f"📋 问题索引: {args.problem_index}")
    print(f"📄 响应文件: {os.path.basename(args.imo_response)}")
    print(f"📄 问题文件: {os.path.basename(args.imo_problem)}")
    print(f"⏱️  超时设置: {args.timeout}秒")
    print(f"🔧 LLM模型: {args.llm_model}")
    print(f"🌐 API URL: {args.base_url}")
    print("-" * 60)

    try:
        # 1. 加载问题文本
        print("📖 加载问题文本...")
        problem_text = load_problem(args.imo_problem, args.problem_index)
        print("\n🔍 问题内容:")
        print("-" * 40)
        print(problem_text)
        print("-" * 40)

        # 2. 加载workflow代码
        print("\n🔧 加载Workflow代码...")
        workflow_code = load_workflow_code(args.imo_response, args.index)
        print(f"代码长度: {len(workflow_code)} 字符")

        # 3. 准备LLM配置
        print("\n⚙️  准备执行环境...")
        from metagpt.provider.llm_provider_registry import create_llm_instance

        llm_config = {
            "provider": args.provider,
            "model": args.llm_model,
            "api_key": args.api_key,
            "base_url": args.base_url
        }
        metagpt_config = convert_config_for_metagpt(llm_config)

        # 4. 导入必要的模块
        operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")

        # 5. 准备全局命名空间
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

        # 6. 构建完整的执行脚本
        print("\n🏗️  构建执行脚本...")

        # Python开始部分（导入和辅助函数）
        python_start = '''import asyncio
import re
import json
import math
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

''' + get_streaming_wrapper(args.stream)

        # Python结束部分（执行调用）
        python_end = f'''

    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {args.timeout}

        try:
            # Wrap LLM for streaming if enabled
            if 'wrap_streaming' in globals():
                self.llm = wrap_streaming(self.llm)

            # Execute the LLM-generated workflow to get the raw result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)

            # Return the raw result directly - answer extraction is now handled in handler
            return raw_result

        except asyncio.TimeoutError:
            # Handle workflow execution timeout gracefully.
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            # Handle other potential errors during workflow execution.
            import traceback
            # 错误详情在这里被定义和使用，不暴露给外部.format()
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{escaped_error_details}}"
'''

        # 组合完整脚本
        full_script = python_start + "\n" + workflow_code + "\n" + python_end

        # 7. 执行workflow
        print("\n🚀 执行Workflow...")
        print("=" * 60)

        start_time = time.time()

        # 执行脚本创建Workflow类
        execution_namespace = {
            'config': metagpt_config,
            'problem_text': problem_text
        }
        exec(full_script, exec_globals, execution_namespace)

        # 获取Workflow类
        WorkflowClass = execution_namespace.get('Workflow')
        if not WorkflowClass:
            raise ValueError("未找到Workflow类")

        # 创建workflow实例
        workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)

        # 执行workflow（调用__call__方法）
        result = await asyncio.wait_for(
            workflow_instance(),
            timeout=args.timeout + 10
        )

        execution_time = time.time() - start_time

        print("=" * 60)
        print(f"\n✅ 执行成功！耗时: {execution_time:.2f}秒")

        # 8. 显示结果
        print("\n📝 Workflow输出:")
        print("-" * 40)
        print(result)
        print("-" * 40)

    except asyncio.TimeoutError:
        print(f"\n⏱️ 执行超时（超过{args.timeout}秒）")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

# ========================================
#           主入口
# ========================================

async def main():
    """主入口"""
    args = parse_arguments()

    try:
        await test_workflow(args)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())