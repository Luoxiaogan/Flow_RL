#!/usr/bin/env python3
"""
Setup script for workflow DAG analysis tools.
Installs required dependencies.
"""

import subprocess
import sys

def install_packages():
    """Install required Python packages."""
    required_packages = [
        'networkx',
        'matplotlib',
        'pandas',
        'tabulate'
    ]

    optional_packages = [
        'graphviz',  # For advanced visualization
        'pyvis'      # For interactive HTML graphs
    ]

    print("=" * 60)
    print("WORKFLOW DAG ANALYSIS - DEPENDENCY INSTALLATION")
    print("=" * 60)

    # Install required packages
    print("\n📦 Installing required packages...")
    for package in required_packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

    print("\n✅ Required packages installed successfully!")

    # Ask about optional packages
    response = input("\n🔧 Install optional packages for advanced visualization? (y/n): ")
    if response.lower() == 'y':
        print("\n📦 Installing optional packages...")
        for package in optional_packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except:
                print(f"⚠️  Warning: Failed to install {package}")

        print("\n⚠️  Note: Graphviz also requires the executable to be installed:")
        print("   Visit: https://graphviz.org/download/")

    print("\n" + "=" * 60)
    print("✨ Setup complete! You can now run the analysis.")
    print("=" * 60)
    print("\nQuick start:")
    print("  python run_analysis.py --limit 10")
    print("\nFor more options:")
    print("  python run_analysis.py --help")

if __name__ == "__main__":
    install_packages()