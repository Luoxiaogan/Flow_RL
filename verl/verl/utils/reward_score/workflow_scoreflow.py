# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ScoreFlow Workflow Reward Score Integration
适配 workflow_reward.py 到 VERL 标准接口
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional


def _add_scoreflow_path():
    """动态添加 InternBootcamp reward 相关路径到 Python path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多个可能的路径
    possible_paths = [
        # 从 verl 目录向上查找
        os.path.join(current_dir, '../../../../Test_FILE/verl_support'),
        os.path.join(current_dir, '../../../Test_FILE/verl_support'),
        os.path.join(current_dir, '../../Test_FILE/verl_support'),
        # 从当前目录向上查找
        os.path.join(current_dir, '../../../../../Flow_RL/Test_FILE/verl_support'),
        os.path.join(current_dir, '../../../../Flow_RL/Test_FILE/verl_support'),
        # 旧路径兼容
        os.path.join(current_dir, '../../../../Test_FILE/verl_support'),
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            logging.debug(f"Added scoreflow path: {abs_path}")
            return abs_path
    
    logging.warning("scoreflow path not found, workflow reward may not work properly")
    return None

# 尝试添加路径
_add_scoreflow_path()

# 导入 compute_score 函数
try:
    from scoreflow_reward import compute_score as _scoreflow_compute_score
    logging.info("Successfully imported scoreflow compute_score")
except ImportError as e:
    logging.error(f"Failed to import scoreflow compute_score: {e}")
    _scoreflow_compute_score = None


def compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict[str, Any]) -> float:
    """
    计算 scoreflow workflow 的分数
    
    Args:
        solution_str: LLM 生成的包含 workflow 的 response
        ground_truth: ground truth 信息（对于 InternBootcamp 通常是 "default"）
        extra_info: 包含 task_name 和 test_cases 等额外信息
    
    Returns:
        float: reward 分数 (0.0 到 1.0)
    """
    if _scoreflow_compute_score is None:
        logging.error("scoreflow compute_score not available")
        return 0.0
    
    try:
        # 调用导入的 compute_score 函数
        score = _scoreflow_compute_score(data_source, solution_str, ground_truth, extra_info)
        return score
    except Exception as e:
        logging.error(f"Error computing scoreflow score: {e}")
        return 0.0


# 导出接口
__all__ = ['compute_score']