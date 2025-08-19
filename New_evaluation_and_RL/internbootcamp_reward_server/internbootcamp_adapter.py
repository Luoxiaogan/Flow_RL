"""
InternBootcamp to ScoreFlow Adapter
Adapts bootcamp classes to BenchmarkHandler interface for seamless integration
"""
import os
import sys
import yaml
import json
import importlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

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
print("  InternBootcamp Adapter的localhost请求将绕过所有代理")

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

# Add InternBootcamp path (基于project_root构建)
INTERNBOOTCAMP_ROOT = project_root_path / "InternBootcamp"
if INTERNBOOTCAMP_ROOT.exists():
    sys.path.insert(0, str(INTERNBOOTCAMP_ROOT))
    print(f"✓ 已添加InternBootcamp路径: {INTERNBOOTCAMP_ROOT}")

# Add path for internbootcamp_utils (prefer local copy)
if (CURRENT_DIR / "internbootcamp_utils.py").exists():
    # Use local copy if available
    sys.path.insert(0, str(CURRENT_DIR))
    print(f"✓ 使用本地internbootcamp_utils.py")
else:
    # Fall back to original location
    TEST_FILE_PATH = project_root_path / "Test_FILE" / "verl_internbootcamp"
    if TEST_FILE_PATH.exists():
        sys.path.insert(0, str(TEST_FILE_PATH))
        print(f"✓ 使用原始位置的internbootcamp_utils.py: {TEST_FILE_PATH}")

# Add ScoreFlow path (基于project_root构建)
sys.path.insert(0, str(project_root_path))
print(f"✓ 已添加ScoreFlow根路径: {project_root_path}")

# Import base handler
from ScoreFlow.scripts.base_handler import BenchmarkHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InternBootcampAdapter(BenchmarkHandler):
    """
    Adapter class that bridges InternBootcamp bootcamp classes with ScoreFlow's BenchmarkHandler
    Provides unified interface for reward calculation
    """
    
    def __init__(self, task_name: str, dataset_path: str = None, config=None, test_cases=None):
        """
        Initialize the adapter
        
        Args:
            task_name: InternBootcamp task name (e.g., 'aalmostarithmeticalprogression')
            dataset_path: Not used for InternBootcamp (kept for interface compatibility)
            config: LLM configuration
            test_cases: List of test case strings from extra_info
        """
        # For InternBootcamp, we don't need dataset_path - set it to empty string
        super().__init__("", config)  # Pass empty string instead of None
        
        self.task_name = task_name
        self.bootcamp_class = None
        self.test_cases = test_cases or []  # Store test cases directly
        
        # Load bootcamp class directly
        self._load_bootcamp_class()
        
        logger.info(f"InternBootcampAdapter initialized for task: {task_name} with {len(self.test_cases)} test cases")
    
    def _load_bootcamp_class(self):
        """Load the bootcamp class for the task"""
        try:
            # 动态导入bootcamp模块
            module_path = f"internbootcamp.bootcamp.{self.task_name}.{self.task_name}"
            module = importlib.import_module(module_path)
            
            # 获取bootcamp类
            class_name = f"{self.task_name.capitalize()}bootcamp"
            self.bootcamp_class = getattr(module, class_name)
            
            logger.info(f"Successfully loaded bootcamp class: {class_name}")
            
        except Exception as e:
            logger.error(f"Failed to load bootcamp class for {self.task_name}: {e}")
            raise
    
    def get_prompt_text(self, data_indices: List[int]) -> str:
        """
        Get prompt text for the given indices
        
        Args:
            data_indices: List of test case indices
            
        Returns:
            Formatted prompt text
        """
        if not data_indices or not self.test_cases:
            return f"Task: {self.task_name}"
        
        try:
            # Get the first test case (or use first index)
            idx = data_indices[0] if data_indices else 0
            if idx >= len(self.test_cases):
                idx = 0
            
            test_case = self.test_cases[idx]
            
            # Parse test case if it's a string
            if isinstance(test_case, str):
                try:
                    # Try JSON first
                    test_case = json.loads(test_case.replace("'", '"'))
                except:
                    # Try eval as fallback
                    try:
                        test_case = eval(test_case)
                    except:
                        pass  # Keep as string
            
            # Use bootcamp's prompt_func if available
            if self.bootcamp_class and hasattr(self.bootcamp_class, 'prompt_func'):
                return self.bootcamp_class.prompt_func(test_case)
            else:
                # Fallback to simple format
                return f"Task: {self.task_name}\nTest Case: {test_case}"
                    
        except Exception as e:
            logger.error(f"Failed to get prompt text for {self.task_name}: {e}")
            return f"Task: {self.task_name}"
    
    def judge(self, result: str, verification_data: Dict) -> bool:
        """
        Judge if the result is correct using bootcamp's verify_score
        
        Args:
            result: Model output/result to verify
            verification_data: Data containing the test case and expected answer
            
        Returns:
            True if correct, False otherwise
        """
        try:
            # Check if bootcamp class has verify_score method
            if not hasattr(self.bootcamp_class, 'verify_score'):
                logger.warning(f"No verify_score method found for {self.task_name}")
                return False
            
            # Call verify_score with appropriate parameters
            score = self.bootcamp_class.verify_score(
                model_output=result,
                identity=verification_data,
                format_score=0.1,  # Default format score weight
                short_penalty=False,  # Don't penalize short answers
                format_penalty=False  # Don't penalize format issues
            )
            
            # Convert score to boolean (threshold at 0.5)
            is_correct = score > 0.5
            
            logger.debug(f"Verification score for {self.task_name}: {score:.2f} -> {is_correct}")
            
            return is_correct
            
        except Exception as e:
            logger.error(f"Failed to verify result for {self.task_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_verification_data(self, index: int) -> Dict:
        """
        Get verification data for a specific test case
        
        Args:
            index: Test case index
            
        Returns:
            Dictionary containing test case data
        """
        try:
            # Use provided test cases
            if self.test_cases and index < len(self.test_cases):
                test_case = self.test_cases[index]
                
                # Parse test case string if needed
                if isinstance(test_case, str):
                    try:
                        # Try JSON first
                        test_case = json.loads(test_case.replace("'", '"'))
                    except:
                        # Try eval as fallback
                        try:
                            test_case = eval(test_case)
                        except:
                            pass  # Keep as string
                
                # Return the test case as verification data
                return test_case if isinstance(test_case, dict) else {'test_case': test_case}
            else:
                logger.warning(f"No test case at index {index} for {self.task_name}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get verification data for {self.task_name}[{index}]: {e}")
            return {}
    
    def build_executable_script(self, workflow_code: str, timeout: int = 180) -> Dict[str, str]:
        """
        Build executable script for MetaGPT execution
        Reuses parent class implementation
        
        Args:
            workflow_code: The workflow code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary with script parts
        """
        # Use parent class implementation
        return super().build_executable_script(workflow_code, timeout)
    
    def get_task_description(self) -> str:
        """
        Get task description from InternBootcamp
        
        Returns:
            Task description string
        """
        try:
            description = self.manager.get_task_description(self.task_name)
            return description
        except Exception as e:
            logger.warning(f"Failed to get task description for {self.task_name}: {e}")
            return f"InternBootcamp task: {self.task_name}"
    
    def __repr__(self):
        """String representation"""
        return f"InternBootcampAdapter(task_name='{self.task_name}')"