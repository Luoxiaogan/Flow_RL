# Bootcamp Task Analysis Tool

This tool analyzes all bootcamp tasks and generates three types of descriptions for each task using an LLM.

## Features

- **Parallel Processing**: Analyzes multiple tasks concurrently (up to 10 at a time)
- **Three Output Types**:
  1. **English Detailed Description**: Complete task description for other models
  2. **Chinese Brief Description**: Concise description for human readers
  3. **Quality Evaluation**: Code quality assessment with scores and correctness check

## Usage

Simply run:

```bash
python run_analysis.py
```

Or directly:

```bash
python analyze_bootcamp_tasks.py
```

## Output

The tool generates two output files in the `analysis_results/` directory:

1. **bootcamp_analysis_YYYYMMDD_HHMMSS.jsonl**: Complete analysis results in JSONL format
   - Each line contains the analysis for one task
   - Last line contains statistics

2. **bootcamp_summary_YYYYMMDD_HHMMSS.json**: Summary statistics in JSON format

## Output Format

Each task analysis includes:
```json
{
  "task_name": "task_identifier",
  "file_path": "relative/path/to/file.py",
  "english_detailed": "Detailed English description...",
  "chinese_brief": "中文简要描述...",
  "quality_evaluation": {
    "quality_score": 4,
    "correctness": "correct",
    "evaluation": "Brief evaluation text"
  }
}
```

## Statistics

The final statistics include:
- Total tasks analyzed
- Average quality score
- Quality score distribution (1-5)
- Correctness distribution (correct/incorrect/unclear)

## Configuration

The LLM configuration is set in the script:
```python
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}
```

## Requirements

- Python 3.7+
- aiohttp
- Standard library modules (asyncio, json, pathlib, etc.)