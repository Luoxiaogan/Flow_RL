# Workflow ID: gsm8k_278_1
# Benchmark: gsm8k
# Data Indices: [970, 426, 273]

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
        Diverse and efficient workflow using the 'Reflect and Regenerate' pattern with parallel exploration.
        This approach first generates an initial solution, then uses reflection to critique it.
        Instead of iterative refinement, it creates multiple alternative solutions based on that reflection,
        then selects the best one via ensemble — a fundamentally different logic from the existing workflow.
        """
        # Step 1: Generate initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution to uncover flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide generation of multiple distinct solution paths
        # This is the key difference: instead of refining one path, we explore several alternatives
        solutions = []
        for i in range(3):  # Generate 3 different approaches informed by reflection
            prompt = (
                f"Given this reflection on the original solution: '{reflection}'. "
                "Now generate a new solution using a different strategy. "
                "Focus on addressing potential weaknesses identified in the reflection."
            )
            new_solution = await self.custom(instruction=prompt)
            solutions.append(new_solution)

        # Step 4: Use ScEnsemble to select the most accurate among these diverse solutions
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer