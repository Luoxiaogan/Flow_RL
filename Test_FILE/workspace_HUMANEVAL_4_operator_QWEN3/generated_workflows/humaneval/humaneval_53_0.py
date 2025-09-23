# Workflow ID: humaneval_53_0
# Benchmark: humaneval
# Data Indices: [49, 98]

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
        Universal code generation workflow with self-validation and adaptive refinement.
        """
        import asyncio

        # STEP 1: Extract problem structure and classify type
        problem_analysis = await self.generate(
            instruction="""Analyze the problem specification in depth:
            1. Extract the exact function signature and parameter types.
            2. Identify the return type from examples (int, float, bool, string, etc.) - precision matters.
            3. Classify the problem domain: mathematical, string manipulation, list processing, algorithmic, etc.
            4. List all example cases and infer the transformation pattern.
            5. Identify edge cases explicitly shown (empty input, zero, single element, etc.).
            6. Note any numerical constraints or special behaviors (modular arithmetic, indexing rules, etc.).
            Format your analysis as a structured report with clear sections.""",
            context=""
        )

        # STEP 2: Generate multiple solution hypotheses in parallel
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code solution based on direct pattern extraction:
                - Use the analysis: {problem_analysis}
                - Implement the most straightforward interpretation of examples.
                - Handle edge cases explicitly mentioned.
                - Return type must match examples exactly.
                - Function name must match ENTRY POINT exactly.
                - No imports unless absolutely necessary (add inside function if needed).
                - Code must be minimal and not over-engineered.
                Output only the function code, nothing else.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code solution based on abstracted formula/algorithm:
                - Use the analysis: {problem_analysis}
                - Look for mathematical patterns, recurrence relations, or algorithmic shortcuts.
                - Consider efficiency and numerical stability if applicable.
                - Still handle edge cases and match return types.
                - Function name must match ENTRY POINT.
                Output only the function code, nothing else.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code solution focused exclusively on edge cases first:
                - Use the analysis: {problem_analysis}
                - Start by handling all edge cases shown in examples.
                - Then generalize to main cases.
                - Ensure type consistency and minimalism.
                - Function name must match ENTRY POINT.
                Output only the function code, nothing else.""",
                context=problem_analysis
            )
        )

        # STEP 3: Revise each hypothesis for precision and compliance
        revised_solutions = []
        for i, hypothesis in enumerate(solution_hypotheses):
            revision = await self.revise(
                instruction=f"""Critically revise this code solution:
                - Verify function name matches ENTRY POINT exactly.
                - Ensure return type matches examples precisely (int vs float matters).
                - Check that all example cases from docstring are handled correctly.
                - Eliminate any unnecessary complexity or imports.
                - Fix off-by-one errors, indexing mistakes, or type mismatches.
                - Ensure no over-engineering — implement exactly what's specified.
                - If edge cases from analysis are not handled, add them.
                Return only the corrected function code.""",
                context=hypothesis
            )
            revised_solutions.append(revision)

        # STEP 4: Ensemble — select best solution
        final_candidate = await self.ensemble(
            instruction="""Select the best solution from the candidates below:
            Criteria:
            1. Correctness: Must handle all example cases and edge cases.
            2. Minimalism: Simplest implementation that satisfies requirements.
            3. Precision: Return type and function name must be exact.
            4. No over-engineering: Implements only what's specified.
            Return ONLY the selected function code, nothing else.""",
            contexts_list=revised_solutions
        )

        # STEP 5: Self-validation — generate test assertions from examples
        validation_check = await self.generate(
            instruction=f"""Generate a self-validation script:
            - Based on the examples in the original docstring, create assert statements.
            - Use the function: {final_candidate}
            - Test all provided examples.
            - Also test edge cases identified in analysis: {problem_analysis}
            - If any test would fail, explain why and what needs fixing.
            - If all tests pass, output 'VALID'.
            Be extremely precise — simulate actual test execution.""",
            context=final_candidate
        )

        # STEP 6: Conditional refinement loop (max 1 iteration for efficiency)
        if "VALID" not in validation_check:
            final_candidate = await self.revise(
                instruction=f"""Fix the code based on validation feedback:
                Validation feedback: {validation_check}
                - Correct any mismatches with examples.
                - Ensure return types are exact.
                - Handle all edge cases.
                - Maintain function name and minimalism.
                Return only the corrected function code.""",
                context=final_candidate
            )

        return final_candidate