# Workflow ID: humaneval_21_0
# Benchmark: humaneval
# Data Indices: [149, 88]

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

        # PHASE 1: DECOMPOSE - Extract core logic and edge cases from specification
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze the function specification and examples to extract the core algorithmic logic.
                Answer these questions:
                1. What is the primary operation? (filtering, sorting, transforming, calculating, etc.)
                2. What are the input and output types?
                3. What conditions or rules govern the transformation?
                4. How are edge cases (empty input, single element, duplicates) handled?
                5. Are there multiple sorting criteria or conditional behaviors?
                Present your analysis as a structured bullet-point summary.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all edge cases and special conditions from the examples.
                Look for:
                - Empty inputs
                - Single-element inputs
                - Boundary values
                - Duplicates
                - Type-specific behaviors
                - Implicit constraints
                List each edge case with a brief description of how it should be handled.""",
                context=""
            )
        ]
        
        logic_analysis, edge_cases = await asyncio.gather(*decomposition_tasks)

        # PHASE 2: STRATEGIZE - Generate multiple implementation approaches
        strategy_instructions = [
            """Implement the solution using an imperative approach:
            - Use explicit loops and conditionals
            - Prioritize readability and step-by-step logic
            - Handle edge cases explicitly
            - Match the exact function signature and return type""",
            
            """Implement the solution using a functional approach:
            - Use list comprehensions, filter(), map(), sorted() with key functions
            - Prioritize conciseness and Pythonic idioms
            - Handle edge cases through conditional expressions
            - Match the exact function signature and return type""",
            
            """Implement the solution using a hybrid approach:
            - Combine the clearest elements of both imperative and functional styles
            - Optimize for both readability and efficiency
            - Include comments explaining key logic decisions
            - Match the exact function signature and return type"""
        ]

        strategy_candidates = await asyncio.gather(
            *[self.generate(instruction=instr + f"\n\nBased on this analysis:\n{logic_analysis}\n\nEdge cases to handle:\n{edge_cases}", context="") 
              for instr in strategy_instructions]
        )

        # PHASE 3: ENSEMBLE - Synthesize the best solution from candidates
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from the three candidates below.
            Selection criteria:
            1. Correctness: Must handle all edge cases identified: {edge_cases}
            2. Precision: Must match return types and function signature exactly
            3. Clarity: Code should be readable and well-structured
            4. Conciseness: Avoid unnecessary complexity while maintaining correctness
            5. Pythonic: Use appropriate Python idioms and standard library functions
            
            Return ONLY the final function implementation with no additional text or explanations.
            The function name MUST match the ENTRY POINT exactly.
            Include necessary imports if any (though most problems won't need them).""",
            contexts_list=strategy_candidates
        )

        # PHASE 4: VALIDATE & REVISE - Ensure compliance with specification
        for attempt in range(3):  # Maximum 3 revision attempts
            validation = await self.generate(
                instruction=f"""Critically review the code below against the original specification.
                Check:
                1. Does the function name EXACTLY match the ENTRY POINT?
                2. Do return types match the examples? (int vs float, list vs tuple, etc.)
                3. Are all edge cases from this analysis handled: {edge_cases}?
                4. Is the logic consistent with the examples in the docstring?
                5. Are there any over-engineered elements that aren't required?
                
                If any issues are found, describe them specifically. If no issues, respond with 'VALID'.
                Do not suggest improvements unless they fix specification violations.""",
                context=synthesized_solution
            )

            if "VALID" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break

            # Revise based on validation feedback
            synthesized_solution = await self.revise(
                instruction=f"""Fix the specification compliance issues identified below.
                Original analysis: {logic_analysis}
                Edge cases: {edge_cases}
                Validation feedback: {validation}
                
                Make ONLY the minimal changes necessary to fix specification violations.
                Preserve the overall structure and approach unless it's fundamentally flawed.
                Return ONLY the corrected function implementation with no additional text.""",
                context=synthesized_solution
            )
        else:
            # Fallback: Generate minimalist version if still failing
            synthesized_solution = await self.generate(
                instruction=f"""Generate the most minimal, specification-compliant solution possible.
                Based on: {logic_analysis}
                Must handle: {edge_cases}
                Focus ONLY on meeting the exact requirements - no extra features or optimizations.
                Return ONLY the function implementation with exact ENTRY POINT name.""",
                context=""
            )

        return synthesized_solution