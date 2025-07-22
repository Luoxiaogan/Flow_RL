# Workflow ID: gsm8k_257_0
# Benchmark: gsm8k
# Data Indices: [0, 593, 989]

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
        This is a diverse and effective workflow using the Iterative Refinement pattern.
        It starts with a simple solution, then refines it twice using Review to progressively improve accuracy and clarity.
        """
        # Step 1: Generate an initial solution using a basic instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: First refinement — review the initial solution for clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve the already-refined solution
        second_refined = await self.review(pre_solution=first_refined)

        # Optional: Use Reflect to analyze the final solution's potential weaknesses
        reflection = await self.reflect(pre_solution=second_refined)

        # Step 4: Final output — return the most refined version
        return second_refined