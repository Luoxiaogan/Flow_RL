#!/usr/bin/env python
"""
Directory cleanup and reorganization script
"""
import os
import shutil
from pathlib import Path

def cleanup_directory():
    """Clean up and reorganize the directory"""
    
    base_dir = Path(__file__).parent
    
    print("Directory Cleanup Plan")
    print("="*50)
    
    # 1. List files to delete
    print("\n1. Files to DELETE:")
    delete_patterns = [
        "standalone_test_reports",
        "simple_test_reports", 
        "local_test_reports",
        "mock_callback_reports",
        "simple_callback_test",
        "*.log"
    ]
    
    for pattern in delete_patterns:
        for path in base_dir.glob(pattern):
            print(f"   - {path.name}")
    
    # 2. Suggested reorganization
    print("\n2. Suggested REORGANIZATION:")
    print("   Create structured directories:")
    print("   - src/training/ (move train.py, data_collator.py, utils.py)")
    print("   - scripts/training/ (move run_*.sh)")
    print("   - scripts/analysis/ (move analysis_*.py)")
    print("   - tests/unit/ (move test_loss_mask.py, test_model.py)")
    print("   - tests/integration/ (move test_evaluation_system.py, etc.)")
    print("   - docs/technical/ (move H100_SETUP.md, LOSS_MASKING.md)")
    print("   - outputs/ (for logs, checkpoints, reports)")
    
    # 3. Files to keep as-is
    print("\n3. Files to KEEP:")
    keep_files = [
        "src/evaluation/",  # Evaluation module
        "configs/",          # Configuration files
        "evaluation_plan.md", # Important documentation
    ]
    
    for file in keep_files:
        print(f"   - {file}")
    
    # 4. Create .gitignore
    print("\n4. Create .gitignore:")
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*.pyc

# Outputs
outputs/
*.log
checkpoint-*/
evaluation_reports/
*_test_reports/
*_callback_test/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Local
local_*.yaml
local_*.json
local_test_data.jsonl
simple_test_data.jsonl
mock_test_data.jsonl
"""
    
    gitignore_path = base_dir / ".gitignore"
    print(f"   Will create: {gitignore_path}")
    
    # Ask for confirmation
    print("\n" + "="*50)
    response = input("Execute cleanup? (y/n): ")
    
    if response.lower() == 'y':
        # Execute cleanup
        print("\nExecuting cleanup...")
        
        # Delete test reports and logs
        for pattern in ["*_test_reports", "*_callback_test", "*.log"]:
            for path in base_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"   Deleted directory: {path.name}")
                elif path.is_file():
                    path.unlink()
                    print(f"   Deleted file: {path.name}")
        
        # Create .gitignore
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print(f"   Created: .gitignore")
        
        print("\nCleanup completed!")
        print("\nNext steps for full reorganization:")
        print("1. Create new directory structure")
        print("2. Move files to appropriate locations")
        print("3. Update import paths if needed")
        print("4. Create README.md with documentation")
    else:
        print("\nCleanup cancelled.")

if __name__ == "__main__":
    cleanup_directory()