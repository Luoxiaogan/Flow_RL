"""
InternBootcamp Reward Function for VERL V2
适配新的数据格式，将task信息从reward_model移到extra_info
"""
import os
import sys
import re
import json
import asyncio
import logging
import importlib
import traceback
import random
import string
import yaml
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import time
import aiohttp
import uuid
print("-"*60)

# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除代理环境变量，确保本地服务通信正常
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]
        print(f"✓ 已清除环境变量: {proxy_var}")

print(f"✓ 已设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}' (InternBootcamp)")
print("  InternBootcamp的localhost请求将绕过所有代理")
# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        service_config = config.get('services', {}).get('internbootcamp_reward', {})
        # 获取project_root，用于构建默认路径
        project_root = config.get('project_root', '/Users/luogan/Code/workflow_generation/Flow_RL')
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    service_config = {}
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

# processed_dataset - 相对路径拼接
processed_dataset = paths_config.get('processed_dataset', 'Processed_dataset')
PROCESSED_DATASET_PATH = project_root_path / processed_dataset

# metagpt_config - 相对路径拼接
metagpt_config = paths_config.get('metagpt_config', 'metagpt_root/config/config2.yaml')
print(metagpt_config)
METAGPT_CONFIG_PATH = project_root_path / metagpt_config

# 从服务配置获取workspace路径
workspace_path = service_config.get('workspace', 'New_evaluation_and_RL/workspace/internbootcamp')
WORKSPACE_PATH = project_root_path / workspace_path

# 添加必要路径
sys.path.insert(0, str(SCOREFLOW_HANDLERS_PATH))  # Add Flow_RL to path for ScoreFlow import
sys.path.append(str(project_root_path))

# 添加InternBootcamp路径（基于project_root）
INTERNBOOTCAMP_PATH = project_root_path / "InternBootcamp"
if INTERNBOOTCAMP_PATH.exists():
    sys.path.append(str(INTERNBOOTCAMP_PATH))
    print(f"✓ 已添加InternBootcamp路径: {INTERNBOOTCAMP_PATH}")
else:
    print(f"⚠ InternBootcamp路径不存在: {INTERNBOOTCAMP_PATH}")

# 使用基于project_root的共享metagpt_root路径（所有程序共用）
SHARED_METAGPT_ROOT = project_root_path / "metagpt_root"
sys.path.append(str(SHARED_METAGPT_ROOT))

# 设置METAGPT_PROJECT_ROOT环境变量（强制使用共享目录）
os.environ["METAGPT_PROJECT_ROOT"] = str(SHARED_METAGPT_ROOT)
METAGPT_PROJECT_ROOT = SHARED_METAGPT_ROOT
print("METAROOT:",METAGPT_PROJECT_ROOT)
# 添加MetaGPT本地路径（从config.yaml中配置的路径推导）
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

# DEBUG模式控制（从config获取）
DEBUG = 1 if service_config.get('debug', False) else 0
DEBUG_PATH = PROJECT_ROOT / "debug_logs"  # 存储在evaluation_workflow目录下

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Debug日志记录器
debug_data = {
    "start_time": None,
    "end_time": None,
    "total_duration": None,
    "total_tasks": [],
    "workflows": [],
    "llm_calls": [],
    "errors": []
}

# MetaGPT原生Token追踪实现
from metagpt.context import Context
from metagpt.utils.cost_manager import CostManager, Costs

class MetaGPTNativeTokenTracker:
    """使用MetaGPT原生功能的Token追踪器"""
    
    def __init__(self):
        self.workflow_contexts = {}  # workflow_id -> Context
        self.workflow_stats = {}     # workflow_id -> stats (for compatibility)
        self.total_stats = {
            'total_workflows': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_cost': 0.0,
            'workflows': []
        }
        print(f"✅ MetaGPT原生Token追踪器已初始化")
        print(f"📊 使用MetaGPT内置CostManager统计Token")
    
    def create_workflow_context(self, workflow_id: str) -> Context:
        """为workflow创建独立的Context和CostManager"""
        # 创建新的Context
        context = Context()
        
        # 创建独立的CostManager
        cost_manager = CostManager()
        cost_manager.max_budget = 100.0  # 设置预算上限
        
        # 关联到context
        context.cost_manager = cost_manager
        
        # 保存到字典
        self.workflow_contexts[workflow_id] = context
        
        print(f"✅ 创建Workflow {workflow_id} 的MetaGPT Context")
        return context
    
    def get_workflow_context(self, workflow_id: str) -> Optional[Context]:
        """获取workflow的context"""
        return self.workflow_contexts.get(workflow_id)
    
    def get_workflow_stats(self, workflow_id: str) -> dict:
        """获取workflow统计（从Context的CostManager获取）"""
        context = self.workflow_contexts.get(workflow_id)
        if not context:
            return {}
        
        # 获取costs信息
        costs = context.cost_manager.get_costs()
        
        return {
            'workflow_id': workflow_id,
            'prompt_tokens': costs.total_prompt_tokens,
            'completion_tokens': costs.total_completion_tokens,
            'total_tokens': costs.total_prompt_tokens + costs.total_completion_tokens,
            'total_cost': costs.total_cost,
            'api_calls': 1 if costs.total_prompt_tokens > 0 else 0  # 简化计数
        }
    
    def print_workflow_stats(self, workflow_id: str):
        """醒目打印workflow的token统计"""
        stats = self.get_workflow_stats(workflow_id)
        
        print(f"\n{'🔥'*30}")
        print(f"{'='*80}")
        if stats and stats.get('total_tokens', 0) > 0:
            print(f"🎯 ✅ TOKEN统计成功 - Workflow: {workflow_id}")
            print(f"{'='*80}")
            print(f"  📝 输入Token (Prompt):     {stats['prompt_tokens']:,}")
            print(f"  💬 输出Token (Completion): {stats['completion_tokens']:,}")
            print(f"  📊 总计Token:              {stats['total_tokens']:,}  ⭐️⭐️⭐️")
            print(f"  💰 估算成本:               ${stats['total_cost']:.6f}")
            print(f"{'='*80}")
            print(f"  ✨ 使用MetaGPT原生CostManager统计")
        else:
            print(f"❌ ⚠️ TOKEN统计失败 - 没有捕获到Token信息！")
            print(f"{'='*80}")
            print(f"  可能的原因:")
            print(f"  1. LLMConfig未设置calc_usage=True")
            print(f"  2. API响应中没有usage字段")
            print(f"  3. CostManager未正确关联")
        print(f"{'='*80}")
        print(f"{'🔥'*30}\n")
    
    def update_total_stats(self, workflow_id: str):
        """更新总体统计信息"""
        stats = self.get_workflow_stats(workflow_id)
        if stats and stats.get('total_tokens', 0) > 0:
            self.total_stats['total_workflows'] += 1
            self.total_stats['total_prompt_tokens'] += stats['prompt_tokens']
            self.total_stats['total_completion_tokens'] += stats['completion_tokens']
            self.total_stats['total_cost'] += stats['total_cost']
            self.total_stats['workflows'].append(stats)
    
    def print_total_stats(self):
        """打印总体统计"""
        print(f"\n{'⭐'*40}")
        print(f"{'='*100}")
        
        if self.total_stats['total_workflows'] > 0:
            print(f"🏆 ✅ 总体TOKEN统计汇总 (MetaGPT Native)")
            print(f"{'='*100}")
            print(f"  📊 处理的Workflows数:         {self.total_stats['total_workflows']}")
            print(f"  📝 总输入Token (Prompt):      {self.total_stats['total_prompt_tokens']:,}")
            print(f"  💬 总输出Token (Completion):  {self.total_stats['total_completion_tokens']:,}")
            print(f"  🎯 总计Token:                 {(self.total_stats['total_prompt_tokens'] + self.total_stats['total_completion_tokens']):,}  🔥🔥🔥")
            print(f"  💰 总估算成本:                ${self.total_stats['total_cost']:.6f}")
            
            # 计算平均值
            avg_tokens = (self.total_stats['total_prompt_tokens'] + 
                         self.total_stats['total_completion_tokens']) / self.total_stats['total_workflows']
            print(f"  📈 平均每个Workflow:          {avg_tokens:.0f} tokens")
        else:
            print(f"❌ ⚠️ 总体TOKEN统计失败 - 没有任何Token数据！")
            print(f"{'='*100}")
            print(f"  🚨 请检查MetaGPT配置")
        print(f"{'='*100}")
        print(f"  ✨ Powered by MetaGPT CostManager")
        print(f"{'='*100}")
        print(f"{'⭐'*40}\n")
    
    # 兼容旧接口
    def init_workflow(self, workflow_id: str):
        """兼容旧接口 - 创建workflow context"""
        return self.create_workflow_context(workflow_id)
    
    def set_workflow_id(self, workflow_id: str):
        """兼容旧接口 - 设置当前workflow ID"""
        self.create_workflow_context(workflow_id)
        self.current_workflow_id = workflow_id
    
    def get_summary(self) -> dict:
        """获取统计摘要（兼容旧接口）"""
        return {
            'total_prompt_tokens': self.total_stats['total_prompt_tokens'],
            'total_completion_tokens': self.total_stats['total_completion_tokens'],
            'total_tokens': self.total_stats['total_prompt_tokens'] + self.total_stats['total_completion_tokens'],
            'total_api_calls': self.total_stats['total_workflows'],
            'workflows_processed': self.total_stats['total_workflows']
        }

# 创建全局Token追踪器（使用MetaGPT原生方法）
GLOBAL_TOKEN_TRACKER = MetaGPTNativeTokenTracker()

print(f"\n{'🚀'*20}")
print(f"✅ MetaGPT原生Token追踪功能已启用")
print(f"   - 使用Context和CostManager进行统计")
print(f"   - 每个workflow独立追踪")
print(f"   - 自动计算成本")
print(f"{'🚀'*20}\n")

