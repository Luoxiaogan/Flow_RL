"""
Incremental report generator for hierarchical evaluation with real-time updates
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class IncrementalReportGenerator(ReportGenerator):
    """
    Enhanced report generator with incremental and hierarchical reporting capabilities
    """
    
    def __init__(self, output_dir: str = 'evaluation_reports'):
        """
        Initialize incremental report generator
        
        Args:
            output_dir: Base directory for reports
        """
        super().__init__(output_dir)
        
        # Tracking for incremental updates
        self.current_progress = {
            'models_completed': 0,
            'benchmarks_completed': 0,
            'operator_groups_completed': 0,
            'samples_evaluated': 0,
            'last_update': datetime.now().isoformat()
        }
        
        # Dashboard file for real-time monitoring
        self.dashboard_file = self.output_dir / 'evaluation_dashboard.html'
        
        logger.info(f"增量报告生成器初始化完成")
    
    def generate_operator_report(self, model: str, benchmark: str, 
                                operator_group: str, scores: List[Dict],
                                samples: List[Dict]) -> Dict:
        """
        Generate report for a single operator group
        
        Args:
            model: Model name
            benchmark: Benchmark name
            operator_group: Operator group name
            scores: Evaluation scores
            samples: Original samples
            
        Returns:
            Operator group report
        """
        logger.info(f"生成Operator组报告: {model}/{benchmark}/{operator_group}")
        
        # Calculate statistics
        stats = self._calculate_operator_statistics(scores, samples)
        
        # Create report
        report = {
            'hierarchy': {
                'model': model,
                'benchmark': benchmark,
                'operator_group': operator_group
            },
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'num_samples': len(scores),
            'sample_details': self._create_sample_details(scores, samples)
        }
        
        # Save operator report
        report_dir = self.output_dir / model / benchmark / operator_group
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_path = report_dir / 'operator_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate operator markdown
        self._generate_operator_markdown(report_dir, report)
        
        # Update progress
        self.current_progress['operator_groups_completed'] += 1
        self.current_progress['samples_evaluated'] += len(scores)
        
        return report
    
    def generate_benchmark_report(self, model: str, benchmark: str,
                                 operator_reports: Dict[str, Dict],
                                 all_scores: List[Dict]) -> Dict:
        """
        Generate report for a complete benchmark
        
        Args:
            model: Model name
            benchmark: Benchmark name
            operator_reports: Dictionary of operator group reports
            all_scores: All scores for this benchmark
            
        Returns:
            Benchmark report
        """
        logger.info(f"生成Benchmark报告: {model}/{benchmark}")
        
        # Aggregate statistics
        benchmark_stats = self._aggregate_benchmark_statistics(operator_reports, all_scores)
        
        # Create report
        report = {
            'hierarchy': {
                'model': model,
                'benchmark': benchmark
            },
            'timestamp': datetime.now().isoformat(),
            'statistics': benchmark_stats,
            'operator_groups': {
                name: {
                    'statistics': op_report['statistics'],
                    'num_samples': op_report['num_samples']
                }
                for name, op_report in operator_reports.items()
            },
            'total_samples': len(all_scores)
        }
        
        # Save benchmark report
        report_dir = self.output_dir / model / benchmark
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_path = report_dir / 'benchmark_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate benchmark visualization
        self._generate_benchmark_charts(report_dir, report)
        
        # Generate benchmark markdown
        self._generate_benchmark_markdown(report_dir, report)
        
        # Update progress
        self.current_progress['benchmarks_completed'] += 1
        
        return report
    
    def generate_model_summary(self, model: str, benchmark_reports: Dict[str, Dict],
                              all_scores: List[Dict]) -> Dict:
        """
        Generate summary report for a complete model evaluation
        
        Args:
            model: Model name
            benchmark_reports: Dictionary of benchmark reports
            all_scores: All scores for this model
            
        Returns:
            Model summary report
        """
        logger.info(f"生成模型总结报告: {model}")
        
        # Calculate overall statistics
        model_stats = self._calculate_model_statistics(benchmark_reports, all_scores)
        
        # Create summary
        summary = {
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'overall_statistics': model_stats,
            'benchmarks': {
                name: {
                    'statistics': report['statistics'],
                    'num_samples': report['total_samples']
                }
                for name, report in benchmark_reports.items()
            },
            'total_samples': len(all_scores),
            'evaluation_time': self._calculate_total_time(benchmark_reports)
        }
        
        # Save model summary
        model_dir = self.output_dir / model
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON summary
        json_path = model_dir / 'model_summary.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Generate model charts
        self._generate_model_charts(model_dir, summary)
        
        # Generate model markdown
        self._generate_model_markdown(model_dir, summary)
        
        # Update progress
        self.current_progress['models_completed'] += 1
        
        # Update dashboard
        self.update_dashboard()
        
        return summary
    
    def update_dashboard(self):
        """
        Update real-time evaluation dashboard
        """
        try:
            html_content = self._generate_dashboard_html()
            
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.debug(f"评估面板已更新: {self.dashboard_file}")
            
        except Exception as e:
            logger.warning(f"更新面板失败: {e}")
    
    def generate_detailed_sample_report(self, model: str, benchmark: str,
                                       operator_group: str, sample_idx: int,
                                       sample: Dict, solution: str,
                                       score: Dict) -> str:
        """
        Generate detailed report for a single sample
        
        Args:
            model: Model name
            benchmark: Benchmark name
            operator_group: Operator group name
            sample_idx: Sample index
            sample: Original sample
            solution: Generated solution
            score: Evaluation score
            
        Returns:
            Path to sample report
        """
        # Create sample report
        sample_report = {
            'hierarchy': {
                'model': model,
                'benchmark': benchmark,
                'operator_group': operator_group,
                'sample_index': sample_idx
            },
            'timestamp': datetime.now().isoformat(),
            'input': {
                'data_source': sample.get('data_source'),
                'prompt': sample.get('prompt'),
                'extra_info': sample.get('extra_info', {})
            },
            'output': {
                'solution': solution,
                'solution_length': len(solution)
            },
            'evaluation': {
                'success': score.get('success', False),
                'score': score.get('score', 0.0),
                'error': score.get('error'),
                'execution_time': score.get('execution_time')
            }
        }
        
        # Save sample report
        sample_dir = self.output_dir / model / benchmark / operator_group / 'samples'
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        sample_path = sample_dir / f'sample_{sample_idx:04d}.json'
        with open(sample_path, 'w', encoding='utf-8') as f:
            json.dump(sample_report, f, indent=2, ensure_ascii=False)
        
        return str(sample_path)
    
    def _calculate_operator_statistics(self, scores: List[Dict], 
                                      samples: List[Dict]) -> Dict:
        """
        Calculate statistics for operator group
        """
        successful = [s for s in scores if s.get('success', False)]
        
        stats = {
            'total': len(scores),
            'successful': len(successful),
            'failed': len(scores) - len(successful),
            'success_rate': len(successful) / len(scores) if scores else 0.0
        }
        
        if successful:
            score_values = [s.get('score', 0.0) for s in successful]
            stats.update({
                'mean_score': sum(score_values) / len(score_values),
                'max_score': max(score_values),
                'min_score': min(score_values),
                'std_score': pd.Series(score_values).std() if len(score_values) > 1 else 0.0
            })
        else:
            stats.update({
                'mean_score': 0.0,
                'max_score': 0.0,
                'min_score': 0.0,
                'std_score': 0.0
            })
        
        # Add data source breakdown
        data_sources = {}
        for sample in samples:
            source = sample.get('data_source', 'unknown')
            if source not in data_sources:
                data_sources[source] = 0
            data_sources[source] += 1
        stats['data_sources'] = data_sources
        
        return stats
    
    def _aggregate_benchmark_statistics(self, operator_reports: Dict[str, Dict],
                                       all_scores: List[Dict]) -> Dict:
        """
        Aggregate statistics across operator groups for benchmark
        """
        # Calculate overall benchmark statistics
        stats = self._calculate_statistics(all_scores, [])
        
        # Add operator group breakdown
        operator_stats = {}
        for name, report in operator_reports.items():
            operator_stats[name] = {
                'success_rate': report['statistics']['success_rate'],
                'mean_score': report['statistics']['mean_score'],
                'num_samples': report['num_samples']
            }
        
        stats['operator_breakdown'] = operator_stats
        
        # Calculate variance across operators
        if operator_stats:
            success_rates = [s['success_rate'] for s in operator_stats.values()]
            mean_scores = [s['mean_score'] for s in operator_stats.values()]
            
            stats['operator_variance'] = {
                'success_rate_std': pd.Series(success_rates).std(),
                'mean_score_std': pd.Series(mean_scores).std()
            }
        
        return stats
    
    def _calculate_model_statistics(self, benchmark_reports: Dict[str, Dict],
                                   all_scores: List[Dict]) -> Dict:
        """
        Calculate overall model statistics
        """
        # Overall statistics
        stats = self._calculate_statistics(all_scores, [])
        
        # Benchmark breakdown
        benchmark_stats = {}
        for name, report in benchmark_reports.items():
            benchmark_stats[name] = {
                'success_rate': report['statistics']['success_rate'],
                'mean_score': report['statistics']['mean_score'],
                'num_samples': report['total_samples']
            }
        
        stats['benchmark_breakdown'] = benchmark_stats
        
        # Calculate variance across benchmarks
        if benchmark_stats:
            success_rates = [s['success_rate'] for s in benchmark_stats.values()]
            mean_scores = [s['mean_score'] for s in benchmark_stats.values()]
            
            stats['benchmark_variance'] = {
                'success_rate_std': pd.Series(success_rates).std(),
                'mean_score_std': pd.Series(mean_scores).std()
            }
        
        return stats
    
    def _create_sample_details(self, scores: List[Dict], samples: List[Dict]) -> List[Dict]:
        """
        Create detailed information for each sample
        """
        details = []
        for i, (score, sample) in enumerate(zip(scores, samples)):
            detail = {
                'index': i,
                'data_source': sample.get('data_source'),
                'success': score.get('success', False),
                'score': score.get('score', 0.0),
                'error': score.get('error')
            }
            
            # Add key extra info if available
            extra_info = sample.get('extra_info', {})
            if 'test_cases' in extra_info:
                detail['num_test_cases'] = len(extra_info['test_cases'])
            
            details.append(detail)
        
        return details
    
    def _calculate_total_time(self, benchmark_reports: Dict[str, Dict]) -> float:
        """
        Calculate total evaluation time from benchmark reports
        """
        # This would need actual timing information from the evaluation process
        # For now, return a placeholder
        return 0.0
    
    def _generate_operator_markdown(self, report_dir: Path, report: Dict):
        """
        Generate markdown report for operator group
        """
        md_path = report_dir / 'README.md'
        
        with open(md_path, 'w', encoding='utf-8') as f:
            hierarchy = report['hierarchy']
            stats = report['statistics']
            
            f.write(f"# Operator Group Report\n\n")
            f.write(f"**Model**: {hierarchy['model']}\n")
            f.write(f"**Benchmark**: {hierarchy['benchmark']}\n")
            f.write(f"**Operator Group**: {hierarchy['operator_group']}\n")
            f.write(f"**Generated**: {report['timestamp']}\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- Total Samples: {stats['total']}\n")
            f.write(f"- Success Rate: {stats['success_rate']:.1%}\n")
            f.write(f"- Mean Score: {stats['mean_score']:.3f}\n")
            f.write(f"- Max Score: {stats['max_score']:.3f}\n")
            f.write(f"- Min Score: {stats['min_score']:.3f}\n\n")
            
            if 'sample_details' in report and report['sample_details']:
                f.write("## Sample Results\n\n")
                f.write("| Index | Success | Score | Error |\n")
                f.write("|-------|---------|-------|--------|\n")
                
                for detail in report['sample_details'][:10]:  # Show first 10
                    success = "✓" if detail['success'] else "✗"
                    score = f"{detail['score']:.3f}"
                    error = detail.get('error', '-')[:30]
                    f.write(f"| {detail['index']} | {success} | {score} | {error} |\n")
                
                if len(report['sample_details']) > 10:
                    f.write(f"\n*Showing first 10 of {len(report['sample_details'])} samples*\n")
    
    def _generate_benchmark_charts(self, report_dir: Path, report: Dict):
        """
        Generate visualization charts for benchmark
        """
        try:
            stats = report['statistics']
            operator_breakdown = stats.get('operator_breakdown', {})
            
            if not operator_breakdown:
                return
            
            # Create figure with subplots
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot 1: Success rates by operator group
            operators = list(operator_breakdown.keys())
            success_rates = [operator_breakdown[op]['success_rate'] for op in operators]
            
            axes[0].bar(operators, success_rates)
            axes[0].set_title('Success Rate by Operator Group')
            axes[0].set_ylabel('Success Rate')
            axes[0].set_ylim(0, 1)
            axes[0].tick_params(axis='x', rotation=45)
            
            # Plot 2: Mean scores by operator group
            mean_scores = [operator_breakdown[op]['mean_score'] for op in operators]
            
            axes[1].bar(operators, mean_scores)
            axes[1].set_title('Mean Score by Operator Group')
            axes[1].set_ylabel('Mean Score')
            axes[1].set_ylim(0, 1)
            axes[1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(report_dir / 'benchmark_charts.png', dpi=100)
            plt.close()
            
        except Exception as e:
            logger.warning(f"生成benchmark图表失败: {e}")
    
    def _generate_benchmark_markdown(self, report_dir: Path, report: Dict):
        """
        Generate markdown report for benchmark
        """
        md_path = report_dir / 'README.md'
        
        with open(md_path, 'w', encoding='utf-8') as f:
            hierarchy = report['hierarchy']
            stats = report['statistics']
            
            f.write(f"# Benchmark Report\n\n")
            f.write(f"**Model**: {hierarchy['model']}\n")
            f.write(f"**Benchmark**: {hierarchy['benchmark']}\n")
            f.write(f"**Generated**: {report['timestamp']}\n\n")
            
            f.write("## Overall Statistics\n\n")
            f.write(f"- Total Samples: {report['total_samples']}\n")
            f.write(f"- Success Rate: {stats['success_rate']:.1%}\n")
            f.write(f"- Mean Score: {stats['mean_score']:.3f}\n\n")
            
            if 'operator_breakdown' in stats:
                f.write("## Operator Group Performance\n\n")
                f.write("| Operator Group | Samples | Success Rate | Mean Score |\n")
                f.write("|----------------|---------|--------------|------------|\n")
                
                for op_name, op_stats in stats['operator_breakdown'].items():
                    f.write(f"| {op_name} ")
                    f.write(f"| {op_stats['num_samples']} ")
                    f.write(f"| {op_stats['success_rate']:.1%} ")
                    f.write(f"| {op_stats['mean_score']:.3f} |\n")
            
            f.write("\n![Benchmark Charts](benchmark_charts.png)\n")
    
    def _generate_model_charts(self, model_dir: Path, summary: Dict):
        """
        Generate visualization charts for model
        """
        try:
            stats = summary['overall_statistics']
            benchmark_breakdown = stats.get('benchmark_breakdown', {})
            
            if not benchmark_breakdown:
                return
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            benchmarks = list(benchmark_breakdown.keys())
            success_rates = [benchmark_breakdown[b]['success_rate'] for b in benchmarks]
            mean_scores = [benchmark_breakdown[b]['mean_score'] for b in benchmarks]
            
            # Create grouped bar chart
            x = range(len(benchmarks))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], success_rates, width, label='Success Rate')
            ax.bar([i + width/2 for i in x], mean_scores, width, label='Mean Score')
            
            ax.set_xlabel('Benchmark')
            ax.set_ylabel('Score')
            ax.set_title(f'Model Performance: {summary["model"]}')
            ax.set_xticks(x)
            ax.set_xticklabels(benchmarks)
            ax.legend()
            ax.set_ylim(0, 1)
            
            plt.tight_layout()
            plt.savefig(model_dir / 'model_performance.png', dpi=100)
            plt.close()
            
        except Exception as e:
            logger.warning(f"生成模型图表失败: {e}")
    
    def _generate_model_markdown(self, model_dir: Path, summary: Dict):
        """
        Generate markdown summary for model
        """
        md_path = model_dir / 'README.md'
        
        with open(md_path, 'w', encoding='utf-8') as f:
            stats = summary['overall_statistics']
            
            f.write(f"# Model Evaluation Summary\n\n")
            f.write(f"**Model**: {summary['model']}\n")
            f.write(f"**Generated**: {summary['timestamp']}\n")
            f.write(f"**Total Samples**: {summary['total_samples']}\n\n")
            
            f.write("## Overall Performance\n\n")
            f.write(f"- Success Rate: {stats['success_rate']:.1%}\n")
            f.write(f"- Mean Score: {stats['mean_score']:.3f}\n")
            f.write(f"- Max Score: {stats['max_score']:.3f}\n")
            f.write(f"- Min Score: {stats['min_score']:.3f}\n\n")
            
            if 'benchmark_breakdown' in stats:
                f.write("## Benchmark Breakdown\n\n")
                f.write("| Benchmark | Samples | Success Rate | Mean Score |\n")
                f.write("|-----------|---------|--------------|------------|\n")
                
                for b_name, b_stats in stats['benchmark_breakdown'].items():
                    f.write(f"| {b_name} ")
                    f.write(f"| {b_stats['num_samples']} ")
                    f.write(f"| {b_stats['success_rate']:.1%} ")
                    f.write(f"| {b_stats['mean_score']:.3f} |\n")
            
            f.write("\n![Model Performance](model_performance.png)\n")
    
    def _generate_dashboard_html(self) -> str:
        """
        Generate HTML content for evaluation dashboard
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Evaluation Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .timestamp {{
            color: #95a5a6;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Model Evaluation Dashboard</h1>
        <p>Real-time evaluation progress monitoring</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{self.current_progress['models_completed']}</div>
            <div class="stat-label">Models Completed</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value">{self.current_progress['benchmarks_completed']}</div>
            <div class="stat-label">Benchmarks Completed</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value">{self.current_progress['operator_groups_completed']}</div>
            <div class="stat-label">Operator Groups</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value">{self.current_progress['samples_evaluated']}</div>
            <div class="stat-label">Samples Evaluated</div>
        </div>
    </div>
    
    <div class="timestamp">
        Last updated: {self.current_progress['last_update']}<br>
        Auto-refresh: every 10 seconds
    </div>
</body>
</html>
"""
        return html