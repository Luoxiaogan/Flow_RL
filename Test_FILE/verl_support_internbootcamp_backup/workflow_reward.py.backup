"""
InternBootcamp工作流奖励计算模块
提供简化的接口来计算工作流的奖励分数
"""
import os
import sys
import json
import asyncio
import traceback
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path
import subprocess
import tempfile
import time

from internbootcamp_utils import InternBootcampManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowRewardCalculator:
    """工作流奖励计算器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.manager = InternBootcampManager()
        
        # 加载配置
        if config is None:
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.llm_config = config['llm_config']['downstream']
        self.reward_config = config['reward_config']
    
    async def execute_workflow(self, workflow_code: str, test_cases: List[Dict[str, Any]], 
                             bootcamp: Any) -> List[Optional[str]]:
        """执行工作流并返回结果"""
        results = []
        
        for test_case in test_cases:
            try:
                # 创建临时Python文件执行工作流
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                    # 构建完整的执行脚本
                    execution_script = self._build_execution_script(
                        workflow_code, 
                        test_case, 
                        bootcamp
                    )
                    f.write(execution_script)
                    temp_file = f.name
                
                # 执行脚本
                timeout = self.reward_config.get('timeout', 30)
                result = await self._run_python_script(temp_file, timeout)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to execute workflow: {e}")
                results.append(None)
            
            finally:
                # 清理临时文件
                if 'temp_file' in locals():
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
        
        return results
    
    def _build_execution_script(self, workflow_code: str, test_case: Dict[str, Any], 
                               bootcamp: Any) -> str:
        """构建执行脚本"""
        # 获取prompt
        prompt = bootcamp.prompt_func(test_case)
        
        script = f"""
import asyncio
import json
import sys
from openai import AsyncOpenAI

# LLM配置
LLM_CONFIG = {json.dumps(self.llm_config)}

# 创建LLM客户端
client = AsyncOpenAI(
    api_key=LLM_CONFIG['api_key'],
    base_url=LLM_CONFIG['base_url']
)

