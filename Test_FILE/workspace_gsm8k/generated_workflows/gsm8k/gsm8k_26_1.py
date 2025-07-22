# Workflow ID: gsm8k_26_1
# Benchmark: gsm8k
# Data Indices: [565, 598]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern with iterative refinement.
        It generates three distinct solutions using different reasoning strategies (sequential, parallel, iterative),
        then selects the best one via ScEnsemble. Finally, it applies a single Review to polish the chosen solution — 
        ensuring both diversity in initial approaches and quality in final output.
        
        Key differences from existing workflow:
        - Uses FlexibleCustom with different reasoning patterns instead of identical Custom calls
        - Applies review only once at the end (not after reflection-based regeneration)
        - No reflection-guided regeneration — instead, relies on ensemble selection + post-processing
        - Control flow: generate 3 diverse solutions → select best → refine once
        """
        # Step 1: Generate three varied solutions using FlexibleCustom with different patterns
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify_knowns", "apply_formula", "verify"],
            custom_instruction="Solve step-by-step using clear logical progression."
        )

        solution2 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["analyze_options", "compare_strategies", "choose_best"],
            custom_instruction="Consider multiple possible interpretations or methods for solving this problem."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine_estimate", "finalize"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then improve through iterative reasoning."
        )

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish — use Review to improve clarity, structure, and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer