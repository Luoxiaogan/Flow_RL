"""
InternBootcamp工具函数模块
提供动态发现、加载和管理bootcamp类的功能
"""
import os
import sys
import json
import re
import importlib
import inspect
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
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

# 添加InternBootcamp到Python路径
project_root_path = Path(project_root)
internbootcamp_root = project_root / "InternBootcamp"
sys.path.insert(0, str(internbootcamp_root))


class InternBootcampManager:
    """InternBootcamp任务管理器"""
    
    def __init__(self):
        self.internbootcamp_root = internbootcamp_root
        self.bootcamp_registry = {}
        self.failed_bootcamps = {}
        self._discover_bootcamps()
    
    def _discover_bootcamps(self):
        """动态发现所有可用的bootcamp类"""
        bootcamp_dir = self.internbootcamp_root / "internbootcamp" / "bootcamp"
        
        if not bootcamp_dir.exists():
            logger.error(f"Bootcamp directory not found: {bootcamp_dir}")
            return
        
        # 扫描所有子目录
        for task_dir in bootcamp_dir.iterdir():
            if not task_dir.is_dir() or task_dir.name.startswith('_'):
                continue
                
            task_name = task_dir.name
            
            # 查找对应的Python文件
            py_file = task_dir / f"{task_name}.py"
            if not py_file.exists():
                logger.debug(f"No Python file found for {task_name}")
                continue
            
            try:
                # 尝试导入模块
                module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
                module = importlib.import_module(module_path)
                
                # 查找bootcamp类
                bootcamp_class = None
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        name.lower().endswith('bootcamp') and
                        hasattr(obj, 'case_generator') and
                        hasattr(obj, 'prompt_func') and
                        hasattr(obj, 'verify_score')):
                        bootcamp_class = obj
                        break
                
                if bootcamp_class:
                    self.bootcamp_registry[task_name] = bootcamp_class
                    logger.info(f"Successfully loaded: {task_name}")
                else:
                    logger.warning(f"No valid bootcamp class found in {task_name}")
                    
            except Exception as e:
                self.failed_bootcamps[task_name] = str(e)
                logger.debug(f"Failed to load {task_name}: {e}")
    
    def get_available_tasks(self) -> List[str]:
        """获取所有可用的任务名称"""
        return sorted(list(self.bootcamp_registry.keys()))
    
    def get_failed_tasks(self) -> Dict[str, str]:
        """获取加载失败的任务及错误信息"""
        return self.failed_bootcamps.copy()
    
    def get_bootcamp_class(self, task_name: str):
        """获取指定的bootcamp类"""
        if task_name not in self.bootcamp_registry:
            raise ValueError(f"Task '{task_name}' not found.")
        return self.bootcamp_registry[task_name]
    
    def generate_task_examples(self, task_name: str, n_examples: int = 2) -> List[Dict[str, Any]]:
        """生成n个任务示例"""
        bootcamp_class = self.get_bootcamp_class(task_name)
        
        examples = []
        errors = []
        
        # 尝试生成指定数量的示例
        attempts = 0
        max_attempts = n_examples * 3  # 允许一些失败
        
        while len(examples) < n_examples and attempts < max_attempts:
            attempts += 1
            try:
                # 创建bootcamp实例
                bootcamp = bootcamp_class()
                
                # 生成case
                identity = bootcamp.case_generator()
                
                # 生成prompt
                prompt = bootcamp.prompt_func(identity)
                
                examples.append({
                    "identity": identity,
                    "prompt": prompt
                })
                
            except Exception as e:
                error_msg = f"Failed to generate example {attempts} for {task_name}: {str(e)}"
                errors.append(error_msg)
                logger.debug(error_msg)
        
        if not examples:
            raise RuntimeError(f"Failed to generate any examples for {task_name}. Errors: {errors}")
        
        if len(examples) < n_examples:
            logger.warning(f"Only generated {len(examples)} examples for {task_name} (requested {n_examples})")
        
        return examples
    
    def get_task_description(self, task_name: str) -> str:
        """从源代码中提取任务描述"""
        try:
            # 获取源文件路径
            py_file = self.internbootcamp_root / "internbootcamp" / "bootcamp" / task_name / f"{task_name}.py"
            
            if not py_file.exists():
                return f"Task description not available for {task_name}"
            
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试提取类文档字符串或文件开头的注释
            # 查找以"""或'''开头的文档字符串
            doc_pattern = r'"""(.*?)"""'
            matches = re.findall(doc_pattern, content, re.DOTALL)
            
            if matches:
                # 取第一个较长的文档字符串作为描述
                for match in matches:
                    if len(match) > 100:  # 假设描述至少100字符
                        # 截取到"Here is a reference code"之前
                        if "Here is a reference code" in match:
                            match = match.split("Here is a reference code")[0]
                        return match.strip()
            
            # 如果没有找到，尝试提取注释
            lines = content.split('\n')
            description_lines = []
            in_comment = False
            
            for line in lines[:50]:  # 只看前50行
                if line.strip().startswith('#'):
                    description_lines.append(line.strip('#').strip())
                elif '"""' in line or "'''" in line:
                    in_comment = not in_comment
                elif in_comment:
                    description_lines.append(line.strip())
            
            if description_lines:
                return '\n'.join(description_lines[:10])  # 最多10行
            
            return f"Task {task_name}: No description available"
            
        except Exception as e:
            logger.error(f"Failed to extract description for {task_name}: {e}")
            return f"Task {task_name}: Description extraction failed"
    
    def test_bootcamp(self, task_name: str) -> Dict[str, Any]:
        """测试一个bootcamp是否正常工作"""
        result = {
            "task_name": task_name,
            "status": "unknown",
            "can_generate": False,
            "can_verify": False,
            "example": None,
            "error": None
        }
        
        try:
            # 测试生成示例
            examples = self.generate_task_examples(task_name, n_examples=1)
            if examples:
                result["can_generate"] = True
                result["example"] = examples[0]
                
                # 测试验证功能
                bootcamp_class = self.get_bootcamp_class(task_name)
                bootcamp = bootcamp_class()
                
                # 尝试用一个简单的答案测试verify_score
                test_answer = "test answer"
                score = bootcamp.verify_score(test_answer, examples[0]["identity"])
                result["can_verify"] = True
                result["status"] = "working"
        
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "failed"
            
        return result
    
    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        return {
            "total_discovered": len(self.bootcamp_registry) + len(self.failed_bootcamps),
            "successfully_loaded": len(self.bootcamp_registry),
            "failed_to_load": len(self.failed_bootcamps),
            "available_tasks": self.get_available_tasks(),
            "failed_tasks": list(self.failed_bootcamps.keys())
        }


def classify_ability(task_name: str) -> str:
    """根据任务名称分类能力类型"""
    task_name_lower = task_name.lower()
    
    # 逻辑推理
    if any(keyword in task_name_lower for keyword in ['sudoku', 'logic', 'puzzle', 'minesweeper', 'kakuro']):
        return "logic_reasoning"
    
    # 数学
    if any(keyword in task_name_lower for keyword in ['math', 'arithmetic', 'algebra', 'geometry', 'calculus']):
        return "math_reasoning"
    
    # 算法
    if any(keyword in task_name_lower for keyword in ['algorithm', 'sort', 'search', 'graph', 'dynamic']):
        return "algorithm_design"
    
    # 编程
    if any(keyword in task_name_lower for keyword in ['code', 'program', 'function', 'class']):
        return "programming"
    
    # 游戏
    if any(keyword in task_name_lower for keyword in ['game', 'chess', 'go', 'poker']):
        return "game_playing"
    
    # 默认
    return "general_reasoning"


def get_task_type(task_name: str) -> str:
    """获取任务类型"""
    task_name_lower = task_name.lower()
    
    if 'puzzle' in task_name_lower:
        return "puzzle"
    elif 'game' in task_name_lower:
        return "game"
    elif 'algorithm' in task_name_lower:
        return "algorithm"
    elif 'math' in task_name_lower:
        return "math"
    elif 'logic' in task_name_lower:
        return "logic"
    else:
        return "general"


if __name__ == "__main__":
    # 测试代码
    manager = InternBootcampManager()
    
    print("=== InternBootcamp Task Statistics ===")
    stats = manager.get_task_stats()
    print(f"Total discovered: {stats['total_discovered']}")
    print(f"Successfully loaded: {stats['successfully_loaded']}")
    print(f"Failed to load: {stats['failed_to_load']}")
    
    print("\n=== Available Tasks (first 10) ===")
    for task in stats['available_tasks'][:10]:
        print(f"- {task}")
    
    # 测试一个具体任务
    test_task = "game24" if "game24" in stats['available_tasks'] else stats['available_tasks'][0]
    print(f"\n=== Testing Task: {test_task} ===")
    
    try:
        # 生成示例
        examples = manager.generate_task_examples(test_task, n_examples=2)
        print(f"Generated {len(examples)} examples")
        
        # 获取描述
        description = manager.get_task_description(test_task)
        print(f"\nTask Description (first 200 chars):\n{description[:200]}...")
        
    except Exception as e:
        print(f"Error testing task: {e}")