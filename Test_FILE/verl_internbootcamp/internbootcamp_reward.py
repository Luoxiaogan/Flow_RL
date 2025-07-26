"""
InternBootcamp Reward Function for VERL
计算LLM生成的workflow在InternBootcamp任务上的表现
"""
import os
import sys
import re
import json
import asyncio
import logging
import importlib
import tempfile
import traceback
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# 添加必要路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "InternBootcamp"))

# 添加MetaGPT路径（根据CLAUDE.md，使用本地安装）
METAGPT_PATH = PROJECT_ROOT / "ScoreFlow" / "metagpt_local"
if METAGPT_PATH.exists():
    sys.path.insert(0, str(METAGPT_PATH))

# 导入必要模块
try:
    from metagpt.provider.llm_provider_registry import create_llm_instance, LLMType
    from metagpt.configs.llm_config import LLMConfig
except ImportError as e:
    # 如果MetaGPT导入失败，尝试其他方式
    print(f"Warning: MetaGPT import failed: {e}")
    print("Trying alternative import...")
    # 可以在这里添加备选导入方案

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InternBootcampRewardCalculator:
    """
    InternBootcamp任务的reward计算器
    """
    
    def __init__(self, config_path: str = None):
        """初始化reward计算器"""
        # 加载配置
        if config_path is None:
            config_path = CURRENT_DIR / "config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.llm_config = self.config['llm_config']['upstream']
        self.reward_config = self.config.get('reward_config', {})
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 30)
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # bootcamp类缓存
        self._bootcamp_cache = {}
        
        # 临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="internbootcamp_reward_")
        logger.info(f"Created temp directory: {self.temp_dir}")
    
    def __del__(self):
        """清理临时目录"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def extract_workflow_from_response(self, response: str) -> Optional[str]:
        """
        从LLM response中提取workflow代码
        查找<graph>标签内的内容
        """
        if not response:
            return None
        
        # 尝试提取<graph>标签内的代码
        graph_pattern = r'<graph>(.*?)</graph>'
        matches = re.findall(graph_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow code: {len(workflow_code)} chars")
            return workflow_code
        
        # 如果没有找到graph标签，尝试查找class Workflow定义
        class_pattern = r'(class\s+(?:InternBootcampWorkflow|Workflow).*?)(?=class\s+\w+|$)'
        matches = re.findall(class_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow class: {len(workflow_code)} chars")
            return workflow_code
        
        logger.warning("No workflow code found in response")
        return None
    
    def build_executable_code(self, workflow_code: str, task_name: str) -> str:
        """
        构建完整的可执行代码
        添加必要的imports和包装
        """
        # 导入statements - 基于conditions.py的PYTHON_START_PREDEFINED
        imports = """
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.llm import LLM
import sys
import os

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import operators
from ScoreFlow.scripts.internbootcamp import operator
"""
        
        # 替换类名（如果需要）
        workflow_code = workflow_code.replace("InternBootcampWorkflow", "Workflow")
        
        # 确保有__call__方法
        if "async def __call__" not in workflow_code:
            # 添加__call__方法（如果没有）
            workflow_code += """
    
    async def __call__(self):
        TIMEOUT = 120
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
"""
        
        # 组合完整代码
        full_code = f"{imports}\n\n{workflow_code}"
        
        return full_code
    
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
            logger.error(f"Failed to load bootcamp class for {task_name}: {e}")
            return None
    
    def convert_config_for_metagpt(self, config_dict: Dict) -> LLMConfig:
        """将配置转换为MetaGPT的LLMConfig格式"""
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
            base_url=config_dict.get('base_url'),
            temperature=config_dict.get('temperature', 0.7)
        )
    
    async def execute_workflow_on_testcase(self, workflow_code: str, task_name: str, 
                                          test_case: Dict, llm_config: Dict) -> float:
        """
        在单个test case上执行workflow并返回分数
        """
        try:
            # 加载bootcamp类
            bootcamp_class = self._load_bootcamp_class(task_name)
            if not bootcamp_class:
                return 0.0
            
            # 获取test case数据
            case_data = test_case.get('case', test_case)
            
            # 使用bootcamp的prompt_func生成问题文本
            if hasattr(bootcamp_class, 'prompt_func'):
                problem_text = bootcamp_class.prompt_func(case_data)
            else:
                # 如果没有prompt_func，直接使用prompt字段
                problem_text = test_case.get('prompt', str(case_data))
            
            logger.debug(f"Problem text: {problem_text[:100]}...")
            
            # 构建完整代码
            full_code = self.build_executable_code(workflow_code, task_name)
            
            # 创建临时文件
            temp_file = os.path.join(self.temp_dir, f"workflow_{task_name}_{id(test_case)}.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(full_code)
            
            # 准备执行环境
            exec_namespace = {'__file__': temp_file}
            
            # 执行代码定义
            exec(full_code, exec_namespace)
            
            # 获取Workflow类
            WorkflowClass = exec_namespace.get('Workflow')
            if not WorkflowClass:
                logger.error("Workflow class not found in executed code")
                return 0.0
            
            # 创建MetaGPT配置
            metagpt_config = self.convert_config_for_metagpt(llm_config)
            
            # 实例化workflow
            workflow = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            # 执行workflow
            result = await asyncio.wait_for(workflow(), timeout=self.timeout)
            
            logger.debug(f"Workflow result: {str(result)[:100]}...")
            
            # 使用bootcamp的verify_score验证结果
            score = bootcamp_class.verify_score(
                model_output=str(result),
                identity=case_data,
                format_score=0.1,
                short_penalty=False,
                format_penalty=False
            )
            
            logger.info(f"Task {task_name} test case score: {score}")
            return float(score)
            
        except asyncio.TimeoutError:
            logger.error(f"Workflow execution timeout for {task_name}")
            return 0.0
        except Exception as e:
            logger.error(f"Error executing workflow for {task_name}: {e}")
            logger.debug(traceback.format_exc())
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, task_name: str, 
                                  test_cases: List[Dict]) -> float:
        """
        异步计算workflow在所有test cases上的平均reward
        """
        if not test_cases:
            return 0.0
        
        # 创建任务列表
        tasks = []
        for test_case in test_cases:
            task = self.execute_workflow_on_testcase(
                workflow_code, task_name, test_case, self.llm_config
            )
            tasks.append(task)
        
        # 并发执行（限制并发数）
        scores = []
        for i in range(0, len(tasks), self.max_concurrent):
            batch = tasks[i:i + self.max_concurrent]
            batch_scores = await asyncio.gather(*batch, return_exceptions=True)
            
            # 处理结果
            for score in batch_scores:
                if isinstance(score, Exception):
                    logger.error(f"Task failed with exception: {score}")
                    scores.append(0.0)
                else:
                    scores.append(score)
        
        # 计算平均分
        avg_score = sum(scores) / len(scores) if scores else 0.0
        logger.info(f"Average score for {task_name}: {avg_score:.3f} ({len(scores)} test cases)")
        
        return avg_score


def compute_score(response: str, data: Dict) -> float:
    """
    计算单个response的reward分数
    
    Args:
        response: LLM生成的包含workflow的response
        data: 包含task信息的数据行（来自parquet文件）
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    try:
        # 创建计算器实例
        calculator = InternBootcampRewardCalculator()
        
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(response)
        if not workflow_code:
            logger.error("No workflow code found in response")
            return 0.0
        
        # 解析reward_model字段
        reward_model = json.loads(data['reward_model'])
        task_name = reward_model['task_name']
        test_cases = reward_model['test_cases']
        
        # 解析test_cases（它们可能是字符串格式）
        parsed_test_cases = []
        for tc in test_cases:
            if isinstance(tc, str):
                try:
                    parsed_tc = eval(tc)  # 安全性考虑：实际使用中应该用ast.literal_eval
                    parsed_test_cases.append({'case': parsed_tc})
                except:
                    parsed_test_cases.append({'case': tc})
            else:
                parsed_test_cases.append(tc)
        
        logger.info(f"Computing reward for task: {task_name} with {len(parsed_test_cases)} test cases")
        
        # 异步计算reward
        reward = asyncio.run(calculator.compute_reward_async(
            workflow_code, task_name, parsed_test_cases
        ))
        
        return reward
        
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        return 0.0


