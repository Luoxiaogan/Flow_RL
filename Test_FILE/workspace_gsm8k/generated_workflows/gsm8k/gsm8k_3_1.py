# Workflow ID: gsm8k_3_1
# Benchmark: gsm8k
# Data Indices: [506, 353, 139]

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
        Parallel Ensemble + Final Review Workflow:
        - Generate 3 diverse solutions using different reasoning strategies via FlexibleCustom.
        - Use ScEnsemble to select the most consistent and accurate solution.
        - Apply a final review to polish the chosen solution for clarity and correctness.
        
        This approach improves robustness by exploring multiple reasoning paths (parallel) 
        and selecting the best one based on internal consistency — mimicking how experts cross-validate ideas.
        """
        # Step 1: Generate 3 independent solutions using varied strategies
        solutions = []
        strategies = [
            ("Sequential", ["analyze", "plan", "solve", "verify"]),
            ("Iterative", ["initial_approach", "refine", "finalize"], {"max_iterations": 2}),
            ("Branching", ["identify_knowns", "consider_alternatives", "choose_best_path", "compute"])
        ]
        
        for i, (pattern, steps, *kwargs) in enumerate(strategies):
            custom_kwargs = {"reasoning_pattern": pattern, "steps": steps}
            if kwargs:
                custom_kwargs.update(kwargs[0])
            
            solution = await self.flexible_custom(
                custom_instruction=f"Use a {pattern} reasoning strategy to solve this problem. Focus on clear logic and step-by-step justification.",
                **custom_kwargs
            )
            solutions.append(solution)

        # Step 2: Enforce consistency across solutions using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement via Review to ensure clarity and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer