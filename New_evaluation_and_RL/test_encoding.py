#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test module import issue"""

import sys
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Print current configuration
print("Current sys.path:")
for p in sys.path[:3]:
    print(f"  - {p}")

# Test what SCOREFLOW_HANDLERS_PATH will be
project_root = Path("D:/temp/Flow_RL")
SCOREFLOW_HANDLERS_PATH = project_root  # Since scoreflow_handlers = "." in config

print(f"\nSCOREFLOW_HANDLERS_PATH would be: {SCOREFLOW_HANDLERS_PATH}")
print(f"Path exists: {SCOREFLOW_HANDLERS_PATH.exists()}")

# Add the path and try to import
sys.path.insert(0, str(SCOREFLOW_HANDLERS_PATH))
print(f"\nAdded to sys.path: {SCOREFLOW_HANDLERS_PATH}")

# Try to import the module
try:
    from ScoreFlow.scripts.base_handler import BenchmarkHandler
    print("\nSuccess! Module imported correctly")
except ImportError as e:
    print(f"\nError importing module: {e}")
    
# Also check what happens with the wrong path
wrong_path = Path("/Users/luogan/Code/workflow_generation/Flow_RL")
print(f"\nWrong path (from hardcoded value): {wrong_path}")
print(f"Wrong path exists: {wrong_path.exists()}")

# Try with wrong path
sys.path.insert(0, str(wrong_path))
try:
    import importlib
    importlib.reload(sys.modules.get('ScoreFlow.scripts.base_handler', None))
    print("Import with wrong path succeeded (unexpected)")
except:
    print("Import with wrong path failed (expected)")