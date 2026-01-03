# Workflow ID: humaneval_54_0
# Benchmark: humaneval
# Data Indices: [110, 36]

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
        Universal code generation workflow for specification-driven function implementation.
        Dynamically adapts strategy based on problem type, examples, and inferred constraints.
        """
        import asyncio
        import re

        # === PHASE 1: PARALLEL PROBLEM DECOMPOSITION ===
        # Extract specification, classify problem, and generate initial solution in parallel
        spec_extraction, problem_classification, initial_solution = await asyncio.gather(
            self.generate(
                instruction="""Extract the precise functional specification from the docstring. Identify:
                - Input parameters and their types
                - Expected output type and format
                - Transformation rules described in text
                - All example input-output pairs (reformat as assertions)
                - Any explicit or implicit constraints
                - Edge cases hinted by examples
                Present as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Classify this problem by type and recommend solution strategy. Consider:
                - Is it mathematical, logical, string-based, or combinatorial?
                - Does it require counting, filtering, swapping, or pattern matching?
                - What algorithmic patterns fit (sliding window, resource allocation, digit analysis, etc.)?
                - Are there hidden invariants or mathematical shortcuts?
                - What are common pitfalls for this problem type?
                Output: [TYPE] + [STRATEGY] + [POTENTIAL EDGE CASES]""",
                context=""
            ),
            self.generate(
                instruction="""Generate a first-pass Python function implementation based ONLY on the examples.
                - Do NOT over-engineer; implement minimal logic that satisfies examples
                - Match function name exactly
                - Preserve return types (int/float/string) exactly as in examples
                - Include no imports or extra text
                - Focus on correctness over elegance
                Output ONLY the function body as Python code.""",
                context=""
            )
        )

        # === PHASE 2: VALIDATION-DRIVEN REFINEMENT ===
        # Validate against examples and refine
        validated_solution = await self.revise(
            instruction=f"""Revise the solution to ensure it satisfies ALL provided examples and inferred constraints.
            SPECIFICATION: {spec_extraction}
            PROBLEM TYPE: {problem_classification}
            
            Validation Checklist:
            1. Does the code handle all example cases correctly?
            2. Are edge cases from specification addressed?
            3. Is return type consistent with examples?
            4. Is logic minimal and directly derived from examples?
            5. Are there any over-engineered components? Remove them.
            
            If any check fails, modify the code accordingly.
            Output ONLY the revised function body as Python code.""",
            context=initial_solution
        )

        # === PHASE 3: PARALLEL PERSPECTIVE GENERATION ===
        # Generate alternative solutions from different angles
        alternative_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an ALTERNATIVE solution using a DIFFERENT algorithmic approach.
                Current solution: {validated_solution}
                Problem classification: {problem_classification}
                
                Requirements:
                - Must satisfy same examples
                - Use different core logic (e.g., if current uses counting, try filtering)
                - Maintain same function signature and return type
                - No imports or extra text
                Output ONLY the function body as Python code.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focused EXCLUSIVELY on edge cases.
                Specification: {spec_extraction}
                Current solution: {validated_solution}
                
                - What edge cases might break the current solution?
                - Implement defensive logic for those cases
                - Keep code minimal
                - Same function signature
                Output ONLY the function body as Python code.""",
                context=""
            )
        )

        # === PHASE 4: ENSEMBLE SYNTHESIS ===
        # Combine best aspects of all solutions
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the BEST solution based on:
            1. Correctness (must satisfy all examples)
            2. Minimalism (no unnecessary logic)
            3. Robustness (handles edge cases)
            4. Clarity (easy to understand)
            5. Adherence to specification (no extra features)
            
            If one solution is clearly superior, select it.
            If solutions have complementary strengths, merge them.
            Output ONLY the final function body as Python code.""",
            contexts_list=[validated_solution] + list(alternative_solutions)
        )

        # === PHASE 5: FINAL SANITY CHECK ===
        # One last revision for spec alignment
        final_output = await self.revise(
            instruction=f"""FINAL CHECK: Ensure this code EXACTLY matches specification.
            - Function name must match ENTRY POINT exactly
            - Return types must match examples precisely
            - No imports, no extra text, no print statements
            - Code must be self-contained
            - If any deviation, fix immediately
            
            Specification: {spec_extraction}
            Output ONLY the corrected function body as Python code.""",
            context=final_solution
        )

        return final_output