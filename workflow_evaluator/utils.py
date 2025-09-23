#!/usr/bin/env python
"""
Utility Functions - 工具函数
提供通用的辅助函数
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib


def setup_logging(config: Dict) -> logging.Logger:
    """
    设置日志

    Args:
        config: 配置字典

    Returns:
        配置好的logger
    """
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建logger
    logger = logging.getLogger('workflow_evaluator')
    logger.setLevel(level)

    # 控制台handler
    if log_config.get('console', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(console_handler)

    # 文件handler
    if log_config.get('file'):
        file_handler = logging.FileHandler(log_config['file'], encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)

    return logger


def load_config(config_path: str = "config.yaml") -> Dict:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"配置文件不存在: {config_path}")
        return {}

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def load_jsonl(file_path: str) -> List[Dict]:
    """
    加载JSONL文件

    Args:
        file_path: JSONL文件路径

    Returns:
        记录列表
    """
    records = []
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return records


def save_jsonl(records: List[Dict], file_path: str):
    """
    保存为JSONL文件

    Args:
        records: 记录列表
        file_path: 输出文件路径
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def generate_id(text: str) -> str:
    """
    生成唯一ID

    Args:
        text: 用于生成ID的文本

    Returns:
        唯一ID
    """
    hash_obj = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode())
    return hash_obj.hexdigest()[:12]


def format_time(seconds: float) -> str:
    """
    格式化时间显示

    Args:
        seconds: 秒数

    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分"


def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", length: int = 50):
    """
    打印进度条

    Args:
        current: 当前进度
        total: 总数
        prefix: 前缀文字
        suffix: 后缀文字
        length: 进度条长度
    """
    percent = current / total if total > 0 else 0
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent*100:.1f}% {suffix}', end='', flush=True)

    # 完成时换行
    if current == total:
        print()


def extract_operators_from_code(workflow_code: str) -> List[str]:
    """
    从workflow代码中提取使用的operators

    Args:
        workflow_code: workflow代码

    Returns:
        operators列表
    """
    operators = []
    operator_patterns = [
        'self.generate', 'self.revise', 'self.summarize',
        'self.ensemble', 'self.decompose', 'self.programmer'
    ]

    for pattern in operator_patterns:
        if pattern in workflow_code:
            operator_name = pattern.split('.')[-1]
            if operator_name not in operators:
                operators.append(operator_name)

    return operators


def validate_workflow_code(workflow_code: str) -> Tuple[bool, Optional[str]]:
    """
    验证workflow代码的基本结构

    Args:
        workflow_code: workflow代码

    Returns:
        (是否有效, 错误信息)
    """
    # 检查必要的类定义
    if 'class Workflow' not in workflow_code:
        return False, "缺少Workflow类定义"

    # 检查必要的方法
    if 'def __init__' not in workflow_code:
        return False, "缺少__init__方法"

    if 'def run_workflow' not in workflow_code:
        return False, "缺少run_workflow方法"

    # 检查是否有await语句（异步执行）
    if 'await ' not in workflow_code:
        return False, "缺少异步执行语句(await)"

    return True, None


def merge_statistics(stats_list: List[Dict]) -> Dict:
    """
    合并多个统计结果

    Args:
        stats_list: 统计结果列表

    Returns:
        合并后的统计结果
    """
    merged = {
        'total': 0,
        'successful': 0,
        'failed': 0,
        'scores': [],
        'execution_times': []
    }

    for stats in stats_list:
        merged['total'] += stats.get('total', 0)
        merged['successful'] += stats.get('successful', 0)
        merged['failed'] += stats.get('failed', 0)
        merged['scores'].extend(stats.get('scores', []))
        merged['execution_times'].extend(stats.get('execution_times', []))

    # 计算汇总指标
    if merged['total'] > 0:
        merged['success_rate'] = merged['successful'] / merged['total']
    else:
        merged['success_rate'] = 0

    if merged['scores']:
        merged['average_score'] = sum(merged['scores']) / len(merged['scores'])
    else:
        merged['average_score'] = 0

    if merged['execution_times']:
        merged['avg_execution_time'] = sum(merged['execution_times']) / len(merged['execution_times'])
    else:
        merged['avg_execution_time'] = 0

    return merged


def filter_records(records: List[Dict], filters: Dict) -> List[Dict]:
    """
    根据过滤条件筛选记录

    Args:
        records: 记录列表
        filters: 过滤条件

    Returns:
        筛选后的记录
    """
    filtered = records

    # 按data_source过滤
    if filters.get('data_sources'):
        filtered = [r for r in filtered if r.get('data_source') in filters['data_sources']]

    # 按operators_group过滤
    if filters.get('operators_groups'):
        filtered = [r for r in filtered if r.get('operators_group') in filters['operators_groups']]

    # 按成功状态过滤
    if 'success' in filters:
        filtered = [r for r in filtered if r.get('success') == filters['success']]

    # 按分数范围过滤
    if filters.get('min_score') is not None:
        filtered = [r for r in filtered if r.get('score', 0) >= filters['min_score']]

    if filters.get('max_score') is not None:
        filtered = [r for r in filtered if r.get('score', 0) <= filters['max_score']]

    return filtered


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total: int, desc: str = "Progress"):
        self.total = total
        self.current = 0
        self.desc = desc
        self.start_time = datetime.now()

    def update(self, n: int = 1):
        """更新进度"""
        self.current += n
        self._display()

    def _display(self):
        """显示进度"""
        if self.total > 0:
            percent = self.current / self.total
            elapsed = (datetime.now() - self.start_time).total_seconds()

            # 估算剩余时间
            if self.current > 0:
                eta = elapsed * (self.total - self.current) / self.current
                eta_str = format_time(eta)
            else:
                eta_str = "计算中..."

            print(f"\r{self.desc}: {self.current}/{self.total} ({percent*100:.1f}%) | "
                  f"已用: {format_time(elapsed)} | 预计剩余: {eta_str}", end='', flush=True)

            if self.current >= self.total:
                print()  # 完成时换行

    def finish(self):
        """结束进度跟踪"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{self.desc}完成! 总用时: {format_time(elapsed)}")


from typing import Tuple