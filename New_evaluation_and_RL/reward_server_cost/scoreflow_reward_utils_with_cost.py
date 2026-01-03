"""
ScoreFlow Reward Function for VERL
适配ScoreFlow系统的reward计算器
"""
import os
import sys
import re
import json
import asyncio
import logging
from loguru import logger as loguru_logger
import importlib
import random
import string
import yaml
import csv
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import time

print("-"*60)
# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除代理环境变量，确保本地服务通信正常
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]
        print(f"✓ 已清除环境变量: {proxy_var}")

print(f"✓ 已设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}'")
print("  ScoreFlow的localhost请求将绕过所有代理")

# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
# 同时加载cost配置文件
COST_CONFIG_FILE = CURRENT_DIR / "config_cost.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        # 获取project_root，用于构建默认路径
        project_root = config.get('project_root', '/Users/luogan/Code/workflow_generation/Flow_RL')
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    project_root = '/Users/luogan/Code/workflow_generation/Flow_RL'

# 转换为Path对象
project_root_path = Path(project_root)

# 从config.yaml获取路径（相对路径），然后基于project_root构建完整路径
# scoreflow_handlers - 如果是"."则使用project_root本身
scoreflow_handlers = paths_config.get('scoreflow_handlers', '.')
if scoreflow_handlers == '.':
    SCOREFLOW_HANDLERS_PATH = project_root_path
else:
    SCOREFLOW_HANDLERS_PATH = project_root_path / scoreflow_handlers
# benchmark_mapping - 相对路径拼接
benchmark_mapping = paths_config.get('benchmark_mapping', 'ScoreFlow/benchmark_mapping.jsonl')
BENCHMARK_MAPPING_PATH = project_root_path / benchmark_mapping

# processed_dataset - 相对路径拼接
processed_dataset = paths_config.get('processed_dataset', 'Processed_dataset')
PROCESSED_DATASET_PATH = project_root_path / processed_dataset

# metagpt_config - 相对路径拼接
metagpt_config = paths_config.get('metagpt_config', 'metagpt_root/config/config2.yaml')
METAGPT_CONFIG_PATH = project_root_path / metagpt_config

# 添加必要路径
# 重要：添加ScoreFlow的根目录，使得ScoreFlow可以被正确导入
sys.path.insert(0, str(SCOREFLOW_HANDLERS_PATH))  # Add Flow_RL to path for ScoreFlow import
# 使用基于project_root的共享metagpt_root路径（所有程序共用）
SHARED_METAGPT_ROOT = project_root_path / "metagpt_root"
sys.path.append(str(SHARED_METAGPT_ROOT))

# 设置METAGPT_PROJECT_ROOT环境变量（强制使用共享目录）
os.environ["METAGPT_PROJECT_ROOT"] = str(SHARED_METAGPT_ROOT)
METAGPT_PROJECT_ROOT = SHARED_METAGPT_ROOT
# 添加MetaGPT本地路径（从config.yaml中配置的路径推导）
# METAGPT_CONFIG_PATH 指向 Test_FILE/config2.yaml，所以 MetaGPT 本地路径在同级目录
if METAGPT_CONFIG_PATH.exists():
    METAGPT_LOCAL = METAGPT_CONFIG_PATH.parent / "metagpt_local" / "metagpt_local"
    if METAGPT_LOCAL.exists():
        sys.path.insert(0, str(METAGPT_LOCAL))

# 设置MetaGPT的工作目录和日志目录
os.environ["METAGPT_WORKSPACE"] = str(METAGPT_PROJECT_ROOT / "workspace")
os.environ["METAGPT_LOG_DIR"] = str(METAGPT_PROJECT_ROOT / "logs")
os.environ["METAGPT_DATA_PATH"] = str(METAGPT_PROJECT_ROOT / "data")

# 创建必要目录
(METAGPT_PROJECT_ROOT / "workspace").mkdir(parents=True, exist_ok=True)
(METAGPT_PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)
(METAGPT_PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)

import asyncio as aio
from typing import List as ListType
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.context import Context
from metagpt.utils.cost_manager import CostManager, Costs

# 导入token追踪和费用计算模块
sys.path.insert(0, str(CURRENT_DIR))
from token_tracker import MetaGPTTokenTracker, get_global_tracker
from cost_calculator import CostCalculator

# SILENT模式控制 - 从config.yaml读取
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        _config_for_silent = yaml.safe_load(f)
        # 从scoreflow_reward服务配置中读取silent设置
        scoreflow_config = _config_for_silent.get('services', {}).get('scoreflow_reward', {})
        SILENT = scoreflow_config.get('silent', False)
        print(f"🔇 静默模式: {'开启' if SILENT else '关闭'} (从config.yaml读取)")
        
        # 设置环境变量，让operator模块知道SILENT模式状态
        if SILENT:
            os.environ['SCOREFLOW_SILENT'] = 'true'
        else:
            os.environ['SCOREFLOW_SILENT'] = 'false'
else:
    SILENT = False  # 默认关闭静默模式
    print(f"🔇 静默模式: 关闭 (默认值)")

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 禁用特定库的日志
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)  # httpx 的底层库
logging.getLogger("openai").setLevel(logging.ERROR)     # OpenAI SDK 的 HTTP 日志
logging.getLogger("metagpt").setLevel(logging.ERROR)    # MetaGPT 的日志
logging.getLogger("werkzeug").setLevel(logging.ERROR)  # 禁用 Flask 访问日志
# 禁用 loguru 的 metagpt 日志
loguru_logger.disable("metagpt")

