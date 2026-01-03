"""
Prompt Builder for Multi-turn Generation

Builds prompts for workflow generation and error repair.
Supports both initial generation and repair/fix prompts.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AttemptHistory:
    """History of a single generation attempt"""
    workflow_code: str
    result: str  # "success", "error", "incorrect"
    error: Optional[str] = None
    traceback: Optional[str] = None
    accuracy: Optional[float] = None
    failed_problems: Optional[List[Dict]] = None


class PromptBuilder:
    """
    Builds prompts for multi-turn workflow generation.

    Supports:
    - Initial generation prompts
    - Error repair prompts (with traceback)
    - Result improvement prompts (with accuracy info)
    """

    # Default templates
    SYSTEM_PROMPT = """You are an expert Python programmer who specializes in creating workflow functions.
Your task is to write a Python function that can solve problems from the given benchmark.

Requirements:
1. Define a function named `solve` that takes a problem dict as input
2. The problem dict contains 'question' (str) and may contain other fields
3. Return the answer as a string
4. Handle edge cases gracefully
5. Use efficient algorithms when possible

Example structure:
```python
def solve(problem: dict) -> str:
    question = problem['question']
    # Your solution logic here
    return answer
```

For async functions, use:
```python
async def solve(problem: dict) -> str:
    question = problem['question']
    # Your solution logic here
    return answer
```
"""

    GENERATION_TEMPLATE = """{system_prompt}

## Task

{task_description}

## Benchmark

{benchmark_name}

{example_problems}

Please generate a Python function that can solve problems like these.
Output only the Python code, enclosed in ```python``` code blocks.
"""

    REPAIR_TEMPLATE = """{base_prompt}

## Previous Attempt

Your previous code:
```python
{previous_code}
```

Execution Error:
```
{error_message}
```

Detailed Traceback:
```
{traceback}
```

## Instructions

Please analyze the error and fix your code. Common issues to check:
1. Variable names and typos
2. Function signatures and return types
3. Data type conversions
4. Edge cases and null checks
5. Import statements

Generate the corrected Python code.
Output only the Python code, enclosed in ```python``` code blocks.
"""

    IMPROVEMENT_TEMPLATE = """{base_prompt}

## Previous Attempt

Your previous code achieved {accuracy:.1%} accuracy ({correct}/{total} correct).

```python
{previous_code}
```

Failed Problems:
{failed_info}

## Instructions

Please improve your code to handle more cases correctly.
Focus on the patterns in the failed problems.

