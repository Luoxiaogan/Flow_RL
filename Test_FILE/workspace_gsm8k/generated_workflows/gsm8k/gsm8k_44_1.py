# Workflow ID: gsm8k_44_1
# Benchmark: gsm8k
# Data Indices: [914, 391, 406]

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
        This workflow combines two distinct patterns:
        1. Parallel Ensemble (Fan-out): Generate 3 independent solutions using FlexibleCustom with different reasoning strategies.
        2. Reflect-and-Regenerate: Use reflection on the best solution to guide a targeted improvement.

        Why it's diverse:
        - Uses parallel exploration (3 different approaches) instead of sequential refinement.
        - Leverages `Reflect` not just for critique but as a catalyst for a new, focused solution.
        - Avoids redundant steps by using structured ensemble selection before finalizing.
        """

        # Step 1: Generate 3 diverse initial solutions using flexible custom in "parallel" mode
        # Each uses a different reasoning strategy to explore various angles
        solutions = []
        for i in range(3):
            pattern = "sequential" if i == 0 else ("iterative" if i == 1 else "branching")
            instruction = (
                "Break down the problem step-by-step and verify your logic."
                if i == 0
                else "Start with an estimate, then refine your answer through multiple passes."
                if i == 1
                else "Consider alternative interpretations of the problem statement and resolve ambiguities first."
            )
            sol = await self.flexible_custom(
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1,
                custom_instruction=instruction
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final solution based on the reflection — this ensures meta-cognitive depth
        final_solution = await self.custom(
            instruction=f"Based on the following reflection on the selected solution: '{reflection}'. "
                        f"Reconstruct the answer with improved clarity, addressing any identified gaps or assumptions."
        )

        return final_solution