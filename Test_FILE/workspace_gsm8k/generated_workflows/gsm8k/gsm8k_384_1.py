# Workflow ID: gsm8k_384_1
# Benchmark: gsm8k
# Data Indices: [972, 922]

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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on it to uncover potential flaws or missed steps, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop mimics how humans refine their thinking — not just by fixing errors, but by understanding why a solution might be incomplete.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"],
            custom_instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a better solution in a single, targeted pass
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Use this insight to generate a more accurate and complete solution."
        )

        return final_solution