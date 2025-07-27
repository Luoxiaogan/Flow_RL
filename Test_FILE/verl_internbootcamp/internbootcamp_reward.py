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
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp

# 添加必要路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "InternBootcamp"))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InternBootcampRewardCalculator:
    """
    InternBootcamp任务的reward计算器 V2
    """
    
    def __init__(self, config_path: str = None):
        """初始化reward计算器"""
        # 加载配置
        if config_path is None:
            config_path = CURRENT_DIR / "config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.llm_config = self.config['llm_config']['upstream']
            self.reward_config = self.config.get('reward_config', {})
        else:
            # 默认配置
            self.llm_config = {
                'provider': 'openai',
                'model': 'qwen-turbo',
                'api_key': '956c41bd0f31beaf68b871d4987af4bb',
                'base_url': 'https://idealab.alibaba-inc.com/api/openai/v1',
                'temperature': 0.7
            }
            self.reward_config = {}
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 30)
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # bootcamp类缓存
        self._bootcamp_cache = {}
        
        logger.info("InternBootcampRewardCalculator V2 initialized")
    
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
    
    async def call_llm_api(self, prompt: str) -> str:
        """调用LLM API"""
        url = self.llm_config['base_url'].rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f"Bearer {self.llm_config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.llm_config['model'],
            'messages': [{"role": "user", "content": prompt}],
            'temperature': self.llm_config.get('temperature', 0.7),
            'max_tokens': 1000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=30) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return ""
    
    async def execute_workflow_simple(self, workflow_code: str, problem_text: str) -> str:
        """
        简化的workflow执行方法
        直接调用LLM API而不是使用MetaGPT
        """
        # 从workflow代码中提取指令
        instruction_pattern = r'instruction\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(instruction_pattern, workflow_code)
        
        if matches:
            instruction = matches[0]
        else:
            instruction = "Solve the problem step by step."
        
        # 构建完整的prompt
        full_prompt = f"{instruction}\n\nProblem: {problem_text}"
        
        # 调用LLM
        result = await self.call_llm_api(full_prompt)
        
        return result
    
    async def compute_score_for_testcase(self, workflow_code: str, task_name: str, 
                                        test_case: str) -> float:
        """
        在单个test case上计算分数
        """
        try:
            # 加载bootcamp类
            bootcamp_class = self._load_bootcamp_class(task_name)
            if not bootcamp_class:
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
            
            # 使用bootcamp的prompt_func生成问题文本
            if hasattr(bootcamp_class, 'prompt_func'):
                problem_text = bootcamp_class.prompt_func(case_data)
            else:
                problem_text = str(case_data)
            
            logger.debug(f"Problem text: {problem_text[:100]}...")
            
            # 执行workflow（简化版）
            result = await self.execute_workflow_simple(workflow_code, problem_text)
            
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
            
        except Exception as e:
            logger.error(f"Error computing score for {task_name}: {e}")
            logger.debug(traceback.format_exc())
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, task_name: str, 
                                  test_cases: List[str]) -> float:
        """
        异步计算workflow在所有test cases上的平均reward
        """
        if not test_cases:
            return 0.0
        
        # 创建任务列表
        tasks = []
        for test_case in test_cases:
            task = self.compute_score_for_testcase(workflow_code, task_name, test_case)
            tasks.append(task)
        
        # 并发执行
        scores = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        valid_scores = []
        for score in scores:
            if isinstance(score, Exception):
                logger.error(f"Task failed with exception: {score}")
                valid_scores.append(0.0)
            else:
                valid_scores.append(score)
        
        # 计算平均分
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        logger.info(f"Average score for {task_name}: {avg_score:.3f} ({len(valid_scores)} test cases)")
        
        return avg_score


# 创建全局计算器实例
_global_calculator = None

def get_calculator():
    """获取全局计算器实例"""
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = InternBootcampRewardCalculator()
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
    try:
        # 获取计算器实例
        calculator = get_calculator()
        
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(solution_str)
        if not workflow_code:
            logger.error("No workflow code found in solution")
            return 0.0
        
        # 从extra_info提取必要信息
        task_name = extra_info.get('task_name', '')
        test_cases = extra_info.get('test_cases', [])
        
        if not task_name:
            logger.error("No task_name found in extra_info")
            return 0.0
        
        logger.info(f"Computing reward for task: {task_name} with {len(test_cases)} test cases")
        
        # 同步计算reward
        # 为了避免事件循环冲突，直接使用同步方式计算
        scores = []
        for test_case in test_cases:
            try:
                score = asyncio.run(calculator.compute_score_for_testcase(
                    workflow_code, task_name, test_case
                ))
                scores.append(score)
            except Exception as e:
                logger.error(f"Error computing score for test case: {e}")
                scores.append(0.0)
        
        # 计算平均分
        reward = sum(scores) / len(scores) if scores else 0.0
        logger.info(f"Computed average reward: {reward:.3f}")
        
        return reward
        
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        return 0.0


async def batch_compute_score(solutions: List[str], ground_truths: List[str], 
                             extra_infos: List[Dict]) -> List[float]:
    """
    批量计算多个solution的reward分数
    
    Args:
        solutions: LLM生成的solution列表
        ground_truths: ground truth列表
        extra_infos: 额外信息列表
    
    Returns:
        List[float]: reward分数列表
    """
    if len(solutions) != len(extra_infos):
        raise ValueError("solutions and extra_infos must have the same length")
    
    # 获取计算器实例
    calculator = get_calculator()
    
    # 收集所有计算任务
    all_rewards = []
    
    for solution, extra_info in zip(solutions, extra_infos):
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(solution)
        if not workflow_code:
            all_rewards.append(0.0)
            continue
        
        try:
            # 提取信息
            task_name = extra_info.get('task_name', '')
            test_cases = extra_info.get('test_cases', [])
            
            if not task_name:
                all_rewards.append(0.0)
                continue
            
            # 计算reward
            reward = await calculator.compute_reward_async(workflow_code, task_name, test_cases)
            all_rewards.append(reward)
            
        except Exception as e:
            logger.error(f"Error processing solution: {e}")
            all_rewards.append(0.0)
    
    return all_rewards


if __name__ == "__main__":
    # 简单测试
    test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
</graph>
"""
    
    test_extra_info = {
        'task_name': 'adidyoumean',
        'test_cases': ["{'input': 'hello'}", "{'input': 'hellno'}", "{'input': 'abacaba'}"]
    }
    
    score = compute_score(test_solution, "default", test_extra_info)
    print(f"Test score: {score}")