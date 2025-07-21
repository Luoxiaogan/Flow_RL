# Workflow ID: gsm8k_64_1
# Benchmark: gsm8k
# Data Indices: [562, 449, 848]

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
        This is a diverse and robust workflow using:
        1. Parallel Ensemble (Fan-out/Fan-in) with varied reasoning prompts
        2. Reflect and Regenerate pattern to challenge assumptions
        3. FlexibleCustom in 'branching' mode for conditional refinement
        """

        # Step 1: Generate 3 distinct solutions using different reasoning styles
        solution_pool = []
        prompts = [
            "Solve step-by-step by first identifying what's given and what must be found.",
            "Approach this as if you're teaching someone who knows nothing — explain each part clearly.",
            "Break the problem into sub-problems, solve each independently, then combine."
        ]
        
        for prompt in prompts:
            sol = await self.custom(instruction=prompt)
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or edge cases
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use FlexibleCustom with branching logic to explore alternative interpretations
        # This allows conditional paths based on reflection insights — e.g., "if assumption X is flawed, try Y"
        improved_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, re-evaluate key assumptions and explore alternate reasoning paths: " + reflection,
            reasoning_pattern="branching",
            steps=["reassess_assumptions", "explore_alternatives", "select_best_path"],
            use_structured_output=True
        )

        # Step 5: Final polish via review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer