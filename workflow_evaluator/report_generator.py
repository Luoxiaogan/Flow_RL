#!/usr/bin/env python
"""
Report Generator - 报告生成器
用于生成测试报告和摘要
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class ReportGenerator:
    """报告生成器类"""

    def __init__(self, config: Dict, analyzer=None):
        """
        初始化报告生成器

        Args:
            config: 配置字典
            analyzer: ResultAnalyzer实例
        """
        self.config = config
        self.analyzer = analyzer
        self.results_dir = Path(config.get('io', {}).get('output_dir', './results'))
        self.summaries_dir = self.results_dir / 'summaries'
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown_report(self, statistics: Dict, report_type: str = "overall") -> str:
        """
        生成Markdown格式报告

        Args:
            statistics: 统计数据
            report_type: 报告类型 (overall, by_datasource, by_operators)

        Returns:
            Markdown格式的报告内容
        """
        lines = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 报告标题
        lines.append("# Workflow评估报告")
        lines.append(f"\n生成时间: {timestamp}")
        lines.append("\n---\n")

        if report_type == "overall":
            lines.extend(self._generate_overall_section(statistics))
        elif report_type == "by_datasource":
            lines.extend(self._generate_datasource_section(statistics))
        elif report_type == "by_operators":
            lines.extend(self._generate_operators_section(statistics))

        return '\n'.join(lines)

    def _generate_overall_section(self, stats: Dict) -> List[str]:
        """生成整体统计部分"""
        lines = []

        lines.append("## 📊 整体统计\n")

        # 基本指标
        lines.append("### 基本指标\n")
        lines.append(f"- **总测试数**: {stats.get('total_tests', 0)}")
        lines.append(f"- **成功数**: {stats.get('total_successful', 0)}")
        lines.append(f"- **失败数**: {stats.get('total_failed', 0)}")
        lines.append(f"- **成功率**: {stats.get('overall_success_rate', 0)*100:.1f}%")
        lines.append(f"- **平均分数**: {stats.get('overall_average_score', 0):.3f}")
        lines.append(f"- **分数标准差**: {stats.get('overall_score_std', 0):.3f}")
        lines.append(f"- **最高分**: {stats.get('overall_max_score', 0):.3f}")
        lines.append(f"- **最低分**: {stats.get('overall_min_score', 0):.3f}")
        lines.append("")

        # 执行性能
        lines.append("### ⚡ 执行性能\n")
        lines.append(f"- **平均执行时间**: {stats.get('avg_execution_time', 0):.2f}秒")
        lines.append(f"- **总执行时间**: {stats.get('total_execution_time', 0):.2f}秒")
        lines.append("")

        # 覆盖范围
        lines.append("### 📈 覆盖范围\n")
        lines.append(f"- **Data Sources数量**: {stats.get('unique_datasources', 0)}")
        lines.append(f"- **Operators组合数**: {stats.get('unique_operators', 0)}")
        lines.append("")

        return lines

    def _generate_datasource_section(self, stats: Dict) -> List[str]:
        """生成按data_source分类的部分"""
        lines = []

        lines.append("## 📁 按Data Source分类统计\n")

        for data_source, ds_stats in stats.items():
            lines.append(f"### {data_source}\n")

            # 基本统计
            lines.append("#### 基本统计")
            lines.append(f"- 测试总数: {ds_stats['total']}")
            lines.append(f"- 成功: {ds_stats['successful']}")
            lines.append(f"- 失败: {ds_stats['failed']}")
            lines.append(f"- 成功率: {ds_stats['success_rate']*100:.1f}%")
            lines.append(f"- 平均分: {ds_stats['average_score']:.3f}")

            if ds_stats.get('score_std', 0) > 0:
                lines.append(f"- 分数标准差: {ds_stats['score_std']:.3f}")
                lines.append(f"- 最高分: {ds_stats['max_score']:.3f}")
                lines.append(f"- 最低分: {ds_stats['min_score']:.3f}")

            lines.append(f"- 平均执行时间: {ds_stats['avg_execution_time']:.2f}秒")
            lines.append("")

            # Operators breakdown
            if ds_stats.get('operators_breakdown'):
                lines.append("#### Operators组合表现")
                lines.append("")
                lines.append("| Operators组合 | 测试数 | 成功率 | 平均分 |")
                lines.append("|-------------|--------|--------|--------|")

                for op_group, op_stats in ds_stats['operators_breakdown'].items():
                    success_rate = op_stats['success_rate'] * 100
                    avg_score = op_stats['average_score']
                    lines.append(f"| {op_group} | {op_stats['total']} | {success_rate:.1f}% | {avg_score:.3f} |")

                lines.append("")

            lines.append("---\n")

        return lines

    def _generate_operators_section(self, stats: Dict) -> List[str]:
        """生成按operators分类的部分"""
        lines = []

        lines.append("## 🔧 按Operators组合分类统计\n")

        for operators_group, op_stats in stats.items():
            lines.append(f"### {operators_group}\n")

            # 基本统计
            lines.append("#### 基本统计")
            lines.append(f"- 测试总数: {op_stats['total']}")
            lines.append(f"- 成功: {op_stats['successful']}")
            lines.append(f"- 失败: {op_stats['failed']}")
            lines.append(f"- 成功率: {op_stats['success_rate']*100:.1f}%")
            lines.append(f"- 平均分: {op_stats['average_score']:.3f}")

            if op_stats.get('score_std', 0) > 0:
                lines.append(f"- 分数标准差: {op_stats['score_std']:.3f}")

            lines.append(f"- 平均执行时间: {op_stats['avg_execution_time']:.2f}秒")
            lines.append("")

            # DataSource breakdown
            if op_stats.get('datasource_breakdown'):
                lines.append("#### 在不同Data Source上的表现")
                lines.append("")
                lines.append("| Data Source | 测试数 | 成功率 | 平均分 |")
                lines.append("|------------|--------|--------|--------|")

                for ds, ds_stats in op_stats['datasource_breakdown'].items():
                    success_rate = ds_stats['success_rate'] * 100
                    avg_score = ds_stats['average_score']
                    lines.append(f"| {ds} | {ds_stats['total']} | {success_rate:.1f}% | {avg_score:.3f} |")

                lines.append("")

            lines.append("---\n")

        return lines

    def generate_complete_report(self) -> str:
        """
        生成完整报告

        Returns:
            完整的Markdown报告
        """
        if not self.analyzer:
            return "错误: 未提供分析器实例"

        lines = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 报告标题
        lines.append("# 📊 Workflow评估完整报告")
        lines.append(f"\n**生成时间**: {timestamp}")
        lines.append("\n---\n")

        # 执行摘要
        lines.append("## 📋 执行摘要\n")
        lines.append("本报告包含Workflow测试的完整分析结果，按以下维度组织：")
        lines.append("1. 整体统计 - 所有测试的汇总指标")
        lines.append("2. Data Source分析 - 按benchmark分类的详细统计")
        lines.append("3. Operators分析 - 按operator组合分类的表现")
        lines.append("4. 最佳表现 - 表现最好的组合排名")
        lines.append("5. 错误分析 - 失败案例的分类和分析")
        lines.append("\n---\n")

        # 整体统计
        if self.analyzer.overall_statistics:
            lines.extend(self._generate_overall_section(self.analyzer.overall_statistics))
            lines.append("\n---\n")

        # 按Data Source统计
        if self.analyzer.statistics_by_datasource:
            lines.extend(self._generate_datasource_section(self.analyzer.statistics_by_datasource))
            lines.append("\n---\n")

        # 按Operators统计
        if self.analyzer.statistics_by_operators:
            lines.extend(self._generate_operators_section(self.analyzer.statistics_by_operators))
            lines.append("\n---\n")

        # 最佳表现
        top_performers = self.analyzer.get_top_performers(5)
        if top_performers:
            lines.append("## 🏆 最佳表现组合\n")
            lines.append("### Top 5 (按平均分)\n")
            lines.append("| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |")
            lines.append("|------|------------|-----------|--------|--------|--------|")

            for idx, perf in enumerate(top_performers['top_by_score'], 1):
                lines.append(
                    f"| {idx} | {perf['data_source']} | {perf['operators_group']} | "
                    f"{perf['average_score']:.3f} | {perf['success_rate']*100:.1f}% | {perf['total_tests']} |"
                )

            lines.append("\n")

            if top_performers['bottom_by_score']:
                lines.append("### Bottom 5 (按平均分)\n")
                lines.append("| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |")
                lines.append("|------|------------|-----------|--------|--------|--------|")

                for idx, perf in enumerate(top_performers['bottom_by_score'], 1):
                    lines.append(
                        f"| {idx} | {perf['data_source']} | {perf['operators_group']} | "
                        f"{perf['average_score']:.3f} | {perf['success_rate']*100:.1f}% | {perf['total_tests']} |"
                    )

                lines.append("\n---\n")

        # 错误分析
        error_analysis = self.analyzer.get_error_analysis()
        if error_analysis and error_analysis['total_errors'] > 0:
            lines.append("## ❌ 错误分析\n")
            lines.append(f"**总错误数**: {error_analysis['total_errors']}\n")

            lines.append("### 错误类型分布\n")
            lines.append("| 错误类型 | 数量 | 占比 |")
            lines.append("|---------|------|------|")

            total_errors = error_analysis['total_errors']
            for error_type, count in error_analysis['error_types'].items():
                percentage = (count / total_errors) * 100 if total_errors > 0 else 0
                lines.append(f"| {error_type} | {count} | {percentage:.1f}% |")

            lines.append("\n")

        # 结论
        lines.append("## 📝 结论\n")
        lines.append("基于以上分析，可以得出以下结论：\n")

        # 自动生成一些结论
        if self.analyzer.overall_statistics:
            success_rate = self.analyzer.overall_statistics.get('overall_success_rate', 0) * 100
            avg_score = self.analyzer.overall_statistics.get('overall_average_score', 0)

            if success_rate > 80:
                lines.append(f"1. ✅ 整体成功率较高 ({success_rate:.1f}%)，表明workflow执行稳定")
            elif success_rate > 60:
                lines.append(f"1. ⚠️ 整体成功率中等 ({success_rate:.1f}%)，仍有改进空间")
            else:
                lines.append(f"1. ❌ 整体成功率较低 ({success_rate:.1f}%)，需要重点优化")

            if avg_score > 0.8:
                lines.append(f"2. ✅ 平均分数较高 ({avg_score:.3f})，workflow质量良好")
            elif avg_score > 0.6:
                lines.append(f"2. ⚠️ 平均分数中等 ({avg_score:.3f})，可以进一步优化")
            else:
                lines.append(f"2. ❌ 平均分数较低 ({avg_score:.3f})，需要改进workflow设计")

        lines.append("\n---\n")
        lines.append("*报告结束*")

        return '\n'.join(lines)

    def save_report(self, content: str, filename: str):
        """
        保存报告到文件

        Args:
            content: 报告内容
            filename: 文件名
        """
        report_path = self.summaries_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"报告已保存至: {report_path}")

    def generate_all_reports(self):
        """生成所有报告"""
        if not self.analyzer:
            print("错误: 未提供分析器实例")
            return

        # 生成完整报告
        complete_report = self.generate_complete_report()
        self.save_report(complete_report, "complete_analysis.md")

        # 按data_source生成单独报告
        if self.analyzer.statistics_by_datasource:
            for data_source in self.analyzer.statistics_by_datasource:
                ds_report = self.generate_markdown_report(
                    {data_source: self.analyzer.statistics_by_datasource[data_source]},
                    "by_datasource"
                )
                self.save_report(ds_report, f"by_data_source/{data_source}_summary.md")

        print("\n所有报告已生成完毕")


def main():
    """主函数 - 用于测试"""
    import yaml
    from result_analyzer import ResultAnalyzer

    # 加载配置
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 创建分析器
    analyzer = ResultAnalyzer(config)
    analyzer.load_results()

    if analyzer.all_results:
        # 执行分析
        analyzer.analyze_overall()
        analyzer.analyze_by_data_source()
        analyzer.analyze_by_operators()

        # 创建报告生成器
        generator = ReportGenerator(config, analyzer)

        # 生成所有报告
        generator.generate_all_reports()
    else:
        print("没有找到测试结果，无法生成报告")


if __name__ == "__main__":
    main()