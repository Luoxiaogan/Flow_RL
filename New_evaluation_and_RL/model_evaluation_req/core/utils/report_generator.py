"""
Report generator for evaluation results with model comparison
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates evaluation reports and comparison charts
    """
    
    def __init__(self, output_dir: str = 'evaluation_reports'):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir = self.output_dir / 'charts'
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"报告输出目录: {self.output_dir}")
    
    def generate_model_report(self, scores: List[Dict],
                             model_info: Dict,
                             test_samples: List[Dict]) -> Dict:
        """
        Generate evaluation report for a single model
        
        Args:
            scores: List of score results from reward server
            model_info: Information about the model
            test_samples: Original test samples
            
        Returns:
            Report dictionary
        """
        logger.info(f"生成模型评估报告: {model_info.get('name', 'unknown')}")
        
        report = {
            'model': model_info,
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(scores),
            'evaluation_results': self._calculate_statistics(scores, test_samples),
            'benchmark_scores': self._calculate_benchmark_scores(scores, test_samples),
            'overall_score': self._calculate_overall_score(scores),
            'success_rate': sum(1 for s in scores if s.get('success', False)) / len(scores) if scores else 0
        }
        
        # Save individual model report
        model_name = model_info.get('name', 'unknown').replace('/', '_')
        self._save_json_report(report, f"model_{model_name}")
        self._save_markdown_report(report, f"model_{model_name}")
        
        return report
    
    def generate_comparison_report(self, all_model_reports: Dict[str, Dict]) -> Dict:
        """
        Generate comparison report across multiple models
        
        Args:
            all_model_reports: Dictionary of model names to their reports
            
        Returns:
            Comparison report dictionary
        """
        if not all_model_reports:
            return {}
        
        logger.info(f"生成 {len(all_model_reports)} 个模型的对比报告")
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'num_models': len(all_model_reports),
            'models': [],
            'benchmark_comparison': {},
            'rankings': {}
        }
        
        # Extract data for comparison
        for model_name, report in all_model_reports.items():
            model_summary = {
                'name': model_name,
                'path': report['model'].get('path', ''),
                'overall_score': report['overall_score'],
                'success_rate': report['success_rate'],
                'total_samples': report['total_samples'],
                'benchmark_scores': report['benchmark_scores']
            }
            comparison['models'].append(model_summary)
        
        # Sort models by overall score
        comparison['models'] = sorted(
            comparison['models'], 
            key=lambda x: x['overall_score'], 
            reverse=True
        )
        
        # Generate benchmark comparison
        all_benchmarks = set()
        for model in comparison['models']:
            all_benchmarks.update(model['benchmark_scores'].keys())
        
        for benchmark in all_benchmarks:
            comparison['benchmark_comparison'][benchmark] = []
            for model in comparison['models']:
                if benchmark in model['benchmark_scores']:
                    comparison['benchmark_comparison'][benchmark].append({
                        'model': model['name'],
                        'score': model['benchmark_scores'][benchmark]['mean_score'],
                        'success_rate': model['benchmark_scores'][benchmark]['success_rate']
                    })
        
        # Generate rankings
        comparison['rankings'] = {
            'by_overall_score': [m['name'] for m in comparison['models']],
            'best_model': comparison['models'][0]['name'] if comparison['models'] else None,
            'worst_model': comparison['models'][-1]['name'] if comparison['models'] else None
        }
        
        # Save comparison report
        self._save_comparison_json(comparison)
        self._save_comparison_markdown(comparison)
        self._generate_comparison_charts(comparison)
        
        return comparison
    
    def _calculate_statistics(self, scores: List[Dict], 
                             test_samples: List[Dict]) -> Dict:
        """
        Calculate detailed statistics
        """
        successful_scores = [s.get('score', 0.0) for s in scores if s.get('success', False)]
        
        stats = {
            'total': len(scores),
            'successful': len(successful_scores),
            'failed': len(scores) - len(successful_scores),
            'mean_score': sum(successful_scores) / len(successful_scores) if successful_scores else 0.0,
            'max_score': max(successful_scores) if successful_scores else 0.0,
            'min_score': min(successful_scores) if successful_scores else 0.0,
            'std_score': pd.Series(successful_scores).std() if len(successful_scores) > 1 else 0.0
        }
        
        return stats
    
    def _calculate_benchmark_scores(self, scores: List[Dict], 
                                   test_samples: List[Dict]) -> Dict:
        """
        Calculate scores grouped by benchmark
        """
        benchmark_scores = {}
        
        # Group by data source
        data_sources = {}
        for i, sample in enumerate(test_samples):
            source = sample.get('data_source', 'unknown')
            
            # Extract benchmark name
            if source.startswith('workflow_'):
                benchmark = source.replace('workflow_', '')
            else:
                benchmark = source
            
            if benchmark not in data_sources:
                data_sources[benchmark] = []
            
            if i < len(scores):
                data_sources[benchmark].append(scores[i])
        
        # Calculate statistics for each benchmark
        for benchmark, benchmark_scores_list in data_sources.items():
            successful = [s.get('score', 0.0) for s in benchmark_scores_list if s.get('success', False)]
            
            benchmark_scores[benchmark] = {
                'num_samples': len(benchmark_scores_list),
                'num_successful': len(successful),
                'mean_score': sum(successful) / len(successful) if successful else 0.0,
                'max_score': max(successful) if successful else 0.0,
                'min_score': min(successful) if successful else 0.0,
                'std_score': pd.Series(successful).std() if len(successful) > 1 else 0.0,
                'success_rate': len(successful) / len(benchmark_scores_list) if benchmark_scores_list else 0.0
            }
        
        return benchmark_scores
    
    def _calculate_overall_score(self, scores: List[Dict]) -> float:
        """
        Calculate overall score
        """
        successful_scores = [s.get('score', 0.0) for s in scores if s.get('success', False)]
        
        if not successful_scores:
            return 0.0
        
        return sum(successful_scores) / len(successful_scores)
    
    def _save_json_report(self, report: Dict, filename: str):
        """
        Save report as JSON
        """
        json_path = self.output_dir / f"{filename}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"JSON 报告已保存: {json_path}")
    
    def _save_markdown_report(self, report: Dict, filename: str):
        """
        Save report as Markdown
        """
        md_path = self.output_dir / f"{filename}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            model_name = report['model'].get('name', 'Unknown Model')
            f.write(f"# Evaluation Report - {model_name}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Date**: {report['timestamp']}\n")
            f.write(f"- **Model Path**: {report['model'].get('path', 'N/A')}\n")
            f.write(f"- **Overall Score**: {report['overall_score']:.2%}\n")
            f.write(f"- **Success Rate**: {report['success_rate']:.2%}\n")
            f.write(f"- **Total Samples**: {report['total_samples']}\n\n")
            
            # Overall Statistics
            stats = report['evaluation_results']
            f.write("## Overall Statistics\n\n")
            f.write(f"- **Successful**: {stats['successful']}/{stats['total']}\n")
            f.write(f"- **Mean Score**: {stats['mean_score']:.3f}\n")
            f.write(f"- **Max Score**: {stats['max_score']:.3f}\n")
            f.write(f"- **Min Score**: {stats['min_score']:.3f}\n")
            f.write(f"- **Std Dev**: {stats['std_score']:.3f}\n\n")
            
            # Benchmark Performance
            f.write("## Benchmark Performance\n\n")
            
            if report.get('benchmark_scores'):
                f.write("| Benchmark | Samples | Success Rate | Mean Score | Max | Min | Std Dev |\n")
                f.write("|-----------|---------|--------------|------------|-----|-----|----------|\n")
                
                for benchmark, scores in sorted(report['benchmark_scores'].items()):
                    f.write(f"| {benchmark} ")
                    f.write(f"| {scores['num_samples']} ")
                    f.write(f"| {scores['success_rate']:.1%} ")
                    f.write(f"| {scores['mean_score']:.3f} ")
                    f.write(f"| {scores['max_score']:.3f} ")
                    f.write(f"| {scores['min_score']:.3f} ")
                    f.write(f"| {scores['std_score']:.3f} |\n")
            
            f.write("\n---\n")
            f.write(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        logger.debug(f"Markdown 报告已保存: {md_path}")
    
    def _save_comparison_json(self, comparison: Dict):
        """
        Save comparison report as JSON
        """
        json_path = self.output_dir / 'model_comparison.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        logger.info(f"对比报告 JSON 已保存: {json_path}")
    
    def _save_comparison_markdown(self, comparison: Dict):
        """
        Save comparison report as Markdown
        """
        md_path = self.output_dir / 'model_comparison.md'
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Model Comparison Report\n\n")
            f.write(f"**Generated**: {comparison['timestamp']}\n")
            f.write(f"**Number of Models**: {comparison['num_models']}\n\n")
            
            # Overall Rankings
            f.write("## Overall Rankings\n\n")
            f.write("| Rank | Model | Overall Score | Success Rate |\n")
            f.write("|------|-------|---------------|---------------|\n")
            
            for i, model in enumerate(comparison['models'], 1):
                f.write(f"| {i} | {model['name']} ")
                f.write(f"| {model['overall_score']:.2%} ")
                f.write(f"| {model['success_rate']:.2%} |\n")
            
            # Benchmark Comparisons
            f.write("\n## Benchmark Comparisons\n\n")
            
            for benchmark, scores in comparison['benchmark_comparison'].items():
                f.write(f"### {benchmark}\n\n")
                f.write("| Model | Mean Score | Success Rate |\n")
                f.write("|-------|------------|---------------|\n")
                
                sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
                for score_data in sorted_scores:
                    f.write(f"| {score_data['model']} ")
                    f.write(f"| {score_data['score']:.3f} ")
                    f.write(f"| {score_data['success_rate']:.1%} |\n")
                f.write("\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Best Model**: {comparison['rankings']['best_model']}\n")
            f.write(f"- **Worst Model**: {comparison['rankings']['worst_model']}\n")
            
            f.write("\n---\n")
            f.write(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        logger.info(f"对比报告 Markdown 已保存: {md_path}")
    
    def _generate_comparison_charts(self, comparison: Dict):
        """
        Generate comparison charts
        """
        try:
            # Set style
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
            # 1. Overall Score Comparison
            fig, ax = plt.subplots(figsize=(12, 6))
            models = [m['name'] for m in comparison['models']]
            scores = [m['overall_score'] for m in comparison['models']]
            
            bars = ax.bar(models, scores)
            ax.set_ylabel('Overall Score')
            ax.set_title('Model Overall Score Comparison')
            ax.set_ylim(0, 1)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{score:.2%}', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(self.charts_dir / 'overall_scores.png', dpi=100)
            plt.close()
            
            # 2. Benchmark Performance Heatmap
            if comparison['benchmark_comparison']:
                # Prepare data for heatmap
                benchmarks = list(comparison['benchmark_comparison'].keys())
                model_names = [m['name'] for m in comparison['models']]
                
                heatmap_data = []
                for model in model_names:
                    model_scores = []
                    for benchmark in benchmarks:
                        score = 0
                        for b_data in comparison['benchmark_comparison'][benchmark]:
                            if b_data['model'] == model:
                                score = b_data['score']
                                break
                        model_scores.append(score)
                    heatmap_data.append(model_scores)
                
                # Create heatmap
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(heatmap_data, annot=True, fmt='.3f', 
                           xticklabels=benchmarks, yticklabels=model_names,
                           cmap='YlOrRd', vmin=0, vmax=1, ax=ax)
                ax.set_title('Model Performance Across Benchmarks')
                plt.tight_layout()
                plt.savefig(self.charts_dir / 'benchmark_heatmap.png', dpi=100)
                plt.close()
            
            logger.info(f"对比图表已生成: {self.charts_dir}")
            
        except Exception as e:
            logger.warning(f"生成图表时出错: {e}")
    
    def generate_detailed_csv(self, all_model_reports: Dict[str, Dict], 
                             test_samples: List[Dict]):
        """
        Generate detailed CSV with all model results
        """
        csv_path = self.output_dir / 'detailed_results.csv'
        
        rows = []
        for model_name, report in all_model_reports.items():
            # Add model-level summary
            rows.append({
                'model': model_name,
                'type': 'summary',
                'overall_score': report['overall_score'],
                'success_rate': report['success_rate'],
                'total_samples': report['total_samples']
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"详细结果 CSV 已保存: {csv_path}")