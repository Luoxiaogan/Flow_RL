# Workflow ID: humaneval_9_0
# Benchmark: humaneval
# Data Indices: [68, 109]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for specification-driven Python function generation.
        Handles any problem in the domain by combining multi-perspective analysis,
        parallel solution generation, rigorous revision, and ensemble synthesis.
        """
        import asyncio
        import re

        # Step 1: Deep specification analysis - extract examples, constraints, and patterns
        spec_analysis = await self.generate(
            instruction="""Perform a comprehensive structural analysis of the problem specification:
            1. Extract all input-output examples and format them as structured test cases.
            2. Identify explicit and implicit constraints (e.g., empty inputs, type requirements, edge cases).
            3. Infer the core algorithmic pattern from examples (e.g., filtering, sorting, mathematical operations).
            4. Determine expected return type and structure (list, int, bool, etc.) from examples.
            5. Identify any special conditions (e.g., "smallest index", "unique elements", "non-negative").
            6. Note any potential pitfalls or ambiguities in the specification.
            Present your analysis in a clear, structured format with labeled sections.""",
            context=""
        )

        # Step 2: Generate three parallel solution perspectives
        literal_solution, algorithmic_solution, constraint_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution based on LITERAL interpretation of examples:
                - Directly translate example behaviors into code
                - Prioritize matching example outputs exactly
                - Handle edge cases shown in examples
                - Use simple, straightforward logic
                - Return type must match examples precisely
                Specification context: {spec_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution based on ALGORITHMIC pattern recognition:
                - Identify the underlying algorithmic pattern (e.g., min/max, sorting, filtering, rotation)
                - Implement the most efficient general solution
                - Consider mathematical or logical optimizations
                - Handle edge cases systematically
                - Return type must be consistent with examples
                Specification context: {spec_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution based on CONSTRAINT-BASED reasoning:
                - Focus on satisfying all explicit and implicit constraints
                - Handle edge cases not shown in examples (empty, single element, boundary values)
                - Ensure type safety and structure compliance
                - Verify against inferred specification requirements
                - Return type must match specification exactly
                Specification context: {spec_analysis}""",
                context=""
            )
        )

        # Step 3: Revise each solution for correctness, type safety, and edge case coverage
        revised_solutions = await asyncio.gather(
            self.revise(
                instruction="""Critically revise this solution:
                1. Verify it handles all examples from specification
                2. Check for type mismatches (int vs float, list vs tuple)
                3. Add missing edge case handling (empty inputs, boundary values)
                4. Ensure function name matches ENTRY POINT exactly
                5. Simplify logic if over-engineered
                6. Fix any logical errors or off-by-one mistakes
                Return only the corrected Python function code.""",
                context=literal_solution
            ),
            self.revise(
                instruction="""Critically revise this solution:
                1. Verify it handles all examples from specification
                2. Check for type mismatches (int vs float, list vs tuple)
                3. Add missing edge case handling (empty inputs, boundary values)
                4. Ensure function name matches ENTRY POINT exactly
                5. Simplify logic if over-engineered
                6. Fix any logical errors or off-by-one mistakes
                Return only the corrected Python function code.""",
                context=algorithmic_solution
            ),
            self.revise(
                instruction="""Critically revise this solution:
                1. Verify it handles all examples from specification
                2. Check for type mismatches (int vs float, list vs tuple)
                3. Add missing edge case handling (empty inputs, boundary values)
                4. Ensure function name matches ENTRY POINT exactly
                5. Simplify logic if over-engineered
                6. Fix any logical errors or off-by-one mistakes
                Return only the corrected Python function code.""",
                context=constraint_solution
            )
        )

        # Step 4: Ensemble synthesis - select or merge the best solution
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these candidates:
            1. Evaluate each solution against the original specification and examples
            2. Select the solution that best balances correctness, simplicity, and completeness
            3. If one solution has superior core logic but another has better edge case handling, merge them
            4. Ensure the final solution passes all visible examples and handles inferred edge cases
            5. Verify function name matches ENTRY POINT exactly
            6. Return ONLY the final Python function code (no explanations, no markdown)
            Specification context: {spec_analysis}""",
            contexts_list=revised_solutions
        )

        # Step 5: Final validation and cleanup
        validated_solution = await self.revise(
            instruction="""Final validation and cleanup:
            1. Remove any explanatory comments or markdown formatting
            2. Ensure code is pure Python function implementation
            3. Verify function signature matches ENTRY POINT exactly
            4. Confirm return types match examples precisely
            5. Simplify any remaining over-engineered logic
            6. Return ONLY the clean Python function code""",
            context=final_solution
        )

        return validated_solution