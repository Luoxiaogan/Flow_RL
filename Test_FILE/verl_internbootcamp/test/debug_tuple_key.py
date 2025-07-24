"""
Debug script to find tuple keys in data structures
"""
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_tuple_keys(obj, path=""):
    """Recursively find any tuple keys in nested dictionaries"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, tuple):
                print(f"Found tuple key at {path}: {key}")
            new_path = f"{path}.{key}" if path else str(key)
            find_tuple_keys(value, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_tuple_keys(item, f"{path}[{i}]")
    return obj

def test_json_serialization(data):
    """Test if data can be JSON serialized"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        print("JSON serialization successful")
        return True
    except TypeError as e:
        print(f"JSON serialization failed: {e}")
        find_tuple_keys(data)
        return False

if __name__ == "__main__":
    # Test data with tuple key
    test_data = {
        "normal_key": "value",
        "nested": {
            ("tuple", "key"): "This will cause error",
            "normal": "ok"
        }
    }
    
    print("Testing data with tuple key:")
    test_json_serialization(test_data)
    
    # Test normal data
    normal_data = {
        "reward_model": {
            "task_name": "test",
            "test_cases": ["case1", "case2"],
            "score": 1.0
        }
    }
    
    print("\nTesting normal reward_model:")
    test_json_serialization(normal_data)