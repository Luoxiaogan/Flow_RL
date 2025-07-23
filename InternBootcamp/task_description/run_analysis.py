#!/usr/bin/env python
"""
Simple runner script for bootcamp task analysis.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import the analyzer
sys.path.insert(0, str(Path(__file__).parent))

from analyze_bootcamp_tasks import main

if __name__ == "__main__":
    print("Starting bootcamp task analysis...")
    print("This will analyze all tasks in parallel and generate descriptions.")
    print("-" * 50)
    
    try:
        asyncio.run(main())
        print("\nAnalysis completed successfully!")
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise