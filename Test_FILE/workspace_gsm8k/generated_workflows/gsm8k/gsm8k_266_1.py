# Workflow ID: gsm8k_266_1
# Benchmark: gsm8k
# Data Indices: [166, 873]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent one. Finally, it applies
        a review step to polish the final answer — ensuring both diversity and quality.
        """
        # Step 1: Generate multiple candidate solutions in parallel using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step decomposition (sequential reasoning)
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"],
                    custom_instruction="Break down the problem systematically."
                )
            elif i == 1:
                # Strategy 2: Estimation-first approach (iterative refinement mindset)
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2,
                    custom_instruction="Start with an estimate, then refine based on logical checks."
                )
            else:
                # Strategy 3: Multi-angle analysis (parallel thinking)
                solution = await self.flexible_custom(
                    reasoning_pattern="parallel",
                    steps=["analyze_option_a", "analyze_option_b", "compare_options"],
                    custom_instruction="Consider multiple interpretations or paths to solve the problem."
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best-performing solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to ensure clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer