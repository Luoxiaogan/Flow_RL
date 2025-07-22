# Workflow ID: gsm8k_172_1
# Benchmark: gsm8k
# Data Indices: [394, 896, 315]

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
        Diverse and robust workflow using Parallel Ensemble with a twist: 
        1. Generate 3 solutions via FlexibleCustom in 'parallel' mode (i.e., independent reasoning paths).
        2. Use ScEnsemble to select the most consistent solution.
        3. Apply a final Review for clarity and correctness — no reflection or regeneration.
        
        This approach differs from the existing one by:
        - Using FlexibleCustom's built-in parallel pattern instead of explicit loops
        - Avoiding reflection/regeneration entirely (no meta-cognitive loop)
        - Leveraging structured output from FlexibleCustom for better consistency
        - Maintaining simplicity while maximizing diversity through different reasoning strategies
        """

        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom in parallel mode ---
        # Each uses a different step configuration to encourage varied reasoning paths
        solution_pool = []
        for i in range(3):
            # Vary the steps to ensure different reasoning structures
            steps = ["analyze", "plan", "solve", "verify"]
            if i == 0:
                instruction = "Solve this problem by first identifying all known values and unknowns."
            elif i == 1:
                instruction = "Break down the problem into arithmetic operations step-by-step."
            else:
                instruction = "Use a visual or narrative explanation to solve the problem clearly."

            sol = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="parallel",
                steps=steps,
                use_structured_output=True
            )
            solution_pool.append(sol)

        # --- Step 2: Select best solution via ensemble ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 3: Final polish with Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer