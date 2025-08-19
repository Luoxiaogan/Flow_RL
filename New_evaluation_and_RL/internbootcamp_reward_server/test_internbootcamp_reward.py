"""
Test script for InternBootcamp Reward Server
Tests various endpoints and functionality
"""
import os
import sys
import json
import time
import requests
import pandas as pd
from pathlib import Path

# Setup paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Server configuration
SERVER_URL = "http://localhost:8900"
TEST_DATA_PATH = PROJECT_ROOT / "New_evaluation_and_RL" / "generate_parquet_and_jsonl" / "internbootcamp_data_test" / "test.parquet"


def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{SERVER_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Service: {data.get('service')}")
        print(f"Version: {data.get('version')}")
        print(f"Port: {data.get('port')}")
        print("✅ Health check passed")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_get_config():
    """Test the config endpoint"""
    print("\n" + "="*60)
    print("Testing Config Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{SERVER_URL}/config")
        response.raise_for_status()
        
        data = response.json()
        print(f"Server Config: {json.dumps(data.get('server_config', {}), indent=2)}")
        print(f"Available InternBootcamp Tasks: {data.get('internbootcamp_tasks', [])[:5]}...")
        print(f"Workspace: {data.get('workspace')}")
        print("✅ Config endpoint passed")
        return True
        
    except Exception as e:
        print(f"❌ Config endpoint failed: {e}")
        return False


def test_get_tasks():
    """Test the tasks endpoint"""
    print("\n" + "="*60)
    print("Testing Tasks Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{SERVER_URL}/tasks")
        response.raise_for_status()
        
        data = response.json()
        print(f"Total available tasks: {data.get('total_available', 0)}")
        print(f"Total failed tasks: {data.get('total_failed', 0)}")
        
        available = data.get('available_tasks', [])
        if available:
            print(f"Sample tasks: {available[:5]}")
        
        print("✅ Tasks endpoint passed")
        return True
        
    except Exception as e:
        print(f"❌ Tasks endpoint failed: {e}")
        return False


def test_compute_score_simple():
    """Test compute_score with a simple workflow"""
    print("\n" + "="*60)
    print("Testing Compute Score with Simple Workflow")
    print("="*60)
    
    # Simple test workflow
    workflow_code = """
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        from operator import Custom
        self.custom = Custom(self.config, self.problem)
    
    async def __call__(self, timeout=180):
        result = await self.custom(instruction="Solve the problem step by step. Think carefully.")
        return result
</code>
"""
    
    # Test request
    request_data = {
        "data_source": "internbootcamp",
        "solution_str": workflow_code,
        "ground_truth": "default",
        "extra_info": {
            "task_name": "sudoku_4x4_easy",
            "test_cases": [0],
            "data_path": ""
        }
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            f"{SERVER_URL}/compute_score",
            json=request_data,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Score: {data.get('score')}")
        print(f"Message: {data.get('message')}")
        print(f"Task Name: {data.get('task_name')}")
        
        if data.get('success'):
            print("✅ Compute score test passed")
            return True
        else:
            print(f"❌ Compute score failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Compute score test failed: {e}")
        return False


def test_compute_score_from_parquet():
    """Test compute_score using data from parquet file"""
    print("\n" + "="*60)
    print("Testing Compute Score with Parquet Data")
    print("="*60)
    
    if not TEST_DATA_PATH.exists():
        print(f"⚠️ Test data file not found: {TEST_DATA_PATH}")
        print("Skipping parquet test")
        return False
    
    try:
        # Load test data
        df = pd.read_parquet(TEST_DATA_PATH)
        print(f"Loaded {len(df)} test entries from parquet")
        
        if len(df) == 0:
            print("⚠️ No test data in parquet file")
            return False
        
        # Use first entry
        test_entry = df.iloc[0]
        
        # Extract prompt (messages format)
        prompt = test_entry.get('prompt', [])
        if isinstance(prompt, str):
            prompt = json.loads(prompt)
        
        # Create a simple workflow as response
        workflow_code = """
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        from operator import Custom
        self.custom = Custom(self.config, self.problem)
    
    async def __call__(self, timeout=180):
        result = await self.custom(instruction="Analyze and solve the InternBootcamp task.")
        return result
</code>
"""
        
        # Extract extra_info
        extra_info = test_entry.get('extra_info', {})
        if isinstance(extra_info, str):
            extra_info = json.loads(extra_info)
        
        # Create request
        request_data = {
            "data_source": test_entry.get('data_source', 'internbootcamp'),
            "solution_str": workflow_code,
            "ground_truth": "default",
            "extra_info": extra_info
        }
        
        print(f"Testing with task: {extra_info.get('task_name', 'unknown')}")
        print("Sending request...")
        
        response = requests.post(
            f"{SERVER_URL}/compute_score",
            json=request_data,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Score: {data.get('score')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('success'):
            print("✅ Parquet test passed")
            return True
        else:
            print(f"❌ Parquet test failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Parquet test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_compute():
    """Test batch compute endpoint"""
    print("\n" + "="*60)
    print("Testing Batch Compute Endpoint")
    print("="*60)
    
    # Create multiple tasks
    tasks = []
    task_names = ["sudoku_4x4_easy", "basic_arithmetic"]
    
    for i, task_name in enumerate(task_names):
        workflow_code = f"""
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        from operator import Custom
        self.custom = Custom(self.config, self.problem)
    
    async def __call__(self, timeout=180):
        result = await self.custom(instruction="Task {i}: Solve the problem.")
        return result
</code>
"""
        
        task = {
            "task_id": f"test_{i}",
            "data_source": "internbootcamp",
            "solution_str": workflow_code,
            "ground_truth": "default",
            "extra_info": {
                "task_name": task_name,
                "test_cases": [0],
                "data_path": ""
            }
        }
        tasks.append(task)
    
    request_data = {"tasks": tasks}
    
    try:
        print(f"Sending batch request with {len(tasks)} tasks...")
        response = requests.post(
            f"{SERVER_URL}/batch_compute",
            json=request_data,
            timeout=120
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total tasks: {data.get('total_tasks')}")
        print(f"Successful tasks: {data.get('successful_tasks')}")
        
        results = data.get('results', [])
        for result in results:
            print(f"  - Task {result['task_id']} ({result.get('task_name')}): "
                  f"score={result.get('score')}, success={result.get('success')}")
        
        if data.get('success'):
            print("✅ Batch compute test passed")
            return True
        else:
            print("❌ Batch compute test failed")
            return False
            
    except Exception as e:
        print(f"❌ Batch compute test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("InternBootcamp Reward Server Test Suite")
    print("="*60)
    print(f"Server URL: {SERVER_URL}")
    print(f"Test Data: {TEST_DATA_PATH}")
    
    # Check if server is running
    print("\nChecking if server is running...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️ Server returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        print("Run: start_internbootcamp_reward.bat")
        return
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Config", test_get_config),
        ("Tasks List", test_get_tasks),
        ("Simple Compute Score", test_compute_score_simple),
        ("Parquet Data Test", test_compute_score_from_parquet),
        ("Batch Compute", test_batch_compute)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(1)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total_count - passed_count} tests failed")


if __name__ == "__main__":
    main()