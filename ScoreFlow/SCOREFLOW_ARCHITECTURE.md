# ScoreFlow Architecture Reference Guide

## Overview

ScoreFlow is a modular benchmark execution framework that generates and executes workflows to solve problems across multiple domains. The system uses LLM-powered operators integrated with MetaGPT's ActionNode framework to create intelligent problem-solving workflows.

## Core Architecture Principles

### 1. Unified Abstract Interface
All benchmarks inherit from `BenchmarkHandler` (base_handler.py), ensuring consistent:
- Data loading from JSONL files
- Problem text extraction
- Answer validation
- Workflow execution patterns

### 2. Operator-Based Workflow System
Four fundamental operators power all workflows:
- **Generate**: Creates new information from context
- **Revise**: Improves existing content  
- **Summarize**: Extracts key information
- **Ensemble**: Evaluates and synthesizes multiple solutions

### 3. Multi-Strategy Validation
- **LLM-based judgment**: Intelligent comparison for complex answers
- **Rule-based extraction**: Pattern matching for structured answers
- **Hybrid approaches**: Fallback mechanisms for robustness

## Directory Structure

```
ScoreFlow/scripts/
├── base_handler.py                 # Abstract base class for all benchmarks
├── common/                         # Shared components
│   ├── operator.py                # Core operator implementations
│   └── operator_an.py            # Pydantic models for structured outputs
├── utils/                         # Utility functions
│   └── code_executor.py         # Safe code execution
└── [benchmark]/                  # Individual benchmark implementations
    ├── conditions.py             # Prompts and configuration
    └── handler.py               # Data processing and validation
```

## Benchmark Implementation Pattern

### Standard Files in Each Benchmark

#### 1. conditions.py
Contains all prompts and configuration:

```python
# Meta-level guidance for workflow generation
META_PROMPTS = """
Strategy for solving {benchmark} problems...
"""

# LLM role definition
SYSTEM_PROMPT = """
You are an expert {domain} problem solver...
"""

# Workflow execution templates
PYTHON_START = """
# Import operators and setup
from common.operator import Generate, Revise, Summarize, Ensemble
import asyncio

# Problem context
problems = {problems}

async def solve():
    # Workflow implementation
"""

PYTHON_END = """
# Execute workflow
result = asyncio.run(solve())
print(result)
"""

# Detailed problem description and operator documentation
START_PROMPT = """
Task: Solve {benchmark} problems
Available operators: Generate, Revise, Summarize, Ensemble
...
"""
```

#### 2. handler.py
Implements benchmark-specific logic:

```python
from scripts.base_handler import BenchmarkHandler

class {Benchmark}Handler(BenchmarkHandler):
    def get_prompt_text(self, num_problems=3):
        """Extract clean problem text for workflow generation"""
        problems = []
        for idx in selected_indices:
            problem_text = self._extract_problem(self.data[idx])
            problems.append(problem_text)
        return problems
    
    def get_verification_data(self, indices):
        """Get data needed for answer validation"""
        return [(self.data[i]['problem'], self.data[i]['answer']) 
                for i in indices]
    
    def judge(self, predicted_answer, ground_truth):
        """Validate predicted answer against ground truth"""
        # Benchmark-specific validation logic
        return is_correct
```

## Benchmark Profiles

### DROP (Reading Comprehension)
- **Domain**: Discrete reasoning over text passages
- **Input**: Passage + Question pairs
- **Output**: Numbers, dates, text spans, or comparative answers
- **Validation**: LLM-based intelligent judgment
- **Key Challenge**: Multi-hop reasoning across paragraphs

### GSM8K (Grade School Math)
- **Domain**: Elementary mathematical word problems
- **Input**: Natural language math problems
- **Output**: Single numerical answers
- **Validation**: LLM-based comparison with ground truth
- **Key Challenge**: Multi-step arithmetic reasoning

### High Level Math (Advanced Mathematics)
- **Domain**: Competition-level mathematics (AIME, LIMR, MATH)
- **Input**: Complex mathematical problems
- **Output**: Mathematical expressions, formulas, proofs
- **Validation**: Rule-based extraction with normalization
- **Key Features**:
  - LaTeX expression parsing
  - Fraction and decimal normalization
  - Numerical tolerance for floating-point comparison
  - Multiple answer format patterns

## Operator System Details

### Core Operators (common/operator.py)

All operators inherit from MetaGPT's ActionNode and use Pydantic for structured outputs:

