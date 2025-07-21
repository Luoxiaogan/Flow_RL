# Workflow ID: gsm8k_96_1
# Benchmark: gsm8k
# Data Indices: [987, 237, 607]

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
        This workflow combines:
        1. Iterative Refinement (initial solution + review cycles)
        2. Reflect-and-Regenerate (critical reflection to guide improvement)
        3. FlexibleCustom with a branching reasoning pattern for structured exploration
        
        It starts by generating an initial solution using a sequential breakdown.
        Then it iteratively refines the solution through two rounds of Review.
        After that, it reflects on the final refined solution to uncover potential blind spots,
        and finally regenerates a new answer guided by that reflection — ensuring meta-cognitive depth.
        """

        # --- Step 1: Initial Solution via Sequential Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step with clear explanations.",
            reasoning_pattern="sequential",
            steps=["understand", "decompose", "compute", "verify"]
        )

        # --- Step 2: Iterative Refinement (2 rounds) ---
        current_solution = initial_solution
        for _ in range(2):
            current_solution = await self.review(pre_solution=current_solution)

        # --- Step 3: Reflect on the improved solution ---
        reflection = await self.reflect(pre_solution=current_solution)

        # --- Step 4: Regenerate based on reflection (Reflect-and-Regenerate Pattern) ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem now, incorporating these insights to avoid any overlooked assumptions or errors."
        )

        return final_answer