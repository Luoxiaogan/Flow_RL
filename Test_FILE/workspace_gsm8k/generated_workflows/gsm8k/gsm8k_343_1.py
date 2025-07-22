# Workflow ID: gsm8k_343_1
# Benchmark: gsm8k
# Data Indices: [451, 600]

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
        This is a diverse and robust workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to uncover potential flaws or missed steps,
        and finally uses that reflection to guide a targeted re-generation of a superior solution.
        This meta-cognitive loop ensures deeper reasoning than a single pass.
        """

        # Step 1: Generate an initial solution using a general-purpose custom prompt
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each logical transition clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a focused, improved instruction for a new solution
        refined_instruction = f"Given the following reflection on the initial attempt: '{reflection}'. " \
                              "Now, generate a revised solution that addresses these points explicitly. " \
                              "Ensure all steps are logically sound, well-justified, and free from ambiguity."

        # Step 4: Generate the final, improved solution based on the reflection
        final_answer = await self.custom(instruction=refined_instruction)

        return final_answer