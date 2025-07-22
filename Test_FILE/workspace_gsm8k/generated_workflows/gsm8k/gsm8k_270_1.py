# Workflow ID: gsm8k_270_1
# Benchmark: gsm8k
# Data Indices: [717, 658, 999]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its weaknesses, then use that reflection to guide a new, targeted solution.
        This is a meta-cognitive loop that avoids repeated refinement and instead focuses on learning from mistakes before trying again.
        It's efficient because it uses one reflection to inform one new attempt — no redundant iterations.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part clearly. Be thorough but concise."
        )

        # Step 2: Critically reflect on the solution — identify flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. Now, solve the problem again with this insight in mind. Focus on addressing the identified issues directly."
        )

        return final_solution