async def batch_compute_score(responses: List[str], data_list: List[Dict]) -> List[float]:
    """
    批量计算多个response的reward分数
    
    Args:
        responses: LLM生成的response列表
        data_list: 对应的数据行列表
    
    Returns:
        List[float]: reward分数列表
    """
    if len(responses) != len(data_list):
        raise ValueError("responses and data_list must have the same length")
    
    # 创建计算器实例
    calculator = InternBootcampRewardCalculator()
    
    # 创建所有任务
    all_tasks = []
    for response, data in zip(responses, data_list):
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(response)
        if not workflow_code:
            all_tasks.append(None)  # 标记为失败
            continue
        
        # 解析数据
        try:
            reward_model = json.loads(data['reward_model'])
            task_name = reward_model['task_name']
            test_cases = reward_model['test_cases']
            
            # 解析test_cases
            parsed_test_cases = []
            for tc in test_cases:
                if isinstance(tc, str):
                    try:
                        parsed_tc = eval(tc)
                        parsed_test_cases.append({'case': parsed_tc})
                    except:
                        parsed_test_cases.append({'case': tc})
                else:
                    parsed_test_cases.append(tc)
            
            # 创建计算任务
            task = calculator.compute_reward_async(workflow_code, task_name, parsed_test_cases)
            all_tasks.append(task)
            
        except Exception as e:
            logger.error(f"Error parsing data: {e}")
            all_tasks.append(None)
    
    # 执行所有任务
    results = []
    for i, task in enumerate(all_tasks):
        if task is None:
            results.append(0.0)
        else:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"Task {i} failed: {e}")
                results.append(0.0)
    
    return results


if __name__ == "__main__":
    # 简单测试
    test_response = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = create(config)
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
</graph>
"""
    
    test_data = {
        'reward_model': json.dumps({
            'task_name': 'adidyoumean',
            'test_cases': ["{'input': 'hello'}"]
        })
    }
    
    score = compute_score(test_response, test_data)
    print(f"Test score: {score}")