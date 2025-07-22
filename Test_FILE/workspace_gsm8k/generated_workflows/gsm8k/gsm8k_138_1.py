# Workflow ID: gsm8k_138_1
# Benchmark: gsm8k
# Data Indices: [777, 916]

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
        Novel workflow combining Reflect-and-Regenerate with Iterative Refinement.
        1. Generate an initial solution using FlexibleCustom (sequential).
        2. Critically reflect on it to uncover potential flaws or assumptions.
        3. Use the reflection to guide a targeted iterative refinement via another FlexibleCustom (iterative pattern).
        4. Finally, review the refined solution for clarity and correctness.
        
        This structure emphasizes meta-cognition (reflection) and progressive improvement,
        unlike the existing ensemble-based approach that generates multiple solutions in parallel.
        """
        # Step 1: Initial solution via structured sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this problem by breaking it into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"]
        )

        # Step 2: Reflect on the initial solution — identify weaknesses without rewriting
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Regenerate a new solution based on reflection — use iterative refinement
        # This is the core difference: instead of generating 3 separate solutions, we now refine one
        # based on critical feedback from reflection
        improved_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve your solution: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_approach", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Final polish via review
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer