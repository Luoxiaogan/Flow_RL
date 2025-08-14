"""
Utility functions for evaluation system
Handles data loading, workflow extraction, and common operations
"""
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and preprocess evaluation data"""
    
    @staticmethod
    def load_parquet(file_path: str) -> pd.DataFrame:
        """
        Load parquet file and handle numpy arrays
        
        Args:
            file_path: Path to parquet file
            
        Returns:
            Loaded DataFrame
        """
        try:
            df = pd.read_parquet(file_path)
            
            # Convert numpy arrays to lists for JSON serialization
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
            
            logger.info(f"Loaded {len(df)} rows from {file_path}")
            logger.info(f"Columns: {df.columns.tolist()}")
            logger.info(f"Data sources: {df['data_source'].value_counts().to_dict()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load parquet file: {e}")
            raise
    
    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict]:
        """
        Load JSONL file
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of dictionaries
        """
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            
            logger.info(f"Loaded {len(data)} rows from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load JSONL file: {e}")
            raise
    
    @staticmethod
    def group_by_benchmark(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Group DataFrame by benchmark (data_source)
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary mapping benchmark names to DataFrames
        """
        grouped = {}
        for benchmark in df['data_source'].unique():
            benchmark_df = df[df['data_source'] == benchmark].copy()
            # Extract benchmark name from "workflow_xxx" format
            clean_name = benchmark.replace('workflow_', '')
            grouped[clean_name] = benchmark_df
            logger.info(f"Benchmark {clean_name}: {len(benchmark_df)} samples")
        
        return grouped


class WorkflowExtractor:
    """Extract and validate workflows from LLM responses"""
    
    @staticmethod
    def extract_workflow(response: str) -> Optional[str]:
        """
        Extract workflow code from response
        Looks for code between <code> tags or <graph> tags
        
        Args:
            response: LLM response
            
        Returns:
            Extracted workflow code or None
        """
        if not response:
            return None
        
        # Try multiple patterns
        patterns = [
            r'<code>(.*?)</code>',
            r'<graph>(.*?)</graph>',
            r'```python(.*?)```',
            r'```(.*?)```'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                workflow = match.group(1).strip()
                # Basic validation
                if 'class Workflow' in workflow or 'def run_workflow' in workflow:
                    return workflow
        
        # If no tags found but contains workflow markers, return entire response
        if 'class Workflow' in response:
            # Try to extract just the class definition
            lines = response.split('\n')
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if 'class Workflow' in line:
                    start_idx = i
                elif start_idx is not None and line and not line[0].isspace() and 'class' not in line:
                    end_idx = i
                    break
            
            if start_idx is not None:
                if end_idx is None:
                    end_idx = len(lines)
                return '\n'.join(lines[start_idx:end_idx])
        
        return None
    
    @staticmethod
    def validate_workflow(workflow: str) -> Tuple[bool, Optional[str]]:
        """
        Validate workflow code
        
        Args:
            workflow: Workflow code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not workflow:
            return False, "Empty workflow"
        
        # Check for required components
        required_patterns = [
            ('class Workflow', 'Missing Workflow class'),
            ('__init__', 'Missing __init__ method'),
            ('run_workflow', 'Missing run_workflow method')
        ]
        
        for pattern, error_msg in required_patterns:
            if pattern not in workflow:
                return False, error_msg
        
        # Check for basic syntax (simple validation)
        try:
            compile(workflow, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def clean_workflow(workflow: str) -> str:
        """
        Clean workflow code for execution
        
        Args:
            workflow: Raw workflow code
            
        Returns:
            Cleaned workflow code
        """
        if not workflow:
            return ""
        
        # Remove common artifacts
        workflow = workflow.strip()
        
        # Remove markdown code fence indicators
        workflow = re.sub(r'^```python\s*\n', '', workflow)
        workflow = re.sub(r'^```\s*\n', '', workflow)
        workflow = re.sub(r'\n```$', '', workflow)
        
        # Ensure proper indentation
        lines = workflow.split('\n')
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        if min_indent > 0 and min_indent != float('inf'):
            lines = [line[min_indent:] if line.strip() else line for line in lines]
            workflow = '\n'.join(lines)
        
        return workflow


class PromptFormatter:
    """Format prompts for different model types"""
    
    @staticmethod
    def format_for_chat(prompt: Any) -> List[Dict[str, str]]:
        """
        Format prompt for chat completion API
        
        Args:
            prompt: Either a string or list of messages
            
        Returns:
            List of message dictionaries
        """
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            return prompt
        else:
            # Try to convert to string
            return [{"role": "user", "content": str(prompt)}]
    
    @staticmethod
    def extract_system_prompt(messages: List[Dict[str, str]]) -> Tuple[Optional[str], List[Dict[str, str]]]:
        """
        Extract system prompt from messages
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Tuple of (system_prompt, remaining_messages)
        """
        if not messages:
            return None, []
        
        if messages[0].get('role') == 'system':
            return messages[0].get('content'), messages[1:]
        
        return None, messages


class ConfigManager:
    """Manage configuration files"""
    
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Set defaults
            defaults = {
                'max_workers': 10,
                'batch_size': 100,
                'timeout': 60,
                'retry_times': 3,
                'temperature': 0.7,
                'max_tokens': 4096
            }
            
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str):
        """
        Save configuration to JSON file
        
        Args:
            config: Configuration dictionary
            config_path: Path to save config
        """
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved config to {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise


class MetricsCalculator:
    """Calculate evaluation metrics"""
    
    @staticmethod
    def calculate_stats(scores: List[float]) -> Dict[str, float]:
        """
        Calculate statistics for scores
        
        Args:
            scores: List of scores
            
        Returns:
            Dictionary of statistics
        """
        if not scores:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0,
                'success_rate': 0.0,
                'count': 0
            }
        
        scores_array = np.array(scores)
        success_count = np.sum(scores_array > 0)
        
        return {
            'mean': float(np.mean(scores_array)),
            'std': float(np.std(scores_array)),
            'min': float(np.min(scores_array)),
            'max': float(np.max(scores_array)),
            'median': float(np.median(scores_array)),
            'success_rate': float(success_count / len(scores)),
            'count': len(scores)
        }
    
    @staticmethod
    def calculate_benchmark_metrics(results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate metrics by benchmark
        
        Args:
            results_df: DataFrame with results
            
        Returns:
            DataFrame with metrics per benchmark
        """
        metrics = []
        
        for benchmark in results_df['data_source'].unique():
            benchmark_data = results_df[results_df['data_source'] == benchmark]
            scores = benchmark_data['score'].tolist()
            
            stats = MetricsCalculator.calculate_stats(scores)
            stats['benchmark'] = benchmark.replace('workflow_', '')
            
            metrics.append(stats)
        
        return pd.DataFrame(metrics)


# Test utilities
if __name__ == "__main__":
    # Test workflow extraction
    test_response = """
    <code>
    class Workflow:
        def __init__(self, config, problem):
            self.config = config
            self.problem = problem
            
        async def run_workflow(self):
            return "solution"
    </code>
    """
    
    extractor = WorkflowExtractor()
    workflow = extractor.extract_workflow(test_response)
    print("Extracted workflow:")
    print(workflow)
    
    valid, error = extractor.validate_workflow(workflow)
    print(f"Valid: {valid}, Error: {error}")
    
    # Test metrics
    scores = [0.8, 0.9, 0.7, 0.0, 1.0, 0.85]
    stats = MetricsCalculator.calculate_stats(scores)
    print("\nMetrics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")