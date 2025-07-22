# Workflow ID: gsm8k_318_1
# Benchmark: gsm8k
# Data Indices: [116, 372, 288]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify weaknesses,
        and finally uses that reflection to guide a new, improved solution — mimicking human meta-cognition.
        This logic is fundamentally different from the existing parallel-ensemble approach:
        - No ensembling of multiple solutions
        - No parallel generation
        - Instead, a single reflective loop that iterates once but with deep introspection
        - Uses the new 'Reflect' operator in a critical way: not just critique, but insight for regeneration
        """

        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations and assumptions clearly."
        )

        # Step 2: Critically reflect on the solution — this is the key innovation
        # The reflection identifies potential flaws, missing steps, or unclear logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a targeted, improved solution
        # This is where the "regenerate" part comes in — we now write a custom instruction based on the reflection
        final_instruction = (
            f"Given the following initial solution: {initial_solution}\n\n"
            f"And the following reflection on its limitations: {reflection}\n\n"
            "Now, provide a revised solution that addresses these points. Be precise, clear, and ensure no assumptions are left unexplained."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer