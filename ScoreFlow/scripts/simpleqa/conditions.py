# Task description
TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is **SimpleQA (World Knowledge Question Answering)**.

**Core Characteristics:**
- **Input:** Factual questions requiring world knowledge
- **Output:** Concise, accurate answers (usually entities, dates, or short facts)
- **Skills:** Knowledge retrieval, fact verification, reasoning about real-world information
- **Topics:** Science, technology, geography, history, culture, and more
'''

# System prompt
SYSTEM_PROMPT = '''Your fundamental purpose is to act as an expert knowledge assistant.
You provide accurate, factual answers to questions about the world.

Your response MUST follow this format:
1. A `<think>...</think>` block with your reasoning
2. A clear, concise answer to the question
'''

# Python code header
PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

# Python code footer (fixed template)
PYTHON_END = '''
    async def __call__(self):
        """
        Main entry point that executes the workflow.
        """
        TIMEOUT = {time}

        try:
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred. Details: {{escaped_error_details}}"
'''

# Operator instructions
START_PROMPT = '''### 2. Available Operators

**1. Generate:** `await self.generate(instruction: str, context: str = "") -> str`
   - Generate an answer based on world knowledge
   
**2. Revise:** `await self.revise(instruction: str, context: str) -> str`
   - Refine or correct an existing answer

**3. Summarize:** `await self.summarize(instruction: str, context: str) -> str`
   - Extract key information or simplify complex topics

**4. Ensemble:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
   - Combine multiple perspectives or sources

### 3. Your Task

Create a workflow to answer world knowledge questions using the operators above.

**Key Strategies:**
1. Understand what the question is asking
2. Identify the type of answer expected (Person, Place, Date, etc.)
3. Use world knowledge to provide accurate answers
4. Keep answers concise and factual
5. Consider the topic domain for context

<think>
For SimpleQA problems, I should:
1. Carefully analyze the question to understand what specific information is requested
2. Consider the topic and answer type to guide the response
3. Generate a factual, accurate answer
4. If needed, use Revise to ensure clarity and accuracy
5. Provide the final answer in a clear, concise format
</think>
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        
        # Step 1: Analyze the question to understand what is being asked
        question_analysis = await self.summarize(
            instruction="Identify: 1) What specific information is being asked for 2) The expected answer type (person, place, date, etc.) 3) Any relevant context clues"
        )
        
        # Step 2: Generate an initial answer based on world knowledge
        initial_answer = await self.generate(
            instruction="Based on your world knowledge, provide a factual answer to this question. Be specific and accurate. Focus on providing exactly what is asked for.",
            context=question_analysis
        )
        
        # Step 3: Refine the answer for clarity and conciseness
        refined_answer = await self.revise(
            instruction="Review this answer and ensure it is: 1) Factually correct 2) Directly answers the question 3) Concise without unnecessary information. Format as 'Final Answer: [your answer]'",
            context=initial_answer
        )
        
        return refined_answer
```
'''