async def llm_call(system_prompt: str, user_prompt: str) -> str:
    \"\"\"调用LLM\"\"\"
    try:
        response = await client.chat.completions.create(
            model=LLM_CONFIG['model'],
            messages=[
                {{"role": "system", "content": system_prompt}},
                {{"role": "user", "content": user_prompt}}
            ],
            temperature=LLM_CONFIG.get('temperature', 0.3)
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling LLM: {{e}}"

# 工作流代码
{workflow_code}

# 执行工作流
async def main():
    workflow = InternBootcampWorkflow()
    problem = '''{prompt}'''
    result = await workflow.solve(problem)
    print("WORKFLOW_RESULT:", result)
    return result

if __name__ == "__main__":
    asyncio.run(main())
"""
        return script
    
    async def _run_python_script(self, script_path: str, timeout: int) -> Optional[str]:
        """运行Python脚本并获取结果"""
        try:
            # 设置环境变量以确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 使用subprocess运行脚本
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # 等待执行完成
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                logger.error(f"Script execution timed out after {timeout} seconds")
                return None
            
            # 解析输出 - 尝试多种编码
            output = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    output = stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if output is None:
                logger.error("Failed to decode script output")
                return None
            
            # 查找WORKFLOW_RESULT
            for line in output.split('\n'):
                if line.startswith('WORKFLOW_RESULT:'):
                    return line[len('WORKFLOW_RESULT:'):].strip()
            
            # 如果有错误，记录它
            if stderr:
                error_msg = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        error_msg = stderr.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if error_msg:
                    logger.error(f"Script error: {error_msg}")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to run script: {e}")
            return None
    
    async def compute_workflow_reward(self, workflow_code: str, task_name: str, 
                                    test_indices: Optional[List[int]] = None) -> float:
        """计算工作流的奖励分数"""
        try:
            # 获取bootcamp类
            bootcamp_class = self.manager.get_bootcamp_class(task_name)
            bootcamp = bootcamp_class()
            
            # 生成测试用例
            n_test_cases = self.reward_config.get('test_cases_per_task', 3)
            test_cases = []
            
            for _ in range(n_test_cases):
                try:
                    test_case = bootcamp.case_generator()
                    test_cases.append(test_case)
                except Exception as e:
                    logger.warning(f"Failed to generate test case: {e}")
            
            if not test_cases:
                logger.error(f"No test cases generated for {task_name}")
                return 0.0
            
            # 执行工作流
            results = await self.execute_workflow(workflow_code, test_cases, bootcamp)
            
            # 计算奖励
            total_score = 0.0
            valid_results = 0
            
            for result, test_case in zip(results, test_cases):
                if result is not None:
                    try:
                        # 使用bootcamp的verify_score方法
                        score = bootcamp.verify_score(result, test_case)
                        total_score += float(score)
                        valid_results += 1
                        logger.debug(f"Test case score: {score}")
                    except Exception as e:
                        logger.error(f"Failed to verify result: {e}")
            
            # 返回平均分数
            if valid_results > 0:
                avg_score = total_score / valid_results
                logger.info(f"Workflow reward for {task_name}: {avg_score:.3f} ({valid_results}/{len(test_cases)} valid)")
                return avg_score
            else:
                logger.warning(f"No valid results for {task_name}")
                return 0.0
            
        except Exception as e:
            logger.error(f"Failed to compute reward for {task_name}: {e}")
            traceback.print_exc()
            return 0.0
    
    async def batch_compute_rewards(self, workflow_codes: List[str], 
                                  task_names: Union[str, List[str]]) -> List[float]:
        """批量计算多个工作流的奖励"""
        # 如果task_names是字符串，转换为列表
        if isinstance(task_names, str):
            task_names = [task_names] * len(workflow_codes)
        
        # 确保长度匹配
        if len(workflow_codes) != len(task_names):
            raise ValueError("workflow_codes and task_names must have the same length")
        
        # 并发计算奖励
        max_concurrent = self.reward_config.get('max_concurrent', 5)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def compute_with_semaphore(workflow_code, task_name):
            async with semaphore:
                return await self.compute_workflow_reward(workflow_code, task_name)
        
        tasks = [
            compute_with_semaphore(code, name) 
            for code, name in zip(workflow_codes, task_names)
        ]
        
        return await asyncio.gather(*tasks)


# 简化接口
async def compute_score(workflow_code: str, task_name: str) -> float:
    """简化的奖励计算接口"""
    calculator = WorkflowRewardCalculator()
    return await calculator.compute_workflow_reward(workflow_code, task_name)


async def batch_compute_rewards(workflow_codes: List[str], 
                              task_names: Union[str, List[str]]) -> List[float]:
    """批量计算奖励的简化接口"""
    calculator = WorkflowRewardCalculator()
    return await calculator.batch_compute_rewards(workflow_codes, task_names)


# 测试代码
if __name__ == "__main__":
    # 测试工作流代码
    test_workflow = """
class InternBootcampWorkflow:
    def __init__(self):
        self.system_prompt = '''You are an expert problem solver. Analyze the problem carefully and provide a clear, correct solution.'''
    
    async def solve(self, problem):
        # 使用LLM解决问题
        response = await llm_call(self.system_prompt, problem)
        return response
"""
    
    async def test():
        # 获取可用任务
        manager = InternBootcampManager()
        available_tasks = manager.get_available_tasks()
        
        if not available_tasks:
            print("No available tasks found")
            return
        
        # 测试第一个任务
        test_task = available_tasks[0]
        print(f"Testing with task: {test_task}")
        
        # 计算奖励
        score = await compute_score(test_workflow, test_task)
        print(f"Reward score: {score:.3f}")
    
    asyncio.run(test())