# 初始化全局token追踪器和费用计算器
if COST_CONFIG_FILE.exists():
    with open(COST_CONFIG_FILE, 'r', encoding='utf-8') as f:
        cost_config = yaml.safe_load(f)
        token_tracking_config = cost_config.get('token_tracking', {})
else:
    token_tracking_config = {}

# 创建全局实例
GLOBAL_TOKEN_TRACKER = get_global_tracker(token_tracking_config)
GLOBAL_COST_CALCULATOR = CostCalculator(COST_CONFIG_FILE)

class WorkflowExecutionManager:
    """管理单个workflow的执行和日志记录 - 并行执行+安全汇总模式"""
    
    def __init__(self, workspace_path: Path, data_source: str, test_cases: List[int]):
        """初始化执行管理器"""
        # 创建workflow专属目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.workflow_id = f"workflow_{timestamp}_{random_id}"
        
        # 创建目录结构
        self.workflow_dir = workspace_path / data_source / self.workflow_id
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # 基本信息
        self.test_cases = test_cases
        self.data_source = data_source
        
        # 并行执行+安全汇总：线程安全的结果收集器
        self.results_collector = []
        self.results_lock = asyncio.Lock()

    def __enter__(self):
        """简化的上下文管理器入口 - 不再需要全局日志重定向"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """简化的上下文管理器出口 - 主要用于清理和汇总"""
        if exc_type:
            logger.info(f"⚠️ 执行过程中发生异常: {exc_type.__name__}: {exc_val}")

    def save_workflow_code(self, workflow_code: str):
        """保存workflow代码"""
        code_file = self.workflow_dir / "workflow.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(workflow_code)
    
    def save_metadata(self, extra_info: Dict):
        """保存元数据"""
        metadata = {
            "workflow_id": self.workflow_id,
            "data_source": self.data_source,
            "test_cases": self.test_cases,
            "timestamp": datetime.now().isoformat(),
            "extra_info": extra_info
        }
        meta_file = self.workflow_dir / "metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def save_raw_output(self, solution_str: str):
        """
        保存LLM的原始输出（solution_str），提供可读性好的格式
        学习自llama_factory_qwen3_thinking_lora的处理逻辑
        """
        raw_file = self.workflow_dir / "raw_output.py"
        
        try:
            # 生成格式化的内容
            formatted_content = self._format_raw_output_content(solution_str)
            
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
        except Exception as e:
            logger.info(f"❌ 保存原始输出失败: {e}")

    def _format_raw_output_content(self, solution_str: str) -> str:
        """
        格式化原始输出内容，基于llama_factory_qwen3_thinking_lora的处理逻辑
        
        Args:
            solution_str: LLM的原始输出文本
            
        Returns:
            格式化后的Python文件内容
        """
        # 文件头部注释
        header = f'''#!/usr/bin/env python
"""
Raw LLM Output for Workflow Generation
Workflow ID: {self.workflow_id}
Data Source: {self.data_source}
Test Cases: {self.test_cases}
Timestamp: {datetime.now().isoformat()}
Generated by ScoreFlow Reward System
"""

'''
        
        # 提取<think></think>部分（如果存在）
        think_content = self._extract_think_section(solution_str)
        
        # 提取代码块（如果存在）
        code_content = self._extract_code_blocks(solution_str)
        
        # 构建思考部分
        if think_content:
            processed_think = self._process_escape_chars(think_content)
            thinking_section = f'''"""
THINKING PROCESS (extracted from <think></think>):
{processed_think}
"""

'''
        else:
            thinking_section = '''"""
THINKING PROCESS: Not found in this output
"""

'''
        
        # 构建代码部分
        if code_content:
            processed_code = self._process_escape_chars(code_content)
            code_section = f'''"""
EXTRACTED CODE BLOCKS:
"""

{processed_code}

'''
        else:
            code_section = '''"""
EXTRACTED CODE BLOCKS: Not found in this output
"""

'''
        
        # 构建代码块后的其他文本部分
        remaining_text = self._extract_text_after_code_blocks(solution_str)
        if remaining_text:
            processed_remaining = self._process_escape_chars(remaining_text)
            remaining_section = f'''"""
TEXT AFTER CODE BLOCKS:
"""

{processed_remaining}

'''
        else:
            remaining_section = '''"""
