# Workflow ID: gsm8k_198_0
# Benchmark: gsm8k
# Data Indices: [91, 833, 260]

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
        This is a diverse and reflective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a superior final answer.
        """
        # Step 1: Generate an initial solution using flexible custom with a structured sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying known quantities and unknowns, then apply relevant formulas or logic step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_logic", "compute"]
        )

        # Step 2: Critically reflect on the initial solution — uncover assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution generation
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{initial_solution}\n\nAnd this reflection on its limitations:\n{reflection}\n\nProvide a revised and more accurate solution."
        )

        return final_answer