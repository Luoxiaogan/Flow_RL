# Workflow ID: gsm8k_67_1
# Benchmark: gsm8k
# Data Indices: [14, 185, 235]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Novel workflow combining Iterative Refinement + Branching Logic via FlexibleCustom.
        1. Use a flexible custom operator in 'iterative' mode to generate an initial solution with refinement steps.
        2. If the reflection suggests ambiguity or incomplete reasoning, branch into a parallel ensemble for robustness.
        3. Otherwise, proceed with iterative review to polish the solution.
        This hybrid approach balances structured progression with adaptive strategy based on meta-cognitive feedback.
        """
        # Step 1: Generate an initial solution using iterative pattern (e.g., "analyze → solve → verify")
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem by iteratively refining your approach. First analyze, then solve, then verify."
        )

        # Step 2: Reflect on the solution to assess quality and identify potential issues
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Conditional branching logic based on reflection content
        if "ambiguous" in reflection.lower() or "missing step" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection indicates weakness, fall back to parallel ensemble for robustness
            solution_candidates = []
            for i in range(3):
                candidate = await self.custom(
                    instruction="Solve the problem independently using a different method each time. Focus on clarity and completeness."
                )
                solution_candidates.append(candidate)
            
            final_answer = await self.sc_ensemble(solutions=solution_candidates)
        else:
            # Otherwise, refine further using iterative Review
            refined_solution = await self.review(pre_solution=initial_solution)
            final_answer = await self.review(pre_solution=refined_solution)

        return final_answer