# Workflow ID: humaneval_37_0
# Benchmark: humaneval
# Data Indices: [163, 9]

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
        import re

        # Phase 1: Problem Classification and Pattern Extraction
        classification = await self.generate(
            instruction="""Analyze the function specification and examples to determine:
            1. What computational pattern is required? (e.g., filtering, mapping, accumulation, recursion)
            2. What are the key constraints? (e.g., input ranges, type requirements, edge cases)
            3. What is the expected output structure? (e.g., list, int, bool, same length as input)
            4. Are there any implicit bounds or clamping (like digits 0-9 or even numbers only)?
            5. Does order matter? Is the function stateful or stateless?
            Provide a structured analysis that will guide code generation.""",
            context=""
        )

        # Phase 2: Generate Multiple Solution Strategies in Parallel
        strategy_instructions = [
            """Generate a solution using imperative loops and conditionals. Focus on clarity and explicit state management. 
            Include detailed comments explaining the logic. Handle edge cases mentioned in examples.""",
            
            """Generate a solution using functional constructs (list comprehensions, built-in functions like max, filter, etc.). 
            Prioritize conciseness and Pythonic style. Ensure type correctness and example alignment.""",
            
            """Generate a solution that strictly mirrors the examples' input-output behavior, even if it seems hardcoded. 
            Focus on passing the provided examples exactly, then generalize minimally. Include type annotations if present in signature."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # Phase 3: Validate Each Strategy Against Provided Examples
        validation_tasks = []
        for i, strategy in enumerate(strategies):
            validation = await self.generate(
                instruction=f"""Simulate executing this code against ALL examples in the docstring:
                For each example input, compute the output step by step.
                Compare with expected output. Identify any mismatches in value, type, or structure.
                If all match, output 'VALID'. If any mismatch, specify exactly which example fails and how.
                Be extremely precise — int vs float, list length, order, etc. matter.
                Code to validate:
                {strategy}""",
                context=classification
            )
            validation_tasks.append(validation)

        # Phase 4: Ensemble Selection - Choose Best Validated Strategy
        selected_strategy = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Must pass all example validations (prefer 'VALID' candidates)
            2. Simplicity: Fewer lines, less complexity
            3. Generality: Not overfitted to examples
            4. Type Safety: Matches return types in examples exactly
            If multiple are valid, pick the most Pythonic. If none are fully valid, pick the one with fewest/smallest errors for revision.""",
            contexts_list=[f"Strategy {i+1} (Validation: {val}):\n{strat}" 
                          for i, (strat, val) in enumerate(zip(strategies, validation_tasks))]
        )

        # Phase 5: Revise for Edge Cases and Type Safety
        final_code = await self.revise(
            instruction="""Revise this code to ensure:
            1. It passes ALL examples in the docstring (fix any mismatches found in validation)
            2. Return types match examples EXACTLY (int vs float, list vs tuple, etc.)
            3. Handle edge cases: empty inputs, single elements, reversed ranges, zeros, negatives if applicable
            4. Use the exact function name from ENTRY POINT
            5. No extra imports or code — output ONLY the function definition
            6. If type hints are in signature, preserve them exactly
            Output ONLY the corrected Python function code, nothing else.""",
            context=selected_strategy
        )

        # Phase 6: Sanitize Output - Extract Only Function Code
        sanitized = await self.generate(
            instruction="""Extract ONLY the Python function code from the following text.
            Remove any explanations, markdown, or extra text. The output must be pure, runnable Python code.
            Ensure the function signature exactly matches the ENTRY POINT.
            If there are type imports (like 'from typing import List'), include them above the function.
            Do NOT include any other text or commentary.""",
            context=final_code
        )

        # Final cleanup: remove any remaining markdown or extra text
        code_lines = sanitized.split('\n')
        cleaned_lines = []
        for line in code_lines:
            if line.strip().startswith('