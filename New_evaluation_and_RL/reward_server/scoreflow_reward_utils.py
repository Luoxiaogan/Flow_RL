"""
ScoreFlow Reward Function for VERL
适配ScoreFlow系统的reward计算器，支持所有benchmark
"""
import os
import sys
import re
import json
import asyncio
import logging
from loguru import logger as loguru_logger
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

# MetaGPT原生Token追踪实现
from metagpt.context import Context
from metagpt.utils.cost_manager import CostManager, Costs

# 导入ScoreFlow组件
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MetaGPTNativeTokenTracker:
    """使用MetaGPT原生功能的Token追踪器"""
    
    def __init__(self):
        self.workflow_contexts = {}  # workflow_id -> Context
        self.workflow_stats = {}     # workflow_id -> stats
        self.total_stats = {
            'total_workflows': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_cost': 0.0,
            'workflows': []
        }
        print(f"✅ MetaGPT原生Token追踪器已初始化")
    
    def create_workflow_context(self, workflow_id: str) -> Context:
        """为workflow创建独立的Context和CostManager"""
        context = Context()
        cost_manager = CostManager()
        cost_manager.max_budget = 100.0
        context.cost_manager = cost_manager
        self.workflow_contexts[workflow_id] = context
        return context
    
    def get_workflow_context(self, workflow_id: str) -> Optional[Context]:
        """获取workflow的context"""
        return self.workflow_contexts.get(workflow_id)
    
    def get_workflow_stats(self, workflow_id: str) -> dict:
        """获取workflow统计（从Context的CostManager获取）"""
        context = self.workflow_contexts.get(workflow_id)
        if not context:
            return {}
        
        costs = context.cost_manager.get_costs()
        return {
            'workflow_id': workflow_id,
            'prompt_tokens': costs.total_prompt_tokens,
            'completion_tokens': costs.total_completion_tokens,
            'total_tokens': costs.total_prompt_tokens + costs.total_completion_tokens,
            'total_cost': costs.total_cost,
            'api_calls': 1 if costs.total_prompt_tokens > 0 else 0
        }
    
    def print_workflow_stats(self, workflow_id: str):
        """打印workflow的token统计"""
        stats = self.get_workflow_stats(workflow_id)
        
        if stats and stats.get('total_tokens', 0) > 0:
            print(f"\n{'='*60}")
            print(f"📊 Token统计 - Workflow: {workflow_id}")
            print(f"  输入Token: {stats['prompt_tokens']:,}")
            print(f"  输出Token: {stats['completion_tokens']:,}")
            print(f"  总计Token: {stats['total_tokens']:,}")
            print(f"{'='*60}\n")
    
    def update_total_stats(self, workflow_id: str):
        """更新总体统计信息"""
        stats = self.get_workflow_stats(workflow_id)
        if stats and stats.get('total_tokens', 0) > 0:
            self.total_stats['total_workflows'] += 1
            self.total_stats['total_prompt_tokens'] += stats['prompt_tokens']
            self.total_stats['total_completion_tokens'] += stats['completion_tokens']
            self.total_stats['total_cost'] += stats['total_cost']
            self.total_stats['workflows'].append(stats)

# 创建全局Token追踪器
GLOBAL_TOKEN_TRACKER = MetaGPTNativeTokenTracker()

# DEBUG和SILENT模式控制 - 从config.yaml读取
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        _config_for_debug = yaml.safe_load(f)
        # 从scoreflow_reward服务配置中读取debug和silent设置
        scoreflow_config = _config_for_debug.get('services', {}).get('scoreflow_reward', {})
        DEBUG = int(scoreflow_config.get('debug', False))
        SILENT = scoreflow_config.get('silent', False)
        print(f"📝 Debug日志模式: {'开启' if DEBUG else '关闭'} (从config.yaml读取)")
        print(f"🔇 静默模式: {'开启' if SILENT else '关闭'} (从config.yaml读取)")
else:
    DEBUG = 0  # 默认关闭debug
    SILENT = False  # 默认关闭静默模式
    print(f"📝 Debug日志模式: 关闭 (默认值)")
    print(f"🔇 静默模式: 关闭 (默认值)")

DEBUG_PATH = PROJECT_ROOT / "debug_logs"  # 存储在evaluation_workflow目录下


# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if SILENT:
    # 禁用特定库的日志
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)  # httpx 的底层库
    logging.getLogger("openai").setLevel(logging.ERROR)     # OpenAI SDK 的 HTTP 日志
    logging.getLogger("metagpt").setLevel(logging.ERROR)    # MetaGPT 的日志
    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # 禁用 Flask 访问日志
    # 禁用 loguru 的 metagpt 日志
    loguru_logger.disable("metagpt")


def debug_print(*args, **kwargs):
    """
    Debug模式下的条件打印函数
    只有当DEBUG == 1时才会输出，否则静默
    
    Usage:
        debug_print("这条消息只在debug模式下显示")
        debug_print("变量值:", variable, "状态:", status)
    """
    if DEBUG == 1:
        print(*args, **kwargs)


def silent_print(*args, **kwargs):
    """
    非静默模式下的条件打印函数
    只有当SILENT == False时才会输出到终端
    用于显示详细信息，在静默模式下会被屏蔽
    
    Usage:
        silent_print("详细执行信息")  # 静默模式下不显示
        print("关键结果信息")  # 始终显示
    """
    if not SILENT:
        print(*args, **kwargs)

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
        # 根据SILENT设置决定是否写到终端
        if not SILENT:
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
    
    def __enter__(self):
        """进入上下文时重定向输出"""
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
        # 恢复原始输出
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # ✅ 关键修复：清理TeeOutput引用，防止内存泄漏
        self.tee_stdout = None
        self.tee_stderr = None
        
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
        silent_print(f"Test Case {self.test_case_index} - 独立执行日志")
        silent_print(f"开始时间: {datetime.now().isoformat()}")
        silent_print(f"日志文件: {self.log_file_path}")
        silent_print(f"🔍 验证信息: 此日志文件将执行test_case_index={self.test_case_index}的内容")
        print(f"{'='*60}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时安全关闭独立日志"""
        # 记录结束
        print(f"{'='*60}")
        silent_print(f"Test Case {self.test_case_index} - 执行完成")
        print(f"结束时间: {datetime.now().isoformat()}")
        print(f"🔍 验证信息: 此日志文件完成了test_case_index={self.test_case_index}的处理")
        if exc_type:
            silent_print(f"执行异常: {exc_type.__name__}: {exc_val}")
        print(f"{'='*60}")
        
        # 恢复原始输出
        if self.original_stdout:
            sys.stdout = self.original_stdout
        if self.original_stderr:
            sys.stderr = self.original_stderr
        
        # ✅ 关键修复：清理SimpleTeeOutput引用，防止内存泄漏
        self.tee_stdout = None
        self.tee_stderr = None
        
        # 安全关闭日志文件
        if self.log_file and not self.log_file.closed:
            try:
                self.log_file.flush()
                self.log_file.close()
            except (ValueError, OSError):
                pass  # 忽略关闭错误


class SimpleTeeOutput:
    """简化的双向输出类 - 超级防御版，处理所有属性丢失情况"""
    def __init__(self, terminal, file_handle):
        # 使用object.__setattr__确保属性设置成功，避免被覆盖
        object.__setattr__(self, 'terminal', terminal)
        object.__setattr__(self, '_file_handle', file_handle)
        object.__setattr__(self, '_closed', False)
        object.__setattr__(self, '_error_count', 0)
        object.__setattr__(self, '_initialized', True)  # 标记初始化完成
        # 安全导入threading模块，防止在某些执行环境中不可用
        try:
            import threading
            object.__setattr__(self, '_lock', threading.RLock())  # 添加线程锁保护
        except ImportError:
            object.__setattr__(self, '_lock', None)  # 如果threading不可用，设为None
    
    def __getattr__(self, name):
        """捕获所有属性访问失败的情况，提供默认值"""
        # 提供所有可能丢失属性的默认值
        if name == '_initialized':
            return False
        if name == '_closed':
            return True  # 默认为已关闭，停止文件写入
        if name == '_error_count':
            return 0
        if name == '_file_handle':
            return None
        if name == 'terminal':
            # 返回标准输出作为备用
            return sys.__stdout__ if hasattr(sys, '__stdout__') else None
        # 其他未知属性
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @property
    def file_handle(self):
        """完全防御性的file_handle访问"""
        try:
            # 尝试正常访问
            return self._file_handle if hasattr(self, '_file_handle') else None
        except AttributeError:
            # 如果仍然失败，返回None
            return None
    
    def write(self, message):
        """安全写入到终端和文件"""
        # 尝试获取锁，如果锁不存在则创建一个
        try:
            lock = getattr(self, '_lock', None)
            if lock is None:
                # 安全导入threading模块
                try:
                    import threading
                    lock = threading.RLock()
                    object.__setattr__(self, '_lock', lock)
                except ImportError:
                    lock = None  # 如果threading不可用，设为None
        except:
            lock = None
        
        # 使用锁保护写操作（如果锁可用）
        if lock:
            with lock:
                return self._do_write(message)
        else:
            return self._do_write(message)
    
    def _do_write(self, message):
        """实际的写操作逻辑"""
        # 根据SILENT设置决定是否写到终端
        if not SILENT:
            try:
                # 获取terminal，使用__getattr__提供的默认值
                terminal = getattr(self, 'terminal', None)
                if terminal:
                    terminal.write(message)
                    terminal.flush()
            except Exception:
                pass
        
        # 始终尝试写入文件（超级防御性错误处理）
        try:
            # 使用property安全访问file_handle
            file_handle = self.file_handle
            # 安全获取_closed属性
            is_closed = getattr(self, '_closed', True)
            
            if file_handle and not is_closed:
                # 三重检查：属性存在、不为None、文件未关闭
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.write(message)
                        file_handle.flush()
                    else:
                        # 尝试设置_closed标志
                        try:
                            object.__setattr__(self, '_closed', True)
                        except:
                            pass
                else:
                    # file_handle没有closed属性，尝试直接写入
                    file_handle.write(message)
                    file_handle.flush()
        except (ValueError, OSError, AttributeError) as e:
            # 发生任何文件相关错误时，尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
                error_count = getattr(self, '_error_count', 0)
                if error_count < 5:  # 限制错误日志数量
                    logger.debug(f"SimpleTeeOutput write error (count={error_count}): {type(e).__name__}")
                    object.__setattr__(self, '_error_count', error_count + 1)
            except:
                pass  # 即使设置属性失败也不崩溃
        except Exception:
            # 捕获所有其他异常，确保不会崩溃
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass
        
        return len(message) if message else 0
    
    def flush(self):
        """安全刷新缓冲区"""
        try:
            # 安全获取terminal
            terminal = getattr(self, 'terminal', None)
            if terminal:
                terminal.flush()
        except Exception:
            pass
        
        try:
            # 使用property安全访问
            file_handle = self.file_handle
            # 安全获取_closed属性
            is_closed = getattr(self, '_closed', True)
            
            if file_handle and not is_closed:
                if hasattr(file_handle, 'closed'):
                    if not file_handle.closed:
                        file_handle.flush()
                else:
                    file_handle.flush()
        except (ValueError, OSError, AttributeError):
            # 尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass
        except Exception:
            # 尝试标记为已关闭
            try:
                object.__setattr__(self, '_closed', True)
            except:
                pass
    
    def isatty(self):
        """检查是否是终端"""
        try:
            terminal = getattr(self, 'terminal', None)
            if terminal:
                return terminal.isatty()
        except Exception:
            pass
        return False
    
    def fileno(self):
        """返回文件描述符"""
        try:
            terminal = getattr(self, 'terminal', None)
            if terminal:
                return terminal.fileno()
        except Exception:
            pass
        return -1
    
    def close(self):
        """显式关闭方法 - 安全清理资源"""
        try:
            # 标记为已关闭
            object.__setattr__(self, '_closed', True)
            
            # 尝试关闭文件句柄
            file_handle = getattr(self, '_file_handle', None)
            if file_handle and hasattr(file_handle, 'close'):
                try:
                    if hasattr(file_handle, 'closed'):
                        if not file_handle.closed:
                            file_handle.close()
                    else:
                        file_handle.close()
                except:
                    pass
        except:
            pass
    
    def __del__(self):
        """析构方法 - 最后的资源清理防线"""
        try:
            # 确保文件句柄被关闭
            self.close()
        except:
            pass  # 绝对不能在__del__中抛出异常


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
        
        silent_print(f"📁 创建workflow目录: {self.workflow_dir}")
        silent_print(f"🔄 初始化并行执行管理器 - ID: {self.workflow_id}")
        silent_print(f"📊 准备执行{len(test_cases)}个test cases: {test_cases}")
    
    def __enter__(self):
        """简化的上下文管理器入口 - 不再需要全局日志重定向"""
        silent_print(f"🚀 开始并行执行会话 - ID: {self.workflow_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """简化的上下文管理器出口 - 主要用于清理和汇总"""
        silent_print(f"🏁 并行执行会话结束 - ID: {self.workflow_id}")
        if exc_type:
            print(f"⚠️ 执行过程中发生异常: {exc_type.__name__}: {exc_val}")
    
    def save_workflow_code(self, workflow_code: str):
        """保存workflow代码"""
        code_file = self.workflow_dir / "workflow.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(workflow_code)
        silent_print(f"💾 保存workflow代码: {code_file}")
    
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
        silent_print(f"💾 保存元数据: {meta_file}")
    
    async def execute_test_case(self, calculator, workflow_code: str, 
                              test_case_index: int, dataset_path: str) -> Dict:
        """执行单个test case并记录日志"""
        log_file = self.workflow_dir / f"test_case_{test_case_index}.log"
        
        # 记录开始时间
        start_time = time.time()
        
        silent_print(f"\n📝 开始记录test case {test_case_index}的执行日志: {log_file}")
        
        # 使用日志捕获器执行
        with WorkflowExecutionLogger(log_file):
            print(f"{'='*60}")
            silent_print(f"开始执行Test Case: {test_case_index}")
            print(f"时间: {datetime.now().isoformat()}")
            silent_print(f"Workflow ID: {self.workflow_id}")
            print(f"Data Source: {self.data_source}")
            print(f"{'='*60}\n")
            
            try:
                # 设置当前workflow目录，供compute_score_for_testcase使用
                calculator._current_workflow_dir = self.workflow_dir
                
                # 执行workflow并获取分数
                score = await calculator.compute_score_for_testcase(
                    workflow_code, self.data_source, test_case_index, dataset_path
                )
                success = True
                error_msg = ""
                
                silent_print(f"\n✅ Test Case {test_case_index} 执行成功")
                
                # 清理临时属性
                if hasattr(calculator, '_current_workflow_dir'):
                    delattr(calculator, '_current_workflow_dir')
                
            except Exception as e:
                success = False
                error_msg = self._sanitize_error(str(e))
                score = 0.0
                silent_print(f"\n❌ Test Case {test_case_index} 执行失败")
                print(f"错误: {e}")
                traceback.print_exc()
            
            # 记录结束信息
            duration = time.time() - start_time
            print(f"\n{'='*60}")
            silent_print(f"Test Case {test_case_index} 执行完成")
            print(f"成功: {success}")
            print(f"分数: {score}")
            print(f"耗时: {duration:.2f}秒")
            print(f"{'='*60}")
            
            # 记录结果
            result_record = {
                "test_case": test_case_index,
                "success": success,
                "score": score,
                "duration": duration,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result_record)
            
            # 这个print必须在with块内部！
            print(f"✅ Test case {test_case_index}日志已保存")
        
        # with块外不能有print语句，否则会导致I/O错误
        return result_record
    
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
    
    def save_results_csv(self):
        """保存所有结果到CSV文件"""
        csv_file = self.workflow_dir / "results.csv"
        
        # 准备CSV数据
        headers = ["test_case", "success", "score", "duration", "error", "timestamp"]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"📊 保存结果CSV: {csv_file}")
        
        # 同时生成汇总信息
        total_score = sum(r['score'] for r in self.results)
        avg_score = total_score / len(self.results) if self.results else 0
        total_duration = sum(r['duration'] for r in self.results)
        
        summary = {
            "workflow_id": self.workflow_id,
            "data_source": self.data_source,
            "total_test_cases": len(self.results),
            "successful_cases": sum(1 for r in self.results if r['success']),
            "failed_cases": sum(1 for r in self.results if not r['success']),
            "average_score": avg_score,
            "total_score": total_score,
            "total_duration": total_duration,
            "timestamp": datetime.now().isoformat()
        }
        
        summary_file = self.workflow_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 保存汇总信息: {summary_file}")
        
        # 打印汇总信息
        print(f"\n{'='*60}")
        print(f"📈 执行汇总")
        print(f"{'='*60}")
        print(f"Workflow ID: {self.workflow_id}")
        print(f"Data Source: {self.data_source}")
        print(f"总测试案例: {summary['total_test_cases']}")
        print(f"成功案例: {summary['successful_cases']}")
        print(f"失败案例: {summary['failed_cases']}")
        print(f"平均分数: {avg_score:.3f}")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"{'='*60}")
        
        return avg_score
    
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
        print(f"🚀 开始并行执行模式 - 总共{len(self.test_cases)}个test cases")
        print(f"⚡ 独立文件并行执行，避免I/O冲突")
        
        total_start_time = time.time()
        
        # 1. 并行执行所有test cases，每个使用独立日志文件
        print(f"\n📋 创建{len(self.test_cases)}个并行任务...")
        tasks = []
        for test_case_index in self.test_cases:
            task = self._execute_single_test_case_isolated(
                calculator, workflow_code, test_case_index, dataset_path
            )
            tasks.append(task)
        
        # 并行执行所有任务
        print(f"⚡ 开始并行执行所有test cases...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 2. 安全收集所有结果到内存
        print(f"\n📊 收集和验证执行结果...")
        all_scores = []
        valid_results = []
        
        async with self.results_lock:
            for i, result in enumerate(results):
                test_case_index = self.test_cases[i]
                
                if isinstance(result, Exception):
                    # 处理异常情况
                    print(f"❌ Test Case {test_case_index} 执行异常: {result}")
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
                    print(f"✅ Test Case {test_case_index} 完成 - 分数: {result.get('score', 0.0):.3f}")
                    valid_results.append(result)
                    all_scores.append(result.get('score', 0.0))
                else:
                    # 处理未知格式
                    print(f"⚠️ Test Case {test_case_index} 返回未知格式: {type(result)}")
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
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        successful_count = sum(1 for r in valid_results if r.get('success', False))
        
        print(f"\n{'='*80}")
        print(f"🏁 并行执行All-Reduce完成")
        print(f"{'='*80}")
        print(f"总执行时间: {total_duration:.2f}秒")
        print(f"并行任务数: {len(self.test_cases)}")
        print(f"成功任务数: {successful_count}")
        print(f"失败任务数: {len(valid_results) - successful_count}")
        print(f"所有分数: {all_scores}")
        print(f"平均分数: {avg_score:.3f}")
        print(f"{'='*80}")
        
        # 4. 串行写入汇总文件（避免I/O冲突）
        final_score = self._finalize_and_save_summary(total_duration)
        
        return final_score
    
    async def _execute_single_test_case_isolated(self, calculator, workflow_code: str, 
                                               test_case_index: int, dataset_path: str) -> dict:
        """
        执行单个test case，使用独立日志文件，避免I/O冲突
        
        Args:
            calculator: ScoreFlowRewardCalculator实例
            workflow_code: workflow代码
            test_case_index: test case索引
            dataset_path: 数据集路径
            
        Returns:
            执行结果字典
        """
        # 创建独立日志文件路径
        individual_log_file = self.workflow_dir / f"test_case_{test_case_index}.log"
        
        # 使用独立日志管理器
        with IndividualTestCaseLogger(individual_log_file, test_case_index):
            start_time = time.time()
            
            try:
                silent_print(f"🔧 设置执行环境...")
                # 设置当前workflow目录，供compute_score_for_testcase使用
                calculator._current_workflow_dir = self.workflow_dir
                
                silent_print(f"⚡ 开始执行workflow...")

                # 执行单个test case
                score = await calculator.compute_score_for_testcase(
                    workflow_code, self.data_source, test_case_index, dataset_path
                )
                
                success = True
                error_msg = ""
                silent_print(f"✅ 执行成功，得分: {score:.3f}")
                
                # 清理临时属性
                if hasattr(calculator, '_current_workflow_dir'):
                    delattr(calculator, '_current_workflow_dir')
                
            except Exception as e:
                success = False
                error_msg = self._sanitize_error(str(e))
                score = 0.0
                silent_print(f"❌ 执行失败: {e}")
            
            # 计算执行时间
            duration = time.time() - start_time
            
            # 构建结果记录
            result_record = {
                "test_case": test_case_index,
                "success": success,
                "score": score,
                "duration": duration,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            
            silent_print(f"📝 执行完成 - 耗时: {duration:.2f}秒")
            return result_record
    
    def _finalize_and_save_summary(self, total_duration: float) -> float:
        """
        All-Reduce汇总阶段：处理所有收集的结果，串行写入汇总文件
        
        Args:
            total_duration: 总执行时间
            
        Returns:
            最终平均分数
        """
        print(f"\n📊 开始All-Reduce汇总阶段...")
        
        if not self.results_collector:
            print("⚠️ 没有收集到任何结果")
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
        
        print(f"✅ All-Reduce汇总完成 - 最终分数: {avg_score:.3f}")
        return avg_score
    
    def _save_results_csv_safe(self):
        """串行安全地保存results.csv，避免并发I/O冲突"""
        csv_file = self.workflow_dir / "results.csv"
        
        print(f"📊 串行写入CSV结果文件: {csv_file}")
        
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
            
            print(f"✅ CSV结果文件保存完成: {len(self.results_collector)}条记录")
            
        except Exception as e:
            print(f"❌ 保存CSV文件失败: {e}")
    
    def _save_summary_json_safe(self, avg_score: float, successful_count: int, 
                               total_test_cases: int, success_rate: float, 
                               total_duration: float):
        """串行安全地保存summary.json，避免并发I/O冲突"""
        summary_file = self.workflow_dir / "summary.json"
        
        print(f"📊 串行写入JSON汇总文件: {summary_file}")
        
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
            
            print(f"✅ JSON汇总文件保存完成")
            print(f"   - 平均分数: {avg_score:.3f}")
            print(f"   - 成功率: {success_rate:.1%}")
            print(f"   - 总耗时: {total_duration:.2f}秒")
            
        except Exception as e:
            print(f"❌ 保存JSON汇总文件失败: {e}")
    
    def _save_global_execution_log_safe(self, avg_score: float, total_duration: float):
        """串行安全地写入全局执行日志汇总"""
        global_log_file = self.workflow_dir / "global_execution.log"
        
        print(f"📝 串行写入全局执行日志: {global_log_file}")
        
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
            
            print(f"✅ 全局执行日志保存完成")
            
        except Exception as e:
            print(f"❌ 保存全局执行日志失败: {e}")


class ScoreFlowRewardCalculator:
    """
    ScoreFlow任务的reward计算器
    复用现有的BenchmarkHandler体系
    """
    
    def __init__(self, config_path: str = None):
        """初始化reward计算器"""
        init_start = time.time()
        
        # 记录初始化开始
        debug_log("init", {"event": "initialization_start"})
        
        # 从config.yaml加载配置（不再依赖config.json）
        if CONFIG_FILE.exists():
            silent_print("\n🚀 使用config.yaml:", CONFIG_FILE)
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
            silent_print("\n🚀 llm_config (for MetaGPT operators):\n", self.llm_config)
            
            # 从scoreflow_reward服务配置获取超时等参数
            scoreflow_config = config.get('services', {}).get('scoreflow_reward', {})
            self.reward_config = {
                'timeout': scoreflow_config.get('timeout', 300),
                'client_http_timeout': scoreflow_config.get('client_http_timeout', 600),  # 新增：HTTP客户端超时
                'test_cases_per_task': 3,
                'max_concurrent': 5
            }
            debug_print("\n🚀 reward_config:\n", self.reward_config)
            
            # 加载token惩罚配置
            self.token_penalty_config = scoreflow_config.get('token_penalty', {})
            debug_print("\n🚀 token_penalty_config:\n", self.token_penalty_config)
            
            # 加载token惩罚配置
            self.token_penalty_config = scoreflow_config.get('token_penalty', {})
            debug_print("\n🚀 token_penalty_config:\n", self.token_penalty_config)
            
            # 读取workspace配置
            workspace_relative = scoreflow_config.get('workspace', 'workspace')
            debug_print("scoreflow_config.get('workspace')=", workspace_relative)
            
            # 将相对路径与project_root_path拼接成绝对路径
            debug_print("⚠️ ⚠️ ⚠️ ⚠️ ⚠️ project_root_path=", project_root_path)
            if workspace_relative:
                self.workspace_path = project_root_path / workspace_relative
            else:
                # 如果没有配置，使用默认路径
                self.workspace_path = project_root_path / "workspace"
            
            debug_print(f"\n🚀 workspace路径: {self.workspace_path}")
        else:
            # 默认配置
            debug_print("\n⚠️ Config file not found, using defaults")
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
            self.token_penalty_config = {}  # 默认禁用token惩罚
            self.workspace_path = PROJECT_ROOT / "workspace"
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 180)
        self.client_http_timeout = self.reward_config.get('client_http_timeout', 600)  # HTTP客户端超时
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # 创建token追踪器
        self.token_tracker = MetaGPTNativeTokenTracker()
        
        # handler缓存
        self._handler_cache = {}
        
        # 加载benchmark mapping
        self.benchmark_mapping = self._load_benchmark_mapping()
        
        silent_print("ScoreFlowRewardCalculator initialized")
        
        # 记录初始化完成
        debug_log("init", {
            "event": "initialization_complete",
            "config_path": str(config_path),
            "llm_config": self.llm_config,
            "reward_config": self.reward_config
        }, init_start)
    
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
        extract_start = time.time()
        
        if not response:
            debug_log("workflow", {
                "event": "extract_workflow_failed",
                "reason": "empty_response",
                "workflow_code": None,
                "response": response,
                "response_length": 0
            }, extract_start)
            return None
        
        # 尝试提取<code>标签内的代码

        code_pattern = re.compile(r'```python\s*\n(.*?)\n```', re.DOTALL)
        matches_python = code_pattern.findall(response)
        silent_print(f"🐺 🐺 🐺 🐺 matches_python=\n\n{matches_python}\n\n")

        # code_pattern = r'<code>(.*?)</code>'
        # matches_code = re.findall(code_pattern, response, re.DOTALL)
        # print(f"🐺 🐺 🐺 🐺 matches_code=\n\n{matches_code}\n\n")

        matches = matches_python
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow code from code tag: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "workflow_code": workflow_code,
                "response": response,
                "method": "code_tag",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        # 如果没有找到code标签，尝试查找class Workflow定义
        debug_print("没有找到```python ```包裹的部分")
        class_pattern = r'(class\s+Workflow.*?)(?=class\s+\w+|$)'
        matches = re.findall(class_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow class: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "workflow_code": workflow_code,
                "response": response,
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
                    silent_print(f"Using base benchmark '{base_name}' mapping for '{benchmark_name}'")

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
            silent_print(f"Loaded handler {handler_class_name} for {benchmark_name}")
            return handler
            
        except Exception as e:
            logger.error(f"Failed to load handler for {benchmark_name}: {e}")
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
    
    async def execute_workflow_metagpt(self, workflow_code: str, benchmark_name: str, 
                                       test_case_index: int, dataset_path: str, 
                                       workflow_dir: Path = None) -> tuple:
        """
        使用MetaGPT框架执行工作流
        完全复用workflow_executor.py的执行逻辑
        
        Args:
            workflow_code: workflow代码
            benchmark_name: benchmark名称
            test_case_index: 测试案例索引
            dataset_path: 数据集路径
            workflow_dir: 工作目录（如果提供，将在此目录保存调试文件）
        """
        exec_start = time.time()
        
        try:
            # 生成workflow标识
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            workflow_id = f"exec_{benchmark_name}_{test_case_index}_{timestamp}_{random_id}"
            
            # 创建workflow的独立Context和CostManager用于token追踪
            workflow_context = self.token_tracker.create_workflow_context(workflow_id)
            
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
            
            # 如果提供了工作目录，保存调试文件
            if workflow_dir:
                debug_file = workflow_dir / f"metagpt_exec_{test_case_index}.py"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(full_script_code)
                logger.debug(f"Saved debug script to {debug_file}")
            
            debug_log("workflow", {
                "event": "metagpt_execution_start",
                "workflow_id": workflow_id,
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "script_length": len(full_script_code),
                "workspace": str(workflow_dir) if workflow_dir else "None"
            })
            
            # 4. 准备执行环境
            debug_print("/n 🚀开始准备执行环境")
            execution_namespace = {}
            
            # 加载operator模块（使用common operators）
            operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
            debug_print("/n 🚀加载common operator成功")
            # 准备全局命名空间
            exec_globals = {
                'asyncio': aio,
                'create': create_llm_instance,
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': ListType,
            }
            
            # 尝试加载benchmark特定的operator_an（如果存在）
            # try:
            #     # 查找benchmark映射信息
            #     benchmark_info = self.benchmark_mapping.get(benchmark_name)
            #     if benchmark_info:
            #         handler_dir = benchmark_info['handler_dir']
            #         # 将handler_dir转换为Python模块路径
            #         an_module_path = handler_dir.replace('/', '.') + '.operator_an'
            #     else:
            #         # 回退到默认命名规则
            #         if benchmark_name.startswith("high_level_math"):
            #             an_module_path = "ScoreFlow.scripts.high_level_math.operator_an"
            #         else:
            #             an_module_path = f"ScoreFlow.scripts.{benchmark_name}.operator_an"
                
            #     operator_an_module = importlib.import_module(an_module_path)
                
            #     # 注入所有公共成员到执行环境
            #     for attr_name in dir(operator_an_module):
            #         if not attr_name.startswith('_'):
            #             exec_globals[attr_name] = getattr(operator_an_module, attr_name)
                
            #     logger.debug(f"Injected {an_module_path} contents into execution environment")
            # except ModuleNotFoundError:
            # 如果没有特定的operator_an，尝试使用common的
            try:
                common_an_module = importlib.import_module("ScoreFlow.scripts.common.operator_an")
                debug_print("/n 🚀🚀🚀加载common operator_an 成功")
                for attr_name in dir(common_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(common_an_module, attr_name)
                debug_print("/n 🚀加载common operator_an的模块成功")
                logger.debug("Using common operator_an module")
            except ModuleNotFoundError:
                logger.debug("No operator_an module found, proceeding without it")
                debug_print("/n 🚀 未找到可选的 'operator_an.py' 模块，跳过注入。")

            # 5. 执行脚本获取Workflow类
            exec(full_script_code, exec_globals, execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError(f"No 'Workflow' class found in the executed script for {workflow_id}")
            
            # 6. 准备LLM配置
            debug_print(f"\n 🚀 我们输出llm_config = \n{self.llm_config}\n")
            provider = self.llm_config.get('provider', 'openai')
            debug_print(f"\n 🚀 我们输出从llm_config得到的provider = \n{provider}\n")
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
            # 使用handler的get_prompt_text方法获取格式化的问题
            problem_text = handler.get_prompt_text([test_case_index])
            
            logger.debug(f"Problem text for {workflow_id}: {problem_text[:200]}...")
            
            # 8. 实例化并执行工作流
            workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            # 关联cost_manager用于token追踪
            if hasattr(workflow_instance, 'llm') and workflow_instance.llm:
                workflow_instance.llm.cost_manager = workflow_context.cost_manager
            
            debug_log("workflow", {
                "event": "workflow_instance_created",
                "workflow_id": workflow_id,
                "class_type": str(type(workflow_instance))
            })
            
            # 9. 根据call_signature执行（处理超时参数）
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
                execution_result = await asyncio.wait_for(
                    workflow_instance(),
                    timeout=self.timeout + 10
                )
            
            debug_log("workflow", {
                "event": "metagpt_execution_completed",
                "workflow_id": workflow_id,
                "result_length": len(str(execution_result)),
                "result_type": str(type(execution_result)),
                "execution_time": time.time() - exec_start
            })
            
            # 获取token统计
            token_stats = self.token_tracker.get_workflow_stats(workflow_id)
            self.token_tracker.print_workflow_stats(workflow_id)  # 打印统计
            self.token_tracker.update_total_stats(workflow_id)  # 更新总体统计
            
            logger.info(f"MetaGPT workflow {workflow_id} executed successfully")
            return str(execution_result), token_stats
            
        except asyncio.TimeoutError:
            logger.error(f"MetaGPT workflow execution timed out for {benchmark_name}")
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "error_type": "TimeoutError",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "execution_time": time.time() - exec_start
            })
            # 即使超时也尝试获取token统计
            token_stats = self.token_tracker.get_workflow_stats(workflow_id) if 'workflow_id' in locals() else {}
            return "Error: Workflow execution timed out", token_stats
            
        except Exception as e:
            error_msg = f"MetaGPT workflow execution failed for {benchmark_name}: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_time": time.time() - exec_start
            })
            
            # 即使失败也尝试获取token统计
            token_stats = self.token_tracker.get_workflow_stats(workflow_id) if 'workflow_id' in locals() else {}
            return f"Error: {str(e)}", token_stats
    
    async def compute_score_for_testcase(self, workflow_code: str, benchmark_name: str, 
                                        test_case_index: int, dataset_path: str) -> float:
        """
        在单个test case上计算分数
        使用MetaGPT执行并使用handler的judge方法验证
        """
        testcase_start = time.time()
        
        debug_log("task", {
            "event": "testcase_start",
            "benchmark_name": benchmark_name,
            "test_case_index": test_case_index,
            "dataset_path": dataset_path,
            "workflow_code_length": len(workflow_code),
            "execution_mode": "metagpt"
        })
        
        try:
            # 加载handler
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                debug_log("task", {
                    "event": "testcase_failed",
                    "reason": "handler_not_found",
                    "benchmark_name": benchmark_name
                }, testcase_start)
                return 0.0
            
            # 获取验证数据
            verification_data = handler.get_verification_data(test_case_index)
            
            # 添加清晰的验证日志，确保test case索引匹配
            print(f"\n🔍 开始处理Test Case {test_case_index}:")
            silent_print(f"   - Benchmark: {benchmark_name}")
            print(f"   - Dataset: {dataset_path}")
            if 'question' in verification_data:
                print(f"   - 问题: {verification_data['question'][:100]}...")
            # if 'index' in verification_data:
            #     print(f"   - 数据集中的index: {verification_data['index']}")
            #     if verification_data['index'] != test_case_index:
            #         print(f"   ⚠️ 警告: 传入索引({test_case_index}) != 数据索引({verification_data['index']})")
            # print(f"")
            
            debug_log("task", {
                "event": "verification_data_loaded",
                "test_case_index": test_case_index,
                "data_index": verification_data.get('index', 'unknown'),
                "has_answer": "answer" in verification_data or "all_answers" in verification_data
            })
            
            # 使用MetaGPT执行workflow（传递workflow_dir用于保存调试文件）
            exec_start = time.time()
            
            # 获取当前的workflow目录（如果在WorkflowExecutionManager上下文中）
            workflow_dir = getattr(self, '_current_workflow_dir', None)
            
            # 执行workflow并获取结果和token统计
            result, token_stats = await self.execute_workflow_metagpt(
                workflow_code, benchmark_name, test_case_index, dataset_path, workflow_dir
            )
            
            debug_log("task", {
                "event": "workflow_executed_via_metagpt",
                "execution_time": time.time() - exec_start,
                "result_length": len(str(result)),
                "result_preview": str(result)[:500] if len(str(result)) > 500 else str(result),
                "token_stats": token_stats
            })
            
            logger.debug(f"MetaGPT workflow result: {str(result)[:100]}...")
            
            # 使用handler的judge方法验证结果
            verify_start = time.time()
            
            print(f"\n🔍 开始验证结果...")
            print(f"   执行结果长度: {len(str(result))} 字符")
            
            # 检查judge是否是协程函数
            import inspect
            if inspect.iscoroutinefunction(handler.judge):
                is_correct = await handler.judge(result, verification_data)
            else:
                is_correct = handler.judge(result, verification_data)
            
            # 输出判断结果
            if is_correct:
                print(f"✅ 判断结果: CORRECT")
            else:
                print(f"❌ 判断结果: INCORRECT")
            
            # 如果有答案，显示期望答案和实际结果
            # if "answer" in verification_data:
            #     print(f"   期望答案: {verification_data['answer']}")
            #     # 尝试从result中提取数字答案
            #     import re
            #     numbers = re.findall(r'\d+', str(result))
            #     if numbers:
            #         print(f"   提取的数字: {numbers[-1]}")  # 通常最后一个数字是答案
            print(f"🐟🐟🐟🐟🐟: workflow的输出是:\n{result}")
            print("="*80)
            print(f"😋😋😋😋😋: 真正的答案是:\n{verification_data}")

            base_score = 1.0 if is_correct else 0.0
            
            # 应用token费用惩罚
            final_score, penalty_details = self.calculate_token_cost_penalty(base_score, token_stats)
            
            # 打印惩罚详情
            if penalty_details and self.token_penalty_config.get('enabled', False):
                print(f"\n💰 Token费用惩罚计算:")
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
                "is_correct": is_correct,
                "token_stats": token_stats,
                "penalty_details": penalty_details,
                "verification_time": time.time() - verify_start,
                "benchmark_name": benchmark_name,
                "execution_mode": "metagpt"
            })
            
            logger.info(f"Benchmark {benchmark_name} test case {test_case_index} score: {final_score} (base: {base_score})")
            
            debug_log("task", {
                "event": "testcase_completed",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "base_score": base_score,
                "final_score": final_score,
                "total_time": time.time() - testcase_start,
                "execution_mode": "metagpt"
            })
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error computing score for {benchmark_name} index {test_case_index}: {e}")
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "compute_score_for_testcase",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_mode": "metagpt"
            }, testcase_start)
            
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, benchmark_name: str, 
                                  test_cases: List[int], dataset_path: str) -> float:
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
            "benchmark_name": benchmark_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "dataset_path": dataset_path,
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
        
        async def limited_compute(test_case_index, index):
            async with semaphore:
                try:
                    score = await self.compute_score_for_testcase(
                        workflow_code, benchmark_name, test_case_index, dataset_path
                    )
                    await update_progress()
                    return (index, score, None)
                except Exception as e:
                    logger.error(f"Test case {test_case_index} failed: {e}")
                    await update_progress()
                    return (index, 0.0, e)
        
        # 使用asyncio.create_task创建更高效的任务
        tasks = [
            asyncio.create_task(limited_compute(test_case_index, i))
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
                logger.error(f"Task {index} failed with exception: {error}")
                valid_scores.append(0.0)
                failed_count += 1
                debug_log("error", {
                    "function": "compute_score_for_testcase",
                    "test_case_index": test_cases[index],
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
        
        logger.info(f"Average score for {benchmark_name}: {avg_score:.3f} "
                   f"({len(valid_scores)} test cases, {success_rate*100:.1f}% success rate)")
        
        debug_log("task", {
            "event": "batch_compute_completed",
            "benchmark_name": benchmark_name,
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

def get_calculator():
    """获取全局计算器实例"""
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = ScoreFlowRewardCalculator()
    return _global_calculator


def compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    计算单个solution的reward分数（符合VERL接口规范）
    
    Args:
        data_source: benchmark名称，如 'gsm8k', 'high_level_math_aime2024'
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息（通常是"default"）
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
        import threading
        
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
    异步计算单个solution的reward分数（内部实现）
    """
    compute_start = time.time()
    
    # 记录任务开始
    debug_log("task", {
        "event": "compute_score_start",
        "data_source": data_source,
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
        test_cases = extra_info.get('test_cases', [])
        data_path = extra_info.get('data_path', '')
        
        # 处理numpy array的情况
        if hasattr(test_cases, 'tolist'):
            test_cases = test_cases.tolist()
        
        # 解析benchmark名称（处理类似 'high_level_math_aime2024' 的情况）
        # 直接使用data_source作为benchmark名称，因为benchmark_mapping中已有完整名称
        benchmark_name = data_source
        
        if not data_path:
            logger.error("No data_path found in extra_info")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_data_path",
                "extra_info": extra_info
            }, compute_start)
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
        silent_print(f"Data path: {data_path}")

        # 记录任务详情
        debug_log("task", {
            "event": "task_details",
            "data_source": data_source,
            "benchmark_name": benchmark_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "data_path": data_path,
            "workflow_code_length": len(workflow_code)
        })
        
        # 创建WorkflowExecutionManager并使用All-Reduce模式
        manager = WorkflowExecutionManager(
            calculator.workspace_path,
            data_source,
            test_cases
        )
        
        # 保存workflow代码和元数据
        manager.save_workflow_code(workflow_code)
        manager.save_metadata(extra_info)
        
        # 使用上下文管理器确保文件生命周期正确，并执行All-Reduce模式
        with manager:  # 自动管理文件打开和关闭
            reward = await manager.execute_all_test_cases_parallel_safe(
                calculator, workflow_code, data_path
            )
        # 文件在此处自动安全关闭
        
        logger.info(f"Computed average reward: {reward:.3f}")
        
        # 记录最终结果
        debug_log("task", {
            "event": "compute_score_completed",
            "data_source": data_source,
            "benchmark_name": benchmark_name,
            "average_reward": reward,
            "num_test_cases": len(test_cases)
        }, compute_start)
        
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
                "data_source": data_source,
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
        solution = await self.custom(instruction="Solve the math problem step by step.")
        return solution
</code>
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