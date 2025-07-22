# Workflow ID: gsm8k_239_1
# Benchmark: gsm8k
# Data Indices: [826, 852]

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
        This workflow uses a Parallel Ensemble strategy with iterative refinement.
        It generates multiple initial solutions in parallel, then refines the best one using Review.
        This is fundamentally different from the existing 'Reflect and Regenerate' logic — 
        it explores diverse reasoning paths first, then improves the top candidate.
        """
        # Step 1: Generate 3 independent solutions using flexible custom with different reasoning steps
        solution1 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["analyze", "apply_formula", "verify"],
            custom_instruction="Approach this as a multi-step arithmetic problem."
        )
        
        solution2 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["identify_knowns", "set_up_equation", "solve"],
            custom_instruction="Break down the problem into known quantities and unknowns."
        )
        
        solution3 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["visualize", "step-by-step_calculation", "check_units"],
            custom_instruction="Use step-by-step calculation focusing on unit consistency."
        )

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Refine the best solution using Review to catch subtle errors or improve clarity
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution