#!/usr/bin/env python3
"""
智能批量过滤JSONL记录脚本
自动遍历workspace文件夹，根据CSV状态批量过滤训练数据
支持合并所有数据并随机打乱
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import sys
from datetime import datetime
from collections import defaultdict
import random


class WorkspaceFilter:
    """工作空间数据过滤器"""
    
    def __init__(self, root_dir: str, csv_key: str = 'ID', jsonl_key: str = 'workflow_id',
                 csv_target_key: str = 'Status', want_info: str = 'verified_correct',
                 enable_merge: bool = True):
        """
        初始化过滤器
        
        Args:
            root_dir: 根目录路径
            csv_key: CSV文件中的ID字段名
            jsonl_key: JSONL文件中的ID字段名
            csv_target_key: CSV中用于过滤的状态字段名
            want_info: 期望的状态值
            enable_merge: 是否启用数据合并功能
        """
        self.root_dir = Path(root_dir)
        self.csv_key = csv_key
        self.jsonl_key = jsonl_key
        self.csv_target_key = csv_target_key
        self.want_info = want_info
        self.enable_merge = enable_merge
        self.statistics = defaultdict(dict)
        
        # 用于收集所有数据（合并功能）
        self.all_filtered_records = []
        self.all_original_records = []
        
    def find_workspace_dirs(self) -> List[Path]:
        """查找所有workspace开头的目录"""
        workspace_dirs = []
        for item in self.root_dir.iterdir():
            if item.is_dir() and item.name.startswith('workspace_'):
                workspace_dirs.append(item)
        return sorted(workspace_dirs)
    
    def find_training_file(self, workspace_dir: Path) -> Optional[Path]:
        """查找training_*_simple.jsonl文件"""
        pattern = 'training_*_simple.jsonl'
        files = list(workspace_dir.glob(pattern))
        
        if not files:
            # 如果没有simple文件，尝试查找普通的training文件
            pattern = 'training_*.jsonl'
            files = list(workspace_dir.glob(pattern))
            # 排除已经过滤的文件
            files = [f for f in files if 'filtered' not in f.name]
        
        if files:
            # 如果有多个文件，选择名字最短的（通常是simple版本）
            return min(files, key=lambda x: len(x.name))
        return None
    
    def find_csv_file(self, workspace_dir: Path) -> Optional[Path]:
        """查找execution_results.csv文件"""
        csv_file = workspace_dir / 'execution_results.csv'
        if csv_file.exists():
            return csv_file
        
        # 尝试其他可能的CSV文件名
        csv_files = list(workspace_dir.glob('*results*.csv'))
        if csv_files:
            return csv_files[0]
        return None
    
    def load_jsonl(self, filepath: Path) -> List[Dict[str, Any]]:
        """加载JSONL文件"""
        records = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"  ⚠️  警告: 第{line_num}行JSON解析失败: {e}")
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
        return records
    
    def load_csv_filter(self, filepath: Path) -> Tuple[set, Dict[str, int]]:
        """加载CSV并返回匹配的ID集合和状态统计"""
        matching_ids = set()
        status_counts = defaultdict(int)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    status = row.get(self.csv_target_key, 'unknown')
                    status_counts[status] += 1
                    
                    if status == self.want_info:
                        matching_ids.add(row[self.csv_key])
        except Exception as e:
            print(f"  ❌ 读取CSV失败: {e}")
            
        return matching_ids, dict(status_counts)
    
    def filter_jsonl_records(self, jsonl_records: List[Dict[str, Any]], 
                            matching_ids: set) -> List[Dict[str, Any]]:
        """过滤JSONL记录"""
        filtered = []
        for record in jsonl_records:
            if str(record.get(self.jsonl_key)) in matching_ids:
                filtered.append(record)
        return filtered
    
    def save_jsonl(self, records: List[Dict[str, Any]], filepath: Path):
        """保存JSONL文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            print(f"  ❌ 保存文件失败: {e}")
            return False
    
    def process_workspace(self, workspace_dir: Path) -> bool:
        """处理单个workspace目录"""
        print(f"\n{'='*60}")
        print(f"📁 处理: {workspace_dir.name}")
        print(f"{'='*60}")
        
        # 查找必要的文件
        training_file = self.find_training_file(workspace_dir)
        csv_file = self.find_csv_file(workspace_dir)
        
        if not training_file:
            print(f"  ⚠️  未找到training文件，跳过此目录")
            self.statistics[workspace_dir.name]['status'] = 'skipped'
            self.statistics[workspace_dir.name]['reason'] = 'no_training_file'
            return False
            
        if not csv_file:
            print(f"  ⚠️  未找到CSV文件，跳过此目录")
            self.statistics[workspace_dir.name]['status'] = 'skipped'
            self.statistics[workspace_dir.name]['reason'] = 'no_csv_file'
            return False
        
        print(f"  📄 训练文件: {training_file.name}")
        print(f"  📊 CSV文件: {csv_file.name}")
        
        # 加载数据
        jsonl_records = self.load_jsonl(training_file)
        print(f"  ✅ 加载了 {len(jsonl_records)} 条JSONL记录")
        
        # 收集原始数据（用于合并）
        if self.enable_merge:
            self.all_original_records.extend(jsonl_records)
        
        matching_ids, status_counts = self.load_csv_filter(csv_file)
        print(f"  📊 CSV状态分布:")
        for status, count in sorted(status_counts.items()):
            marker = "✅" if status == self.want_info else "  "
            print(f"    {marker} {status}: {count}")
        
        # 过滤记录
        filtered_records = self.filter_jsonl_records(jsonl_records, matching_ids)
        filter_rate = len(filtered_records) / len(jsonl_records) * 100 if jsonl_records else 0
        
        print(f"  🔍 过滤结果: {len(filtered_records)} 条记录 ({filter_rate:.1f}%)")
        
        # 收集过滤后的数据（用于合并）
        if self.enable_merge:
            self.all_filtered_records.extend(filtered_records)
        
        # 保存结果
        output_filename = f"filtered_{training_file.stem}.jsonl"
        output_path = workspace_dir / output_filename
        
        if self.save_jsonl(filtered_records, output_path):
            print(f"  💾 已保存到: {output_filename}")
            
            # 记录统计信息
            self.statistics[workspace_dir.name] = {
                'status': 'success',
                'input_records': len(jsonl_records),
                'csv_matches': len(matching_ids),
                'output_records': len(filtered_records),
                'filter_rate': filter_rate,
                'status_distribution': status_counts
            }
            return True
        else:
            self.statistics[workspace_dir.name]['status'] = 'failed'
            return False
    
    def merge_and_save_all_data(self):
        """合并并保存所有数据到根目录"""
        if not self.enable_merge:
            return
        
        print(f"\n{'='*60}")
        print(f"🔄 合并所有数据")
        print(f"{'='*60}")
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. 保存合并后的过滤数据
        if self.all_filtered_records:
            print(f"\n📊 过滤后的数据:")
            print(f"  总记录数: {len(self.all_filtered_records)}")
            
            # 随机打乱
            random.shuffle(self.all_filtered_records)
            print(f"  ✅ 已随机打乱顺序")
            
            # 保存文件
            filtered_merged_path = self.root_dir / f"merged_filtered_{timestamp}.jsonl"
            if self.save_jsonl(self.all_filtered_records, filtered_merged_path):
                print(f"  💾 已保存到: {filtered_merged_path.name}")
                
                # 同时保存一个不带时间戳的版本，方便使用
                filtered_merged_latest = self.root_dir / "merged_filtered_latest.jsonl"
                if self.save_jsonl(self.all_filtered_records, filtered_merged_latest):
                    print(f"  💾 已保存到: {filtered_merged_latest.name} (最新版本)")
        else:
            print(f"\n⚠️  没有过滤后的数据可合并")
        
        # 2. 保存合并后的原始数据
        if self.all_original_records:
            print(f"\n📊 原始数据:")
            print(f"  总记录数: {len(self.all_original_records)}")
            
            # 随机打乱
            random.shuffle(self.all_original_records)
            print(f"  ✅ 已随机打乱顺序")
            
            # 保存文件
            original_merged_path = self.root_dir / f"merged_original_{timestamp}.jsonl"
            if self.save_jsonl(self.all_original_records, original_merged_path):
                print(f"  💾 已保存到: {original_merged_path.name}")
                
                # 同时保存一个不带时间戳的版本，方便使用
                original_merged_latest = self.root_dir / "merged_original_latest.jsonl"
                if self.save_jsonl(self.all_original_records, original_merged_latest):
                    print(f"  💾 已保存到: {original_merged_latest.name} (最新版本)")
        else:
            print(f"\n⚠️  没有原始数据可合并")
        
        # 3. 打印合并统计
        if self.all_filtered_records or self.all_original_records:
            print(f"\n📈 合并统计:")
            print(f"  原始数据总量: {len(self.all_original_records)} 条")
            print(f"  过滤后数据总量: {len(self.all_filtered_records)} 条")
            if self.all_original_records:
                merge_filter_rate = len(self.all_filtered_records) / len(self.all_original_records) * 100
                print(f"  总体保留率: {merge_filter_rate:.1f}%")
    
    def run(self):
        """执行批量处理"""
        print(f"\n🚀 开始批量处理")
        print(f"📂 根目录: {self.root_dir}")
        print(f"🔍 过滤条件: {self.csv_target_key} = {self.want_info}")
        print(f"🔄 数据合并: {'启用' if self.enable_merge else '禁用'}")
        
        workspace_dirs = self.find_workspace_dirs()
        
        if not workspace_dirs:
            print("\n❌ 未找到任何workspace目录")
            return
        
        print(f"\n📊 找到 {len(workspace_dirs)} 个workspace目录")
        
        success_count = 0
        for workspace_dir in workspace_dirs:
            if self.process_workspace(workspace_dir):
                success_count += 1
        
        # 合并所有数据
        if self.enable_merge:
            self.merge_and_save_all_data()
        
        # 打印汇总统计
        self.print_summary(success_count, len(workspace_dirs))
    
    def print_summary(self, success_count: int, total_count: int):
        """打印汇总统计"""
        print(f"\n{'='*60}")
        print(f"📊 处理汇总")
        print(f"{'='*60}")
        print(f"✅ 成功处理: {success_count}/{total_count}")
        
        if self.statistics:
            print(f"\n📈 详细统计:")
            
            total_input = 0
            total_output = 0
            
            for workspace_name, stats in sorted(self.statistics.items()):
                if stats.get('status') == 'success':
                    print(f"\n  {workspace_name}:")
                    print(f"    输入记录: {stats['input_records']}")
                    print(f"    输出记录: {stats['output_records']}")
                    print(f"    过滤率: {stats['filter_rate']:.1f}%")
                    
                    total_input += stats['input_records']
                    total_output += stats['output_records']
                elif stats.get('status') == 'skipped':
                    print(f"\n  {workspace_name}: ⚠️  跳过 ({stats.get('reason', 'unknown')})")
                else:
                    print(f"\n  {workspace_name}: ❌ 失败")
            
            if total_input > 0:
                print(f"\n📊 总体统计:")
                print(f"  总输入记录: {total_input}")
                print(f"  总输出记录: {total_output}")
                print(f"  总体过滤率: {total_output/total_input*100:.1f}%")
        
        print(f"\n✨ 处理完成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """主函数"""
    # 配置参数
    root_dir = '/home/lg/workflow_tooluse/Flow_RL_luogan/Test_FILE'
    
    # 可以通过命令行参数覆盖默认路径
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    
    # 设置随机种子（可选，确保可重现性）
    # random.seed(42)
    
    # 创建过滤器并运行
    filter_processor = WorkspaceFilter(
        root_dir=root_dir,
        csv_key='ID',
        jsonl_key='workflow_id',
        csv_target_key='Status',
        want_info='verified_correct',
        enable_merge=True  # 启用数据合并功能
    )
    
    try:
        filter_processor.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断处理")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()