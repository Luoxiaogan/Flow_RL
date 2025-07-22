#!/usr/bin/env python3
"""
Comprehensive tool for managing InternBootcamp modules.
Combines functionality for checking errors, fixing imports, and generating registry.
"""

import os
import sys
import re
import json
import importlib
import argparse
from pathlib import Path
from datetime import datetime

class BootcampTools:
    def __init__(self):
        self.bootcamp_dir = Path(__file__).parent / 'internbootcamp' / 'bootcamp'
        sys.path.insert(0, str(Path(__file__).parent))
    
    def fix_imports(self, dry_run=False):
        """Fix import statements in bootcamp files."""
        fixed_count = 0
        error_count = 0
        
        print("Fixing imports in bootcamp files...")
        
        for root, dirs, files in os.walk(self.bootcamp_dir):
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py') and file not in ['__init__.py', 'base.py']:
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if 'from bootcamp import Basebootcamp' in content:
                            new_content = content.replace(
                                'from bootcamp import Basebootcamp',
                                'from ..base import Basebootcamp'
                            )
                            
                            if not dry_run:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                            
                            print(f"[FIXED] {file_path.relative_to(self.bootcamp_dir)}")
                            fixed_count += 1
                    except Exception as e:
                        print(f"[ERROR] {file_path.relative_to(self.bootcamp_dir)}: {e}")
                        error_count += 1
        
        print(f"\nSummary: Fixed {fixed_count} files, {error_count} errors")
    
    def scan_classes(self):
        """Scan all bootcamp files and find class names."""
        registry = {}
        
        print("Scanning for bootcamp classes...")
        
        for root, dirs, files in os.walk(self.bootcamp_dir):
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py') and file not in ['__init__.py', 'base.py', 'BaseEnvironment.py']:
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find class definitions
                        pattern = r'class\s+(\w+)\s*\([^)]*Basebootcamp[^)]*\)'
                        matches = re.findall(pattern, content)
                        
                        if matches:
                            rel_path = file_path.relative_to(self.bootcamp_dir)
                            module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
                            
                            for class_name in matches:
                                module_path = '.' + '.'.join(module_parts)
                                registry[class_name] = module_path
                    except Exception:
                        pass
        
        return dict(sorted(registry.items()))
    
    def generate_registry(self):
        """Generate bootcamp registry files."""
        registry = self.scan_classes()
        
        # Save as JSON
        with open('bootcamp_registry.json', 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        # Save as Python code
        with open('bootcamp_registry_generated.py', 'w', encoding='utf-8') as f:
            f.write("# Auto-generated bootcamp registry\n")
            f.write("BOOTCAMP_REGISTRY = {\n")
            for key, value in registry.items():
                f.write(f'    "{key}": "{value}",\n')
            f.write("}\n")
        
        print(f"Generated registry with {len(registry)} entries")
        print("Files created: bootcamp_registry.json, bootcamp_registry_generated.py")
    
    def check_module(self, module_path, class_name):
        """Check a single bootcamp module."""
        try:
            module = importlib.import_module(module_path)
            bootcamp_class = getattr(module, class_name)
            
            from internbootcamp.bootcamp import Basebootcamp
            if not issubclass(bootcamp_class, Basebootcamp):
                return "warning", "Not a subclass of Basebootcamp"
            
            # Check required methods
            missing_methods = []
            for method in ['prompt_func', 'extract_output', '_verify_correction']:
                if not hasattr(bootcamp_class, method):
                    missing_methods.append(method)
                elif getattr(bootcamp_class, method) is getattr(Basebootcamp, method, None):
                    missing_methods.append(f"{method} (not overridden)")
            
            if missing_methods:
                return "warning", f"Missing/not overridden: {', '.join(missing_methods)}"
            
            return "success", "All checks passed"
            
        except ImportError as e:
            return "error", f"ImportError: {str(e)}"
        except Exception as e:
            return "error", f"{type(e).__name__}: {str(e)}"
    
    def check_all(self, output_file='bootcamp_check_results.json'):
        """Check all bootcamp modules for errors."""
        # Load registry
        try:
            with open('bootcamp_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
        except FileNotFoundError:
            print("ERROR: bootcamp_registry.json not found. Run --generate-registry first.")
            return
        
        print(f"Checking {len(registry)} bootcamp modules...")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {"success": [], "warning": [], "error": []}
        
        for i, (class_name, module_path) in enumerate(registry.items(), 1):
            if module_path.startswith('.'):
                full_module_path = 'internbootcamp.bootcamp' + module_path
            else:
                full_module_path = module_path
            
            status, message = self.check_module(full_module_path, class_name)
            
            results[status].append({
                "name": class_name,
                "module": full_module_path,
                "message": message
            })
            
            if i % 100 == 0:
                print(f"Progress: {i}/{len(registry)} checked...")
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Successful: {len(results['success'])}")
        print(f"  Warnings: {len(results['warning'])}")
        print(f"  Errors: {len(results['error'])}")
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {output_file}")
    
    def check_single(self, bootcamp_name):
        """Check a single bootcamp module with detailed output."""
        try:
            with open('bootcamp_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
        except FileNotFoundError:
            print("ERROR: bootcamp_registry.json not found. Run --generate-registry first.")
            return
        
        if bootcamp_name not in registry:
            print(f"Error: '{bootcamp_name}' not found in registry")
            print("\nUse --list to see all available bootcamps")
            return
        
        module_path = registry[bootcamp_name]
        if module_path.startswith('.'):
            full_module_path = 'internbootcamp.bootcamp' + module_path
        else:
            full_module_path = module_path
        
        print(f"Checking: {bootcamp_name}")
        print(f"Module: {full_module_path}")
        print("=" * 60)
        
        status, message = self.check_module(full_module_path, bootcamp_name)
        print(f"Status: {status.upper()}")
        print(f"Message: {message}")
    
    def list_bootcamps(self):
        """List all available bootcamps."""
        try:
            with open('bootcamp_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
        except FileNotFoundError:
            print("ERROR: bootcamp_registry.json not found. Run --generate-registry first.")
            return
        
        print(f"Available bootcamps ({len(registry)} total):\n")
        for name in sorted(registry.keys()):
            print(f"  {name}")

def main():
    parser = argparse.ArgumentParser(description='InternBootcamp management tools')
    parser.add_argument('--fix-imports', action='store_true', help='Fix import statements')
    parser.add_argument('--generate-registry', action='store_true', help='Generate bootcamp registry')
    parser.add_argument('--check-all', action='store_true', help='Check all bootcamp modules')
    parser.add_argument('--check', metavar='NAME', help='Check a specific bootcamp')
    parser.add_argument('--list', action='store_true', help='List all bootcamps')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (for fix-imports)')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    tools = BootcampTools()
    
    if args.fix_imports:
        tools.fix_imports(dry_run=args.dry_run)
    
    if args.generate_registry:
        tools.generate_registry()
    
    if args.check_all:
        tools.check_all()
    
    if args.check:
        tools.check_single(args.check)
    
    if args.list:
        tools.list_bootcamps()

if __name__ == "__main__":
    main()