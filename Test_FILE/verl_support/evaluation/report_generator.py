"""
Report Generator - Creates evaluation reports in various formats
Generates JSONL results, markdown summaries, and CSV exports
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate evaluation reports"""
    
    def __init__(self, output_dir: str, model_name: str = "unknown"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
            model_name: Name of the evaluated model
        """
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model_name = model_name.replace('/', '_').replace('\\', '_')
        
        # Create output directory
        self.output_dir = Path(output_dir) / f"{self.timestamp}_{self.model_name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Report output directory: {self.output_dir}")
    
    def _ensure_serializable(self, obj):
        """Ensure object is JSON serializable"""
        import numpy as np
        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: self._ensure_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_serializable(item) for item in obj]
        else:
            return obj
    
    def save_detailed_results(
        self,
        results: List[Dict[str, Any]],
        benchmark: str
    ) -> Path:
        """
        Save detailed results as JSONL
        
        Args:
            results: List of result dictionaries
            benchmark: Benchmark name
            
        Returns:
            Path to saved file
        """
        output_file = self.output_dir / f"{benchmark}_results.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                # Ensure all fields are serializable
                clean_result = {
                    'prompt': self._ensure_serializable(result.get('prompt', '')),
                    'response': result.get('response', ''),
                    'workflow': result.get('workflow', ''),
                    'score': float(result.get('score', 0.0)) if result.get('score') is not None else 0.0,
                    'success': bool(result.get('success', False)),
                    'error': result.get('error'),
                    'inference_time': float(result.get('inference_time', 0.0)) if result.get('inference_time') is not None else 0.0,
                    'scoring_time': float(result.get('scoring_time', 0.0)) if result.get('scoring_time') is not None else 0.0,
                    'metadata': self._ensure_serializable(result.get('metadata', {}))
                }
                f.write(json.dumps(clean_result, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(results)} results to {output_file}")
        return output_file
    
    def generate_summary_report(
        self,
        all_results: Dict[str, List[Dict]],
        config: Dict[str, Any] = None
    ) -> Path:
        """
        Generate markdown summary report
        
        Args:
            all_results: Dictionary mapping benchmark names to results
            config: Configuration used for evaluation
            
        Returns:
            Path to summary report
        """
        report_file = self.output_dir / "summary_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("# 📊 Evaluation Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Model**: `{self.model_name}`\n\n")
            
            # Configuration
            if config:
                f.write("## ⚙️ Configuration\n\n")
                f.write("```json\n")
                f.write(json.dumps(config, indent=2))
                f.write("\n```\n\n")
            
            # Overall statistics
            f.write("## 📈 Overall Statistics\n\n")
            
            total_samples = sum(len(results) for results in all_results.values())
            total_success = sum(
                sum(1 for r in results if r.get('success', False))
                for results in all_results.values()
            )
            overall_scores = []
            for results in all_results.values():
                overall_scores.extend([r.get('score', 0.0) for r in results])
            
            f.write(f"- **Total Samples**: {total_samples}\n")
            f.write(f"- **Successful Inferences**: {total_success} ({100*total_success/max(total_samples, 1):.1f}%)\n")
            f.write(f"- **Overall Average Score**: {sum(overall_scores)/max(len(overall_scores), 1):.3f}\n\n")
            
            # Benchmark results table
            f.write("## 📋 Benchmark Results\n\n")
            f.write("| Benchmark | Samples | Avg Score | Std Dev | Success Rate | Min | Max | Median |\n")
            f.write("|-----------|---------|-----------|---------|--------------|-----|-----|--------|\n")
            
            benchmark_stats = []
            for benchmark, results in all_results.items():
                scores = [r.get('score', 0.0) for r in results]
                success_count = sum(1 for r in results if r.get('success', False))
                
                if scores:
                    import numpy as np
                    stats = {
                        'benchmark': benchmark,
                        'samples': len(results),
                        'avg_score': np.mean(scores),
                        'std_dev': np.std(scores),
                        'success_rate': success_count / len(results),
                        'min_score': np.min(scores),
                        'max_score': np.max(scores),
                        'median_score': np.median(scores)
                    }
                    benchmark_stats.append(stats)
                    
                    f.write(f"| {benchmark} | {stats['samples']} | "
                           f"{stats['avg_score']:.3f} | {stats['std_dev']:.3f} | "
                           f"{stats['success_rate']:.1%} | {stats['min_score']:.3f} | "
                           f"{stats['max_score']:.3f} | {stats['median_score']:.3f} |\n")
            
            # Performance analysis
            f.write("\n## ⏱️ Performance Analysis\n\n")
            
            inference_times = []
            scoring_times = []
            for results in all_results.values():
                inference_times.extend([r.get('inference_time', 0) for r in results])
                scoring_times.extend([r.get('scoring_time', 0) for r in results])
            
            if inference_times:
                f.write(f"- **Average Inference Time**: {np.mean(inference_times):.2f}s\n")
                f.write(f"- **Average Scoring Time**: {np.mean(scoring_times):.2f}s\n")
                f.write(f"- **Total Evaluation Time**: {sum(inference_times) + sum(scoring_times):.2f}s\n\n")
            
            # Error analysis
            f.write("## ❌ Error Analysis\n\n")
            
            for benchmark, results in all_results.items():
                errors = [r for r in results if r.get('error')]
                if errors:
                    f.write(f"### {benchmark}\n\n")
                    f.write(f"- Failed samples: {len(errors)}/{len(results)}\n")
                    
                    # Group errors by type
                    error_types = {}
                    for error in errors[:10]:  # Show first 10 errors
                        error_msg = error.get('error', 'Unknown error')
                        error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
                        error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                    f.write("- Error types:\n")
                    for error_type, count in error_types.items():
                        f.write(f"  - {error_type}: {count}\n")
                    f.write("\n")
            
            # Sample outputs
            f.write("## 📝 Sample Outputs\n\n")
            
            for benchmark, results in all_results.items():
                f.write(f"### {benchmark}\n\n")
                
                # Show best and worst examples
                sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
                
                if sorted_results:
                    # Best example
                    best = sorted_results[0]
                    f.write("**Best Example (Score: {:.3f})**\n\n".format(best.get('score', 0)))
                    f.write("<details>\n<summary>View Details</summary>\n\n")
                    f.write("```python\n")
                    f.write(best.get('workflow', 'No workflow extracted')[:1000])
                    if len(best.get('workflow', '')) > 1000:
                        f.write("\n... (truncated)")
                    f.write("\n```\n</details>\n\n")
                    
                    # Worst example (if different from best)
                    if len(sorted_results) > 1:
                        worst = sorted_results[-1]
                        if worst.get('score', 0) < best.get('score', 0):
                            f.write("**Worst Example (Score: {:.3f})**\n\n".format(worst.get('score', 0)))
                            f.write("<details>\n<summary>View Details</summary>\n\n")
                            if worst.get('error'):
                                f.write(f"Error: {worst['error']}\n\n")
                            f.write("```python\n")
                            f.write(worst.get('workflow', 'No workflow extracted')[:1000])
                            if len(worst.get('workflow', '')) > 1000:
                                f.write("\n... (truncated)")
                            f.write("\n```\n</details>\n\n")
        
        logger.info(f"Generated summary report: {report_file}")
        return report_file
    
    def generate_csv_export(
        self,
        all_results: Dict[str, List[Dict]]
    ) -> Path:
        """
        Export results to CSV
        
        Args:
            all_results: Dictionary mapping benchmark names to results
            
        Returns:
            Path to CSV file
        """
        csv_file = self.output_dir / "results.csv"
        
        # Flatten results
        rows = []
        for benchmark, results in all_results.items():
            for result in results:
                rows.append({
                    'benchmark': benchmark,
                    'score': result.get('score', 0.0),
                    'success': result.get('success', False),
                    'error': result.get('error', ''),
                    'inference_time': result.get('inference_time', 0.0),
                    'scoring_time': result.get('scoring_time', 0.0),
                    'workflow_length': len(result.get('workflow', '')),
                    'response_length': len(result.get('response', ''))
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Exported results to CSV: {csv_file}")
        return csv_file
    
    def generate_plots(
        self,
        all_results: Dict[str, List[Dict]]
    ) -> List[Path]:
        """
        Generate visualization plots
        
        Args:
            all_results: Dictionary mapping benchmark names to results
            
        Returns:
            List of paths to generated plots
        """
        plot_files = []
        
        # Prepare data
        data = []
        for benchmark, results in all_results.items():
            for result in results:
                data.append({
                    'benchmark': benchmark,
                    'score': result.get('score', 0.0)
                })
        
        if not data:
            return plot_files
        
        df = pd.DataFrame(data)
        
        # Set style
        sns.set_style("whitegrid")
        
        # 1. Box plot of scores by benchmark
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='benchmark', y='score', data=df)
        plt.title('Score Distribution by Benchmark')
        plt.xlabel('Benchmark')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_file = self.output_dir / "score_distribution.png"
        plt.savefig(plot_file, dpi=100)
        plt.close()
        plot_files.append(plot_file)
        
        # 2. Bar plot of average scores
        plt.figure(figsize=(10, 6))
        avg_scores = df.groupby('benchmark')['score'].mean().sort_values(ascending=False)
        avg_scores.plot(kind='bar')
        plt.title('Average Scores by Benchmark')
        plt.xlabel('Benchmark')
        plt.ylabel('Average Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_file = self.output_dir / "average_scores.png"
        plt.savefig(plot_file, dpi=100)
        plt.close()
        plot_files.append(plot_file)
        
        # 3. Success rate plot
        plt.figure(figsize=(10, 6))
        success_rates = df[df['score'] > 0].groupby('benchmark').size() / df.groupby('benchmark').size()
        success_rates.plot(kind='bar')
        plt.title('Success Rate by Benchmark')
        plt.xlabel('Benchmark')
        plt.ylabel('Success Rate')
        plt.xticks(rotation=45)
        plt.ylim(0, 1)
        plt.tight_layout()
        
        plot_file = self.output_dir / "success_rates.png"
        plt.savefig(plot_file, dpi=100)
        plt.close()
        plot_files.append(plot_file)
        
        logger.info(f"Generated {len(plot_files)} plots")
        return plot_files
    
    def save_raw_data(
        self,
        data: Any,
        filename: str
    ) -> Path:
        """
        Save raw data for debugging
        
        Args:
            data: Data to save
            filename: Filename
            
        Returns:
            Path to saved file
        """
        output_file = self.output_dir / filename
        
        if isinstance(data, pd.DataFrame):
            data.to_parquet(output_file)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved raw data to {output_file}")
        return output_file


# Example usage
if __name__ == "__main__":
    # Create sample results
    sample_results = {
        'gsm8k': [
            {
                'prompt': 'Solve this math problem...',
                'response': 'Here is the solution...',
                'workflow': 'class Workflow:...',
                'score': 0.85,
                'success': True,
                'inference_time': 2.3,
                'scoring_time': 1.5
            },
            {
                'prompt': 'Another problem...',
                'response': 'Solution...',
                'workflow': 'class Workflow:...',
                'score': 0.0,
                'success': False,
                'error': 'Timeout error',
                'inference_time': 60.0,
                'scoring_time': 0.0
            }
        ],
        'mbpp': [
            {
                'prompt': 'Write a function...',
                'response': 'def solve():...',
                'workflow': 'class Workflow:...',
                'score': 0.92,
                'success': True,
                'inference_time': 1.8,
                'scoring_time': 1.2
            }
        ]
    }
    
    # Generate report
    generator = ReportGenerator("./test_reports", "test_model")
    
    # Save detailed results
    for benchmark, results in sample_results.items():
        generator.save_detailed_results(results, benchmark)
    
    # Generate summary
    generator.generate_summary_report(sample_results, {'test': 'config'})
    
    # Generate CSV
    generator.generate_csv_export(sample_results)
    
    # Generate plots
    generator.generate_plots(sample_results)