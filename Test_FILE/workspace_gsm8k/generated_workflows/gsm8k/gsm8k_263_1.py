# Workflow ID: gsm8k_263_1
# Benchmark: gsm8k
# Data Indices: [250, 398]

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
        Diverse and effective workflow combining Iterative Refinement + Branching Logic.
        
        1. Generate an initial solution using FlexibleCustom in sequential mode (structured thinking).
        2. Use Review to improve it iteratively up to 3 times — mimicking human refinement.
        3. After each review, use Reflect to analyze the current state — this creates a feedback loop.
        4. Based on reflection content, branch logic: if reflection suggests ambiguity, switch to parallel exploration; otherwise, continue refining.
        5. If branching occurs, generate 2 new solutions via Custom with different strategies, then select best via ScEnsemble.
        6. Final output is either the refined solution or the ensemble result — whichever is more confident.

        This design introduces conditional branching based on meta-cognitive insight (Reflect), making it fundamentally different from static ensembling or fixed iteration.
        """
        # --- Step 1: Initial structured approach ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using a clear reasoning structure.",
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "compute", "verify"]
        )

        # --- Step 2: Iterative refinement with reflection-driven branching ---
        current_solution = initial_solution
        for iteration in range(3):  # Max 3 refinements
            reflection = await self.reflect(pre_solution=current_solution)

            # Check if reflection indicates uncertainty or incompleteness
            if "uncertain" in reflection.lower() or "ambiguous" in reflection.lower() or "missing" in reflection.lower():
                # Branch: Switch to parallel exploration for robustness
                alternative_solutions = []
                for _ in range(2):
                    sol = await self.custom(
                        instruction="Solve this problem using a completely different method than before."
                    )
                    alternative_solutions.append(sol)

                # Select best among alternatives
                final_solution = await self.sc_ensemble(solutions=alternative_solutions)
                return final_solution

            # Otherwise, keep refining
            current_solution = await self.review(pre_solution=current_solution)

        # If no branching occurred, return the final refined solution
        return current_solution