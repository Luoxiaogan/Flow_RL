"""
Report generator for evaluation results
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates evaluation reports in various formats
    """
    
    def __init__(self, output_dir: str = 'evaluation_reports'):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"报告输出目录: {self.output_dir}")
    
    def generate_report(self, scores: List[Dict], 
                       checkpoint_info: Dict,
                       test_samples: List[Dict]) -> Dict:
        """
        Generate comprehensive evaluation report
        
        Args:
            scores: List of score results from reward server
            checkpoint_info: Information about the checkpoint
            test_samples: Original test samples
            
        Returns:
            Report dictionary
        """
        logger.info("生成评估报告...")
        
        # Calculate statistics
        report = {
            'checkpoint': checkpoint_info,
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(scores),
            'evaluation_results': self._calculate_statistics(scores, test_samples)
        }
        
        # Calculate benchmark-specific scores
        report['benchmark_scores'] = self._calculate_benchmark_scores(scores, test_samples)
        
        # Calculate overall score
        report['overall_score'] = self._calculate_overall_score(scores)
        
        # Success rate
        report['success_rate'] = sum(1 for s in scores if s.get('success', False)) / len(scores) if scores else 0
        
        # Save reports in different formats
        self._save_json_report(report, checkpoint_info['step'])
        self._save_markdown_report(report, checkpoint_info['step'])
        self._save_detailed_csv(scores, test_samples, checkpoint_info['step'])
        
        logger.info(f"✓ 报告已生成: checkpoint-{checkpoint_info['step']}")
        
        return report
    
    def _calculate_statistics(self, scores: List[Dict], 
                             test_samples: List[Dict]) -> Dict:
        """
        Calculate detailed statistics
        
        Args:
            scores: List of score results
            test_samples: Original test samples
            
        Returns:
            Statistics dictionary
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
        
        Args:
            scores: List of score results
            test_samples: Original test samples
            
        Returns:
            Benchmark scores dictionary
        """
        benchmark_scores = {}
        
        # Group by data source
        data_sources = {}
        for i, sample in enumerate(test_samples):
            source = sample.get('data_source', 'unknown')
            
            # Extract benchmark name from data source
            # e.g., "workflow_gsm8k" -> "gsm8k"
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
        
        Args:
            scores: List of score results
            
        Returns:
            Overall score (0.0 to 1.0)
        """
        successful_scores = [s.get('score', 0.0) for s in scores if s.get('success', False)]
        
        if not successful_scores:
            return 0.0
        
        return sum(successful_scores) / len(successful_scores)
    
    def _save_json_report(self, report: Dict, step: int):
        """
        Save report as JSON
        
        Args:
            report: Report dictionary
            step: Training step
        """
        json_path = self.output_dir / f"eval_checkpoint_{step}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON 报告已保存: {json_path}")
    
    def _save_markdown_report(self, report: Dict, step: int):
        """
        Save report as Markdown
        
        Args:
            report: Report dictionary
            step: Training step
        """
        md_path = self.output_dir / f"eval_checkpoint_{step}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Evaluation Report - Checkpoint {step}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Date**: {report['timestamp']}\n")
            # f.write(f"- **Checkpoint**: {report['checkpoint']['path']}\n")
            checkpoint_path = report['checkpoint'].get('path', f"Step {report['checkpoint'].get('step', 'unknown')}")
            f.write(f"- **Checkpoint**: {checkpoint_path}\n")
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
            else:
                f.write("No benchmark-specific scores available.\n")
            
            f.write("\n---\n")
            f.write(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        logger.info(f"Markdown 报告已保存: {md_path}")
    
    def _save_detailed_csv(self, scores: List[Dict], 
                          test_samples: List[Dict], 
                          step: int):
        """
        Save detailed results as CSV
        
        Args:
            scores: List of score results
            test_samples: Original test samples
            step: Training step
        """
        csv_path = self.output_dir / f"eval_checkpoint_{step}_details.csv"
        
        # Prepare data for DataFrame
        rows = []
        for i, (sample, score) in enumerate(zip(test_samples, scores)):
            row = {
                'index': i,
                'data_source': sample.get('data_source', 'unknown'),
                'success': score.get('success', False),
                'score': score.get('score', 0.0),
                'error': score.get('error', ''),
            }
            
            # Add extra info if available
            extra_info = sample.get('extra_info', {})
            if 'test_cases' in extra_info:
                row['test_cases'] = str(extra_info['test_cases'])
            if 'raw_data' in extra_info:
                row['raw_data'] = extra_info['raw_data']
            
            rows.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logger.info(f"详细 CSV 已保存: {csv_path}")
    
    def generate_comparison_report(self, all_reports: List[Dict]) -> Dict:
        """
        Generate comparison report across multiple checkpoints
        
        Args:
            all_reports: List of all evaluation reports
            
        Returns:
            Comparison report dictionary
        """
        if not all_reports:
            return {}
        
        comparison = {
            'num_checkpoints': len(all_reports),
            'checkpoints': [],
            'trend': {}
        }
        
        # Extract data for each checkpoint
        for report in sorted(all_reports, key=lambda x: x['checkpoint']['step']):
            comparison['checkpoints'].append({
                'step': report['checkpoint']['step'],
                'overall_score': report['overall_score'],
                'success_rate': report['success_rate'],
                'timestamp': report['timestamp']
            })
        
        # Calculate trends
        scores = [c['overall_score'] for c in comparison['checkpoints']]
        if len(scores) > 1:
            comparison['trend'] = {
                'improving': scores[-1] > scores[0],
                'best_checkpoint': max(comparison['checkpoints'], key=lambda x: x['overall_score'])['step'],
                'worst_checkpoint': min(comparison['checkpoints'], key=lambda x: x['overall_score'])['step'],
                'average_score': sum(scores) / len(scores)
            }
        
        # Save comparison report
        comparison_path = self.output_dir / 'checkpoint_comparison.json'
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        logger.info(f"对比报告已保存: {comparison_path}")
        
        return comparison


# Test function
def test_report_generator():
    """
    Test the report generator
    """
    generator = ReportGenerator('test_reports')
    
    # Test data
    scores = [
        {'success': True, 'score': 0.8},
        {'success': True, 'score': 0.9},
        {'success': False, 'score': 0.0, 'error': 'Timeout'},
    ]
    
    test_samples = [
        {'data_source': 'workflow_gsm8k', 'extra_info': {'test_cases': [1, 2]}},
        {'data_source': 'workflow_gsm8k', 'extra_info': {'test_cases': [3, 4]}},
        {'data_source': 'workflow_drop', 'extra_info': {'test_cases': [5]}},
    ]
    
    checkpoint_info = {
        'step': 1000,
        'path': './checkpoint-1000',
        'output_dir': './output'
    }
    
    # Generate report (synchronous)
    report = generator.generate_report(scores, checkpoint_info, test_samples)
    
    print("Report generated:")
    print(f"  Overall Score: {report['overall_score']:.2%}")
    print(f"  Success Rate: {report['success_rate']:.2%}")
    print(f"  Benchmarks: {list(report['benchmark_scores'].keys())}")


if __name__ == "__main__":
    test_report_generator()