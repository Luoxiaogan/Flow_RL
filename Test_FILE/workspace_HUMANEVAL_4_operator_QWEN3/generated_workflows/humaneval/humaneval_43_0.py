# Workflow ID: humaneval_43_0
# Benchmark: humaneval
# Data Indices: [90, 38]

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
        Universal workflow for generating correct Python functions from specifications.
        Dynamically adapts strategy based on problem type and validation feedback.
        """
        import asyncio

        # Phase 1: Deep problem analysis and classification
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this code generation problem. Structure your response as follows:

1. FUNCTION SIGNATURE: Extract exact function name and parameters.
2. INPUT/OUTPUT TYPES: Infer expected types from examples.
3. EXAMPLE PATTERNS: For each example, describe what it demonstrates about behavior, edge cases, and return values.
4. PROBLEM CLASSIFICATION: Categorize as one of: [Mathematical, String Manipulation, List Processing, Encoding/Decoding, Algorithmic Pattern, Other]. Justify your choice.
5. KEY INSIGHTS: What is the core algorithmic trick or pattern? Are there any 'aha' moments required?
6. EDGE CASES: List all edge cases demonstrated or implied by examples.
7. RETURN TYPE PRECISION: Note if examples require specific types (int vs float, None vs 0, etc.).

Be exhaustive. Your analysis will guide all subsequent steps.""",
            context=""
        )

        # Phase 2: Parallel strategy generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a direct, minimal Python implementation based on the analysis:
{analysis}

Guidelines:
- Implement exactly what examples demonstrate — no more, no less.
- Prioritize clarity and correctness over cleverness.
- Handle all edge cases identified in analysis.
- Match return types precisely.
- Do not add imports unless absolutely necessary.
- Return ONLY the function body (no signature, no extra text).""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an alternative solution by exploring mathematical or algebraic reformulations:
{analysis}

Ask: Can this be solved with formulas, set operations, or mathematical identities? 
For string problems: consider symmetry, inverses, or cyclic properties.
For list problems: consider sorting, deduplication, or sliding windows.
Return ONLY the function body.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a robust, defensively-coded solution focused on edge cases:
{analysis}

Explicitly handle:
- Empty inputs
- Single-element cases
- Duplicate values
- Boundary values
- Type conversions
Return ONLY the function body.""",
                context=""
            )
        ]

        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Phase 3: Ensemble synthesis and selection
        selected_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions and select or synthesize the best one. Criteria:

1. CORRECTNESS: Must match all example behaviors exactly.
2. MINIMALISM: No unnecessary operations or complexity.
3. EDGE CASE HANDLING: Must address all edge cases from analysis.
4. TYPE PRECISION: Return types must match examples (int/float/None).
5. READABILITY: Code should be clear and self-explanatory.

If no single solution is perfect, synthesize a new one by combining the best parts of each.
Return ONLY the final function body — nothing else.""",
            contexts_list=strategy_candidates
        )

        # Phase 4: Iterative validation and refinement (up to 3 iterations)
        current_code = selected_solution
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this code against the original problem:

ANALYSIS:
{analysis}

CODE:
{current_code}

Check:
- Does it handle ALL examples correctly?
- Are edge cases covered?
- Is return type precise?
- Any off-by-one errors?
- Any unnecessary complexity?
- Any missing imports?

If perfect, respond with 'VALIDATED'.
Otherwise, describe exactly what's wrong and how to fix it.""",
                context=current_code
            )

            if "VALIDATED" in validation_feedback.upper():
                break

            # Revise based on feedback
            current_code = await self.revise(
                instruction=f"""Fix the code based on this feedback:
{validation_feedback}

Preserve correct parts. Only change what's necessary.
Return ONLY the revised function body.""",
                context=current_code
            )

        # Phase 5: Final sanitization and output
        final_code = await self.summarize(
            instruction="""Sanitize this code for final output:

1. Remove any comments or print statements.
2. Ensure it contains ONLY the function body (no signature, no extra text).
3. Verify no unnecessary whitespace or formatting.
4. Confirm it's ready to be inserted into the function template.

Return ONLY the clean function body.""",
            context=current_code
        )

        return final_code