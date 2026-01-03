# Workflow ID: humaneval_71_0
# Benchmark: humaneval
# Data Indices: [140, 10]

import asyncio

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

        # PHASE 1: PARALLEL PATTERN EXTRACTION
        # Generate three independent interpretations of the transformation rule
        pattern_tasks = [
            self.generate(
                instruction="""Analyze the docstring examples step by step. 
                Derive the exact transformation rule as if you were designing a state machine.
                For each example, show the input, expected output, and the state transitions or conditions that explain the transformation.
                Focus on character-by-character processing and edge cases like leading/trailing spaces, empty strings, or special characters.
                Format your response as a structured rule description with clear conditions and actions.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the docstring examples from a string manipulation perspective.
                Try to express the transformation as a sequence of regex substitutions or string operations.
                For each example, show the input, expected output, and the regex/operation that would achieve it.
                Consider edge cases and ensure your rules are comprehensive.
                Format your response as a series of operations with explanations.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the docstring examples algorithmically.
                Describe the transformation as a loop or recursive process that processes the string in chunks or runs.
                Identify patterns like 'consecutive spaces', 'palindromic suffixes', etc., and how they trigger different behaviors.
                For each example, trace through the algorithm step by step.
                Format your response as pseudocode with detailed comments explaining each decision point.""",
                context=""
            )
        ]
        pattern_interpretations = await asyncio.gather(*pattern_tasks)

        # PHASE 2: ENSEMBLE SYNTHESIS
        # Combine the three interpretations into a unified, robust algorithm description
        synthesized_strategy = await self.ensemble(
            instruction="""You are given three different interpretations of the same code generation problem.
            Your task is to synthesize them into one coherent, complete, and correct algorithm description.
            Resolve any conflicts by choosing the interpretation that best explains ALL examples.
            Fill in any gaps by combining insights from multiple interpretations.
            The final output should be a clear, step-by-step algorithm that a programmer could implement directly.
            Include explicit handling of edge cases mentioned in any of the interpretations.
            Format as a numbered list of steps with clear conditions and actions.""",
            contexts_list=pattern_interpretations
        )

        # PHASE 3: INITIAL CODE GENERATION
        initial_code = await self.generate(
            instruction=f"""Implement the function exactly as specified, using the following synthesized strategy:
            {synthesized_strategy}

            CRITICAL REQUIREMENTS:
            - Function name MUST match the ENTRY POINT exactly
            - Return type MUST match the examples in the docstring (int vs float, string formatting, etc.)
            - Handle all edge cases mentioned in the strategy
            - No helper functions unless absolutely necessary (prefer inline logic)
            - No imports unless explicitly required (and only if allowed by the domain)
            - Code must be minimal and exactly match the specification — no over-engineering

            Return ONLY the function implementation, nothing else.""",
            context=synthesized_strategy
        )

        # PHASE 4: SELF-VALIDATION AND REVISION LOOP (max 2 iterations)
        current_code = initial_code
        for iteration in range(2):
            # Generate validation assertions from docstring examples
            validation_assertions = await self.generate(
                instruction="""Extract all examples from the docstring and convert them into assert statements.
                For each example, write an assert statement that checks if the function output matches the expected output.
                Format as a Python code block with assert statements only.
                Example: assert fix_spaces("Example") == "Example"
                Include edge cases and boundary conditions.""",
                context=""
            )

            # Simulate validation by checking if current code would pass these asserts
            validation_check = await self.generate(
                instruction=f"""Given the following code and assert statements, would the code pass all assertions?
                Code:
                {current_code}

                Assertions:
                {validation_assertions}

                Analyze step by step. If any assertion would fail, explain why and what needs to be fixed.
                If all pass, say 'ALL ASSERTIONS PASS'.
                Be brutally honest — this is for debugging.""",
                context=current_code
            )

            if "ALL ASSERTIONS PASS" in validation_check:
                break

            # Revise code based on validation feedback
            current_code = await self.revise(
                instruction=f"""Revise the code to fix the issues identified in the validation check.
                Validation feedback:
                {validation_check}

                Ensure the function name matches ENTRY POINT exactly.
                Ensure return types match examples precisely.
                Handle all edge cases.
                Return ONLY the revised function implementation, nothing else.""",
                context=current_code
            )

        # PHASE 5: COMPLIANCE ENFORCEMENT
        final_code = await self.revise(
            instruction="""Final compliance check:
            1. Does the function name EXACTLY match the ENTRY POINT? If not, fix it.
            2. Does the return type match the examples in the docstring? (e.g., int vs float, string formatting)
            3. Are there any unnecessary imports or helper functions? Remove them.
            4. Is the code minimal and exactly as specified? Remove any over-engineering.
            5. Does it handle all edge cases from the examples?

            Return ONLY the final function implementation, nothing else.""",
            context=current_code
        )

        return final_code