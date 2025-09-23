# Workflow ID: humaneval_65_0
# Benchmark: humaneval
# Data Indices: [31, 106]

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
        
        # PHASE 1: DEEP PROBLEM DECOMPOSITION
        # Extract patterns, edge cases, and rules from examples
        decomposition = await self.generate(
            instruction="""Perform a forensic analysis of the problem specification. Extract:
            1. All input/output examples and infer the transformation rule.
            2. Whether indexing starts at 0 or 1 (if applicable).
            3. Return types for each example (int, float, list, etc.) - note any inconsistencies.
            4. Explicit edge cases shown in examples.
            5. Implicit edge cases not shown but logically necessary (e.g., n=0, n=1, negative numbers, empty inputs).
            6. Algorithmic hints or mathematical patterns.
            Format as a structured outline with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION ATTEMPTS
        # Generate 3 diverse approaches
        attempt_a, attempt_b, attempt_c = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a LITERAL solution that follows the examples exactly.
                - Implement the most straightforward interpretation of the examples.
                - Do not generalize beyond what's shown.
                - Prioritize matching example outputs over efficiency.
                - Use simple loops or conditionals.
                Problem decomposition for context:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a MATHEMATICAL/GENERALIZED solution.
                - Derive underlying formulas or algorithms from the patterns.
                - Optimize for efficiency and elegance.
                - Use mathematical insights (e.g., factorial formulas, prime properties).
                - Handle edge cases systematically.
                Problem decomposition for context:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a DEFENSIVE/EDGE-CASE solution.
                - Prioritize handling all edge cases (explicit and implicit).
                - Add type checks and boundary validations.
                - Ensure return types match examples exactly.
                - Sacrifice elegance for robustness.
                Problem decomposition for context:
                {decomposition}""",
                context=decomposition
            )
        )

        # PHASE 3: PARALLEL META-VALIDATION
        # Critique each attempt against imagined test cases
        critique_a, critique_b, critique_c = await asyncio.gather(
            self.revise(
                instruction="""Critique this solution:
                - Does it handle ALL examples in the docstring correctly?
                - Are edge cases (especially implicit ones) covered?
                - Is the return type EXACTLY as shown in examples (int vs float matters)?
                - Is there any over-engineering or unnecessary complexity?
                - What hidden test cases might break this?
                Provide specific line-by-line feedback and mark as 'PASSED' or 'FAILED'.""",
                context=attempt_a
            ),
            self.revise(
                instruction="""Critique this solution:
                - Does it handle ALL examples in the docstring correctly?
                - Are edge cases (especially implicit ones) covered?
                - Is the return type EXACTLY as shown in examples (int vs float matters)?
                - Is there any over-engineering or unnecessary complexity?
                - What hidden test cases might break this?
                Provide specific line-by-line feedback and mark as 'PASSED' or 'FAILED'.""",
                context=attempt_b
            ),
            self.revise(
                instruction="""Critique this solution:
                - Does it handle ALL examples in the docstring correctly?
                - Are edge cases (especially implicit ones) covered?
                - Is the return type EXACTLY as shown in examples (int vs float matters)?
                - Is there any over-engineering or unnecessary complexity?
                - What hidden test cases might break this?
                Provide specific line-by-line feedback and mark as 'PASSED' or 'FAILED'.""",
                context=attempt_c
            )
        )

        # PHASE 4: ENSEMBLE SYNTHESIS
        # Combine best elements into final solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the three attempts and their critiques:
            - Must pass all example cases exactly as specified.
            - Must handle all edge cases identified in critiques.
            - Prioritize correctness over elegance, but prefer efficient approaches when correct.
            - Return types must match examples precisely (int, not float; list structure exact).
            - Remove any unnecessary imports, comments, or over-engineering.
            - Function name must match ENTRY POINT exactly.
            You may merge parts of different solutions. If conflicts exist, choose the version that best satisfies the critiques.
            Output ONLY the final Python function code, nothing else.""",
            contexts_list=[attempt_a, attempt_b, attempt_c, critique_a, critique_b, critique_c]
        )

        # PHASE 5: FINAL PRECISION REFINEMENT
        # Ensure type precision and remove any fluff
        polished_solution = await self.revise(
            instruction="""Final polish:
            - Ensure return types EXACTLY match examples (if examples show int, return int; if float, return float).
            - Remove any unnecessary comments, debug prints, or imports.
            - Verify function name matches ENTRY POINT exactly.
            - No over-engineering - implement exactly what's specified.
            - Ensure no external imports are included (they'll be auto-added).
            Output ONLY the clean Python function code, nothing else.""",
            context=final_solution
        )

        return polished_solution