Generate the improved Python code.
Output only the Python code, enclosed in ```python``` code blocks.
"""

    def __init__(
        self,
        system_prompt: str = None,
        generation_template: str = None,
        repair_template: str = None,
        improvement_template: str = None
    ):
        """
        Initialize the prompt builder.

        Args:
            system_prompt: Custom system prompt
            generation_template: Custom generation template
            repair_template: Custom repair template
            improvement_template: Custom improvement template
        """
        self.system_prompt = system_prompt or self.SYSTEM_PROMPT
        self.generation_template = generation_template or self.GENERATION_TEMPLATE
        self.repair_template = repair_template or self.REPAIR_TEMPLATE
        self.improvement_template = improvement_template or self.IMPROVEMENT_TEMPLATE

    def build_generation_prompt(
        self,
        task_description: str,
        benchmark_name: str,
        example_problems: List[Dict[str, Any]] = None,
        max_examples: int = 3
    ) -> str:
        """
        Build the initial generation prompt.

        Args:
            task_description: Description of the task
            benchmark_name: Name of the benchmark
            example_problems: Optional list of example problems
            max_examples: Maximum number of examples to include

        Returns:
            Generated prompt string
        """
        # Format example problems
        examples_str = ""
        if example_problems:
            examples = example_problems[:max_examples]
            examples_str = "## Example Problems\n\n"
            for i, prob in enumerate(examples, 1):
                question = prob.get('question', prob.get('problem', ''))
                answer = prob.get('answer', prob.get('solution', ''))
                examples_str += f"### Example {i}\n"
                examples_str += f"Question: {question}\n"
                if answer:
                    examples_str += f"Answer: {answer}\n"
                examples_str += "\n"

        return self.generation_template.format(
            system_prompt=self.system_prompt,
            task_description=task_description,
            benchmark_name=benchmark_name,
            example_problems=examples_str
        )

    def build_repair_prompt(
        self,
        base_prompt: str,
        previous_code: str,
        error_message: str,
        traceback: str = None
    ) -> str:
        """
        Build a repair prompt for fixing errors.

        Args:
            base_prompt: Original generation prompt
            previous_code: Code that failed
            error_message: Error message from execution
            traceback: Full traceback (optional but recommended)

        Returns:
            Repair prompt string
        """
        return self.repair_template.format(
            base_prompt=base_prompt,
            previous_code=previous_code,
            error_message=error_message,
            traceback=traceback or error_message
        )

    def build_improvement_prompt(
        self,
        base_prompt: str,
        previous_code: str,
        accuracy: float,
        correct: int,
        total: int,
        failed_problems: List[Dict[str, Any]] = None
    ) -> str:
        """
        Build an improvement prompt for better accuracy.

        Args:
            base_prompt: Original generation prompt
            previous_code: Code that was partially successful
            accuracy: Accuracy achieved (0-1)
            correct: Number of correct answers
            total: Total number of problems
            failed_problems: List of failed problem details

        Returns:
            Improvement prompt string
        """
        # Format failed problems info
        failed_info = ""
        if failed_problems:
            failed_info = "The following problems failed:\n"
            for i, prob in enumerate(failed_problems[:5], 1):  # Limit to 5
                prob_id = prob.get('id', i)
                error = prob.get('error', 'Incorrect answer')
                expected = prob.get('expected', 'N/A')
                got = prob.get('got', 'N/A')
                failed_info += f"- Problem {prob_id}: {error}\n"
                failed_info += f"  Expected: {expected}\n"
                failed_info += f"  Got: {got}\n"

        return self.improvement_template.format(
            base_prompt=base_prompt,
            previous_code=previous_code,
            accuracy=accuracy,
            correct=correct,
            total=total,
            failed_info=failed_info
        )

    def build_prompt_from_history(
        self,
        base_prompt: str,
        history: List[AttemptHistory]
    ) -> str:
        """
        Build prompt based on attempt history.

        Automatically chooses between generation, repair, or improvement
        based on the last attempt result.

        Args:
            base_prompt: Original generation prompt
            history: List of previous attempts

        Returns:
            Appropriate prompt string
        """
        if not history:
            # No history - return base prompt
            return base_prompt

        last_attempt = history[-1]

        if last_attempt.result == "error":
            # Previous attempt had an error - build repair prompt
            return self.build_repair_prompt(
                base_prompt=base_prompt,
                previous_code=last_attempt.workflow_code,
                error_message=last_attempt.error or "Unknown error",
                traceback=last_attempt.traceback
            )

        elif last_attempt.result == "incorrect" and last_attempt.accuracy is not None:
            # Previous attempt was partially correct - build improvement prompt
            # Calculate correct/total from accuracy
            if last_attempt.failed_problems:
                total = len(last_attempt.failed_problems)
                # Estimate total based on accuracy
                if last_attempt.accuracy > 0:
                    total = int(total / (1 - last_attempt.accuracy))
                correct = total - len(last_attempt.failed_problems)
            else:
                total = 10  # Default assumption
                correct = int(last_attempt.accuracy * total)

            return self.build_improvement_prompt(
                base_prompt=base_prompt,
                previous_code=last_attempt.workflow_code,
                accuracy=last_attempt.accuracy,
                correct=correct,
                total=total,
                failed_problems=last_attempt.failed_problems
            )

        else:
            # Success or unknown - return base prompt
            return base_prompt

    def extract_code_from_response(self, response: str) -> Optional[str]:
        """
        Extract Python code from LLM response.

        Looks for code in ```python``` or ``` blocks.

        Args:
            response: LLM response text

        Returns:
            Extracted code or None if not found
        """
        import re

        # Try ```python first
        pattern = r'```python\s*\n(.*?)```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try generic ``` blocks
        pattern = r'```\s*\n(.*?)```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            # Check if it looks like Python
            if 'def ' in code or 'async def' in code:
                return code

        # Try to find def solve directly
        pattern = r'((?:async\s+)?def\s+solve\s*\([^)]*\).*?)(?=\n(?:def |class |$)|$)'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None
