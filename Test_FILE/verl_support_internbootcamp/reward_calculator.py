"""
详细的Reward计算器
支持多种任务类型的reward计算和详细记录
"""
import json
import re
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class RewardCalculator:
    """通用的Reward计算器"""
    
    def __init__(self):
        self.calculation_history = []
        
    def calculate_reward(self, task_name: str, example: Dict[str, Any], 
                        output: str, detailed: bool = True) -> Dict[str, Any]:
        """计算reward并返回详细信息"""
        start_time = datetime.now()
        
        # 获取期望输出
        expected_output = example.get('output', '')
        
        # 根据任务类型选择计算方法
        if 'sudoku' in task_name.lower():
            reward, details = self._calculate_sudoku_reward(expected_output, output)
        elif 'minesweeper' in task_name.lower():
            reward, details = self._calculate_minesweeper_reward(expected_output, output)
        elif 'kakuro' in task_name.lower():
            reward, details = self._calculate_kakuro_reward(expected_output, output)
        elif 'graph' in task_name.lower():
            reward, details = self._calculate_graph_reward(expected_output, output)
        else:
            # 默认使用精确匹配
            reward, details = self._calculate_exact_match_reward(expected_output, output)
        
        # 创建详细记录
        record = {
            "task_name": task_name,
            "example_id": example.get('identity', 'unknown'),
            "reward": reward,
            "success": reward > 0,
            "calculation_time": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }
        
        if detailed:
            record.update({
                "input": example.get('input', ''),
                "expected_output": expected_output,
                "actual_output": output,
                "details": details
            })
        
        # 保存到历史记录
        self.calculation_history.append(record)
        
        return record
    
    def _calculate_sudoku_reward(self, expected: str, actual: str) -> Tuple[float, Dict[str, Any]]:
        """计算数独任务的reward"""
        details = {
            "type": "sudoku",
            "metrics": {}
        }
        
        try:
            # 解析期望和实际的数独网格
            expected_grid = self._parse_grid(expected)
            actual_grid = self._parse_grid(actual)
            
            if not expected_grid or not actual_grid:
                details["error"] = "Failed to parse grid"
                return 0.0, details
            
            # 检查网格大小
            if len(expected_grid) != len(actual_grid):
                details["error"] = "Grid size mismatch"
                return 0.0, details
            
            n = len(expected_grid)
            total_cells = n * n
            correct_cells = 0
            
            # 逐个单元格比较
            for i in range(n):
                for j in range(n):
                    if expected_grid[i][j] == actual_grid[i][j]:
                        correct_cells += 1
            
            # 检查约束满足情况
            row_valid = self._check_sudoku_rows(actual_grid)
            col_valid = self._check_sudoku_cols(actual_grid)
            region_valid = self._check_sudoku_regions(actual_grid)
            
            # 计算部分分数
            cell_accuracy = correct_cells / total_cells
            constraint_score = (row_valid + col_valid + region_valid) / 3.0
            
            # 综合reward
            if correct_cells == total_cells and constraint_score == 1.0:
                reward = 1.0  # 完全正确
            else:
                reward = 0.7 * cell_accuracy + 0.3 * constraint_score
            
            details["metrics"] = {
                "correct_cells": correct_cells,
                "total_cells": total_cells,
                "cell_accuracy": cell_accuracy,
                "row_validity": row_valid,
                "col_validity": col_valid,
                "region_validity": region_valid,
                "constraint_score": constraint_score
            }
            
            return reward, details
            
        except Exception as e:
            details["error"] = str(e)
            return 0.0, details
    
    def _calculate_minesweeper_reward(self, expected: str, actual: str) -> Tuple[float, Dict[str, Any]]:
        """计算扫雷任务的reward"""
        details = {
            "type": "minesweeper",
            "metrics": {}
        }
        
        try:
            # 解析地雷位置
            expected_mines = self._parse_mine_positions(expected)
            actual_mines = self._parse_mine_positions(actual)
            
            if expected_mines is None or actual_mines is None:
                details["error"] = "Failed to parse mine positions"
                return 0.0, details
            
            # 转换为集合进行比较
            expected_set = set(expected_mines)
            actual_set = set(actual_mines)
            
            # 计算指标
            true_positives = len(expected_set & actual_set)
            false_positives = len(actual_set - expected_set)
            false_negatives = len(expected_set - actual_set)
            
            # 计算精确率和召回率
            precision = true_positives / len(actual_set) if actual_set else 0.0
            recall = true_positives / len(expected_set) if expected_set else 0.0
            
            # F1分数作为reward
            if precision + recall > 0:
                f1_score = 2 * (precision * recall) / (precision + recall)
            else:
                f1_score = 0.0
            
            details["metrics"] = {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "expected_mines": len(expected_set),
                "predicted_mines": len(actual_set)
            }
            
            return f1_score, details
            
        except Exception as e:
            details["error"] = str(e)
            return 0.0, details
    
    def _calculate_kakuro_reward(self, expected: str, actual: str) -> Tuple[float, Dict[str, Any]]:
        """计算Kakuro任务的reward"""
        details = {
            "type": "kakuro",
            "metrics": {}
        }
        
        try:
            # 解析网格
            expected_grid = self._parse_grid(expected)
            actual_grid = self._parse_grid(actual)
            
            if not expected_grid or not actual_grid:
                details["error"] = "Failed to parse grid"
                return 0.0, details
            
            # 比较网格
            total_cells = sum(len(row) for row in expected_grid)
            correct_cells = 0
            
            for i in range(len(expected_grid)):
                for j in range(len(expected_grid[i])):
                    if i < len(actual_grid) and j < len(actual_grid[i]):
                        if expected_grid[i][j] == actual_grid[i][j]:
                            correct_cells += 1
            
            accuracy = correct_cells / total_cells if total_cells > 0 else 0.0
            
            details["metrics"] = {
                "correct_cells": correct_cells,
                "total_cells": total_cells,
                "accuracy": accuracy
            }
            
            return accuracy, details
            
        except Exception as e:
            details["error"] = str(e)
            return 0.0, details
    
    def _calculate_graph_reward(self, expected: str, actual: str) -> Tuple[float, Dict[str, Any]]:
        """计算图论任务的reward"""
        details = {
            "type": "graph",
            "metrics": {}
        }
        
        try:
            # 尝试解析为数值（最短路径等）
            try:
                expected_val = float(expected.strip())
                actual_val = float(actual.strip())
                
                # 如果是数值，检查是否相等
                if abs(expected_val - actual_val) < 1e-6:
                    reward = 1.0
                else:
                    # 根据相对误差给部分分
                    relative_error = abs(expected_val - actual_val) / abs(expected_val)
                    reward = max(0, 1 - relative_error)
                
                details["metrics"] = {
                    "expected_value": expected_val,
                    "actual_value": actual_val,
                    "relative_error": relative_error if 'relative_error' in locals() else 0
                }
                
                return reward, details
                
            except:
                # 如果不是数值，使用字符串匹配
                return self._calculate_exact_match_reward(expected, actual)
                
        except Exception as e:
            details["error"] = str(e)
            return 0.0, details
    
    def _calculate_exact_match_reward(self, expected: str, actual: str) -> Tuple[float, Dict[str, Any]]:
        """精确匹配计算reward"""
        details = {
            "type": "exact_match",
            "metrics": {}
        }
        
        # 标准化字符串
        expected_clean = self._normalize_string(expected)
        actual_clean = self._normalize_string(actual)
        
        # 完全匹配
        if expected_clean == actual_clean:
            reward = 1.0
            details["metrics"]["match"] = True
        else:
            # 计算相似度
            similarity = self._string_similarity(expected_clean, actual_clean)
            reward = similarity * 0.5  # 部分分最多0.5
            details["metrics"]["match"] = False
            details["metrics"]["similarity"] = similarity
        
        details["metrics"]["expected_normalized"] = expected_clean
        details["metrics"]["actual_normalized"] = actual_clean
        
        return reward, details
    
    def _parse_grid(self, grid_str: str) -> Optional[List[List[int]]]:
        """解析网格字符串"""
        try:
            lines = grid_str.strip().split('\n')
            grid = []
            for line in lines:
                if line.strip():
                    row = [int(x) for x in line.split()]
                    grid.append(row)
            return grid if grid else None
        except:
            return None
    
    def _parse_mine_positions(self, mine_str: str) -> Optional[List[Tuple[int, int]]]:
        """解析地雷位置"""
        try:
            # 尝试JSON格式
            if mine_str.strip().startswith('{'):
                mine_dict = json.loads(mine_str)
                positions = []
                for key in mine_dict:
                    # 解析 "(x,y)" 格式
                    match = re.match(r'\((\d+),\s*(\d+)\)', key)
                    if match:
                        positions.append((int(match.group(1)), int(match.group(2))))
                return positions
            else:
                # 尝试其他格式
                positions = []
                for match in re.finditer(r'\((\d+),\s*(\d+)\)', mine_str):
                    positions.append((int(match.group(1)), int(match.group(2))))
                return positions
        except:
            return None
    
    def _check_sudoku_rows(self, grid: List[List[int]]) -> float:
        """检查数独行约束"""
        n = len(grid)
        valid_rows = 0
        for row in grid:
            if len(set(row)) == n and all(1 <= x <= n for x in row):
                valid_rows += 1
        return valid_rows / n
    
    def _check_sudoku_cols(self, grid: List[List[int]]) -> float:
        """检查数独列约束"""
        n = len(grid)
        valid_cols = 0
        for j in range(n):
            col = [grid[i][j] for i in range(n)]
            if len(set(col)) == n and all(1 <= x <= n for x in col):
                valid_cols += 1
        return valid_cols / n
    
    def _check_sudoku_regions(self, grid: List[List[int]]) -> float:
        """检查数独区域约束"""
        n = len(grid)
        region_size = int(np.sqrt(n))
        if region_size * region_size != n:
            return 1.0  # 不是标准数独，跳过区域检查
        
        valid_regions = 0
        total_regions = region_size * region_size
        
        for r in range(region_size):
            for c in range(region_size):
                region = []
                for i in range(r * region_size, (r + 1) * region_size):
                    for j in range(c * region_size, (c + 1) * region_size):
                        region.append(grid[i][j])
                if len(set(region)) == n and all(1 <= x <= n for x in region):
                    valid_regions += 1
        
        return valid_regions / total_regions
    
    def _normalize_string(self, s: str) -> str:
        """标准化字符串"""
        # 移除空白字符
        s = ' '.join(s.split())
        # 转小写
        s = s.lower()
        # 移除标点符号
        s = re.sub(r'[^\w\s]', '', s)
        return s.strip()
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度"""
        # 简单的字符级相似度
        if not s1 or not s2:
            return 0.0
        
        # 计算最长公共子序列
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs = dp[m][n]
        return (2.0 * lcs) / (m + n)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取reward计算统计信息"""
        if not self.calculation_history:
            return {}
        
        rewards = [r['reward'] for r in self.calculation_history]
        success_count = sum(1 for r in self.calculation_history if r['success'])
        
        stats = {
            "total_calculations": len(self.calculation_history),
            "successful_calculations": success_count,
            "success_rate": success_count / len(self.calculation_history),
            "average_reward": sum(rewards) / len(rewards),
            "max_reward": max(rewards),
            "min_reward": min(rewards),
            "std_reward": np.std(rewards),
            "by_task": {}
        }
        
        # 按任务统计
        task_rewards = {}
        for record in self.calculation_history:
            task = record['task_name']
            if task not in task_rewards:
                task_rewards[task] = []
            task_rewards[task].append(record['reward'])
        
        for task, rewards in task_rewards.items():
            stats["by_task"][task] = {
                "count": len(rewards),
                "average_reward": sum(rewards) / len(rewards),
                "success_rate": sum(1 for r in rewards if r > 0) / len(rewards)
            }
        
        return stats
    
    def save_history(self, filepath: str):
        """保存计算历史"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "history": self.calculation_history,
                "statistics": self.get_statistics(),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)


# 全局计算器实例
global_calculator = RewardCalculator()


def calculate_reward(task_name: str, example: Dict[str, Any], output: str) -> float:
    """简化的reward计算接口"""
    result = global_calculator.calculate_reward(task_name, example, output, detailed=False)
    return result['reward']