# Workflow ID: gsm8k_188_1
# Benchmark: gsm8k
# Data Indices: [130, 11, 167]

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
        Reflect and Regenerate Workflow: 
        1. Generate an initial solution using a structured approach.
        2. Critically reflect on its assumptions, logic gaps, or alternative interpretations.
        3. Use that reflection to guide a targeted, improved solution.
        This mimics human meta-cognition—learning from mistakes before finalizing.
        """
        # --- STEP 1: Generate initial solution with flexible custom (structured reasoning) ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # --- STEP 2: Reflect critically on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use reflection to generate a refined solution ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem carefully, addressing potential flaws or missed perspectives. "
                        f"Provide a clear, accurate, and well-justified final answer."
        )

        return final_answer