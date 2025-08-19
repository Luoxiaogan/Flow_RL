"""
InternBootcamp Reward Calculator
Maximally reuses ScoreFlow's code with minimal modifications
"""
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

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
print("  InternBootcamp的localhost请求将绕过所有代理")

# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CONFIG_FILE = PROJECT_ROOT / "New_evaluation_and_RL" / "config.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        # 获取project_root，用于构建默认路径
        project_root = config.get('project_root', 'D:/temp/Flow_RL')
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    project_root = 'D:/temp/Flow_RL'

# 转换为Path对象
project_root_path = Path(project_root)

# 从config.yaml获取InternBootcamp相关路径（如果有配置的话）
# InternBootcamp特定配置文件
IB_CONFIG_FILE = PROJECT_ROOT / "internbootcamp_config.yaml"
if IB_CONFIG_FILE.exists():
    with open(IB_CONFIG_FILE, 'r', encoding='utf-8') as f:
        ib_config = yaml.safe_load(f)
        # 可以从这里读取InternBootcamp特定配置
        internbootcamp_config = ib_config.get('internbootcamp', {})
else:
    internbootcamp_config = {}

# 设置InternBootcamp相关路径
INTERNBOOTCAMP_ROOT = project_root_path / "InternBootcamp"
INTERNBOOTCAMP_WORKSPACE = PROJECT_ROOT / "internbootcamp_workspace"

# 创建必要目录
INTERNBOOTCAMP_WORKSPACE.mkdir(parents=True, exist_ok=True)

# 添加必要路径
sys.path.insert(0, str(project_root_path / "New_evaluation_and_RL"))
sys.path.insert(0, str(project_root_path))  # 添加根路径用于ScoreFlow导入

# 如果有InternBootcamp目录，添加到路径
if INTERNBOOTCAMP_ROOT.exists():
    sys.path.insert(0, str(INTERNBOOTCAMP_ROOT))

print(f"✓ InternBootcamp工作空间: {INTERNBOOTCAMP_WORKSPACE}")
print("-"*60)

# Import ScoreFlow's reward calculator
from reward_server.scoreflow_reward_utils import (
    ScoreFlowRewardCalculator,
    compute_score as scoreflow_compute_score,
    _compute_score_async as scoreflow_compute_async
)

