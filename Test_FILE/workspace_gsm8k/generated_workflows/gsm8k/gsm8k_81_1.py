# Workflow ID: gsm8k_81_1
# Benchmark: gsm8k
# Data Indices: [762, 59, 735]

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
        This is a diverse and complex workflow combining:
        - Parallel Ensemble with three distinct reasoning strategies (each using FlexibleCustom with different patterns)
        - Selective refinement based on reflection only if the ensemble result is uncertain
        - Final review for polish

        Key differences from existing:
        1. Uses FlexibleCustom in parallel with *different reasoning patterns* per branch — not just multiple Custom calls.
        2. No Reflect + Regenerate loop — instead, uses reflection as an optional trigger for refinement after ensemble.
        3. Ensembles early to reduce noise before any deep critique.
        """

        # Step 1: Generate 3 solutions using different reasoning patterns via FlexibleCustom
        solution_list = []
        strategies = [
            ("sequential", ["analyze", "plan", "solve", "verify"]),
            ("iterative", ["initial_guess", "refine", "finalize"], {"max_iterations": 2}),
            ("branching", ["identify_knowns", "consider_alternatives", "choose_best_path"])
        ]

        for i, (pattern, steps, kwargs) in enumerate(strategies):
            custom_instruction = f"Use {pattern} reasoning: {', '.join(steps)}. Be thorough."
            flex_op = operator.FlexibleCustom(
                self.config, self.problem,
                reasoning_pattern=pattern,
                steps=steps,
                **kwargs
            )
            sol = await flex_op(custom_instruction=custom_instruction)
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to pick the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Optional — reflect on the best solution to check for hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Only if reflection indicates potential issues, regenerate; otherwise, proceed directly
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "uncertain" in reflection.lower():
            improved_solution = await self.custom(
                instruction=f"Based on this reflection: '{reflection}'. "
                            f"Re-solve the problem with corrected reasoning. Avoid previous pitfalls."
            )
            final_solution = await self.review(pre_solution=improved_solution)
        else:
            final_solution = await self.review(pre_solution=best_solution)

        return final_solution