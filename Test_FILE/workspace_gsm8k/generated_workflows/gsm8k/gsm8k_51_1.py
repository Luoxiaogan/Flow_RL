# Workflow ID: gsm8k_51_1
# Benchmark: gsm8k
# Data Indices: [325, 528]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to uncover hidden assumptions or errors,
        and finally uses that reflection to guide a targeted regeneration of the solution — ensuring meta-cognitive depth
        without unnecessary iterations or parallelism.
        """
        # Step 1: Generate an initial solution using a flexible custom operator in iterative mode
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_attempt", "review", "refine"],
            max_iterations=2,
            custom_instruction="Start with a direct approach, then refine based on feedback."
        )

        # Step 2: Critically reflect on the initial solution — identify flaws, assumptions, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, improved solution by explicitly addressing the critique
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution:\n{reflection}\n\n"
                        f"Re-solve the problem with a focus on correcting the identified issues. Be precise and structured."
        )

        return final_solution