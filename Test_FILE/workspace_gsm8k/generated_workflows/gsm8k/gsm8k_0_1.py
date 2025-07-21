# Workflow ID: gsm8k_0_1
# Benchmark: gsm8k
# Data Indices: [476, 238, 594]

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
        Diverse workflow using the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning.
        Step 2: Critically reflect on the result to uncover assumptions or gaps.
        Step 3: Use that reflection to guide a new Custom call that explicitly addresses flaws.
        This approach emphasizes meta-cognition and stepwise improvement over raw ensembling.
        """
        # --- INITIAL SOLUTION WITH STRUCTURED REASONING ---
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["understand", "analyze", "solve", "verify"],
            custom_instruction="Break down the problem systematically. Focus on clarity and logical progression."
        )

        # --- REFLECT ON THE INITIAL SOLUTION ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- REGENERATE WITH REFLECTION GUIDANCE ---
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        "Now, solve the problem again with improved logic, addressing any identified weaknesses. "
                        "Ensure each step is justified and clearly explained."
        )

        return final_answer