"""
Analyze a sample of bootcamp tasks to demonstrate the functionality.
"""

import asyncio
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent))

from analyze_bootcamp_tasks import BootcampAnalyzer

async def analyze_sample():
    """Analyze a sample of tasks."""
    bootcamp_dir = Path(__file__).parent.parent / "internbootcamp" / "bootcamp"
    output_dir = Path(__file__).parent / "sample_analysis_results"
    
    analyzer = BootcampAnalyzer(bootcamp_dir, output_dir)
    
    # Get all task directories
    all_task_dirs = [d for d in bootcamp_dir.iterdir() 
                    if d.is_dir() and not d.name.startswith('__') 
                    and d.name not in ['ChemStructure2Property', 'arc', 'arrowmaze', 'bigcodebench']]
    
    # Sample 10 random tasks
    sample_size = min(10, len(all_task_dirs))
    sample_tasks = random.sample(all_task_dirs, sample_size)
    
    print(f"Analyzing {sample_size} sample tasks out of {len(all_task_dirs)} total tasks...")
    print("Selected tasks:")
    for task in sample_tasks:
        print(f"  - {task.name}")
    print()
    
    # Analyze the sample
    analyzer.results = []
    for i, task_dir in enumerate(sample_tasks, 1):
        print(f"\nProcessing task {i}/{sample_size}: {task_dir.name}")
        try:
            result = await analyzer.analyze_task(task_dir)
            if result:
                analyzer.results.append(result)
                print(f"  [SUCCESS] Successfully analyzed and written to {analyzer.output_file.name}")
            else:
                print(f"  [FAIL] No result obtained")
        except Exception as e:
            print(f"  [ERROR] Error: {str(e)}")
    
    # Save final statistics
    analyzer.save_final_statistics()
    
    # Print summary
    stats = analyzer.generate_statistics()
    print(f"\n{'='*50}")
    print(f"Analysis Summary:")
    print(f"  - Total tasks analyzed: {stats['total_tasks']}")
    print(f"  - Average quality score: {stats['average_quality_score']:.2f}")
    print(f"  - Correctness distribution: {stats['correctness_distribution']}")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("Starting sample bootcamp task analysis...")
    print("This will analyze 10 random tasks as a demonstration.")
    print("-" * 50)
    
    try:
        asyncio.run(analyze_sample())
        print("\nSample analysis completed successfully!")
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise