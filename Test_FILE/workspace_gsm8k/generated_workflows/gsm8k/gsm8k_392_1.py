# Workflow ID: gsm8k_392_1
# Benchmark: gsm8k
# Data Indices: [500, 591]

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
        Diverse workflow using Parallel Ensemble with iterative refinement via FlexibleCustom.
        Step 1: Generate 3 solutions using different reasoning patterns (sequential, parallel, iterative).
        Step 2: Use ScEnsemble to pick the best one based on consistency and clarity.
        Step 3: Apply a final review to polish the selected solution.
        
        This logic differs from the existing one by:
        - Using FlexibleCustom with distinct reasoning patterns instead of just custom prompts
        - Employing a structured ensemble approach that leverages diverse internal strategies
        - Avoiding reflection-based regeneration in favor of pre-emptive diversity
        """
        # --- PARALLEL ENSEMBLE WITH DIVERSE REASONING STRATEGIES ---
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                sol = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "compute", "verify"],
                    custom_instruction="Solve this math problem by breaking it into clear, sequential steps."
                )
            elif i == 1:
                # Iterative reasoning: refine through multiple passes
                sol = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2,
                    custom_instruction="Start with an estimate, then improve your answer iteratively."
                )
            else:
                # Parallel reasoning: consider multiple interpretations simultaneously
                sol = await self.flexible_custom(
                    reasoning_pattern="parallel",
                    steps=["interpretation_a", "interpretation_b", "combine"],
                    custom_instruction="Explore multiple ways to interpret the problem and synthesize the best approach."
                )
            solutions.append(sol)

        # --- SCENSBLE (Fan-in): Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- FINAL REVIEW FOR POLISHING AND CLARITY ---
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution