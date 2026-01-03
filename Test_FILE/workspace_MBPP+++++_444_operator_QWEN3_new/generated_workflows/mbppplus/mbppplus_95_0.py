# Workflow ID: mbppplus_95_0
# Benchmark: mbppplus
# Data Indices: [219, 337, 347]

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
        import json

        # PHASE 1: Problem Decomposition & Specification Inference
        specification = await self.generate(
            instruction="""Analyze the problem to infer a complete functional specification. Consider:
            1. Input parameter types, constraints, and valid ranges
            2. Expected return type and format
            3. Edge cases implied by test cases (empty inputs, boundaries, duplicates, type variations)
            4. Assumptions that must hold for correctness
            5. Ambiguities in the problem statement that need resolution
            6. Performance or complexity constraints if any
            Structure your response as a detailed specification document with clear sections.
            Do not write code yet — focus solely on understanding requirements and constraints.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        # Three different implementation philosophies explored in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Implement the function using a LITERAL approach:
                - Follow the reference solution's style and logic exactly
                - Assume inputs are always valid as per basic test cases
                - Prioritize simplicity and directness
                - Do not add extra validation unless explicitly required
                Specification context: {specification}
                Output ONLY the function implementation with necessary imports.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Implement the function using a DEFENSIVE approach:
                - Add explicit type checking and bounds validation
                - Handle edge cases even if not shown in basic tests
                - Return appropriate values or fail gracefully for invalid inputs
                - Prioritize robustness over simplicity
                Specification context: {specification}
                Output ONLY the function implementation with necessary imports.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Implement the function using an OPTIMIZED approach:
                - Consider performance and algorithmic efficiency
                - Use appropriate data structures and algorithms
                - Handle edge cases intelligently without over-engineering
                - Balance readability with efficiency
                Specification context: {specification}
                Output ONLY the function implementation with necessary imports.""",
                context=specification
            )
        ]
        
        literal_impl, defensive_impl, optimized_impl = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Individual Revision Against Specification
        revision_tasks = [
            self.revise(
                instruction=f"""Critique this implementation against the specification:
                - Does it handle all inferred edge cases?
                - Does it respect type contracts and return types?
                - Are there logical gaps or potential failures?
                - Is it unnecessarily complex or oversimplified?
                Suggest precise corrections. Specification: {specification}""",
                context=literal_impl
            ),
            self.revise(
                instruction=f"""Critique this implementation against the specification:
                - Does it handle all inferred edge cases?
                - Does it respect type contracts and return types?
                - Are there logical gaps or potential failures?
                - Is it unnecessarily complex or oversimplified?
                Suggest precise corrections. Specification: {specification}""",
                context=defensive_impl
            ),
            self.revise(
                instruction=f"""Critique this implementation against the specification:
                - Does it handle all inferred edge cases?
                - Does it respect type contracts and return types?
                - Are there logical gaps or potential failures?
                - Is it unnecessarily complex or oversimplified?
                Suggest precise corrections. Specification: {specification}""",
                context=optimized_impl
            )
        ]
        
        revised_literal, revised_defensive, revised_optimized = await asyncio.gather(*revision_tasks)

        # PHASE 4: Synthesis via Ensemble
        final_implementation = await self.ensemble(
            instruction="""You are given three revised implementations of the same function.
            Synthesize them into a single optimal solution that:
            1. Matches the reference solution's simplicity where edge cases don't require complexity
            2. Incorporates defensive checks ONLY where edge cases are likely or specified
            3. Preserves exact type contracts and return formats
            4. Is minimally complex and maximally readable
            5. Passes all basic test cases and handles inferred edge cases
            Output ONLY the final function implementation with necessary imports — nothing else.""",
            contexts_list=[revised_literal, revised_defensive, revised_optimized]
        )

        # PHASE 5: Validation and Conditional Refinement (Self-Correction Loop)
        validation = await self.generate(
            instruction=f"""Validate this implementation against the original problem:
            - Does it pass all basic test cases shown?
            - Does it handle the edge cases inferred in the specification?
            - Are there any type mismatches or logical errors?
            - Is the implementation unnecessarily complex?
            If any issues are found, describe them precisely. Otherwise, respond 'VALID'.
            Implementation: {final_implementation}""",
            context=final_implementation
        )

        # Conditional refinement — only if validation finds issues
        if "VALID" not in validation.upper():
            final_implementation = await self.revise(
                instruction=f"""Fix the issues identified in validation:
                Validation feedback: {validation}
                Preserve the core logic but correct the specific problems.
                Output ONLY the corrected function implementation with necessary imports.""",
                context=final_implementation
            )

        return final_implementation