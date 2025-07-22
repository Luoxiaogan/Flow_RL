# Workflow ID: gsm8k_340_0
# Benchmark: gsm8k
# Data Indices: [667, 802]

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
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a new, improved solution.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying known quantities and unknowns, then apply relevant mathematical operations step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior final solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Use this insight to produce a more accurate, well-structured, and logically sound answer."
        )

        return final_solution