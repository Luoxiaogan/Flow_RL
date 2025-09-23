# Workflow ID: mbppplus_15_0
# Benchmark: mbppplus
# Data Indices: [252, 97]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: STRUCTURED DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into atomic, executable subproblems.
            For each subproblem:
            - State precisely what needs to be computed or transformed
            - Specify input and output types
            - List edge cases to consider (empty inputs, boundaries, type mismatches)
            - Note any dependencies on other subproblems
            Return as structured list with 'id', 'description', 'dependencies'.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Based on the decomposition, propose a solution strategy that is:
            - Mathematically rigorous for computational problems
            - Algorithmically efficient (avoid brute force where possible)
            - Explicitly handles all listed edge cases
            - Preserves required data types and structure
            Explain step by step how you would implement this.""",
            
            """Based on the decomposition, propose an alternative solution strategy that:
            - Prioritizes code simplicity and readability
            - Uses built-in Python functions and idioms
            - Includes defensive checks for invalid inputs
            - Matches expected output format exactly
            Explain your approach with concrete examples.""",
            
            """Based on the decomposition, propose a third solution strategy that:
            - Optimizes for performance on large inputs
            - Uses appropriate data structures (sets, generators, etc.)
            - Avoids unnecessary computations or memory usage
            - Still handles all edge cases from decomposition
            Justify your design choices."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=str(decomposition)) for instr in strategy_instructions]
        )

        # PHASE 3: STRATEGY SYNTHESIS
        # Summarize each strategy to reduce noise
        strategy_summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Extract key algorithmic steps and edge case handling. Ignore fluff.",
                context=strat
            ) for strat in strategies]
        )

        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all three strategies into one optimal approach.
            Prioritize:
            1. Correctness on all edge cases
            2. Matching expected output type and structure
            3. Code clarity and maintainability
            4. Computational efficiency
            Return a step-by-step implementation plan that combines the strengths of all approaches.""",
            contexts_list=strategy_summaries
        )

        # PHASE 4: CODE GENERATION WITH VALIDATION LOOP
        code = None
        validation_feedback = ""
        
        for attempt in range(3):
            code = await self.programmer(
                instruction=f"""Implement the solution following this plan:
                {synthesized_strategy}
                
                CRITICAL REQUIREMENTS:
                - Use EXACT function name and signature from problem
                - Handle ALL edge cases mentioned in decomposition
                - Return correct data type (list vs tuple vs dict vs int)
                - Never assume input validity - validate defensively
                - Match reference solution behavior without copying code
                - Include minimal necessary imports inside function if needed
                
                If implementation requires helper functions, define them inside the main function.
                """,
                context=validation_feedback,
                max_retries=1
            )

            # Validate the generated code
            validation_feedback = await self.generate(
                instruction=f"""Critically analyze this code:
                {code}
                
                Check for:
                1. Correct handling of edge cases (empty inputs, single elements, boundaries)
                2. Exact match of expected return type and structure
                3. Potential bugs or logical errors
                4. Type mismatches or conversion errors
                5. Efficiency issues on large inputs
                6. Compliance with problem constraints
                
                If perfect, respond with 'VALID'.
                If flawed, list specific issues and how to fix them.""",
                context=code
            )

            if "VALID" in validation_feedback.upper():
                break

        # PHASE 5: FINAL REVISION & CLEANUP
        final_code = await self.revise(
            instruction="""Final polish:
            - Ensure function signature exactly matches problem
            - Remove any debug prints or unnecessary comments
            - Optimize for readability without sacrificing correctness
            - Verify all edge cases are handled
            - Ensure no external dependencies beyond standard library
            - Return ONLY the function implementation with necessary imports""",
            context=code
        )

        return final_code