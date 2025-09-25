#!/usr/bin/env python
"""
Main Script - 主运行脚本
Workflow评估系统的入口点
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List
import json

# 导入模块
from data_processor import DataProcessor
from workflow_executor import WorkflowExecutor
from result_analyzer import ResultAnalyzer
from report_generator import ReportGenerator
from utils import (
    load_config, setup_logging, ProgressTracker,
    format_time, validate_workflow_code
)


class WorkflowEvaluatorSystem:
    """Workflow评估系统主类"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化系统

        Args:
            config_path: 配置文件路径
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config)

        # 初始化各组件
        self.processor = DataProcessor(self.config)
        self.executor = WorkflowExecutor(self.config)
        self.analyzer = ResultAnalyzer(self.config)
        self.generator = ReportGenerator(self.config, self.analyzer)

        self.logger.info("Workflow评估系统初始化完成")

    async def run_full_pipeline(self, input_file: str, filters: Optional[Dict] = None):
        """
        运行完整的评估流程

        Args:
            input_file: 输入JSONL文件
            filters: 过滤条件
        """
        print("\n" + "="*80)
        print(" Workflow评估系统 - 完整流程")
        print("="*80)

        # Step 1: 数据处理
        print("\n[步骤 1/5] 数据处理")
        print("-"*40)
        processed_records = self.processor.process_file(input_file, filters)

        if not processed_records:
            print("错误: 没有可处理的记录")
            return

        # 保存处理后的数据
        processed_file = Path(self.config['io']['output_dir']) / 'raw' / 'processed_data.jsonl'
        self.processor.save_processed_data(processed_records, str(processed_file))

        # Step 2: 检查Reward Server
        print("\n[步骤 2/5] 检查Reward Server")
        print("-"*40)
        if not await self.executor.check_reward_server_health():
            print("错误: Reward Server未运行，请先启动服务器")
            return

        # Step 3: 执行测试（使用分组执行，每组完成后立即保存）
        print("\n[步骤 3/5] 执行Workflow测试（分组执行）")
        print("-"*40)

        # 获取并发数配置
        concurrency = self.config.get('test', {}).get('concurrency',
                     self.config.get('test', {}).get('batch_size', 8))  # 兼容旧配置
        output_dir = self.config.get('io', {}).get('output_dir', './results')

        # 使用新的分组执行方法
        results = await self.executor.execute_batch_grouped(
            processed_records,
            concurrency=concurrency,
            output_dir=output_dir
        )

        # 打印执行统计
        self.executor.print_statistics()

        # Step 4: 结果分析
        print("\n[步骤 4/5] 分析测试结果")
        print("-"*40)

        # 重新加载所有结果进行分析
        self.analyzer.load_results()
        self.analyzer.analyze_overall()
        self.analyzer.analyze_by_data_source()
        self.analyzer.analyze_by_operators()
        self.analyzer.save_statistics()
        self.analyzer.print_summary()

        # Step 5: 生成报告
        print("\n[步骤 5/5] 生成测试报告")
        print("-"*40)
        self.generator.generate_all_reports()

        print("\n" + "="*80)
        print(" 评估完成！")
        print("="*80)
        print(f"结果保存在: {self.config['io']['output_dir']}")

    async def run_single_test(self, workflow_code: str, data_source: str):
        """
        测试单个workflow

        Args:
            workflow_code: workflow代码
            data_source: 数据源
        """
        print("\n测试单个Workflow")
        print("-"*40)

        # 验证workflow代码
        is_valid, error_msg = validate_workflow_code(workflow_code)
        if not is_valid:
            print(f"错误: Workflow代码无效 - {error_msg}")
            return

        # 构建测试记录
        test_record = {
            'test_id': self.processor.generate_test_id({}),
            'data_source': data_source,
            'operators_group': 'custom',
            'input': {
                'workflow_code': workflow_code
            }
        }

        # 执行测试
        result = await self.executor.execute_single_workflow(test_record)

        # 显示结果
        print("\n测试结果:")
        print(f"  - 成功: {result.get('success', False)}")
        print(f"  - 分数: {result.get('score', 0.0):.3f}")
        print(f"  - 执行时间: {result.get('execution_time', 0):.2f}秒")

        if result.get('error'):
            print(f"  - 错误: {result['error']}")

        return result

    async def analyze_existing_results(self):
        """分析现有结果"""
        print("\n分析现有测试结果")
        print("-"*40)

        # 加载结果
        self.analyzer.load_results()

        if not self.analyzer.all_results:
            print("没有找到测试结果")
            return

        # 执行分析
        self.analyzer.analyze_overall()
        self.analyzer.analyze_by_data_source()
        self.analyzer.analyze_by_operators()

        # 保存统计
        self.analyzer.save_statistics()

        # 打印摘要
        self.analyzer.print_summary()

        # 生成报告
        print("\n生成分析报告...")
        self.generator.generate_all_reports()

        print("\n分析完成！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Workflow评估系统")

    # 添加命令行参数
    parser.add_argument(
        'command',
        choices=['test', 'analyze', 'single'],
        help='执行的命令: test(完整测试), analyze(分析现有结果), single(测试单个workflow)'
    )

    parser.add_argument(
        '--input',
        default='/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT',
        help='输入JSONL文件路径'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径'
    )

    parser.add_argument(
        '--data-source',
        choices=['gsm8k', 'mbpp', 'humaneval', 'drop', 'math500'],
        help='指定data_source (仅用于过滤或single命令)'
    )

    parser.add_argument(
        '--operators',
        help='指定operators组合，用逗号分隔 (如: generate,revise,summarize)'
    )

    parser.add_argument(
        '--workflow-file',
        help='包含workflow代码的文件 (仅用于single命令)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        help='限制测试数量'
    )

    parser.add_argument(
        '--concurrency',
        type=int,
        default=8,
        help='并发执行数量'
    )

    parser.add_argument(
        '--batch-size',  # 保留旧参数名以兼容
        type=int,
        dest='concurrency_legacy',
        help='批处理大小（已废弃，请使用--concurrency）'
    )

    args = parser.parse_args()

    # 创建系统实例
    system = WorkflowEvaluatorSystem(args.config)

    # 构建过滤器
    filters = {}
    if args.data_source:
        filters['data_sources'] = [args.data_source]
    if args.operators:
        filters['operators_groups'] = args.operators.split(',')

    # 执行命令
    if args.command == 'test':
        # 完整测试流程
        asyncio.run(system.run_full_pipeline(args.input, filters))

    elif args.command == 'analyze':
        # 分析现有结果
        asyncio.run(system.analyze_existing_results())

    elif args.command == 'single':
        # 测试单个workflow
        if not args.workflow_file:
            print("错误: single命令需要指定--workflow-file")
            sys.exit(1)

        if not args.data_source:
            print("错误: single命令需要指定--data-source")
            sys.exit(1)

        # 读取workflow代码
        with open(args.workflow_file, 'r', encoding='utf-8') as f:
            workflow_code = f.read()

        asyncio.run(system.run_single_test(workflow_code, args.data_source))


if __name__ == "__main__":
    main()