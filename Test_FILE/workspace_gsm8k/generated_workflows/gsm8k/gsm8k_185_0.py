# Workflow ID: gsm8k_185_0
# Benchmark: gsm8k
# Data Indices: [21, 493]

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
        This is a diverse and efficient workflow using iterative refinement with flexible custom reasoning.
        It leverages the 'iterative' pattern in FlexibleCustom to build a solution step-by-step,
        then applies a single review for final polish — balancing simplicity and effectiveness.
        """
        # Step 1: Use FlexibleCustom in iterative mode to build a structured, step-by-step solution
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["identify_knowns", "define_unknowns", "apply_formulas", "compute_total"],
            max_iterations=2,
            custom_instruction="Solve this math word problem by breaking it into clear logical steps."
        )

        # Step 2: Review the solution once to catch any missing details or errors
        final_solution = await self.review(pre_solution=initial_solution)

        return final_solution