def save_debug_data():
    """保存debug数据到文件"""
    if DEBUG == 1:
        DEBUG_PATH.mkdir(exist_ok=True)
        debug_data["end_time"] = datetime.now().isoformat()
        if debug_data["start_time"]:
            start = datetime.fromisoformat(debug_data["start_time"])
            end = datetime.fromisoformat(debug_data["end_time"])
            debug_data["total_duration"] = (end - start).total_seconds()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = DEBUG_PATH / f"debug_{timestamp}.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Debug data saved to {debug_file}")

def debug_log(category: str, data: Any, start_time: float = None):
    """记录debug信息，包含时间戳和耗时"""
    if DEBUG == 1:
        # 添加时间戳
        data["timestamp"] = datetime.now().isoformat()
        
        # 计算耗时
        if start_time is not None:
            data["duration"] = time.time() - start_time
        
        # 记录到对应类别
        if category == "task":
            debug_data["total_tasks"].append(data)
        elif category == "workflow":
            debug_data["workflows"].append(data)
        elif category == "llm_call":
            debug_data["llm_calls"].append(data)
        elif category == "error":
            debug_data["errors"].append(data)
        elif category == "init":
            debug_data["start_time"] = data["timestamp"]


class TeeOutput:
    """同时输出到终端和文件的辅助类"""
    def __init__(self, terminal, file):
        self.terminal = terminal
        self.file = file
    
    def write(self, message):
        """写入到终端和文件"""
        self.terminal.write(message)
        self.terminal.flush()  # 立即刷新终端
        self.file.write(message)
        self.file.flush()  # 立即刷新文件
        return len(message)
    
    def flush(self):
        """刷新缓冲区"""
        self.terminal.flush()
        self.file.flush()
    
    def isatty(self):
        """检查是否是终端"""
        return self.terminal.isatty()
    
    def fileno(self):
        """返回文件描述符"""
        return self.terminal.fileno()


class SafeTeeOutput:
    """安全的双向输出类 - 防止向已关闭文件写入"""
    def __init__(self, terminal, file_handle, manager_ref):
        self.terminal = terminal
        self.file_handle = file_handle
        self.manager_ref = manager_ref  # 引用manager，确保文件不被提前关闭
        self._closed = False
    
    def write(self, message):
        """安全写入到终端和文件"""
        # 总是写入到终端
        try:
            self.terminal.write(message)
            self.terminal.flush()
        except Exception:
            pass  # 忽略终端写入错误
        
        # 只有在文件未关闭且上下文活跃时才写入文件
        if (not self._closed and 
            self.file_handle and 
            not self.file_handle.closed and 
            self.manager_ref._context_active):
            try:
                self.file_handle.write(message)
                self.file_handle.flush()
            except (ValueError, OSError) as e:
                # 文件已关闭或其他I/O错误，标记为已关闭
                self._closed = True
        
        return len(message)
    
    def flush(self):
        """安全刷新缓冲区"""
        try:
            self.terminal.flush()
        except Exception:
            pass
        
        if (not self._closed and 
            self.file_handle and 
            not self.file_handle.closed):
            try:
                self.file_handle.flush()
            except (ValueError, OSError):
                self._closed = True
    
    def close_when_safe(self):
        """标记为可安全关闭状态"""
        self._closed = True
    
    def isatty(self):
        """检查是否是终端"""
        try:
            return self.terminal.isatty()
        except Exception:
            return False
    
    def fileno(self):
        """返回文件描述符"""
        try:
            return self.terminal.fileno()
        except Exception:
            return -1


