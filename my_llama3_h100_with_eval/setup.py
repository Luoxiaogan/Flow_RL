"""Setup script for the project"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llama3-h100-eval",
    version="1.0.0",
    author="Your Name",
    description="LLaMA3/Qwen training with automatic evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llama3-h100-eval",
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
        "all": ["wandb", "matplotlib", "numpy"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
