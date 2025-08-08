"""
InternBootcamp Handler for ScoreFlow
通用处理器，支持InternBootcamp中的所有任务类型
"""
import os
import sys
import json
import importlib
import traceback
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加InternBootcamp到Python路径
internbootcamp_root = Path(__file__).parent.parent.parent.parent / "InternBootcamp"
sys.path.insert(0, str(internbootcamp_root))

from ..base_handler import BenchmarkHandler


class InternBootcampHandler(BenchmarkHandler):
    """
    InternBootcamp的通用处理器
    动态加载并调用对应的bootcamp类进行验证
    """
    
    def __init__(self, dataset_path=None):
        # 如果没有提供dataset_path，使用默认路径
        if dataset_path is None:
            dataset_path = str(Path(__file__).parent.parent.parent.parent / "InternBootcamp" / "workflow_test_v2" / "bootcamp_dataset.jsonl")
        
        super().__init__(dataset_path=dataset_path)
        # 注意：父类已经设置了self.dataset_path，所以不需要再设置self.data_path
        # self.data也已经由父类的__init__通过调用_load_data()加载了
        self._bootcamp_cache = {}  # 缓存已加载的bootcamp类
        
    def _load_data(self) -> List[Dict]:
        """加载InternBootcamp数据集"""
        data = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data
    
    def _load_bootcamp_class(self, task_name: str):
        """动态加载对应的bootcamp类"""
        if task_name in self._bootcamp_cache:
            return self._bootcamp_cache[task_name]
        
        try:
            # 尝试导入对应的bootcamp模块
            module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
            module = importlib.import_module(module_path)
            
            # 获取bootcamp类（类名通常是 TasknameBootcamp 格式）
            class_name = f"{task_name.capitalize()}bootcamp"
            bootcamp_class = getattr(module, class_name)
            
            self._bootcamp_cache[task_name] = bootcamp_class
            return bootcamp_class
            
        except Exception as e:
            print(f"Failed to load bootcamp class for {task_name}: {e}")
            traceback.print_exc()
            return None
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        根据索引生成用于工作流生成的提示文本
        """
        prompts = []
        for idx in indices:
            if idx >= len(self.data):
                continue
                
            item = self.data[idx]
            task_name = item['task_name']
            task_description = item['task_description']
            
            # 获取第一个测试用例作为示例
            if item['test_cases']:
                test_case = item['test_cases'][0]
                case_prompt = test_case.get('prompt', '')
                
                prompt = f"""Task Type: {task_name}

Task Description:
{task_description}

Example Problem:
{case_prompt}

Please analyze this type of problem and create a workflow to solve it."""
                prompts.append(prompt)
        
        return "\n\n---\n\n".join(prompts)
    
    def get_verification_data(self, index: int) -> Dict:
        """
        获取用于验证的完整数据
        """
        if index >= len(self.data):
            return {}
            
        item = self.data[index]
        return {
            'task_name': item['task_name'],
            'task_type': item.get('task_type', 'unknown'),
            'task_description': item['task_description'],
            'test_cases': item['test_cases'],
            'index': index
        }
    
    def judge(self, model_output: Any, ground_truth_data: Dict) -> bool:
        """
        使用InternBootcamp的验证器判断答案是否正确
        """
        if not ground_truth_data:
            return False
            
        task_name = ground_truth_data.get('task_name')
        test_cases = ground_truth_data.get('test_cases', [])
        
        if not task_name or not test_cases:
            return False
        
        # 加载对应的bootcamp类
        bootcamp_class = self._load_bootcamp_class(task_name)
        if not bootcamp_class:
            print(f"Could not load bootcamp class for {task_name}")
            return False
        
        # 验证所有测试用例
        passed_count = 0
        total_count = len(test_cases)
        
        for test_case in test_cases:
            try:
                # 获取测试用例数据
                case_data = test_case.get('case', {})
                
                # 调用bootcamp的verify_score方法
                score = bootcamp_class.verify_score(
                    model_output=str(model_output),
                    identity=case_data,
                    format_score=0.1,  # 给格式正确一定分数
                    short_penalty=False,  # 不惩罚短输出
                    format_penalty=False  # 不强制要求think标签
                )
                
                # 分数大于0.9认为通过
                if score >= 0.9:
                    passed_count += 1
                    
            except Exception as e:
                print(f"Error verifying test case for {task_name}: {e}")
                traceback.print_exc()
                continue
        
        # 所有测试用例都通过才算成功
        success = (passed_count == total_count and total_count > 0)
        if success:
            print(f"Task {task_name}: All {total_count} test cases passed!")
        else:
            print(f"Task {task_name}: {passed_count}/{total_count} test cases passed")
            
        return success
    
    def build_executable_script(self, workflow_code: str, timeout: int = 180) -> dict:
        """
        构建可执行的Python脚本部分
        返回包含各部分的字典，与base_handler保持一致
        """
        # 导入conditions模块获取模板
        from ScoreFlow.scripts.internbootcamp.conditions import PYTHON_START, PYTHON_END
        
        # 处理PYTHON_END中的超时占位符
        if '{time}' in PYTHON_END:
            final_python_end = PYTHON_END.format(time=timeout)
            call_signature = "await workflow_instance()"  # 旧版格式
        else:
            final_python_end = PYTHON_END
            call_signature = f"await workflow_instance(timeout={timeout})"  # 新版格式
        
        # 返回字典格式（与base_handler保持一致）
        return {
            "python_start": PYTHON_START,
            "workflow_code": workflow_code,
            "python_end": final_python_end,
            "call_signature": call_signature
        }