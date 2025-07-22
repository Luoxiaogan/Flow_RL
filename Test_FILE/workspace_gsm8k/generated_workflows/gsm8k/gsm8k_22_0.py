# Workflow ID: gsm8k_22_0
# Benchmark: gsm8k
# Data Indices: [495, 807]

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
        Diverse workflow using the 'Reflect and Regenerate' pattern with iterative refinement.
        This structure encourages deep meta-cognition by analyzing the solution's weaknesses before improving it.
        """
        # Step 1: Generate an initial solution using a flexible custom operator in sequential mode
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear steps, then solve each part logically."
        )

        # Step 2: Critically reflect on the initial solution to uncover potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via a custom instruction
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Reconstruct your answer focusing on addressing the identified weaknesses. "
                        f"Ensure all steps are justified and assumptions are explicit."
        )

        return final_answer