# Import the adapter
from internbootcamp_adapter import InternBootcampAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InternBootcampRewardCalculator(ScoreFlowRewardCalculator):
    """
    InternBootcamp-specific reward calculator
    Inherits from ScoreFlow and only overrides necessary methods
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize InternBootcamp reward calculator
        
        Args:
            config_path: Path to configuration file
        """
        # Load InternBootcamp config if available
        if config_path is None:
            config_path = PROJECT_ROOT / "New_evaluation_and_RL" / "internbootcamp_config.yaml"
        
        # Initialize parent class
        super().__init__(config_path)
        
        # Load InternBootcamp-specific configuration
        self._load_internbootcamp_config(config_path)
        
        logger.info("InternBootcampRewardCalculator initialized")
    
    def _load_internbootcamp_config(self, config_path):
        """Load InternBootcamp-specific configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                ib_config = yaml.safe_load(f)
                
                # Update workspace path for InternBootcamp
                reward_config = ib_config.get('reward_server', {})
                if 'workspace' in reward_config:
                    workspace = reward_config['workspace']
                    if not Path(workspace).is_absolute():
                        # Convert relative path to absolute
                        project_root = ib_config.get('project_root', str(PROJECT_ROOT))
                        self.workspace_path = Path(project_root) / workspace
                    else:
                        self.workspace_path = Path(workspace)
                    
                    # Create workspace directory if it doesn't exist
                    self.workspace_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"InternBootcamp workspace: {self.workspace_path}")
                
                # Update LLM config if provided
                if 'llm_config' in ib_config:
                    self.llm_config.update(ib_config['llm_config'])
                    logger.info("Updated LLM config from InternBootcamp config")
    
    def _load_benchmark_handler(self, benchmark_name: str, dataset_path: str, extra_info: Dict = None):
        """
        Override to support InternBootcamp tasks
        
        Args:
            benchmark_name: Benchmark or task name
            dataset_path: Dataset path (not used for InternBootcamp)
            extra_info: Extra information containing test_cases for InternBootcamp
            
        Returns:
            Handler instance (InternBootcampAdapter or BenchmarkHandler)
        """
        # Check if this is an InternBootcamp task
        if benchmark_name.startswith('internbootcamp_'):
            # Extract task name
            task_name = benchmark_name.replace('internbootcamp_', '')
            
            # Get test cases from extra_info
            test_cases = extra_info.get('test_cases', []) if extra_info else []
            
            # Create and return InternBootcamp adapter
            try:
                adapter = InternBootcampAdapter(
                    task_name=task_name,
                    dataset_path="",  # InternBootcamp doesn't use dataset_path
                    config=self.llm_config,
                    test_cases=test_cases  # Pass test cases directly
                )
                
                # Cache the adapter
                cache_key = f"{benchmark_name}_{task_name}"
                self._handler_cache[cache_key] = adapter
                
                logger.info(f"Loaded InternBootcampAdapter for task: {task_name}")
                return adapter
                
            except Exception as e:
                logger.error(f"Failed to load InternBootcampAdapter for {task_name}: {e}")
                import traceback
                traceback.print_exc()
                return None
        else:
            # Not an InternBootcamp task, use parent class method
            return super()._load_benchmark_handler(benchmark_name, dataset_path)


# Global calculator instance
_global_calculator = None


def get_calculator(config_path: str = None):
    """
    Get global calculator instance
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        InternBootcampRewardCalculator instance
    """
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = InternBootcampRewardCalculator(config_path)
    return _global_calculator


def compute_score(data_source: str, solution_str: str, 
                 ground_truth: str, extra_info: Dict) -> float:
    """
    Compute score (compatible with VERL interface)
    
    InternBootcamp-specific implementation that handles test cases from extra_info
    
    Args:
        data_source: Data source name (e.g., 'internbootcamp' or task name)
        solution_str: Solution string containing workflow code
        ground_truth: Ground truth (usually 'default')
        extra_info: Extra information including task_name, test_cases, etc.
        
    Returns:
        Score between 0.0 and 1.0
    """
    # If data_source is 'internbootcamp' and task_name is in extra_info
    if data_source == 'internbootcamp' and 'task_name' in extra_info:
        # Add prefix for proper routing
        data_source = f"internbootcamp_{extra_info['task_name']}"
    elif not data_source.startswith('internbootcamp_') and 'task_name' in extra_info:
        # Ensure InternBootcamp tasks have the proper prefix
        task_name = extra_info.get('task_name', '')
        if task_name:  # Only add prefix if task_name exists
            data_source = f"internbootcamp_{task_name}"
    
    # Log the request
    logger.info(f"Computing score for: {data_source}")
    logger.debug(f"Extra info: {extra_info}")
    
    # Direct async computation for InternBootcamp
    import asyncio
    
    try:
        # Check if already in event loop
        loop = asyncio.get_running_loop()
        
        # Already in event loop, use thread pool
        import concurrent.futures
        
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                # Direct computation
                result = new_loop.run_until_complete(
                    _compute_score_async_internbootcamp(data_source, solution_str, ground_truth, extra_info)
                )
                return result
            finally:
                new_loop.close()
                asyncio.set_event_loop(None)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=600)
            
    except RuntimeError:
        # Not in event loop, can use asyncio.run
        return asyncio.run(
            _compute_score_async_internbootcamp(data_source, solution_str, ground_truth, extra_info)
        )


async def _compute_score_async_internbootcamp(data_source: str, solution_str: str, 
                                              ground_truth: str, extra_info: Dict) -> float:
    """
    InternBootcamp-specific async score computation
    
    Handles InternBootcamp data format which doesn't use data_path
    """
    try:
        calculator = get_calculator()
        
        # Extract task name from data_source
        if data_source.startswith('internbootcamp_'):
            task_name = data_source.replace('internbootcamp_', '')
        else:
            task_name = extra_info.get('task_name', '')
        
        # Get test cases from extra_info
        test_cases = extra_info.get('test_cases', [])
        
        if not task_name:
            logger.error(f"No task name found for InternBootcamp")
            return 0.0
        
        if not test_cases:
            logger.error(f"No test cases found for InternBootcamp task {task_name}")
            return 0.0
        
        logger.info(f"Computing InternBootcamp score for task: {task_name} with {len(test_cases)} test cases")
        
        # For InternBootcamp, add a dummy data_path to satisfy ScoreFlow
        modified_extra_info = extra_info.copy()
        if 'data_path' not in modified_extra_info:
            # Use a dummy path that ScoreFlow will accept
            modified_extra_info['data_path'] = f"internbootcamp/{task_name}"
        
        # Load handler with test cases
        handler = calculator._load_benchmark_handler(
            f"internbootcamp_{task_name}", 
            modified_extra_info['data_path'],  # Pass the dummy data_path
            modified_extra_info  # Pass extra_info to get test_cases
        )
        
        if not handler:
            logger.error(f"Failed to load handler for {task_name}")
            return 0.0
        
        # Import ScoreFlow's async computation
        from reward_server.scoreflow_reward_utils import _compute_score_async
        
        # Temporarily set handler in calculator's cache
        cache_key = f"internbootcamp_{task_name}_{modified_extra_info['data_path']}"
        calculator._handler_cache[cache_key] = handler
        
        # Use ScoreFlow's computation with our handler
        import reward_server.scoreflow_reward_utils as utils_module
        original_calculator = utils_module._global_calculator
        utils_module._global_calculator = calculator
        
        try:
            score = await _compute_score_async(
                f"internbootcamp_{task_name}",
                solution_str,
                ground_truth,
                modified_extra_info
            )
            return score
        finally:
            # Restore original calculator
            utils_module._global_calculator = original_calculator
            
    except Exception as e:
        logger.error(f"Error in InternBootcamp score computation: {e}")
        import traceback
        traceback.print_exc()
        return 0.0


# Test function
if __name__ == "__main__":
    # Test the InternBootcamp reward calculator
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
        'task_name': 'sudoku_4x4_easy',
        'test_cases': [0],
        'data_path': '',  # Not used for InternBootcamp
    }
    
    # Test score computation
    score = compute_score(
        'internbootcamp',
        test_solution,
        'default',
        test_extra_info
    )
    
    print(f"Test score: {score}")