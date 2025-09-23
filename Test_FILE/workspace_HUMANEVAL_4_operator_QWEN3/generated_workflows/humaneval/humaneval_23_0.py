# Workflow ID: humaneval_23_0
# Benchmark: humaneval
# Data Indices: [121, 43]

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
        Universal code generation workflow that handles any function specification
        by dynamically adapting strategy based on problem analysis and example patterns.
        """
        import asyncio
        import re

        # Step 1: Classify problem type and extract core constraints from examples
        classification = await self.generate(
            instruction="""Analyze the problem specification and examples to determine:
            1. Primary operation type (filtering, searching, transforming, aggregating, etc.)
            2. Key constraints (index-based, value-based, pairwise, etc.)
            3. Edge cases implied by examples (empty inputs, single elements, boundary conditions)
            4. Return type and format requirements
            5. Any mathematical or logical patterns in the examples
            
            Structure your response as:
            TYPE: [operation type]
            CONSTRAINTS: [list of constraints]
            EDGE_CASES: [list of edge cases]
            RETURN_FORMAT: [specific return type and format]
            PATTERNS: [observed mathematical/logical patterns]""",
            context=""
        )

        # Step 2: Extract and formalize example patterns
        pattern_summary = await self.summarize(
            instruction="""From the examples in the docstring, extract:
            - Input-output mappings with annotations
            - Conditions that trigger specific behaviors
            - Type signatures and value ranges
            - Positional or structural dependencies
            Format as a structured specification that can guide implementation.""",
            context=classification
        )

        # Step 3: Generate multiple solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code based on this strategy:
                Strategy: Direct iteration with explicit index/value checks
                Constraints: {pattern_summary}
                Must match exact function name from ENTRY POINT.
                Return type must match examples precisely.
                Handle edge cases: {classification}
                Code must be minimal — no extra functionality beyond specification.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python code based on this strategy:
                Strategy: Functional approach using comprehensions and built-ins
                Constraints: {pattern_summary}
                Must match exact function name from ENTRY POINT.
                Return type must match examples precisely.
                Handle edge cases: {classification}
                Code must be minimal — no extra functionality beyond specification.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python code based on this strategy:
                Strategy: Mathematical pattern recognition and formula application
                Constraints: {pattern_summary}
                Must match exact function name from ENTRY POINT.
                Return type must match examples precisely.
                Handle edge cases: {classification}
                Code must be minimal — no extra functionality beyond specification.""",
                context=""
            )
        )

        # Step 4: Revise each solution against constraints and edge cases
        revised_solutions = []
        for attempt in solution_attempts:
            revised = await self.revise(
                instruction=f"""Critique and improve this code:
                - Verify it satisfies ALL constraints from: {pattern_summary}
                - Ensure it handles ALL edge cases from: {classification}
                - Confirm return type matches examples exactly
                - Remove any functionality not explicitly required
                - Fix any index, type, or logic errors
                - Ensure function name matches ENTRY POINT exactly
                Return ONLY the corrected Python code, nothing else.""",
                context=attempt
            )
            revised_solutions.append(revised)

        # Step 5: Ensemble best solution or synthesize from multiple
        final_code = await self.ensemble(
            instruction="""Select or synthesize the best solution:
            Criteria:
            1. Correctness: Must satisfy all example cases and implied constraints
            2. Precision: Return type and structure must match examples exactly
            3. Minimalism: No extra features, imports, or generalizations
            4. Robustness: Handles edge cases demonstrated in examples
            5. Clarity: Code should be readable but not over-commented
            
            If multiple solutions are valid, synthesize the most robust version.
            Return ONLY the final Python code, nothing else.""",
            contexts_list=revised_solutions
        )

        # Step 6: Final pruning pass to remove any hallucinated extras
        pruned_code = await self.revise(
            instruction="""Final cleanup:
            - Remove ANY code not directly required by the specification
            - No error handling, input validation, or type hints unless in examples
            - Ensure function signature matches ENTRY POINT exactly
            - Return type must be identical to examples (int vs float matters)
            - No extra imports, comments, or print statements
            Return ONLY the clean Python code, nothing else.""",
            context=final_code
        )

        return pruned_code