class WorkflowExecutionLogger:
    """workflow执行日志捕获器"""
    
    def __init__(self, log_file_path: Path):
        """初始化日志捕获器"""
        self.log_file_path = log_file_path
        self.log_file = None
        self.original_stdout = None
        self.original_stderr = None
        self.tee_stdout = None
        self.tee_stderr = None
        self._context_active = False
    
    def __enter__(self):
        """进入上下文时重定向输出"""
        self._context_active = True
        
        # 确保目录存在
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 打开日志文件
        self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=1)
        
        # 保存原始输出
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 创建双向输出对象
        self.tee_stdout = TeeOutput(self.original_stdout, self.log_file)
        self.tee_stderr = TeeOutput(self.original_stderr, self.log_file)
        
        # 重定向输出
        sys.stdout = self.tee_stdout
        sys.stderr = self.tee_stderr
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时恢复输出"""
        self._context_active = False
        
        # 恢复原始输出
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # 关闭日志文件
        if self.log_file:
            self.log_file.close()


class IndividualTestCaseLogger:
    """单个test case的独立日志管理器 - 避免并发I/O冲突"""
    
    def __init__(self, log_file_path: Path, test_case_index: int):
        """
        初始化独立日志管理器
        
        Args:
            log_file_path: 日志文件路径
            test_case_index: test case索引号
        """
        self.log_file_path = log_file_path
        self.test_case_index = test_case_index
        self.log_file = None
        self.original_stdout = None
        self.original_stderr = None
        self.tee_stdout = None
        self.tee_stderr = None
    
    def __enter__(self):
        """进入上下文时设置独立日志重定向"""
        # 确保目录存在
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 打开独立日志文件
        self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=1)
        
        # 保存原始输出
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 创建安全的双向输出对象（简化版，无manager引用）
        self.tee_stdout = SimpleTeeOutput(self.original_stdout, self.log_file)
        self.tee_stderr = SimpleTeeOutput(self.original_stderr, self.log_file)
        
        # 重定向输出到独立文件
        sys.stdout = self.tee_stdout
        sys.stderr = self.tee_stderr
        
        # 记录开始
        print(f"{'='*60}")
        print(f"Test Case {self.test_case_index} - 独立执行日志")
        print(f"开始时间: {datetime.now().isoformat()}")
        print(f"日志文件: {self.log_file_path}")
        print(f"🔍 验证信息: 此日志文件将执行test_case_index={self.test_case_index}的内容")
        print(f"{'='*60}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时安全关闭独立日志"""
        # 记录结束
        print(f"{'='*60}")
        print(f"Test Case {self.test_case_index} - 执行完成")
        print(f"结束时间: {datetime.now().isoformat()}")
        print(f"🔍 验证信息: 此日志文件完成了test_case_index={self.test_case_index}的处理")
        if exc_type:
            print(f"执行异常: {exc_type.__name__}: {exc_val}")
        print(f"{'='*60}")
        
        # 恢复原始输出
        if self.original_stdout:
            sys.stdout = self.original_stdout
        if self.original_stderr:
            sys.stderr = self.original_stderr
        
        # 安全关闭日志文件
        if self.log_file and not self.log_file.closed:
            try:
                self.log_file.flush()
                self.log_file.close()
            except (ValueError, OSError):
                pass  # 忽略关闭错误


class SimpleTeeOutput:
    """简化的双向输出类 - 用于独立日志"""
    def __init__(self, terminal, file_handle):
        self.terminal = terminal
        self.file_handle = file_handle
    
    def write(self, message):
        """安全写入到终端和文件"""
        # 写入终端
        try:
            self.terminal.write(message)
            self.terminal.flush()
        except Exception:
            pass
        
        # 写入文件
        try:
            if self.file_handle and not self.file_handle.closed:
                self.file_handle.write(message)
                self.file_handle.flush()
        except (ValueError, OSError):
            pass  # 文件已关闭，忽略错误
        
        return len(message)
    
    def flush(self):
        """安全刷新缓冲区"""
        try:
            self.terminal.flush()
        except Exception:
            pass
        
        try:
            if self.file_handle and not self.file_handle.closed:
                self.file_handle.flush()
        except (ValueError, OSError):
            pass
    
    def isatty(self):
        """检查是否是终端"""
        try:
            return self.terminal.isatty()
        except Exception:
            return False
    
    def fileno(self):
        """返回文件描述符"""
        try:
            return self.terminal.fileno()
        except Exception:
            return -1


