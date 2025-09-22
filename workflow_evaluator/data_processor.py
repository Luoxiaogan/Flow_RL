#!/usr/bin/env python
"""
Data Processor - 数据处理器
用于解析JSONL文件，提取workflow代码，并按data_source和operator分类
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib


class DataProcessor:
    """数据处理器类"""

    def __init__(self, config: Dict):
        """
        初始化数据处理器

        Args:
            config: 配置字典
        """
        self.config = config
        self.processed_count = 0
        self.error_count = 0
        self.classification_stats = {}

    def load_jsonl(self, file_path: str) -> List[Dict]:
        """
        加载JSONL文件

        Args:
            file_path: JSONL文件路径

        Returns:
            数据记录列表
        """
        records = []
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        print(f"正在加载文件: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"  警告: 第{line_num}行JSON解析失败: {e}")
                    self.error_count += 1
                    continue

        print(f"  成功加载 {len(records)} 条记录")
        return records

    def extract_workflow_code(self, record: Dict) -> Optional[str]:
        """
        从记录中提取workflow代码

        Args:
            record: 数据记录

        Returns:
            提取的workflow代码，如果提取失败返回None
        """
        try:
            # 从response字段中提取
            if 'response' in record:
                response = record['response']

                # 如果response是字典，获取content字段
                if isinstance(response, dict):
                    content = response.get('content', '')
                else:
                    content = str(response)

                # 提取```python和```之间的代码
                code_pattern = r'```python\s*(.*?)```'
                matches = re.findall(code_pattern, content, re.DOTALL)

                if matches:
                    # 返回最后一个匹配的代码块（通常是最完整的）
                    return matches[-1].strip()

                # 如果没有找到代码块，尝试查找class Workflow
                if 'class Workflow' in content:
                    # 提取从class Workflow开始到文件结束的内容
                    start_idx = content.find('class Workflow')
                    return content[start_idx:].strip()

            return None

        except Exception as e:
            print(f"  提取workflow代码失败: {e}")
            return None

    def classify_record(self, record: Dict) -> Tuple[str, str]:
        """
        对记录进行分类

        Args:
            record: 数据记录

        Returns:
            (data_source, operators_group_str) 元组
        """
        # 获取data_source，并移除可能存在的workflow_前缀
        data_source = record.get('data_source', 'unknown')
        if data_source.startswith('workflow_'):
            data_source = data_source[9:]  # 移除 'workflow_' 前缀

        # 获取operators_group并转换为字符串
        operators_group = record.get('operators_group', [])
        if isinstance(operators_group, list):
            operators_group_str = '_'.join(sorted(operators_group))
        else:
            operators_group_str = str(operators_group)

        # 如果为空，设置默认值
        if not operators_group_str:
            operators_group_str = 'unknown'

        return data_source, operators_group_str

    def generate_test_id(self, record: Dict) -> str:
        """
        生成测试ID

        Args:
            record: 数据记录

        Returns:
            唯一的测试ID
        """
        # 使用记录的关键信息生成哈希ID
        key_info = f"{record.get('data_source', '')}"
        key_info += f"{record.get('operators_group', '')}"
        key_info += f"{record.get('benchmark', '')}"
        key_info += f"{datetime.now().isoformat()}"

        hash_obj = hashlib.md5(key_info.encode())
        return hash_obj.hexdigest()[:12]

    def process_record(self, record: Dict) -> Optional[Dict]:
        """
        处理单条记录

        Args:
            record: 原始数据记录

        Returns:
            处理后的记录，如果处理失败返回None
        """
        try:
            # 提取workflow代码
            workflow_code = self.extract_workflow_code(record)
            if not workflow_code:
                print(f"  警告: 无法提取workflow代码")
                self.error_count += 1
                return None

            # 分类
            data_source, operators_group = self.classify_record(record)

            # 构建处理后的记录
            processed_record = {
                'test_id': self.generate_test_id(record),
                'timestamp': datetime.now().isoformat(),
                'data_source': data_source,
                'operators_group': operators_group,
                'original_operators_list': record.get('operators_group', []),
                'input': {
                    'prompt': record.get('prompt', ''),
                    'workflow_code': workflow_code,
                    'benchmark': record.get('benchmark', ''),
                    'extra_info': record.get('extra_info', {})
                },
                'metadata': {
                    'ability': record.get('ability', ''),
                    'reward_model': record.get('reward_model', {}),
                    'proportion': record.get('proportion', 0),
                    'operators_config_idx': record.get('operators_config_idx', 0)
                },
                'status': 'pending'  # 待测试
            }

            # 更新统计
            self.processed_count += 1
            self._update_stats(data_source, operators_group)

            return processed_record

        except Exception as e:
            print(f"  处理记录失败: {e}")
            self.error_count += 1
            return None

    def _update_stats(self, data_source: str, operators_group: str):
        """更新分类统计"""
        if data_source not in self.classification_stats:
            self.classification_stats[data_source] = {}

        if operators_group not in self.classification_stats[data_source]:
            self.classification_stats[data_source][operators_group] = 0

        self.classification_stats[data_source][operators_group] += 1

    def process_file(self, file_path: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        处理整个JSONL文件

        Args:
            file_path: JSONL文件路径
            filters: 过滤条件

        Returns:
            处理后的记录列表
        """
        print("\n" + "="*60)
        print("开始处理数据文件")
        print("="*60)

        # 加载数据
        records = self.load_jsonl(file_path)

        # 处理每条记录
        processed_records = []
        for idx, record in enumerate(records, 1):
            print(f"\n处理记录 {idx}/{len(records)}...")

            # 应用过滤器
            if filters:
                if not self._apply_filters(record, filters):
                    print(f"  跳过: 不符合过滤条件")
                    continue

            processed = self.process_record(record)
            if processed:
                processed_records.append(processed)

        # 打印统计信息
        self.print_statistics()

        return processed_records

    def _apply_filters(self, record: Dict, filters: Dict) -> bool:
        """应用过滤器"""
        # 检查data_source过滤
        if filters.get('data_sources'):
            if record.get('data_source') not in filters['data_sources']:
                return False

        # 检查operators_group过滤
        if filters.get('operators_groups'):
            operators = record.get('operators_group', [])
            if not any(op in filters['operators_groups'] for op in operators):
                return False

        return True

    def print_statistics(self):
        """打印处理统计信息"""
        print("\n" + "="*60)
        print("数据处理统计")
        print("="*60)
        print(f"总处理记录数: {self.processed_count}")
        print(f"错误记录数: {self.error_count}")
        print(f"成功率: {(self.processed_count/(self.processed_count+self.error_count)*100):.1f}%")

        print("\n分类统计:")
        for data_source, operators_stats in self.classification_stats.items():
            print(f"\n{data_source}:")
            for operators, count in operators_stats.items():
                print(f"  - {operators}: {count} 条")

    def save_processed_data(self, records: List[Dict], output_path: str):
        """
        保存处理后的数据

        Args:
            records: 处理后的记录列表
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"\n处理后的数据已保存至: {output_path}")


def main():
    """主函数 - 用于测试"""
    import yaml

    # 加载配置
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 创建处理器
    processor = DataProcessor(config)

    # 处理文件
    input_file = '../baseline/test_IMO_0922_QZH_with_responses.jsonl'
    if Path(input_file).exists():
        processed_records = processor.process_file(input_file)

        # 保存处理后的数据
        output_file = 'results/raw/processed_data.jsonl'
        processor.save_processed_data(processed_records, output_file)
    else:
        print(f"输入文件不存在: {input_file}")


if __name__ == "__main__":
    main()