```python
class Generate(ActionNode):
    """Creates new content based on instructions and context"""
    async def run(self, instruction, context=""):
        # LLM generates new information
        return generated_content

class Revise(ActionNode):
    """Improves existing content with specific instructions"""
    async def run(self, instruction, old_text):
        # LLM revises based on feedback
        return revised_text

class Summarize(ActionNode):
    """Extracts key information from longer text"""
    async def run(self, instruction, long_text):
        # LLM creates concise summary
        return summary

class Ensemble(ActionNode):
    """Evaluates and synthesizes multiple solutions"""
    async def run(self, instruction, text_list):
        # LLM selects best or creates synthesis
        return best_solution
```

### Pydantic Models (common/operator_an.py)

Ensure structured, validated outputs:

```python
class GenerateOp(BaseModel):
    instruction: str
    context: str = ""
    output: str
    
class ReviseOp(BaseModel):
    instruction: str
    old_text: str
    output: str

class EnsembleOp(BaseModel):
    instruction: str
    text_list: List[str]
    output: str
```

## Workflow Execution Flow

1. **Problem Selection**: Handler selects N problems from dataset
2. **Prompt Construction**: Combines META_PROMPTS, SYSTEM_PROMPT, and START_PROMPT with selected problems
3. **Workflow Generation**: LLM creates Python workflow using operators
4. **Code Assembly**: Handler wraps workflow with PYTHON_START/END templates
5. **Execution**: Workflow runs in safe multiprocessing environment
6. **Validation**: Handler judges outputs against ground truth
7. **Result Collection**: Successful workflows saved as training data

## Advanced Features

### FlexibleCustom Operator
Special operator for complex reasoning patterns:
- Dynamic prompt construction
- Multi-step reasoning chains
- Custom validation logic
- Used for advanced mathematical proofs and multi-hop reasoning

### Asynchronous Execution
- All operators support async/await
- Enables parallel operator execution
- Improves performance for complex workflows

### Error Handling
- Graceful degradation on operator failures
- Timeout management (configurable per benchmark)
- Comprehensive logging for debugging

## Integration Points

### MetaGPT Integration
- Uses MetaGPT's ActionNode framework
- Leverages MetaGPT's LLM configuration (config2.yaml)
- Compatible with MetaGPT's agent architecture

### Data Format
All benchmarks use JSONL format:
```json
{"problem": "...", "answer": "...", "metadata": {...}}
```

### API Configuration
- Primary LLM: Configured in config2.yaml
- Supports OpenAI-compatible APIs
- Model switching via environment variables

## Best Practices for Adding New Benchmarks

1. **Inherit from BenchmarkHandler**: Ensures consistent interface
2. **Implement Required Methods**:
   - `get_prompt_text()`: Extract clean problem text
   - `get_verification_data()`: Provide validation data
   - `judge()`: Implement domain-specific validation
3. **Define Prompts in conditions.py**: Follow existing template patterns
4. **Reuse Common Operators**: Avoid reimplementing standard functionality
5. **Add Custom Operators Only When Necessary**: Extend for domain-specific needs
6. **Test with Multiple Problems**: Ensure robustness across dataset
7. **Document Special Requirements**: Note any unique dependencies or configurations

## Common Pitfalls and Solutions

### Import Path Issues
- **Problem**: Benchmarks importing from other benchmarks
- **Solution**: Move shared code to common/ directory

### Template Format Confusion
- **Problem**: Mix of old and new template formats
- **Solution**: Use latest PYTHON_START/END pattern consistently

### Answer Format Variations
- **Problem**: Inconsistent answer formats in datasets
- **Solution**: Implement robust normalization in judge() method

### Timeout Management
- **Problem**: Complex workflows exceeding time limits
- **Solution**: Configure appropriate timeouts in conditions.py

## Performance Considerations

- **Operator Granularity**: Balance between flexibility and efficiency
- **Parallel Execution**: Use async operators for independent tasks
- **Caching**: Implement result caching for expensive operations
- **Batch Processing**: Process multiple problems simultaneously when possible

## Future Extensibility

The architecture supports:
- New operator types (e.g., Search, Verify, Calculate)
- Multi-modal problems (images, tables, graphs)
- Interactive workflows with user feedback
- Distributed execution across multiple nodes
- Real-time workflow optimization based on execution feedback

---

This architecture enables flexible, robust problem-solving across diverse domains while maintaining consistency and extensibility.