class InternBootcampRewardCalculator:
    """
    InternBootcamp任务的reward计算器 V2
    """
    
    def __init__(self, config_path: str = None):
        """初始化reward计算器 - 全部从config.yaml读取配置"""
        init_start = time.time()
        
        # 记录初始化开始
        debug_log("init", {"event": "initialization_start"})
        
        # 统一从config.yaml加载配置
        config_file = Path(config_path) if config_path else CONFIG_FILE
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # 读取config.yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        
        # 获取API配置 - 使用metagpt_api_proxy配置
        api_config = yaml_config.get('services', {}).get('metagpt_api_proxy', {})
        
        # 构建LLM配置
        self.llm_config = {
            'provider': 'openai',  # InternBootcamp使用OpenAI兼容接口
            'model': yaml_config.get('api_metagpt', {}).get('model', 'qwen-turbo'),
            'api_key': 'sk-placeholder-will-be-replaced-by-proxy',
            'base_url': "http://localhost:"+str(api_config.get('port')),
            'temperature': yaml_config.get('api_metagpt', {}).get('temperature', 0.9)
        }
        
        # 获取InternBootcamp reward服务配置
        self.reward_config = yaml_config.get('services', {}).get('internbootcamp_reward', {})
        
        # 加载token惩罚配置
        self.token_penalty_config = self.reward_config.get('token_penalty', {})
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 300)  # 默认5分钟
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # 设置workspace路径
        self.workspace_path = WORKSPACE_PATH
        
        # bootcamp类缓存
        self._bootcamp_cache = {}
        
        logger.info("InternBootcampRewardCalculator V2 initialized")
        
        # 记录初始化完成
        debug_log("init", {
            "event": "initialization_complete",
            "config_path": str(config_path),
            "llm_config": self.llm_config,
            "reward_config": self.reward_config
        }, init_start)
    
    def extract_workflow_from_response(self, response: str) -> Optional[str]:
        """
        从LLM response中提取workflow代码
        查找<code>标签内的内容
        """
        extract_start = time.time()
        
        if not response:
            debug_log("workflow", {
                "event": "extract_workflow_failed",
                "reason": "empty_response",
                "response_length": 0
            }, extract_start)
            return None
        
        # 尝试提取<code>标签内的代码
        code_pattern = r'<code>(.*?)</code>'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow code: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "method": "code_tag",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        # 如果没有找到code标签，尝试查找class Workflow定义
        class_pattern = r'(class\s+(?:InternBootcampWorkflow|Workflow).*?)(?=class\s+\w+|$)'
        matches = re.findall(class_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow class: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "method": "class_pattern",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        logger.warning("No workflow code found in response")
        debug_log("workflow", {
            "event": "extract_workflow_failed",
            "reason": "no_workflow_found",
            "response_preview": response[:500] if len(response) > 500 else response,
            "response_length": len(response)
        }, extract_start)
        return None
    
    def _load_bootcamp_class(self, task_name: str):
        """动态加载对应的bootcamp类"""
        if task_name in self._bootcamp_cache:
            return self._bootcamp_cache[task_name]
        
        try:
            # 导入bootcamp模块
            module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
            module = importlib.import_module(module_path)
            
            # 获取bootcamp类
            class_name = f"{task_name.capitalize()}bootcamp"
            bootcamp_class = getattr(module, class_name)
            
            self._bootcamp_cache[task_name] = bootcamp_class
            logger.info(f"Loaded bootcamp class: {class_name}")
            return bootcamp_class
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to load bootcamp class for {task_name}: {e}")
            debug_log("workflow", {
                "event": "bootcamp_class_not_found",
                "task_name": task_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return None
    
    def calculate_token_cost_penalty(self, base_score: float, token_stats: dict) -> tuple:
        """
        基于token使用费用计算惩罚后的分数
        
        Args:
            base_score: 原始分数（准确率）
            token_stats: token统计信息字典
        
        Returns:
            (final_score, penalty_details) 元组
        """
        if not self.token_penalty_config.get('enabled', False):
            return base_score, {}
        
        # 获取token数量
        input_tokens = token_stats.get('prompt_tokens', 0)
        output_tokens = token_stats.get('completion_tokens', 0)
        
        # 获取价格配置
        pricing = self.token_penalty_config.get('pricing', {})
        input_price = pricing.get('input_price_per_million', 0.5)
        output_price = pricing.get('output_price_per_million', 1.5)
        
        # 计算费用（美元）
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price
        total_cost = input_cost + output_cost
        
        # 获取惩罚策略
        strategy = self.token_penalty_config.get('penalty_strategy', {})
        mode = strategy.get('mode', 'linear')
        penalty_rate = strategy.get('penalty_rate', 0.1)
        max_penalty = strategy.get('max_penalty', 0.3)
        
        # 根据模式计算惩罚值
        if mode == 'linear':
            penalty = total_cost * penalty_rate
        elif mode == 'square':
            penalty = (total_cost ** 2) * penalty_rate
        elif mode == 'exponential':
            import math
            penalty = (math.exp(total_cost) - 1) * penalty_rate
        else:
            penalty = 0.0
        
        # 应用最大惩罚限制
        penalty = min(penalty, max_penalty)
        
        # 计算最终分数
        final_score = max(0.0, base_score * (1 - penalty))
        
        # 构建详细信息
        penalty_details = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'penalty_mode': mode,
            'penalty_rate': penalty_rate,
            'penalty_value': penalty,
            'base_score': base_score,
            'final_score': final_score
        }
        
        return final_score, penalty_details
         
    async def execute_workflow_metagpt(self, workflow_code: str, task_name: str, 
                                       test_case_data: Dict) -> tuple:
        """
        使用MetaGPT框架执行工作流
        完全复用workflow_executor.py的执行逻辑
        返回 (result, token_stats) 元组
        """
        exec_start = time.time()
        
        try:
            # 1. 创建临时工作空间（使用config中配置的路径）
            workspace_dir = WORKSPACE_PATH
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            workflow_id = f"reward_{task_name}_{timestamp}_{random_id}"
            
            # 创建workflow的独立Context和CostManager
            global GLOBAL_TOKEN_TRACKER
            workflow_context = GLOBAL_TOKEN_TRACKER.create_workflow_context(workflow_id)
            
            # 2. 保存工作流文件（用于调试）
            workflow_file = workspace_dir / f"{workflow_id}.py"
            meta_file = workspace_dir / f"{workflow_id}.meta.json"
            
            # 3. 获取Handler并构建脚本
            from ScoreFlow.scripts.internbootcamp.handler import InternBootcampHandler
            handler = InternBootcampHandler()
            
            # 使用修复后的build_executable_script方法
            script_parts = handler.build_executable_script(workflow_code, timeout=500)
            
            # 拼接完整脚本
            full_script_code = (
                script_parts["python_start"] + "\n" +
                script_parts["workflow_code"] + "\n" +
                script_parts["python_end"]
            )
            
            # 保存完整脚本用于调试
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(full_script_code)
            
            # 保存元数据
            meta_data = {
                "id": workflow_id,
                "benchmark": "internbootcamp",
                "task_name": task_name,
                "test_case": test_case_data,
                "timestamp": timestamp
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            debug_log("workflow", {
                "event": "metagpt_execution_start",
                "workflow_id": workflow_id,
                "task_name": task_name,
                "script_length": len(full_script_code),
                "workspace": str(workspace_dir)
            })
            
            # 4. 准备执行环境
            execution_namespace = {}
            
            # 加载operator模块（使用common operators）
            operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
            
            # 先准备LLM配置（移到前面，因为后续需要使用）
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
                base_url=self.llm_config.get('base_url'),
                calc_usage=True  # 重要：启用token计算
            )
            
            # 创建LLM实例并关联cost_manager
            llm_instance = create_llm_instance(metagpt_config)
            if workflow_context and hasattr(llm_instance, 'cost_manager'):
                llm_instance.cost_manager = workflow_context.cost_manager
            
            # 准备全局命名空间
            exec_globals = {
                'asyncio': aio,
                'create': lambda config: llm_instance,  # 使用已配置好的llm实例
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': ListType,
            }
            
            # 尝试加载internbootcamp特定的operator_an（如果存在）
            try:
                an_module_path = "ScoreFlow.scripts.internbootcamp.operator_an"
                operator_an_module = importlib.import_module(an_module_path)
                
                # 注入所有公共成员到执行环境
                for attr_name in dir(operator_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(operator_an_module, attr_name)
                
                logger.debug(f"Injected {an_module_path} contents into execution environment")
            except ModuleNotFoundError:
                # internbootcamp可能没有特定的operator_an，使用common的
                try:
                    common_an_module = importlib.import_module("ScoreFlow.scripts.common.operator_an")
                    for attr_name in dir(common_an_module):
                        if not attr_name.startswith('_'):
                            exec_globals[attr_name] = getattr(common_an_module, attr_name)
                    logger.debug("Using common operator_an module")
                except ModuleNotFoundError:
                    logger.debug("No operator_an module found, proceeding without it")
            
            # 5. 执行脚本获取Workflow类
            exec(full_script_code, exec_globals, execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if WorkflowClass is None:
                WorkflowClass = execution_namespace.get('InternBootcampWorkflow')
            if not WorkflowClass:
                raise ValueError(f"No 'Workflow' class found in the executed script for {workflow_id}")
            
            # 6. 格式化问题文本（使用bootcamp的prompt_func）
            bootcamp_class = self._load_bootcamp_class(task_name)
            if bootcamp_class and hasattr(bootcamp_class, 'prompt_func'):
                problem_text = bootcamp_class.prompt_func(test_case_data)
            else:
                problem_text = str(test_case_data)
            
            logger.debug(f"Problem text for {workflow_id}: {problem_text[:200]}...")
            
            # 7. 实例化并执行工作流
            workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            # 确保workflow使用的llm关联了cost_manager
            if hasattr(workflow_instance, 'llm') and workflow_instance.llm:
                workflow_instance.llm.cost_manager = workflow_context.cost_manager
            
            debug_log("workflow", {
                "event": "workflow_instance_created",
                "workflow_id": workflow_id,
                "class_type": str(type(workflow_instance))
            })
            
            # 8. 根据call_signature执行（处理超时参数）
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
                        workflow_instance(timeout=500),
                        timeout=190
                    )
            else:
                # 旧版格式，不传timeout
                execution_result = await asyncio.wait_for(
                    workflow_instance(),
                    timeout=190
                )
            
            debug_log("workflow", {
                "event": "metagpt_execution_completed",
                "workflow_id": workflow_id,
                "result_length": len(str(execution_result)),
                "result_type": str(type(execution_result)),
                "execution_time": time.time() - exec_start
            })
            
            # 获取token统计 - 使用MetaGPT原生方法
            token_stats = GLOBAL_TOKEN_TRACKER.get_workflow_stats(workflow_id)
            GLOBAL_TOKEN_TRACKER.print_workflow_stats(workflow_id)
            
            # 更新总体统计
            GLOBAL_TOKEN_TRACKER.update_total_stats(workflow_id)
            
            logger.info(f"MetaGPT workflow {workflow_id} executed successfully")
            return str(execution_result), token_stats
            
        except asyncio.TimeoutError:
            logger.error(f"MetaGPT workflow execution timed out for {task_name}")
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "error_type": "TimeoutError",
                "task_name": task_name,
                "execution_time": time.time() - exec_start
            })
            # 即使超时也尝试获取token统计
            token_stats = GLOBAL_TOKEN_TRACKER.get_workflow_stats(workflow_id) if 'workflow_id' in locals() else {}
            return "Error: Workflow execution timed out", token_stats
            
        except Exception as e:
            error_msg = f"MetaGPT workflow execution failed for {task_name}: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "task_name": task_name,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_time": time.time() - exec_start
            })
            
            # 即使失败也尝试获取token统计
            token_stats = GLOBAL_TOKEN_TRACKER.get_workflow_stats(workflow_id) if 'workflow_id' in locals() else {}
            return f"Error: {str(e)}", token_stats
    
    async def compute_score_for_testcase(self, workflow_code: str, task_name: str, 
                                        test_case: str) -> float:
        """
        在单个test case上计算分数
        使用MetaGPT执行而非简化执行
        """
        testcase_start = time.time()
        
        debug_log("task", {
            "event": "testcase_start",
            "task_name": task_name,
            "test_case": test_case,
            "workflow_code_length": len(workflow_code),
            "execution_mode": "metagpt"  # 新增标记
        })
        
        try:
            # 加载bootcamp类
            bootcamp_class = self._load_bootcamp_class(task_name)
            if not bootcamp_class:
                debug_log("task", {
                    "event": "testcase_failed",
                    "reason": "bootcamp_class_not_found",
                    "task_name": task_name
                }, testcase_start)
                return 0.0
            
            # 解析test case
            if isinstance(test_case, str):
                try:
                    # 尝试解析为JSON
                    case_data = json.loads(test_case.replace("'", '"'))
                except:
                    # 尝试使用eval
                    try:
                        case_data = eval(test_case)
                    except:
                        case_data = {'input': test_case}
            else:
                case_data = test_case
            
            debug_log("task", {
                "event": "test_case_parsed",
                "raw_test_case": test_case,
                "parsed_data": case_data
            })
            
            # ===== 关键修改：使用MetaGPT执行 =====
            exec_start = time.time()
            
            # 调用新的MetaGPT执行方法，获取结果和token统计
            result, token_stats = await self.execute_workflow_metagpt(workflow_code, task_name, case_data)
            
            debug_log("task", {
                "event": "workflow_executed_via_metagpt",  # 更新事件名
                "execution_time": time.time() - exec_start,
                "result_length": len(str(result)),
                "result_preview": str(result),
                "token_stats": token_stats
            })
            
            logger.debug(f"MetaGPT workflow result: {str(result)[:100]}...")
            
            # 使用bootcamp的verify_score验证结果
            verify_start = time.time()
            score = bootcamp_class.verify_score(
                model_output=str(result),
                identity=case_data,
                format_score=0.1,
                short_penalty=False,
                format_penalty=False
            )
            
            base_score = float(score)
            
            # 应用token费用惩罚
            final_score, penalty_details = self.calculate_token_cost_penalty(base_score, token_stats)
            
            # 打印惩罚详情
            if penalty_details and self.token_penalty_config.get('enabled', False):
                print(f"\n💰 Token费用惩罚计算 (InternBootcamp):")
                print(f"  输入Tokens: {penalty_details['input_tokens']:,}")
                print(f"  输出Tokens: {penalty_details['output_tokens']:,}")
                print(f"  输入费用: ${penalty_details['input_cost']:.6f}")
                print(f"  输出费用: ${penalty_details['output_cost']:.6f}")
                print(f"  总费用: ${penalty_details['total_cost']:.6f}")
                print(f"  基础分数: {penalty_details['base_score']:.3f}")
                print(f"  惩罚值: {penalty_details['penalty_value']:.3f}")
                print(f"  最终分数: {penalty_details['final_score']:.3f}\n")
            
            debug_log("task", {
                "event": "score_verified",
                "base_score": base_score,
                "final_score": final_score,
                "token_stats": token_stats,
                "penalty_details": penalty_details,
                "verification_time": time.time() - verify_start,
                "task_name": task_name,
                "execution_mode": "metagpt"
            })
            
            logger.info(f"Task {task_name} test case score (MetaGPT): {final_score} (base: {base_score})")
            
            debug_log("task", {
                "event": "testcase_completed",
                "task_name": task_name,
                "base_score": base_score,
                "final_score": final_score,
                "total_time": time.time() - testcase_start,
                "execution_mode": "metagpt"
            })
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error computing score for {task_name}: {e}")
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "compute_score_for_testcase",
                "task_name": task_name,
                "test_case": test_case,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_mode": "metagpt"
            }, testcase_start)
            
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, task_name: str, 
                                  test_cases: List[str]) -> float:
        """
        异步计算workflow在所有test cases上的平均reward
        使用优化的并行处理策略
        """
        if not test_cases:
            return 0.0
        
        # 记录开始时间
        batch_start = time.time()
        
        debug_log("task", {
            "event": "batch_compute_start",
            "task_name": task_name,
            "num_test_cases": len(test_cases),
            "max_concurrent": self.max_concurrent
        })
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
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
        
        async def limited_compute(test_case, index):
            async with semaphore:
                try:
                    score = await self.compute_score_for_testcase(workflow_code, task_name, test_case)
                    await update_progress()
                    return (index, score, None)
                except Exception as e:
                    logger.error(f"Test case {index} failed: {e}")
                    await update_progress()
                    return (index, 0.0, e)
        
        # 使用asyncio.create_task创建更高效的任务
        tasks = [
            asyncio.create_task(limited_compute(test_case, i))
            for i, test_case in enumerate(test_cases)
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
                logger.error(f"Task {index} failed with exception: {error}")
                valid_scores.append(0.0)
                failed_count += 1
                debug_log("error", {
                    "function": "compute_score_for_testcase",
                    "test_case_index": index,
                    "error": {
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "traceback": traceback.format_exc() if error else None
                    }
                })
            else:
                valid_scores.append(score)
        
        # 计算平均分
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        success_rate = (len(valid_scores) - failed_count) / len(valid_scores) if valid_scores else 0.0
        
        logger.info(f"Average score for {task_name}: {avg_score:.3f} "
                   f"({len(valid_scores)} test cases, {success_rate*100:.1f}% success rate)")
        
        debug_log("task", {
            "event": "batch_compute_completed",
            "task_name": task_name,
            "scores": valid_scores,
            "average_score": avg_score,
            "num_test_cases": len(test_cases),
            "failed_count": failed_count,
            "success_rate": success_rate,
            "batch_duration": time.time() - batch_start
        })
        
        return avg_score


# 创建全局计算器实例
_global_calculator = None

def get_calculator(config_path: str = None):
    """
    获取全局计算器实例
    
    Args:
        config_path: 可选的配置文件路径，默认使用config.yaml
    """
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = InternBootcampRewardCalculator(config_path)
    return _global_calculator


def compute_score(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    计算单个solution的reward分数（符合VERL接口规范）
    
    Args:
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息（对于InternBootcamp通常是"default"）
        extra_info: 包含task_name和test_cases等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    # 检查是否已经在事件循环中
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # 如果不在事件循环中，使用 asyncio.run
        return asyncio.run(_compute_score_async(solution_str, ground_truth, extra_info))
    else:
        # 如果已经在事件循环中，在单独线程中开启新的事件循环以保持同步接口
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(lambda: asyncio.run(_compute_score_async(solution_str, ground_truth, extra_info)))
            return future.result()


async def _compute_score_async(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    异步计算单个solution的reward分数（内部实现）
    """
    compute_start = time.time()
    
    # 记录任务开始
    debug_log("task", {
        "event": "compute_score_start",
        "ground_truth": ground_truth,
        "extra_info": extra_info,
        "solution_length": len(solution_str) if solution_str else 0
    })
    
    try:
        # 获取计算器实例
        calculator = get_calculator()
        
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(solution_str)
        if not workflow_code:
            logger.error("No workflow code found in solution")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_workflow_code",
                "solution_preview": solution_str[:500] if solution_str and len(solution_str) > 500 else solution_str
            }, compute_start)
            return 0.0
        
        # 从extra_info提取必要信息
        task_name = extra_info.get('task_name', '')
        test_cases = extra_info.get('test_cases', [])
        
        # 处理numpy array的情况
        if hasattr(test_cases, 'tolist'):
            test_cases = test_cases.tolist()
        
        if not task_name:
            logger.error("No task_name found in extra_info")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_task_name",
                "extra_info": extra_info
            }, compute_start)
            return 0.0
        
        logger.info(f"Computing reward for task: {task_name} with {len(test_cases)} test cases")
        
        # 记录任务详情
        debug_log("task", {
            "event": "task_details",
            "task_name": task_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "workflow_code_length": len(workflow_code)
        })
        
        # 使用已有的异步并行方法
        reward = await calculator.compute_reward_async(workflow_code, task_name, test_cases)
        
        logger.info(f"Computed average reward: {reward:.3f}")
        
        # 记录最终结果
        debug_log("task", {
            "event": "compute_score_completed",
            "task_name": task_name,
            "average_reward": reward,
            "num_test_cases": len(test_cases)
        }, compute_start)
        
        # 输出总体token统计 - 使用MetaGPT原生方法
        GLOBAL_TOKEN_TRACKER.print_total_stats()
        
        # 保存debug数据
        save_debug_data()
        
        return reward
        
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        
        # 记录错误
        debug_log("error", {
            "function": "compute_score",
            "error": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            },
            "context": {
                "extra_info": extra_info,
                "solution_length": len(solution_str) if solution_str else 0
            }
        }, compute_start)
        
        # 保存debug数据
        save_debug_data()
        
        return 0.0




if __name__ == "__main__":
    # 简单测试
    test_solution = """
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
</code>
"""
    
    test_extra_info = {
        'task_name': 'adidyoumean',
        'test_cases': ["{'input': 'hello'}", "{'input': 'hellno'}", "{'input': 'abacaba'}"]
    }
    
    # 使用异步方式运行测试
    async def test():
        score = await _compute_score_async(test_solution, "default", test_extra_info)
        print(f"Test score: {score}")
    
    asyncio.run(test())