"""
Detailed score recorder for individual sample evaluation tracking
"""
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class DetailedScoreRecorder:
    """
    Records and manages detailed scores for each evaluated sample
    """
    
    def __init__(self, output_dir: str = 'evaluation_reports'):
        """
        Initialize detailed score recorder
        
        Args:
            output_dir: Base directory for storing detailed scores
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for scores organized by hierarchy
        self.scores = {
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'total_samples': 0,
                'total_models': 0
            },
            'models': {}  # model -> benchmark -> operator_group -> samples
        }
        
        # Current evaluation context
        self.current_model = None
        self.current_benchmark = None
        self.current_operator_group = None
        
        logger.info(f"详细评分记录器初始化完成，输出目录: {self.output_dir}")
    
    def set_context(self, model: str = None, benchmark: str = None, 
                    operator_group: str = None):
        """
        Set the current evaluation context
        
        Args:
            model: Current model name
            benchmark: Current benchmark name  
            operator_group: Current operator group name
        """
        if model:
            self.current_model = model
            if model not in self.scores['models']:
                self.scores['models'][model] = {
                    'metadata': {
                        'name': model,
                        'start_time': datetime.now().isoformat()
                    },
                    'benchmarks': {}
                }
                self.scores['metadata']['total_models'] += 1
        
        if benchmark and self.current_model:
            self.current_benchmark = benchmark
            if benchmark not in self.scores['models'][self.current_model]['benchmarks']:
                self.scores['models'][self.current_model]['benchmarks'][benchmark] = {
                    'metadata': {
                        'name': benchmark,
                        'start_time': datetime.now().isoformat()
                    },
                    'operator_groups': {}
                }
        
        if operator_group and self.current_benchmark:
            self.current_operator_group = operator_group
            model_data = self.scores['models'][self.current_model]
            benchmark_data = model_data['benchmarks'][self.current_benchmark]
            
            if operator_group not in benchmark_data['operator_groups']:
                benchmark_data['operator_groups'][operator_group] = {
                    'metadata': {
                        'name': operator_group,
                        'start_time': datetime.now().isoformat()
                    },
                    'samples': []
                }
    
    def record_sample_score(self, sample: Dict, solution: str, 
                           score_result: Dict, sample_index: int = None):
        """
        Record detailed score for a single sample
        
        Args:
            sample: Original test sample
            solution: Generated solution
            score_result: Score result from reward server
            sample_index: Optional index of the sample
            
        Returns:
            Recorded score entry
        """
        if not all([self.current_model, self.current_benchmark]):
            logger.warning("记录样本分数时缺少上下文信息")
            return None
        
        # Create detailed score entry
        score_entry = {
            'index': sample_index if sample_index is not None else self.scores['metadata']['total_samples'],
            'timestamp': datetime.now().isoformat(),
            'sample': {
                'data_source': sample.get('data_source', 'unknown'),
                'prompt': sample.get('prompt', ''),
                'extra_info': sample.get('extra_info', {})
            },
            'solution': solution,
            'evaluation': {
                'success': score_result.get('success', False),
                'score': score_result.get('score', 0.0),
                'error': score_result.get('error', None),
                'execution_time': score_result.get('execution_time', None)
            },
            'context': {
                'model': self.current_model,
                'benchmark': self.current_benchmark,
                'operator_group': self.current_operator_group
            }
        }
        
        # Store in appropriate location
        if self.current_operator_group:
            path = (self.scores['models'][self.current_model]
                   ['benchmarks'][self.current_benchmark]
                   ['operator_groups'][self.current_operator_group]['samples'])
        else:
            # If no operator group, store at benchmark level
            benchmark_data = (self.scores['models'][self.current_model]
                            ['benchmarks'][self.current_benchmark])
            if 'samples' not in benchmark_data:
                benchmark_data['samples'] = []
            path = benchmark_data['samples']
        
        path.append(score_entry)
        self.scores['metadata']['total_samples'] += 1
        
        # Auto-save after each sample (configurable)
        if self.scores['metadata']['total_samples'] % 10 == 0:
            self._auto_save()
        
        return score_entry
    
    def get_scores_by_operator(self, model: str, benchmark: str, 
                               operator_group: str) -> List[Dict]:
        """
        Get all scores for a specific operator group
        
        Args:
            model: Model name
            benchmark: Benchmark name
            operator_group: Operator group name
            
        Returns:
            List of score entries
        """
        try:
            return (self.scores['models'][model]
                   ['benchmarks'][benchmark]
                   ['operator_groups'][operator_group]['samples'])
        except KeyError:
            logger.warning(f"未找到指定的评分数据: {model}/{benchmark}/{operator_group}")
            return []
    
    def get_scores_by_benchmark(self, model: str, benchmark: str) -> Dict:
        """
        Get all scores for a specific benchmark
        
        Args:
            model: Model name
            benchmark: Benchmark name
            
        Returns:
            Dictionary containing all operator groups and samples
        """
        try:
            return self.scores['models'][model]['benchmarks'][benchmark]
        except KeyError:
            logger.warning(f"未找到指定的基准测试数据: {model}/{benchmark}")
            return {}
    
    def get_scores_by_model(self, model: str) -> Dict:
        """
        Get all scores for a specific model
        
        Args:
            model: Model name
            
        Returns:
            Dictionary containing all benchmarks and samples
        """
        try:
            return self.scores['models'][model]
        except KeyError:
            logger.warning(f"未找到指定的模型数据: {model}")
            return {}
    
    def calculate_statistics(self, scores: List[Dict]) -> Dict:
        """
        Calculate statistics for a list of scores
        
        Args:
            scores: List of score entries
            
        Returns:
            Statistics dictionary
        """
        if not scores:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'mean_score': 0.0,
                'max_score': 0.0,
                'min_score': 0.0,
                'success_rate': 0.0
            }
        
        successful_scores = [s['evaluation']['score'] 
                           for s in scores 
                           if s['evaluation']['success']]
        
        return {
            'total': len(scores),
            'successful': len(successful_scores),
            'failed': len(scores) - len(successful_scores),
            'mean_score': sum(successful_scores) / len(successful_scores) if successful_scores else 0.0,
            'max_score': max(successful_scores) if successful_scores else 0.0,
            'min_score': min(successful_scores) if successful_scores else 0.0,
            'success_rate': len(successful_scores) / len(scores)
        }
    
    def export_to_json(self, filepath: str = None, 
                       model: str = None, benchmark: str = None,
                       operator_group: str = None) -> str:
        """
        Export scores to JSON file
        
        Args:
            filepath: Optional custom filepath
            model: Filter by model
            benchmark: Filter by benchmark
            operator_group: Filter by operator group
            
        Returns:
            Path to saved file
        """
        # Determine what to export
        if operator_group and benchmark and model:
            data = self.get_scores_by_operator(model, benchmark, operator_group)
            default_name = f"{model}_{benchmark}_{operator_group}_scores.json"
        elif benchmark and model:
            data = self.get_scores_by_benchmark(model, benchmark)
            default_name = f"{model}_{benchmark}_scores.json"
        elif model:
            data = self.get_scores_by_model(model)
            default_name = f"{model}_scores.json"
        else:
            data = self.scores
            default_name = "all_scores.json"
        
        # Determine filepath
        if not filepath:
            filepath = self.output_dir / default_name
        else:
            filepath = Path(filepath)
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"评分数据已导出到 JSON: {filepath}")
        return str(filepath)
    
    def export_to_csv(self, filepath: str = None,
                      model: str = None, benchmark: str = None,
                      operator_group: str = None) -> str:
        """
        Export scores to CSV file with detailed columns
        
        Args:
            filepath: Optional custom filepath
            model: Filter by model
            benchmark: Filter by benchmark
            operator_group: Filter by operator group
            
        Returns:
            Path to saved file
        """
        # Collect all samples to export
        samples_to_export = []
        
        if model:
            models_to_process = [model] if model in self.scores['models'] else []
        else:
            models_to_process = list(self.scores['models'].keys())
        
        for model_name in models_to_process:
            model_data = self.scores['models'][model_name]
            
            if benchmark:
                benchmarks_to_process = ([benchmark] 
                                        if benchmark in model_data['benchmarks'] 
                                        else [])
            else:
                benchmarks_to_process = list(model_data['benchmarks'].keys())
            
            for benchmark_name in benchmarks_to_process:
                benchmark_data = model_data['benchmarks'][benchmark_name]
                
                # Process operator groups
                if 'operator_groups' in benchmark_data:
                    if operator_group:
                        groups_to_process = ([operator_group]
                                           if operator_group in benchmark_data['operator_groups']
                                           else [])
                    else:
                        groups_to_process = list(benchmark_data['operator_groups'].keys())
                    
                    for group_name in groups_to_process:
                        group_data = benchmark_data['operator_groups'][group_name]
                        for sample in group_data.get('samples', []):
                            samples_to_export.append(self._flatten_sample(sample))
                
                # Process direct samples (no operator group)
                for sample in benchmark_data.get('samples', []):
                    samples_to_export.append(self._flatten_sample(sample))
        
        if not samples_to_export:
            logger.warning("没有找到要导出的样本")
            return None
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(samples_to_export)
        
        # Determine filepath
        if not filepath:
            suffix = []
            if model:
                suffix.append(model)
            if benchmark:
                suffix.append(benchmark)
            if operator_group:
                suffix.append(operator_group)
            
            filename = "_".join(suffix) if suffix else "all"
            filepath = self.output_dir / f"{filename}_scores.csv"
        else:
            filepath = Path(filepath)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"评分数据已导出到 CSV: {filepath}")
        return str(filepath)
    
    def _flatten_sample(self, sample: Dict) -> Dict:
        """
        Flatten nested sample dictionary for CSV export
        
        Args:
            sample: Nested sample dictionary
            
        Returns:
            Flattened dictionary
        """
        flattened = {
            'index': sample.get('index', ''),
            'timestamp': sample.get('timestamp', ''),
            'model': sample.get('context', {}).get('model', ''),
            'benchmark': sample.get('context', {}).get('benchmark', ''),
            'operator_group': sample.get('context', {}).get('operator_group', ''),
            'data_source': sample.get('sample', {}).get('data_source', ''),
            'success': sample.get('evaluation', {}).get('success', False),
            'score': sample.get('evaluation', {}).get('score', 0.0),
            'error': sample.get('evaluation', {}).get('error', ''),
            'execution_time': sample.get('evaluation', {}).get('execution_time', ''),
            'solution_length': len(sample.get('solution', '')),
            'prompt_preview': str(sample.get('sample', {}).get('prompt', ''))[:100] + '...'
        }
        
        # Add extra info fields if they exist
        extra_info = sample.get('sample', {}).get('extra_info', {})
        if isinstance(extra_info, dict):
            for key, value in extra_info.items():
                if key in ['test_cases', 'data_path']:
                    flattened[f'extra_{key}'] = str(value)
        
        return flattened
    
    def _auto_save(self):
        """
        Auto-save current scores to a temporary file
        """
        try:
            temp_file = self.output_dir / f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
            logger.debug(f"自动保存评分数据: {temp_file}")
        except Exception as e:
            logger.warning(f"自动保存失败: {e}")
    
    def save_final_report(self):
        """
        Save final comprehensive report
        """
        # Save complete JSON
        final_json = self.output_dir / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_json, 'w', encoding='utf-8') as f:
            # Add completion time
            self.scores['metadata']['end_time'] = datetime.now().isoformat()
            json.dump(self.scores, f, indent=2, ensure_ascii=False)
        
        # Save summary CSV
        self.export_to_csv(
            self.output_dir / f"final_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        logger.info(f"最终报告已保存: {final_json}")
        
        return str(final_json)
    
    def get_progress_summary(self) -> Dict:
        """
        Get current evaluation progress summary
        
        Returns:
            Progress summary dictionary
        """
        summary = {
            'total_models': len(self.scores['models']),
            'total_samples': self.scores['metadata']['total_samples'],
            'current_context': {
                'model': self.current_model,
                'benchmark': self.current_benchmark,
                'operator_group': self.current_operator_group
            },
            'models': {}
        }
        
        for model_name, model_data in self.scores['models'].items():
            model_summary = {
                'benchmarks_completed': len(model_data['benchmarks']),
                'total_samples': 0,
                'successful_samples': 0
            }
            
            for benchmark_data in model_data['benchmarks'].values():
                # Count samples from operator groups
                if 'operator_groups' in benchmark_data:
                    for group_data in benchmark_data['operator_groups'].values():
                        samples = group_data.get('samples', [])
                        model_summary['total_samples'] += len(samples)
                        model_summary['successful_samples'] += sum(
                            1 for s in samples if s['evaluation']['success']
                        )
                
                # Count direct samples
                samples = benchmark_data.get('samples', [])
                model_summary['total_samples'] += len(samples)
                model_summary['successful_samples'] += sum(
                    1 for s in samples if s['evaluation']['success']
                )
            
            if model_summary['total_samples'] > 0:
                model_summary['success_rate'] = (
                    model_summary['successful_samples'] / model_summary['total_samples']
                )
            else:
                model_summary['success_rate'] = 0.0
            
            summary['models'][model_name] = model_summary
        
        return summary