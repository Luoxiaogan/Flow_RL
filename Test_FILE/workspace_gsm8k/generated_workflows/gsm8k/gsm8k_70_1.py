# Workflow ID: gsm8k_70_1
# Benchmark: gsm8k
# Data Indices: [220, 191, 608]

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
        It first generates an initial solution, then critically reflects on it to uncover potential flaws or improvements,
        and finally uses that reflection to guide a targeted re-solution — mimicking human metacognition.
        This approach prioritizes depth over breadth, focusing on iterative insight rather than parallel exploration.
        """

        # --- Step 1: Generate an initial solution using a structured, sequential approach ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning. Do not skip any logical steps.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "identify_variables", "formulate_plan", "execute_calculation", "verify"]
        )

        # --- Step 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to generate a refined, improved final answer ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution:\n\n{reflection}\n\nUse this insight to produce a more accurate and well-reasoned final answer."
        )

        return final_answer