TEXT AFTER CODE BLOCKS: Not found in this output
"""

'''

        return header + thinking_section + code_section + remaining_section
    
    def _extract_think_section(self, text: str) -> str:
        """提取<think></think>部分"""
        import re
        think_pattern = r'<think>(.*?)</think>'
        think_match = re.search(think_pattern, text, re.DOTALL)
        return think_match.group(1).strip() if think_match else ""
    
    def _extract_code_blocks(self, text: str) -> str:
        """提取```python或```代码块"""
        import re
        # 先尝试```python
        code_pattern = r'```python\n(.*?)```'
        code_match = re.search(code_pattern, text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # 然后尝试普通```代码块
        code_pattern = r'```\n(.*?)```'
        code_match = re.search(code_pattern, text, re.DOTALL)
        return code_match.group(1).strip() if code_match else ""
    
    def _extract_text_after_code_blocks(self, text: str) -> str:
        """提取```python```代码块之后的文本内容"""
        import re
        
        # 找到最后一个代码块的结束位置
        code_patterns = [r'```python\n(.*?)```', r'```\n(.*?)```']
        
        last_end_pos = -1
        for pattern in code_patterns:
            matches = list(re.finditer(pattern, text, re.DOTALL))
            if matches:
                last_end_pos = max(last_end_pos, matches[-1].end())
        
        # 如果找到了代码块，提取后面的内容
        if last_end_pos > -1:
            remaining = text[last_end_pos:].strip()
            # 过滤掉空的或只有换行的内容
            if remaining and len(remaining) > 10:  # 至少要有一些实际内容
                return remaining
        
        return ""
    
    def _process_escape_chars(self, text: str) -> str:
        """处理转义字符，类似参考文件的逻辑"""
        if not text:
            return ""
        # 处理常见的转义字符
        return text.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
    
    def _sanitize_error(self, error_msg: str) -> str:
        """清理错误信息，使其适合CSV存储"""
        # 移除换行符和特殊字符
        cleaned = error_msg.replace('\n', ' | ')
        cleaned = cleaned.replace('\r', '')
        cleaned = cleaned.replace('"', "'")
        cleaned = cleaned.replace(',', ';')  # 替换逗号避免CSV问题
        # 限制长度
        if len(cleaned) > 500:
            cleaned = cleaned[:497] + "..."
        return cleaned
    
    async def execute_all_test_cases_parallel_safe(self, calculator, workflow_code: str, dataset_path: str) -> float:
        """
        并行执行+安全汇总模式：并行执行所有test cases，安全汇总结果
        
        Args:
            calculator: ScoreFlowRewardCalculator实例
            workflow_code: 要执行的workflow代码
            dataset_path: 数据集路径
            
        Returns:
            平均分数 (0.0-1.0)
        """
        total_start_time = time.time()
        
        # 1. 并行执行所有test cases，每个使用独立日志文件
        tasks = []
        for test_case_index in self.test_cases:
            task = self._execute_without_logging(
                calculator, workflow_code, test_case_index, dataset_path
            )
            tasks.append(task)
        
        # 并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 2. 安全收集所有结果到内存
        all_scores = []
        valid_results = []
        
        async with self.results_lock:
            for i, result in enumerate(results):
                test_case_index = self.test_cases[i]
                
                if isinstance(result, Exception):
                    # 处理异常情况
                    logger.info(f"❌ Test Case {test_case_index} 执行异常: {result}")
                    error_result = {
                        "test_case": test_case_index,
                        "success": False,
                        "score": 0.0,
                        "duration": 0.0,
                        "error": self._sanitize_error(str(result)),
                        "timestamp": datetime.now().isoformat()
                    }
                    valid_results.append(error_result)
                    all_scores.append(0.0)
                elif isinstance(result, dict):
                    # 处理正常结果
                    valid_results.append(result)
                    all_scores.append(result.get('score', 0.0))
                else:
                    # 处理未知格式
                    logger.info(f"⚠️ Test Case {test_case_index} 返回未知格式: {type(result)}")
                    unknown_result = {
                        "test_case": test_case_index,
                        "success": False,
                        "score": 0.0,
                        "duration": 0.0,
                        "error": f"Unknown result type: {type(result)}",
                        "timestamp": datetime.now().isoformat()
                    }
                    valid_results.append(unknown_result)
                    all_scores.append(0.0)
            
            # 将所有结果添加到collector
            self.results_collector.extend(valid_results)
        
        # 3. All-Reduce: 统一计算最终分数并写入汇总文件
        total_duration = time.time() - total_start_time

        # 4. 串行写入汇总文件（避免I/O冲突）
        final_score = self._finalize_and_save_summary(total_duration)
        
        return final_score
    
    async def _execute_without_logging(self, calculator, workflow_code: str, 
                                     test_case_index: int, dataset_path: str) -> dict:
        """无日志执行 - 使用上下文局部重定向"""
        start_time = time.time()
        
        try:
            calculator._current_workflow_dir = self.workflow_dir
            
            # 临时禁用MetaGPT的流式日志输出
            import metagpt.logs as metagpt_logs
            original_llm_stream_log = metagpt_logs._llm_stream_log
            metagpt_logs._llm_stream_log = lambda msg: None  # 静音LLM流式输出
            
            try:
                score = await calculator.compute_score_for_testcase(
                    workflow_code, self.data_source, test_case_index, dataset_path
                )
                success = True
                error_msg = ""
            finally:
                # 恢复MetaGPT的日志函数
                metagpt_logs._llm_stream_log = original_llm_stream_log
            
            if hasattr(calculator, '_current_workflow_dir'):
                delattr(calculator, '_current_workflow_dir')
                
        except Exception as e:
            success = False
            error_msg = self._sanitize_error(str(e))
            score = 0.0
        
        duration = time.time() - start_time
        
        result_record = {
            "test_case": test_case_index,
            "success": success,
            "score": score,
            "duration": duration,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        
        return result_record
        
    def _finalize_and_save_summary(self, total_duration: float) -> float:
        """
        All-Reduce汇总阶段：处理所有收集的结果，串行写入汇总文件
        
        Args:
            total_duration: 总执行时间
            
        Returns:
            最终平均分数
        """
        
        if not self.results_collector:
            logger.info("⚠️ 没有收集到任何结果")
            return 0.0
        
        # 1. 统计汇总信息
        all_scores = [r.get('score', 0.0) for r in self.results_collector]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        successful_count = sum(1 for r in self.results_collector if r.get('success', False))
        total_test_cases = len(self.results_collector)
        success_rate = successful_count / total_test_cases if total_test_cases > 0 else 0.0
        
        # 2. 串行写入results.csv（避免I/O冲突）
        self._save_results_csv_safe()
        
        # 3. 串行写入summary.json（避免I/O冲突）
        self._save_summary_json_safe(avg_score, successful_count, total_test_cases, 
                                   success_rate, total_duration)
        
        # 4. 写入全局执行日志汇总
        self._save_global_execution_log_safe(avg_score, total_duration)

        return avg_score
    
    def _save_results_csv_safe(self):
        """串行安全地保存results.csv, 避免并发I/O冲突"""
        csv_file = self.workflow_dir / "results.csv"
        
        # 准备CSV表头
        headers = ["test_case", "success", "score", "duration", "error", "timestamp"]
        
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                # 按test_case索引排序，保证顺序一致
                sorted_results = sorted(self.results_collector, 
                                      key=lambda x: x.get('test_case', 0))
                
                for result in sorted_results:
                    # 确保所有字段都存在
                    csv_row = {
                        'test_case': result.get('test_case', ''),
                        'success': result.get('success', False),
                        'score': result.get('score', 0.0),
                        'duration': result.get('duration', 0.0),
                        'error': self._sanitize_error(result.get('error', '')),
                        'timestamp': result.get('timestamp', '')
                    }
                    writer.writerow(csv_row)
            
        except Exception as e:
            logger.info(f"❌ 保存CSV文件失败: {e}")

    def _save_summary_json_safe(self, avg_score: float, successful_count: int,
                               total_test_cases: int, success_rate: float, 
                               total_duration: float):
        """串行安全地保存summary.json, 避免并发I/O冲突"""
        summary_file = self.workflow_dir / "summary.json"
        
        # 计算更多统计信息
        all_scores = [r.get('score', 0.0) for r in self.results_collector]
        all_durations = [r.get('duration', 0.0) for r in self.results_collector]
        
        summary_data = {
            "workflow_id": self.workflow_id,
            "data_source": self.data_source,
            "execution_summary": {
                "total_test_cases": total_test_cases,
                "successful_cases": successful_count,
                "failed_cases": total_test_cases - successful_count,
                "success_rate": success_rate,
                "average_score": avg_score,
                "total_duration_seconds": total_duration,
                "average_duration_per_case": sum(all_durations) / len(all_durations) if all_durations else 0.0
            },
            "score_statistics": {
                "min_score": min(all_scores) if all_scores else 0.0,
                "max_score": max(all_scores) if all_scores else 0.0,
                "scores_distribution": all_scores
            },
            "execution_mode": "parallel_safe",
            "timestamp": datetime.now().isoformat(),
            "test_cases_executed": self.test_cases
        }
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.info(f"❌ 保存JSON汇总文件失败: {e}")

    def _save_global_execution_log_safe(self, avg_score: float, total_duration: float):
        """串行安全地写入全局执行日志汇总"""
        global_log_file = self.workflow_dir / "global_execution.log"
        
        try:
            with open(global_log_file, 'w', encoding='utf-8') as f:
                f.write(f"{'='*80}\n")
                f.write(f"Workflow执行汇总报告\n")
                f.write(f"{'='*80}\n")
                f.write(f"Workflow ID: {self.workflow_id}\n")
                f.write(f"数据源: {self.data_source}\n")
                f.write(f"执行模式: 并行安全模式 (parallel_safe)\n")
                f.write(f"执行时间: {datetime.now().isoformat()}\n")
                f.write(f"总耗时: {total_duration:.2f}秒\n")
                f.write(f"\n执行结果:\n")
                f.write(f"- 测试用例总数: {len(self.test_cases)}\n")
                f.write(f"- 执行的test cases: {self.test_cases}\n")
                f.write(f"- 最终平均分数: {avg_score:.3f}\n")
                f.write(f"- 成功案例数: {sum(1 for r in self.results_collector if r.get('success', False))}\n")
                f.write(f"- 失败案例数: {sum(1 for r in self.results_collector if not r.get('success', False))}\n")
                f.write(f"\n详细结果:\n")
                
                # 按test case顺序输出详细结果
                sorted_results = sorted(self.results_collector, 
                                      key=lambda x: x.get('test_case', 0))
                for result in sorted_results:
                    success = "✅" if result.get('success', False) else "❌"
                    f.write(f"  Test Case {result.get('test_case', 'N/A')}: {success} "
                           f"分数={result.get('score', 0.0):.3f} "
                           f"耗时={result.get('duration', 0.0):.2f}s\n")
                    if result.get('error'):
                        f.write(f"    错误: {result.get('error', '')}\n")
                
                f.write(f"\n{'='*80}\n")
                f.write(f"执行完成\n")
                f.write(f"{'='*80}\n")

        except Exception as e:
            logger.info(f"❌ 保存全局执行日志失败: {e}")

class ScoreFlowRewardCalculator:
    """
    ScoreFlow任务的reward计算器
    复用现有的BenchmarkHandler体系
    """
    def __init__(self, config_path: str = None):
        """初始化reward计算器"""
        if CONFIG_FILE.exists():
            # 使用metagpt_api_proxy配置
            proxy_port = config.get('services', {}).get('metagpt_api_proxy', {}).get('port', 5009)
            temperature = config.get('api_metagpt', {}).get('temperature', 0.1)
            self.llm_config = {
                'provider': 'openai',
                'model': 'qwen-turbo',
                'api_key': 'sk-placeholder-will-be-replaced-by-proxy',
                'base_url': f'http://localhost:{proxy_port}',
                'temperature': temperature
            }
            
            # 从scoreflow_reward服务配置获取超时等参数
            scoreflow_config = config.get('services', {}).get('scoreflow_reward', {})
            self.reward_config = {
                'timeout': scoreflow_config.get('timeout', 300),
                'client_http_timeout': scoreflow_config.get('client_http_timeout', 600),  # 新增：HTTP客户端超时
                'test_cases_per_task': 3,
                'max_concurrent': 5
            }
            
            # 读取workspace配置
            workspace_relative = scoreflow_config.get('workspace', 'workspace')
            # 将相对路径与project_root_path拼接成绝对路径
            if workspace_relative:
                self.workspace_path = project_root_path / workspace_relative
            else:
                # 如果没有配置，使用默认路径
                self.workspace_path = project_root_path / "workspace"
        else:
            # 默认配置
            logger.info("\n ⚠️ Config file not found, using defaults")
            self.llm_config = {
                'provider': 'openai',
                'model': 'qwen-turbo',
                'api_key': 'sk-placeholder',
                'base_url': 'http://localhost:5009',
                'temperature': 0.3
            }
            self.reward_config = {
                'timeout': 300,
                'client_http_timeout': 600,  # 默认HTTP客户端超时
                'test_cases_per_task': 3,
                'max_concurrent': 5
            }
            self.workspace_path = PROJECT_ROOT / "workspace"
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 300)
        self.client_http_timeout = self.reward_config.get('client_http_timeout', 600)  # HTTP客户端超时
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # 初始化token追踪器和费用计算器
        self.token_tracker = GLOBAL_TOKEN_TRACKER
        self.cost_calculator = GLOBAL_COST_CALCULATOR
        
        # handler缓存
        self._handler_cache = {}
        # 加载benchmark mapping
        self.benchmark_mapping = self._load_benchmark_mapping()        
    
    def _load_benchmark_mapping(self) -> Dict[str, Dict]:
        """Load benchmark mapping from jsonl file"""
        mapping_file = BENCHMARK_MAPPING_PATH
        if not mapping_file.exists():
            logger.warning(f"Benchmark mapping file not found: {mapping_file}, using default mapping")
            return {}
        
        mapping = {}
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    benchmark = data['benchmark']
                    mapping[benchmark] = data
        
        return mapping
    
    def extract_workflow_from_response(self, response: str) -> Optional[str]:
        """
        从LLM response中提取workflow代码
        查找<code>标签内的内容或class Workflow定义
        """
        
        if not response:
            logger.info("Empty response, cannot extract workflow")
            return None
        
        code_pattern = re.compile(r'```python\s*\n(.*?)\n```', re.DOTALL)
        matches_python = code_pattern.findall(response)
        matches = matches_python
        
        if matches:
            workflow_code = matches[0].strip()
            return workflow_code
        
        logger.info("没有找到```python ```包裹的部分")
        class_pattern = r'(class\s+Workflow.*?)(?=class\s+\w+|$)'
        matches = re.findall(class_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            return workflow_code
        
        logger.info("No workflow code found in response")
        return None
    
    def _load_benchmark_handler(self, benchmark_name: str, dataset_path: str):
        """动态加载对应的benchmark handler"""
        cache_key = f"{benchmark_name}_{dataset_path}"
        if cache_key in self._handler_cache:
            return self._handler_cache[cache_key]
        
        try:
            provider = self.llm_config.get('provider', 'openai')
            api_type_map = {
                'openai': 'OPENAI', 'azure': 'AZURE', 'gemini': 'GEMINI',
                'claude': 'CLAUDE', 'moonshot': 'MOONSHOT',
                'zhipuai': 'ZHIPUAI', 'qianfan': 'QIANFAN',
            }
            
            # 转换为MetaGPT的LLMConfig
            from metagpt.provider.llm_provider_registry import LLMType
            
            # 获取LLMType枚举
            llm_type_str = api_type_map.get(provider.lower(), 'OPENAI')
            llm_type = getattr(LLMType, llm_type_str)
            
            metagpt_config = LLMConfig(
                api_type=llm_type,
                model=self.llm_config.get('model'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url')
            )
            
            # 查找benchmark映射信息
            benchmark_info = self.benchmark_mapping.get(benchmark_name)
            
            # 如果精确匹配失败，尝试去掉后缀（如_limr）再匹配
            if not benchmark_info and '_' in benchmark_name:
                # 尝试去掉最后一个下划线后的部分
                base_name = '_'.join(benchmark_name.split('_')[:-1])
                benchmark_info = self.benchmark_mapping.get(base_name)
                if benchmark_info:
                    logger.info(f"Using base benchmark '{base_name}' mapping for '{benchmark_name}'")

            if benchmark_info:
                # 使用mapping中的handler class名称和路径
                handler_class_name = benchmark_info['handler_class']
                handler_dir = benchmark_info['handler_dir']
                
                # 转换handler_dir到Python模块路径（与generate_verl_training_data.py相同的逻辑）
                scoreflow_root = str(SCOREFLOW_HANDLERS_PATH)
                
                # 提取相对路径从handler_dir
                if handler_dir.startswith(scoreflow_root):
                    # 移除scoreflow_root前缀和前导斜杠
                    relative_path = handler_dir[len(scoreflow_root):].lstrip('/')
                    handler_module_path = relative_path.replace('/', '.') + '.handler'
                else:
                    # 回退：从绝对路径中提取ScoreFlow部分
                    if handler_dir.startswith('/'):
                        scoreflow_index = handler_dir.find('ScoreFlow')
                        if scoreflow_index != -1:
                            relative_path = handler_dir[scoreflow_index:]
                            handler_module_path = relative_path.replace('/', '.') + '.handler'
                        else:
                            raise ValueError(f"Cannot find ScoreFlow in handler_dir: {handler_dir}")
                    else:
                        handler_module_path = handler_dir.replace('/', '.') + '.handler'
            else:
                # 回退到默认命名规则
                if benchmark_name.startswith("high_level_math"):
                    handler_module_path = "ScoreFlow.scripts.high_level_math.handler"
                    # 修正类名为实际存在的类名
                    handler_class_name = "HighlevelmathHandler"
                else:
                    handler_module_path = f"ScoreFlow.scripts.{benchmark_name}.handler"
                    handler_class_name = f"{benchmark_name.capitalize()}Handler"
            
            # 导入handler模块
            handler_module = importlib.import_module(handler_module_path)
            
            # 获取handler类
            handler_class = getattr(handler_module, handler_class_name)
            
            # 实例化handler
            handler = handler_class(dataset_path=dataset_path, config=metagpt_config)
            
            self._handler_cache[cache_key] = handler
            return handler
            
        except Exception as e:
            logger.info(f"Failed to load handler for {benchmark_name}: {e}")
            return None
    
    async def execute_workflow_metagpt(self, workflow_code: str, benchmark_name: str, 
                                       test_case_index: int, dataset_path: str, 
                                       workflow_dir: Path = None) -> tuple:
        """
        使用MetaGPT框架执行工作流（带token追踪）
        完全复用workflow_executor.py的执行逻辑
        
        Args:
            workflow_code: workflow代码
            benchmark_name: benchmark名称
            test_case_index: 测试案例索引
            dataset_path: 数据集路径
            workflow_dir: 工作目录（如果提供，将在此目录保存调试文件）
            
        Returns:
            (execution_result, token_stats) 元组
        """
        exec_start = time.time()
        
        try:
            # 生成workflow标识
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            workflow_id = f"exec_{benchmark_name}_{test_case_index}_{timestamp}_{random_id}"
            
            # 创建workflow的独立Context和CostManager用于token追踪
            workflow_context = None
            if self.token_tracker and self.token_tracker.enabled:
                # 获取模型名称用于费用计算
                model_name = self.llm_config.get('model', 'unknown')
                workflow_context = self.token_tracker.create_workflow_context(workflow_id, model_name)
            
            # 获取Handler并构建脚本
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                raise ValueError(f"Failed to load handler for {benchmark_name}")
            
            # 使用handler构建可执行脚本
            script_parts = handler.build_executable_script(workflow_code, timeout=self.timeout)
            
            # 拼接完整脚本
            full_script_code = (
                script_parts["python_start"] + "\n" +
                script_parts["workflow_code"] + "\n" +
                script_parts["python_end"]
            )
            
            # 4. 准备执行环境
            execution_namespace = {}
            
            # 加载operator模块（使用common operators）
            operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
            # 准备全局命名空间
            exec_globals = {
                'asyncio': aio,
                'create': create_llm_instance,
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': ListType,
            }
            try:
                common_an_module = importlib.import_module("ScoreFlow.scripts.common.operator_an")
                for attr_name in dir(common_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(common_an_module, attr_name)
            except ModuleNotFoundError:
                logger.info("/n 🚀 未找到可选的 'operator_an.py' 模块，跳过注入。")

            # 5. 执行脚本获取Workflow类
            exec(full_script_code, exec_globals, execution_namespace)
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError(f"No 'Workflow' class found in the executed script for {workflow_id}")
            
            # 6. 准备LLM配置
            provider = self.llm_config.get('provider', 'openai')
            api_type_map = {
                'openai': LLMType.OPENAI, 'azure': LLMType.AZURE, 
                'gemini': LLMType.GEMINI, 'claude': LLMType.CLAUDE,
                'moonshot': LLMType.MOONSHOT, 'zhipuai': LLMType.ZHIPUAI,
                'qianfan': LLMType.QIANFAN,
            }
            api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
            
            metagpt_config = LLMConfig(
                api_type=api_type,
                model=self.llm_config.get('model'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url')
            )
            
            # 7. 格式化问题文本
            problem_text = handler.get_prompt_text([test_case_index])
            
            # 8. 实例化并执行工作流
            workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            # 关联cost_manager用于token追踪
            if workflow_context and hasattr(workflow_instance, 'llm') and workflow_instance.llm:
                workflow_instance.llm.cost_manager = workflow_context.cost_manager
            
            # 9. 根据call_signature执行（处理超时参数）
            # 在SILENT模式下禁用MetaGPT的流式输出
            if SILENT:
                import metagpt.logs as metagpt_logs
                original_llm_stream_log = metagpt_logs._llm_stream_log
                metagpt_logs._llm_stream_log = lambda msg: None  # 静音LLM流式输出
            
            try:
                if "timeout=" in script_parts["call_signature"]:
                    # 新版格式，传入timeout参数
                    timeout_match = re.search(r'timeout=(\d+)', script_parts["call_signature"])
                    if timeout_match:
                        timeout_value = int(timeout_match.group(1))
                        execution_result = await asyncio.wait_for(
                            workflow_instance(timeout=timeout_value),
                            timeout=timeout_value + 10  # 额外10秒缓冲
                        )
                    else:
                        execution_result = await asyncio.wait_for(
                            workflow_instance(timeout=self.timeout),
                            timeout=self.timeout + 10
                        )
                else:
                    # 旧版格式，不传timeout
                    # handler返回的call_signature是"await workflow_instance()"
                    execution_result = await asyncio.wait_for(
                        workflow_instance(),
                        timeout=self.timeout + 10
                    )
            finally:
                # 恢复MetaGPT的日志函数
                if SILENT:
                    metagpt_logs._llm_stream_log = original_llm_stream_log
            # 获取token统计
            token_stats = {}
            if self.token_tracker and self.token_tracker.enabled:
                token_stats = self.token_tracker.get_workflow_stats(workflow_id)
                self.token_tracker.print_workflow_stats(workflow_id)  # 打印统计
                self.token_tracker.update_total_stats(workflow_id)  # 更新总体统计
            
            # logger.info(f"MetaGPT workflow {workflow_id} executed successfully")
            return str(execution_result), token_stats
            
        except asyncio.TimeoutError:
            logger.info(f"MetaGPT workflow execution timed out for {benchmark_name}")
            # 即使超时也尝试获取token统计
            token_stats = {}
            if self.token_tracker and self.token_tracker.enabled and 'workflow_id' in locals():
                token_stats = self.token_tracker.get_workflow_stats(workflow_id)
            return "Error: Workflow execution timed out", token_stats

        except Exception as e:
            error_msg = f"MetaGPT workflow execution failed for {benchmark_name}: {e}"
            logger.info(error_msg)
            # 即使失败也尝试获取token统计
            token_stats = {}
            if self.token_tracker and self.token_tracker.enabled and 'workflow_id' in locals():
                token_stats = self.token_tracker.get_workflow_stats(workflow_id)
            return f"Error: {str(e)}", token_stats
    
    async def compute_score_for_testcase(self, workflow_code: str, benchmark_name: str, 
                                        test_case_index: int, dataset_path: str) -> float:
        """
        在单个test case上计算分数
        使用MetaGPT执行并使用handler的judge方法验证
        """
        try:
            # 加载handler
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                logger.info(f"Failed to load handler for {benchmark_name}")
                return 0.0
            
            # 获取验证数据
            verification_data = handler.get_verification_data(test_case_index)
            # 获取当前的workflow目录（如果在WorkflowExecutionManager上下文中）
            workflow_dir = getattr(self, '_current_workflow_dir', None)
            # 执行workflow并获取结果和token统计
            result_tuple = await self.execute_workflow_metagpt(
                workflow_code, benchmark_name, test_case_index, dataset_path, workflow_dir
            )
            
            # 解包结果和token统计
            if isinstance(result_tuple, tuple):
                result, token_stats = result_tuple
            else:
                # 兼容旧版本（如果没有token追踪）
                result = result_tuple
                token_stats = {}
            
            # 检查judge是否是协程函数
            import inspect
            if inspect.iscoroutinefunction(handler.judge):
                is_correct = await handler.judge(result, verification_data)
            else:
                is_correct = handler.judge(result, verification_data)
            
            # 输出判断结果
            if is_correct:
                pass
            else:
                logger.info(f"❌ 判断结果: INCORRECT")

            base_score = 1.0 if is_correct else 0.0
            
            # 应用费用惩罚（如果启用）
            final_score = base_score
            if self.cost_calculator and token_stats:
                final_score, penalty_details = self.cost_calculator.apply_cost_penalty(base_score, token_stats)
                if penalty_details.get('penalty_applied'):
                    logger.info(f"💰 费用惩罚已应用: {base_score:.3f} -> {final_score:.3f}")
            
            # logger.info(f"Benchmark {benchmark_name} test case {test_case_index} score: {final_score}")
            return final_score
            
        except Exception as e:
            logger.info(f"Error computing score for {benchmark_name} index {test_case_index}: {e}")            
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, benchmark_name: str, 
                                  test_cases: List[int], dataset_path: str) -> float:
        """
        异步计算workflow在所有test cases上的平均reward
        使用优化的并行处理策略
        """
        if not test_cases:
            return 0.0
        
        # 创建进度跟踪
        completed_count = 0
        total_count = len(test_cases)
        progress_lock = asyncio.Lock()
        
        async def update_progress():
            nonlocal completed_count
            async with progress_lock:
                completed_count += 1
                if completed_count % max(1, total_count // 10) == 0:  # 每10%报告一次进度
                    logger.info(f"Progress: {completed_count}/{total_count} test cases completed ({completed_count/total_count*100:.1f}%)")
        
        async def compute_single_testcase(test_case_index, index):
            # ✅ 直接执行，不使用本地信号量（并发控制由外层Flask装饰器负责）
            try:
                score = await self.compute_score_for_testcase(
                    workflow_code, benchmark_name, test_case_index, dataset_path
                )
                await update_progress()
                return (index, score, None)
            except Exception as e:
                logger.info(f"Test case {test_case_index} failed: {e}")
                await update_progress()
                return (index, 0.0, e)
        
        # 使用asyncio.create_task创建更高效的任务
        tasks = [
            asyncio.create_task(compute_single_testcase(test_case_index, i))
            for i, test_case_index in enumerate(test_cases)
        ]
        
        # 使用as_completed实现更灵活的结果处理
        results = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
        
        # 按原始顺序排序结果
        results.sort(key=lambda x: x[0])
        
        # 处理结果
        valid_scores = []
        failed_count = 0
        for index, score, error in results:
            if error is not None:
                logger.info(f"Task {index} failed with exception: {error}")
                valid_scores.append(0.0)
                failed_count += 1
            else:
                valid_scores.append(score)
        
        # 计算平均分
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        success_rate = (len(valid_scores) - failed_count) / len(valid_scores) if valid_scores else 0.0
        logger.info(f"Average score for {benchmark_name}: {avg_score:.3f} "
                   f"({len(valid_scores)} test cases, {success_rate*100:.1f}% success rate)")
        return avg_score

# 创建全局计算器实例
_global_calculator = None

def get_calculator():
    """获取全局计算器实例"""
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = ScoreFlowRewardCalculator()
    return _global_calculator

def compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    计算单个solution的reward分数(符合VERL接口规范)
    
    Args:
        data_source: benchmark名称, 如 'gsm8k', 'high_level_math_aime2024'
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息(通常是"default")
        extra_info: 包含test_cases, data_path等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    if data_source.startswith("workflow_"):
        data_source = data_source.replace("workflow_", "")
        # 为了兼容VERL 训练框架的命名约定
        # 在生成 VERL 训练数据时，会自动添加workflow_ 前缀来标识这是工作流生成任务。
    try:
        # 检查是否已有事件循环正在运行
        loop = asyncio.get_running_loop()
        
        # 如果已经在事件循环中，需要使用不同的策略
        import concurrent.futures
        
        # 在新线程中运行异步代码，避免嵌套事件循环
        def run_in_thread():
            # 在新线程中创建新的事件循环
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_compute_score_async(data_source, solution_str, ground_truth, extra_info))
            finally:
                new_loop.close()
                asyncio.set_event_loop(None)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            # 使用配置的client_http_timeout，默认600秒
            calculator = get_calculator()
            timeout_value = calculator.client_http_timeout if hasattr(calculator, 'client_http_timeout') else 600
            return future.result(timeout=timeout_value)
            
    except RuntimeError:
        # 如果不在事件循环中，直接使用 asyncio.run
        return asyncio.run(_compute_score_async(data_source, solution_str, ground_truth, extra_info))

async def _compute_score_async(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    异步计算单个solution的reward分数(内部实现)
    """
    
    try:
        # 获取计算器实例
        calculator = get_calculator()
        
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(solution_str)
        if not workflow_code:
            logger.info("No workflow code found in solution")
            return 0.0
        
        # 从extra_info提取必要信息
        test_cases = extra_info.get('test_cases', [])
        data_path = extra_info.get('data_path', '')
        
        # 处理numpy array的情况
        if hasattr(test_cases, 'tolist'):
            test_cases = test_cases.tolist()
        
        # 解析benchmark名称（处理类似 'high_level_math_aime2024' 的情况）
        # 直接使用data_source作为benchmark名称，因为benchmark_mapping中已有完整名称
        benchmark_name = data_source
        
        if not data_path:
            logger.info("No data_path found in extra_info")
            return 0.0
        
        # 构建完整的数据路径
        if not os.path.isabs(data_path):
            # 使用配置的 processed_dataset 路径作为基准
            # 如果 data_path 已经包含 "Processed_dataset"，需要去掉这部分
            if data_path.startswith("Processed_dataset/"):
                # 去掉 "Processed_dataset/" 前缀，直接拼接
                relative_path = data_path.replace("Processed_dataset/", "", 1)
                data_path = os.path.join(PROCESSED_DATASET_PATH, relative_path)
            else:
                # 直接拼接
                data_path = os.path.join(PROCESSED_DATASET_PATH, data_path)

        logger.info(f"Computing reward for benchmark: {benchmark_name} with {len(test_cases)} test cases")
        
        # 创建WorkflowExecutionManager并使用All-Reduce模式
        manager = WorkflowExecutionManager(
            calculator.workspace_path,
            data_source,
            test_cases
        )
        
        # 保存workflow代码、元数据和原始输出
        manager.save_workflow_code(workflow_code)
        manager.save_metadata(extra_info)
        manager.save_raw_output(solution_str)  # 保存LLM的原始输出
        
        # 使用上下文管理器确保文件生命周期正确，并执行All-Reduce模式
        with manager:  # 自动管理文件打开和关闭
            reward = await manager.execute_all_test_cases_parallel_safe(
                calculator, workflow_code, data_path
            )
        # 文件在此处自动安全关闭
        logger.info(f"AVG_Score:{reward:.3f}. [{benchmark_name}] with {len(test_cases)} test cases")
        return reward
        
    except Exception as e:
        logger.info(f"Error computing score: {e}")
        return 0.0

if __name__ == "__main__":
    # 简单测试
    test_solution = """
```python
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the math problem step by step.")
        return solution
```
"""
    
    test_extra_info = {
        'data_path': 'Processed_dataset/gsm8k/test.jsonl',
        'test_cases': [0, 1, 2],  # 使用前3个测试用例
        'raw_data': 0,
        'answer': 'test_answer'
    }
    
    # 使用异步方式运行测试
    async def test():
        score = await _compute_score_async('gsm8k', test_solution, "default", test_extra_info)
        print(f"Test score: {score}")
    
    asyncio.run(test())