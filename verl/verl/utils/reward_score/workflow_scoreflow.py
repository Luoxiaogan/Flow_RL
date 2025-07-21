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

# 添加 ScoreFlow 路径支持
def _add_scoreflow_path():
    """动态添加 ScoreFlow 相关路径到 Python path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多个可能的 ScoreFlow 路径
    possible_paths = [
        # 从 verl 目录向上查找
        os.path.join(current_dir, '../../../../Test_FILE/verl_support'),
        os.path.join(current_dir, '../../../Test_FILE/verl_support'),
        os.path.join(current_dir, '../../Test_FILE/verl_support'),
        # 从当前目录向上查找
        os.path.join(current_dir, '../../../../../Flow_RL/Test_FILE/verl_support'),
        os.path.join(current_dir, '../../../../Flow_RL/Test_FILE/verl_support'),
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            logging.debug(f"Added ScoreFlow path: {abs_path}")
            return abs_path
    
    logging.warning("ScoreFlow path not found, workflow reward may not work properly")
    return None

# 动态导入 workflow_reward 模块
def _import_workflow_reward():
    """动态导入 workflow_reward 模块"""
    scoreflow_path = _add_scoreflow_path()
    
    try:
        from workflow_reward import WorkflowRewardCalculator, compute_score as scoreflow_compute_score
        return WorkflowRewardCalculator, scoreflow_compute_score
    except ImportError as e:
        logging.error(f"Failed to import workflow_reward: {e}")
        return None, None

# 缓存导入的模块
_WorkflowRewardCalculator, _scoreflow_compute_score = _import_workflow_reward()


def compute_score(solution_str: str, ground_truth: Any, extra_info: Optional[Dict] = None) -> float:
    """
    VERL 标准接口：计算 ScoreFlow 工作流的奖励分数
    
    Args:
        solution_str (str): 生成的工作流代码
        ground_truth (Any): 包含数据源信息的真值数据
        extra_info (Optional[Dict]): 额外信息，应包含:
            - data_source: 数据集名称 (如 'gsm8k', 'mbpp')
            - config_path: 可选的配置文件路径
    
    Returns:
        float: 奖励分数 (0.0 到 1.0)
    """
    if _scoreflow_compute_score is None:
        logging.error("ScoreFlow workflow_reward module not available")
        return 0.0
    
    # 解析参数
    if extra_info is None:
        extra_info = {}
    
    # 从 ground_truth 或 extra_info 中获取数据源
    data_source = None
    if isinstance(ground_truth, dict):
        data_source = ground_truth.get('data_source')
    
    if not data_source:
        data_source = extra_info.get('data_source')
    
    if not data_source:
        logging.error("data_source not found in ground_truth or extra_info")
        return 0.0
    
    # 获取配置路径
    config_path = extra_info.get('config_path')
    
    try:
        # 调用 ScoreFlow 的计算函数
        reward = _scoreflow_compute_score(
            workflow_code=solution_str,
            data_source=data_source,
            config_path=config_path
        )
        
        logging.info(f"ScoreFlow workflow reward computed: {reward:.4f} for {data_source}")
        return float(reward)
        
    except Exception as e:
        logging.error(f"Error computing ScoreFlow workflow reward: {e}")
        return 0.0


async def async_compute_score(solution_str: str, ground_truth: Any, extra_info: Optional[Dict] = None) -> float:
    """
    异步版本的奖励计算，支持 VERL 的异步执行模式
    """
    if _WorkflowRewardCalculator is None:
        logging.error("ScoreFlow WorkflowRewardCalculator not available")
        return 0.0
    
    # 解析参数
    if extra_info is None:
        extra_info = {}
    
    # 从 ground_truth 或 extra_info 中获取数据源和测试索引
    data_source = None
    test_indices = None
    
    if isinstance(ground_truth, dict):
        data_source = ground_truth.get('data_source')
        test_indices = ground_truth.get('test_indices', ground_truth.get('data_indices'))
    
    if not data_source:
        data_source = extra_info.get('data_source')
    
    if not test_indices:
        test_indices = extra_info.get('test_indices', extra_info.get('data_indices'))
    
    if not data_source:
        logging.error("data_source not found in ground_truth or extra_info")
        return 0.0
    
    try:
        # 加载配置
        config_path = extra_info.get('config_path')
        from utils import load_config
        config = load_config(config_path)
        
        # 创建计算器
        calculator = _WorkflowRewardCalculator(config)
        
        # 如果没有提供测试索引，加载默认的测试集
        if not test_indices:
            test_indices = calculator.load_test_indices(data_source)
        
        # 计算奖励
        reward = await calculator.compute_workflow_reward(
            workflow_code=solution_str,
            test_indices=test_indices,
            data_source=data_source
        )
        
        logging.info(f"ScoreFlow async workflow reward computed: {reward:.4f} for {data_source}")
        return float(reward)
        
    except Exception as e:
        logging.error(f"Error computing ScoreFlow async workflow reward: {e}")
        return 0.0


def batch_compute_scores(solution_strs: list, ground_truths: list, extra_infos: list = None) -> list:
    """
    批量计算多个工作流的奖励分数
    
    Args:
        solution_strs: 工作流代码列表
        ground_truths: 对应的真值数据列表
        extra_infos: 对应的额外信息列表
    
    Returns:
        list: 奖励分数列表
    """
    if extra_infos is None:
        extra_infos = [{}] * len(solution_strs)
    
    rewards = []
    for i, (solution_str, ground_truth, extra_info) in enumerate(zip(solution_strs, ground_truths, extra_infos)):
        try:
            reward = compute_score(solution_str, ground_truth, extra_info)
            rewards.append(reward)
            logging.debug(f"Batch workflow {i+1}/{len(solution_strs)} reward: {reward:.4f}")
        except Exception as e:
            logging.error(f"Error computing reward for workflow {i+1}: {e}")
            rewards.append(0.0)
    
    return rewards


# 为了兼容性，提供一些别名
scoreflow_compute_score = compute_score
workflow_compute_score = compute_score 