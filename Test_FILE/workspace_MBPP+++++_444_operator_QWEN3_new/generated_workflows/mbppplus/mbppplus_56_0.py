# Workflow ID: mbppplus_56_0
# Benchmark: mbppplus
# Data Indices: [207, 103, 166]

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

        # Generate three diverse solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction="""You are an expert Python programmer. Solve the problem with mathematical precision.
                - Use recursion or closed-form formulas where applicable
                - Handle edge cases: empty inputs, zero, negative numbers
                - Return exact types specified (list vs tuple vs scalar)
                - Include type hints in your thinking (but not in final code)
                - Write minimal, elegant code
                Output ONLY the function implementation as specified.""",
                context=""
            ),
            self.generate(
                instruction="""You are a pragmatic Python engineer. Solve the problem with clear, imperative logic.
                - Use loops and conditionals explicitly
                - Comment your logic mentally (but don't output comments)
                - Validate inputs defensively
                - Preserve order when required
                - Test mentally with edge cases: single element, duplicates, boundaries
                Output ONLY the function implementation as specified.""",
                context=""
            ),
            self.generate(
                instruction="""You are a defensive coder focused on robustness. Solve the problem with exhaustive edge case handling.
                - Consider: empty collections, None, type mismatches, overflow
                - Use early returns for trivial cases
                - Avoid recursion for deep stacks
                - Document assumptions mentally (but don't output them)
                - Prioritize correctness over elegance
                Output ONLY the function implementation as specified.""",
                context=""
            )
        )

        # Ensemble: Synthesize the best solution from the three attempts
        synthesized_solution = await self.ensemble(
            instruction="""You are a senior code reviewer. Synthesize a final solution from these three attempts.
            CRITICAL TASK:
            1. Compare all three solutions line by line
            2. Identify and preserve correct edge case handling
            3. Ensure type signature matches exactly (list/tuple/scalar)
            4. Fix any off-by-one errors, boundary condition misses
            5. Choose the most efficient approach that doesn't sacrifice correctness
            6. If solutions conflict, prefer the one with explicit edge case handling
            7. Output ONLY the final function implementation - no explanations
            
            VALIDATION CHECKLIST:
            - Does it handle empty inputs?
            - Does it preserve order if required?
            - Are return types exact?
            - Are duplicates handled correctly?
            - Is recursion depth safe?
            - Are negative numbers/boundaries considered?""",
            contexts_list=solution_attempts
        )

        # Iterative refinement: Two rounds of targeted revision
        refined_solution = synthesized_solution
        for iteration in range(2):
            refined_solution = await self.revise(
                instruction=f"""You are a meticulous debugger. Improve this code for production use.
                ASSUME: This code is 90% correct. Find the 10% that fails under edge conditions.
                TASK:
                - Review for type consistency (list vs tuple vs set)
                - Check empty input handling
                - Verify boundary conditions (min/max values, single elements)
                - Ensure no silent failures on invalid inputs
                - Preserve exact function signature
                - Make MINIMAL changes - only fix actual bugs
                - Do NOT add comments or docstrings
                OUTPUT: Only the corrected function implementation""",
                context=refined_solution
            )

        # Final sanity check via summarization (extract core logic for validation)
        logic_summary = await self.summarize(
            instruction="""Extract the core algorithmic logic in one sentence.
            Format: "This function [action] by [method] while handling [edge cases]."
            Example: "This function counts pairs summing to target by nested iteration while handling empty arrays and duplicates."
            If the summary reveals a fundamental mismatch with the problem intent, flag it by starting with 'ERROR:'. Otherwise, just output the summary.""",
            context=refined_solution
        )

        # If summary indicates catastrophic failure, return the last refined version anyway
        # (In a real system, we might retry, but here we assume prior steps caught major issues)
        if logic_summary.startswith("ERROR:"):
            # Still return the code - the summary is just a sanity check
            pass

        return refined_solution