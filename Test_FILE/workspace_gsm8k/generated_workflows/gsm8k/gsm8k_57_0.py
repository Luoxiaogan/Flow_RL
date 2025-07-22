# Workflow ID: gsm8k_57_0
# Benchmark: gsm8k
# Data Indices: [100, 226]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect and Regenerate pattern to refine the best solution based on critical reflection
        3. Iterative Refinement using FlexibleCustom for deeper improvement
        """

        # Step 1: Generate multiple independent solutions via parallel ensemble
        solutions = []
        for i in range(3):  # Generate 3 different approaches
            instruction = f"Provide a step-by-step solution to this math problem, focusing on clarity and logical structure."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the best initial solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution — identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new Custom call for a refined solution
        improved_instruction = (
            "Given the following initial solution and reflection, "
            "reconstruct a more accurate and logically complete answer. "
            "Focus on addressing the issues raised in the reflection: "
            f"{reflection}"
        )
        refined_solution = await self.custom(instruction=improved_instruction)

        # Step 5: Optional iterative refinement using FlexibleCustom with iterative pattern
        # This adds depth by allowing structured re-evaluation of the refined solution
        flexible_iter = operator.FlexibleCustom(
            self.config,
            self.problem,
            reasoning_pattern="iterative",
            steps=["verify_assumptions", "check_calculations", "final_review"],
            max_iterations=2
        )
        final_solution = await flexible_iter(
            custom_instruction="Now, verify the logic and calculations thoroughly.",
            previous_results=[refined_solution]
        )

        return final_solution