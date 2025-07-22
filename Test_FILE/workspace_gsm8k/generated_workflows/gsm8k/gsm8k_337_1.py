# Workflow ID: gsm8k_337_1
# Benchmark: gsm8k
# Data Indices: [469, 17]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and robust parallel ensemble-based workflow.
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it applies a
        single review to polish the chosen solution — ensuring both diversity of thought
        and final quality.
        
        Key differences from existing logic:
        - Uses Parallel Ensemble (fan-out/fan-in) instead of iterative refinement
        - Generates 3 distinct solutions with varied prompts (not just one with multiple reviews)
        - Employs flexible custom operators with different reasoning patterns for each attempt
        - Includes final review for quality assurance after selection
        """
        # Step 1: Generate three diverse solutions using different strategies
        solutions = []
        strategies = [
            ("sequential", ["understand_problem", "identify_knowns", "formulate_plan", "execute_calculation"]),
            ("iterative", ["initial_approach", "refine", "finalize"], 2),
            ("branching", ["analyze", "consider_alternatives", "choose_best"])
        ]
        
        for i, (pattern, steps, *kwargs) in enumerate(strategies):
            max_iter = kwargs[0] if kwargs else 1
            instruction = f"Apply a {pattern} approach to solve this math problem. Break it down logically."
            
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern=pattern,
                steps=steps,
                max_iterations=max_iter
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish — apply one round of review to improve clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer