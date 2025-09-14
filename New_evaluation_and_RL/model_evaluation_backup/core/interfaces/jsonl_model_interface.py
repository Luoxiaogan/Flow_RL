"""
JSONL model interface for evaluating pre-generated outputs
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

from .model_interface import BaseModelInterface

logger = logging.getLogger(__name__)

class JSONLModelInterface(BaseModelInterface):
    """
    Model interface that reads pre-generated outputs from JSONL files
    Used for evaluating validation logs from RL training
    Only supports exact matching to ensure evaluation accuracy
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize JSONL model interface
        
        Args:
            model_config: Configuration containing:
                - jsonl_path: Path to JSONL file or list of paths
        """
        super().__init__(model_config)
        
        self.jsonl_paths = model_config.get('jsonl_path', [])
        if isinstance(self.jsonl_paths, str):
            self.jsonl_paths = [self.jsonl_paths]
        
        # Storage for loaded data
        self.data_map = {}  # input -> output mapping (exact match only)
        self.all_entries = []  # All entries for reporting
        
        logger.info(f"初始化 JSONL 模型接口: {self.model_name}")
        logger.info(f"  JSONL 文件: {self.jsonl_paths}")
        logger.info(f"  匹配模式: 精确匹配")
    
    async def initialize(self):
        """
        Load JSONL files into memory
        """
        logger.info(f"加载 JSONL 数据: {self.model_name}")
        
        for jsonl_path in self.jsonl_paths:
            path = Path(jsonl_path)
            
            if not path.exists():
                logger.warning(f"JSONL 文件不存在: {jsonl_path}")
                continue
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if not line.strip():
                            continue
                        
                        try:
                            entry = json.loads(line)
                            
                            # Store in map
                            input_text = entry.get('input', '')
                            output_text = entry.get('output', '')
                            
                            if input_text and output_text:
                                # Store in map for exact matching
                                self.data_map[input_text] = output_text
                                
                                # Store all entries for reporting
                                self.all_entries.append({
                                    'input': input_text,
                                    'output': output_text,
                                    'score': entry.get('score', 0),
                                    'step': entry.get('step', 0),
                                    'accuracy': entry.get('accuracy', 0),
                                    'source_file': str(path),
                                    'line': line_num
                                })
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"解析 JSON 失败 (文件: {path}, 行: {line_num}): {e}")
                
                logger.info(f"从 {path} 加载了 {len(self.all_entries)} 条记录")
            
            except Exception as e:
                logger.error(f"读取 JSONL 文件失败 {jsonl_path}: {e}")
                raise
        
        if not self.all_entries:
            logger.warning(f"警告: 没有加载到任何数据 (模型: {self.model_name})")
        else:
            logger.info(f"总共加载 {len(self.all_entries)} 条记录")
            
            # Statistics
            if self.all_entries:
                steps = set(e.get('step', 0) for e in self.all_entries)
                logger.info(f"  训练步数: {sorted(steps)}")
                
                avg_score = sum(e.get('score', 0) for e in self.all_entries) / len(self.all_entries)
                avg_acc = sum(e.get('accuracy', 0) for e in self.all_entries) / len(self.all_entries)
                logger.info(f"  平均分数: {avg_score:.2f}")
                logger.info(f"  平均准确率: {avg_acc:.2%}")
    
    async def generate(self, 
                       prompt: Union[str, List[Dict[str, str]]],
                       **kwargs) -> str:
        """
        Return pre-generated output for the given prompt (exact match only)
        
        Args:
            prompt: Input prompt
            **kwargs: Ignored for JSONL model
            
        Returns:
            Pre-generated output or error message
        """
        # Convert chat format to string if needed
        if isinstance(prompt, list):
            # Extract user message from chat format
            user_messages = [msg['content'] for msg in prompt if msg['role'] == 'user']
            prompt = ' '.join(user_messages) if user_messages else str(prompt)
        
        # Exact match only
        if prompt in self.data_map:
            logger.debug(f"精确匹配成功")
            return self.data_map[prompt]
        else:
            logger.warning(f"精确匹配失败，输入未找到: {prompt[:100]}...")
            # Return error message
            return "# Error: No matching pre-generated output found for this input (exact match required)"
    
    async def cleanup(self):
        """
        Clean up resources (clear memory)
        """
        logger.info(f"清理 JSONL 模型资源: {self.model_name}")
        self.data_map.clear()
        self.all_entries.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded data
        
        Returns:
            Dictionary with statistics
        """
        if not self.all_entries:
            return {
                'total_entries': 0,
                'status': 'no_data'
            }
        
        steps = [e.get('step', 0) for e in self.all_entries]
        scores = [e.get('score', 0) for e in self.all_entries]
        accuracies = [e.get('accuracy', 0) for e in self.all_entries]
        
        return {
            'total_entries': len(self.all_entries),
            'unique_inputs': len(self.data_map),
            'training_steps': sorted(set(steps)),
            'score_range': [min(scores), max(scores)],
            'avg_score': sum(scores) / len(scores),
            'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            'source_files': list(set(e['source_file'] for e in self.all_entries))
        }