# Workflow ID: mbppplus_47_0
# Benchmark: mbppplus
# Data Indices: [35, 290, 208]

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
        Universal workflow for algorithmic decision problems.
        Uses dynamic validation cascade with adaptive branching.
        """
        import asyncio
        import re

        # PHASE 1: PROBLEM DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Perform forensic problem decomposition. Analyze:
            1. Input types and structures (numbers, strings, tuples, etc.)
            2. Expected output format and type (bool, string, etc.)
            3. Hidden constraints (edge cases, boundary conditions)
            4. Potential failure modes (empty inputs, type mismatches, overflows)
            5. Mathematical or logical invariants that must hold
            Format as structured JSON-like outline with explicit categories.
            Think like a test case designer trying to break naive solutions.""",
            context=""
        )

        # PHASE 2: PARALLEL HYPOTHESIS GENERATION
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Hypothesis #1 (Mathematical Purity):
                Based on decomposition: {decomposition}
                Implement with minimal assumptions. Focus on algebraic/logical correctness.
                Prioritize elegance over defensive programming. Assume ideal inputs.
                Return ONLY the function implementation as specified in the problem.
                Do NOT include explanations or comments.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis #2 (Defensive Robustness):
                Based on decomposition: {decomposition}
                Implement with maximum fault tolerance. Explicitly handle:
                - Empty/None inputs
                - Type mismatches
                - Boundary values
                - Overflow/underflow conditions
                Return ONLY the function implementation as specified.
                Include explicit edge case checks even if they seem redundant.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis #3 (Minimalist Pragmatism):
                Based on decomposition: {decomposition}
                Implement the simplest possible solution that passes visible tests.
                Avoid unnecessary checks or complexity. Optimize for readability.
                Return ONLY the function implementation as specified.
                Favor Python idioms and built-ins over custom logic.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis #4 (Exhaustive Validation):
                Based on decomposition: {decomposition}
                Implement with comprehensive input validation and edge case coverage.
                Include assertions or explicit checks for every inferred constraint.
                Return ONLY the function implementation as specified.
                Document edge cases handled via inline comments if needed.""",
                context=decomposition
            )
        )

        # PHASE 3: META-VALIDATION (Attempt to falsify each hypothesis)
        validation_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""META-VALIDATION: Assume this solution is WRONG.
                Your task: Find the smallest, simplest input that would break it.
                If you can't find any, explain why it's PROVABLY correct.
                Consider: type errors, boundary conditions, mathematical edge cases.
                Return in format: "BREAKING CASE: [input] → [expected vs actual]" OR "PROVABLY CORRECT: [reasoning]".
                Be ruthless. Even one counterexample invalidates the solution.""",
                context=hypothesis
            ) for hypothesis in solution_hypotheses]
        )

        # PHASE 4: ADAPTIVE ENSEMBLE SYNTHESIS
        final_solution = await self.ensemble(
            instruction="""SYNTHESIZE FINAL SOLUTION:
            You have 4 solution hypotheses with their validation results.
            Select or merge to create the optimal solution based on:
            1. Correctness (must be provably correct or have no known breaking cases)
            2. Robustness (handles edge cases explicitly)
            3. Simplicity (minimal complexity without sacrificing correctness)
            4. Readability (clear, Pythonic code)
            If multiple solutions are equally valid, prefer the one with explicit edge case handling.
            Return ONLY the final function implementation as specified in the original problem.
            Do NOT include any explanations, comments, or markdown.""",
            contexts_list=[f"HYPOTHESIS:\n{hyp}\nVALIDATION:\n{val}" 
                          for hyp, val in zip(solution_hypotheses, validation_results)]
        )

        # PHASE 5: FINAL SANITY CHECK (Optional refinement)
        # If validation detected potential issues, attempt one refinement
        if any("BREAKING CASE" in val for val in validation_results):
            refined_solution = await self.revise(
                instruction=f"""REFINEMENT: The following breaking cases were identified:
                {chr(10).join(validation_results)}
                
                Revise the solution to handle these cases explicitly.
                Maintain the original function signature and return type.
                Prioritize correctness over elegance.
                Return ONLY the revised function implementation.""",
                context=final_solution
            )
            return refined_solution

        return final_solution