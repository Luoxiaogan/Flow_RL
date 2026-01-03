# Workflow DAG Analysis Project

This project provides tools for extracting, analyzing, and visualizing workflow topologies from Python code blocks.

## 📂 Project Structure

```
workflow_dag_analysis/
├── scripts/                    # Analysis and visualization scripts
│   ├── extract_python_code.py          # Extract Python code from workflows
│   ├── extract_workflow_dag.py         # DAG extraction with Graphviz
│   ├── extract_workflow_dag_simple.py  # Simplified DAG extraction (matplotlib)
│   ├── extract_workflow_summary.py     # Statistical analysis of workflows
│   └── sample_workflow.py              # Sample workflow for testing
├── data/                       # Input data files
│   └── extracted_python_code.jsonl     # Extracted workflow code blocks
├── results/                    # Generated visualizations and reports
│   ├── *.png                           # DAG visualizations
│   ├── *.json                          # Analysis reports
│   └── *.csv                           # Summary data
└── docs/                       # Documentation
    └── README.md                        # This file
```

## 🚀 Quick Start

### 1. Extract Python Code from Workflows
```bash
cd scripts/
python extract_python_code.py ../../../Test_FILE/training_data/workflow_dataset.json
```

### 2. Extract and Visualize DAGs
```bash
# Simple version (uses matplotlib, no external dependencies)
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --output-dir ../results/ --limit 10

# Advanced version (requires Graphviz)
python extract_workflow_dag.py --input ../data/extracted_python_code.jsonl --output-dir ../results/ --limit 10
```

### 3. Generate Statistical Analysis
```bash
python extract_workflow_summary.py --input ../data/extracted_python_code.jsonl --output-dir ../results/
```

## 📊 Script Descriptions

### `extract_python_code.py`
Extracts Python code blocks from workflow JSON files.
- **Input**: Workflow dataset JSON file
- **Output**: JSONL file with extracted code blocks
- **Usage**: First step in the analysis pipeline

### `extract_workflow_dag_simple.py`
Simplified DAG extraction and visualization using NetworkX and matplotlib.
- **Features**:
  - Extracts operator dependencies
  - Includes INPUT/OUTPUT nodes
  - Identifies parallel execution patterns
  - No external dependencies required
- **Output**: PNG visualizations and JSON metrics

### `extract_workflow_dag.py`
Advanced DAG extraction with Graphviz visualization.
- **Features**:
  - High-quality graph rendering
  - Hierarchical layout
  - Detailed dependency tracking
- **Requirements**: Graphviz executable must be installed

### `extract_workflow_summary.py`
Statistical analysis and pattern extraction.
- **Features**:
  - Operator distribution analysis
  - Workflow pattern identification
  - Benchmark statistics
  - CSV and JSON reports
- **Output**: Comprehensive analysis reports

## 📈 Analysis Metrics

The tools extract and analyze the following metrics:

1. **Topology Metrics**:
   - Number of operators
   - Number of dependencies
   - DAG verification
   - Longest execution path
   - Maximum parallelism

2. **Operator Statistics**:
   - Type distribution (Generate, Revise, Summarize, Ensemble)
   - Usage frequency
   - Common combinations

3. **Workflow Patterns**:
   - Parallel execution (asyncio.gather)
   - Multi-step workflows
   - Ensemble aggregation
   - Context dependencies

## 🎨 Visualization

DAG visualizations use color coding for different node types:
- 🟢 **Green**: Input node
- 🌸 **Pink**: Output node
- 🔵 **Blue**: Generate operators
- 🟣 **Purple**: Revise operators
- 🟡 **Yellow**: Summarize operators
- 🟠 **Orange**: Ensemble operators

## 📝 Data Format

### Input Format (extracted_python_code.jsonl)
```json
{
  "workflow_id": "humaneval_8_0",
  "benchmark": "humaneval",
  "data_indices": [23, 137],
  "python_code_blocks": ["..."],
  "num_code_blocks": 1
}
```

### Output Format (DAG analysis)
```json
{
  "workflow_id": "humaneval_8_0",
  "num_operators": 5,
  "longest_path": 4,
  "parallel_operations": 2,
  "operator_types": {
    "generate": 3,
    "ensemble": 1,
    "revise": 1
  }
}
```

## 🛠️ Dependencies

### Required Python Packages
```bash
pip install networkx matplotlib pandas tabulate
```

### Optional (for advanced visualization)
```bash
pip install graphviz pyvis
# Also requires Graphviz executable: https://graphviz.org/download/
```

## 📊 Sample Results

From analysis of 50 workflows:
- **Average operators per workflow**: 6.7
- **Most common operators**: Generate (100%), Revise (100%), Ensemble (100%)
- **Common patterns**: Parallel execution (96%), Multi-step (74%)
- **Typical combination**: Generate → Revise → Ensemble

## 🔍 Usage Examples

### Analyze specific workflow
```bash
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --workflow-id humaneval_8_0
```

### Generate summary report
```bash
python extract_workflow_summary.py --input ../data/extracted_python_code.jsonl --limit 100
```

### Verbose output with detailed metrics
```bash
python extract_workflow_dag_simple.py --input ../data/extracted_python_code.jsonl --verbose
```

## 📄 License

This project is part of the Flow_RL workflow analysis system.