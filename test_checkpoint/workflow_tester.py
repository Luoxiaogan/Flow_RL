#!/usr/bin/env python3
"""
Workflow Tester Module for Checkpoint Testing
Tests generated workflows using API execution and validates results
"""

import asyncio
import json
import os
import sys
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import argparse
from pathlib import Path
import importlib
import csv
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Add parent directory to path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CURRENT_DIR))
from ScoreFlow.scripts.base_handler import BenchmarkHandler


def get_benchmark_handler(benchmark_name: str, dataset_path: str) -> BenchmarkHandler:
    """Dynamically import and instantiate the handler for specified benchmark."""
    try:
        handler_module_path = f"ScoreFlow.scripts.{benchmark_name.lower()}.handler"
        handler_module = importlib.import_module(handler_module_path)
        
        # Convention: Handler class name is BenchmarkNameHandler (e.g., Gsm8kHandler)
        handler_class_name = f"{benchmark_name.capitalize()}Handler"
        handler_class = getattr(handler_module, handler_class_name)
        
        return handler_class(dataset_path=dataset_path)
    except (ModuleNotFoundError, AttributeError, ValueError) as e:
        print(f"Cannot load handler for benchmark '{benchmark_name}': {e}")
        raise


class WorkflowTester:
    """
    Tests generated workflows by executing them and validating results
    """
    
    def __init__(
        self,
        exec_llm_config: Dict[str, str],
        output_dir: str = "test_results",
        max_concurrent_executions: int = 5,
        execution_timeout: int = 180
    ):
        self.exec_llm_config = exec_llm_config
        self.output_dir = Path(output_dir)
        self.max_concurrent_executions = max_concurrent_executions
        self.execution_timeout = execution_timeout
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Results CSV file
        self.results_file = self.output_dir / "test_results.csv"
        self._init_results_file()
    
    def _init_results_file(self):
        """Initialize results CSV file with headers"""
        if not self.results_file.exists():
            with open(self.results_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'workflow_id', 'benchmark', 'data_indices', 
                    'status', 'error_message', 'execution_time',
                    'timestamp'
                ])
    
    def load_workflow_metadata(self, workflow_path: Path) -> Dict[str, Any]:
        """Load workflow metadata from .meta.json file"""
        metadata_path = workflow_path.with_suffix('.meta.json')
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def build_executable_script(
        self,
        workflow_code: str,
        benchmark: str,
        verification_data: List[Dict],
        exec_llm_config: Dict[str, str]
    ) -> str:
        """
        Build executable Python script with workflow code and environment
        """
        # Load benchmark-specific modules
        conditions_module = importlib.import_module(
            f"ScoreFlow.scripts.{benchmark.lower()}.conditions"
        )
        
        # Build script
        script_parts = []
        
        # Add imports
        script_parts.append("import asyncio")
        script_parts.append("import sys")
        script_parts.append("import os")
        script_parts.append("from typing import *")
        
        # Add ScoreFlow path
        script_parts.append(f"sys.path.insert(0, '{os.path.dirname(CURRENT_DIR)}')")
        
        # Import operator module
        script_parts.append(f"from ScoreFlow.scripts.{benchmark.lower()}.operator import *")
        
        # Try to import operator_an if exists
        try:
            importlib.import_module(f"ScoreFlow.scripts.{benchmark.lower()}.operator_an")
            script_parts.append(f"from ScoreFlow.scripts.{benchmark.lower()}.operator_an import *")
        except ImportError:
            pass
        
        # Add MetaGPT imports
        script_parts.append("from ScoreFlow.scripts.utils.code_executor import create_llm_instance")
        
        # Add LLM configuration
        script_parts.append(f"EXEC_LLM = {repr(exec_llm_config)}")
        
        # Add workflow code
        script_parts.append("\n# === WORKFLOW CODE ===")
        script_parts.append(workflow_code)
        
        # Add execution code
        script_parts.append("\n# === EXECUTION CODE ===")
        script_parts.append(f"test_data = {repr(verification_data)}")
        script_parts.append("""
async def main():
    workflow = Workflow()
    results = []
    
    for data in test_data:
        try:
            result = await workflow.run(data)
            results.append(result)
        except Exception as e:
            print(f"Error processing data: {e}")
            results.append(None)
    
    return results

if __name__ == "__main__":
    import json
    results = asyncio.run(main())
    print("###RESULTS_START###")
    print(json.dumps(results))
    print("###RESULTS_END###")
""")
        
        return "\n".join(script_parts)
    
    def execute_workflow(
        self,
        script_content: str,
        workflow_id: str
    ) -> Tuple[bool, Any, str]:
        """
        Execute workflow script and capture results
        
        Returns:
            Tuple of (success, results, error_message)
        """
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as tmp_file:
            tmp_file.write(script_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Execute script with timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    subprocess.run,
                    [sys.executable, tmp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.execution_timeout
                )
                
                try:
                    result = future.result(timeout=self.execution_timeout)
                except TimeoutError:
                    return False, None, f"Execution timeout ({self.execution_timeout}s)"
            
            # Parse output
            if result.returncode != 0:
                return False, None, f"Execution failed: {result.stderr}"
            
            # Extract results from output
            output = result.stdout
            if "###RESULTS_START###" in output and "###RESULTS_END###" in output:
                start = output.find("###RESULTS_START###") + len("###RESULTS_START###")
                end = output.find("###RESULTS_END###")
                results_json = output[start:end].strip()
                
                try:
                    results = json.loads(results_json)
                    return True, results, None
                except json.JSONDecodeError as e:
                    return False, None, f"Failed to parse results: {e}"
            else:
                return False, None, "Results markers not found in output"
                
        except subprocess.TimeoutExpired:
            return False, None, f"Execution timeout ({self.execution_timeout}s)"
        except Exception as e:
            return False, None, f"Execution error: {str(e)}"
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    async def test_single_workflow(
        self,
        workflow_path: Path
    ) -> Dict[str, Any]:
        """
        Test a single workflow
        """
        workflow_id = workflow_path.stem
        
        try:
            # Load metadata
            metadata = self.load_workflow_metadata(workflow_path)
            benchmark = metadata['benchmark']
            data_indices = metadata['data_indices']
            dataset_path = metadata['dataset_path']
            
            # Load workflow code
            with open(workflow_path, 'r') as f:
                workflow_code = f.read()
            
            # Get handler
            handler = get_benchmark_handler(benchmark, dataset_path)
            
            # Get verification data
            verification_data = []
            for idx in data_indices:
                data = handler.get_verification_data(idx)
                verification_data.append(data)
            
            # Build executable script
            script_content = self.build_executable_script(
                workflow_code,
                benchmark,
                verification_data,
                self.exec_llm_config
            )
            
            # Execute workflow
            start_time = datetime.now()
            success, results, error_msg = self.execute_workflow(
                script_content,
                workflow_id
            )
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if success and results:
                # Validate results using handler's judge method
                all_correct = True
                for i, (result, data) in enumerate(zip(results, verification_data)):
                    if result is None:
                        all_correct = False
                        break
                    
                    is_correct = handler.judge(result, data)
                    if not is_correct:
                        all_correct = False
                        break
                
                status = "verified_correct" if all_correct else "verified_incorrect"
                error_message = None if all_correct else "Some results incorrect"
            else:
                status = "execution_failed"
                error_message = error_msg
            
            # Record result
            result_record = {
                'workflow_id': workflow_id,
                'benchmark': benchmark,
                'data_indices': data_indices,
                'status': status,
                'error_message': error_message,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to CSV
            with open(self.results_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'workflow_id', 'benchmark', 'data_indices',
                    'status', 'error_message', 'execution_time',
                    'timestamp'
                ])
                writer.writerow(result_record)
            
            return result_record
            
        except Exception as e:
            # Handle unexpected errors
            error_trace = traceback.format_exc()
            result_record = {
                'workflow_id': workflow_id,
                'benchmark': metadata.get('benchmark', 'unknown'),
                'data_indices': metadata.get('data_indices', []),
                'status': 'error',
                'error_message': f"Unexpected error: {str(e)}\n{error_trace}",
                'execution_time': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save error to CSV
            with open(self.results_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'workflow_id', 'benchmark', 'data_indices',
                    'status', 'error_message', 'execution_time',
                    'timestamp'
                ])
                writer.writerow(result_record)
            
            return result_record
    
    async def test_workflows(
        self,
        workflow_paths: List[Path]
    ) -> List[Dict[str, Any]]:
        """
        Test multiple workflows with parallelism
        """
        results = []
        
        # Process in batches
        for i in range(0, len(workflow_paths), self.max_concurrent_executions):
            batch = workflow_paths[i:i + self.max_concurrent_executions]
            batch_coroutines = [
                self.test_single_workflow(path) for path in batch
            ]
            
            batch_results = await asyncio.gather(*batch_coroutines)
            results.extend(batch_results)
            
            # Progress update
            completed = min(i + self.max_concurrent_executions, len(workflow_paths))
            print(f"Progress: {completed}/{len(workflow_paths)} workflows tested")
        
        return results


async def main():
    """
    Main function for testing the workflow tester
    """
    parser = argparse.ArgumentParser(description="Test generated workflows")
    parser.add_argument("--workflow-dir", type=str, required=True,
                        help="Directory containing generated workflows")
    parser.add_argument("--exec-llm", type=str, required=True,
                        help="Execution LLM config (JSON string)")
    parser.add_argument("--output-dir", type=str, default="test_results",
                        help="Output directory for results")
    parser.add_argument("--max-concurrent", type=int, default=5,
                        help="Maximum concurrent executions")
    parser.add_argument("--timeout", type=int, default=180,
                        help="Execution timeout in seconds")
    
    args = parser.parse_args()
    
    # Parse execution LLM config
    try:
        exec_llm_config = json.loads(args.exec_llm)
    except json.JSONDecodeError as e:
        print(f"Failed to parse exec-llm config: {e}")
        sys.exit(1)
    
    # Create tester
    tester = WorkflowTester(
        exec_llm_config=exec_llm_config,
        output_dir=args.output_dir,
        max_concurrent_executions=args.max_concurrent,
        execution_timeout=args.timeout
    )
    
    # Find all workflow files
    workflow_dir = Path(args.workflow_dir)
    workflow_paths = list(workflow_dir.glob("*.py"))
    
    if not workflow_paths:
        print(f"No workflow files found in {workflow_dir}")
        return
    
    print(f"Found {len(workflow_paths)} workflows to test")
    
    # Test workflows
    results = await tester.test_workflows(workflow_paths)
    
    # Print summary
    total = len(results)
    correct = sum(1 for r in results if r['status'] == 'verified_correct')
    incorrect = sum(1 for r in results if r['status'] == 'verified_incorrect')
    failed = sum(1 for r in results if r['status'] == 'execution_failed')
    errors = sum(1 for r in results if r['status'] == 'error')
    
    print("\n=== Test Summary ===")
    print(f"Total workflows: {total}")
    print(f"Verified correct: {correct} ({correct/total*100:.1f}%)")
    print(f"Verified incorrect: {incorrect} ({incorrect/total*100:.1f}%)")
    print(f"Execution failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    print(f"\nResults saved to: {tester.results_file}")


if __name__ == "__main__":
    asyncio.run(main())