# Workflow ID: gsm8k_117_1
# Benchmark: gsm8k
# Data Indices: [145, 478, 579]

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
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on its weaknesses, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop leverages insight from critique to produce higher-quality outputs without redundant refinement passes.
        Uses only one iteration of reflection — efficient and focused.
        """
        # Step 1: Generate an initial solution using structured reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear explanations."
        )

        # Step 2: Critically reflect on the solution — identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, targeted Custom call for a better solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Use this insight to generate a more accurate and complete solution."
        )

        return final_solution