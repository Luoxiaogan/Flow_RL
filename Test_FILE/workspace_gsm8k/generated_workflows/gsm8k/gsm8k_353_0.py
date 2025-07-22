# Workflow ID: gsm8k_353_0
# Benchmark: gsm8k
# Data Indices: [420, 518, 917]

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
        It generates an initial solution, critically reflects on it, and then uses that reflection
        to produce a refined final answer — mimicking human metacognition for improved accuracy.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key quantities and relationships in the problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via Custom
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nRevise your approach to ensure clarity, correctness, and completeness. Provide a step-by-step solution."
        )

        return final_solution