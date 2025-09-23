# Workflow ID: humaneval_47_0
# Benchmark: humaneval
# Data Indices: [74, 66]

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

        # STEP 1: Deep problem decomposition - extract contracts from examples
        decomposition = await self.generate(
            instruction="""Perform deep structural analysis of the problem:
            1. Identify the exact function signature and entry point.
            2. For each example in the docstring, extract the input-output contract.
            3. Infer implicit rules (e.g., tiebreakers, edge case handling).
            4. Classify problem type: string, math, list, algorithm, or hybrid.
            5. List potential edge cases not explicitly shown but logically implied.
            6. Determine return type precision requirements (int vs float, list structure, etc.).
            Format as structured markdown with clear sections.""",
            context=""
        )

        # STEP 2: Parallel solution generation with diverse strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution focusing ONLY on replicating example behavior:
                - Treat examples as executable specifications
                - Implement exactly what examples demonstrate
                - Prioritize matching outputs over elegance
                - Include all edge cases from decomposition: {decomposition}
                - Output ONLY the function body as valid Python code""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate solution from first principles:
                - Derive general algorithm independent of examples
                - Optimize for correctness across all possible inputs
                - Handle edge cases systematically: {decomposition}
                - Use mathematical/logical reasoning over string manipulation when possible
                - Output ONLY the function body as valid Python code""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate defensive solution focused on edge cases:
                - Assume malicious or pathological inputs
                - Handle empty inputs, type boundaries, and extreme values
                - Add explicit guards for inferred constraints from: {decomposition}
                - Prioritize robustness over performance
                - Output ONLY the function body as valid Python code""",
                context=decomposition
            )
        )

        # STEP 3: Cross-revision - each solution critiques and improves others
        revised_solutions = []
        for i, solution in enumerate(solution_attempts):
            other_solutions = [s for j, s in enumerate(solution_attempts) if j != i]
            combined_others = "\n\n---\n\n".join(other_solutions)
            revised = await self.revise(
                instruction=f"""Critically revise this solution by cross-examining with alternatives:
                Original solution: {solution}
                
                Alternative approaches:
                {combined_others}
                
                Tasks:
                1. Identify weaknesses or edge cases missed in original
                2. Incorporate strongest elements from alternatives
                3. Ensure strict compliance with all example contracts
                4. Verify return type and structure matches exactly
                5. Remove any non-code text or explanations
                Output ONLY the improved function body as valid Python code""",
                context=solution
            )
            revised_solutions.append(revised)

        # STEP 4: Ensemble synthesis - merge best parts into final solution
        final_code = await self.ensemble(
            instruction="""Synthesize the ultimate solution by merging the best elements:
            - Combine algorithmic elegance with edge case robustness
            - Ensure 100% compliance with all example contracts
            - Prefer simplest implementation that satisfies all constraints
            - Verify function name matches entry point exactly
            - Output ONLY the function body as valid Python code (no explanations, no markdown)
            - Remove any import statements or non-essential code""",
            contexts_list=revised_solutions
        )

        # STEP 5: Final sanitization - ensure pure code output
        sanitized = await self.revise(
            instruction="""Final cleanup:
            - Remove any non-Python code, comments, or explanations
            - Ensure only function body remains (no function signature)
            - Verify no print statements or debug code
            - Confirm return types match examples exactly
            - Output ONLY the clean Python code""",
            context=final_code
        )

        return sanitized