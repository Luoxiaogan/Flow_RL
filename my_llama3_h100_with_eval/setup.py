"""Setup script for the project"""
from setuptools import setup, find_packages

setup(
    name="llama3-h100-eval",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "accelerate>=0.25.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "eval": ["aiohttp", "pandas", "tqdm"],
    },
)
