# Workflow ID: gsm8k_170_0
# Benchmark: gsm8k
# Data Indices: [978, 590]

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
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect + Regenerate pattern to improve the best solution
        3. Iterative Refinement using FlexibleCustom for structured improvement
        """

        # Step 1: Generate 3 different initial approaches in parallel
        solution_pool = []
        for i in range(3):
            instruction = f"Generate an initial solution using a unique approach: {['analyze cost structure', 'use profit formula directly', 'break into revenue vs. cost components'][i]}"
            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # Step 2: Select the best solution via ScEnsemble
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect on the best solution — identify weaknesses or assumptions
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use reflection to guide a new, improved solution with FlexibleCustom
        improved_instruction = (
            f"Based on the following reflection: '{reflection}'. "
            "Now, re-solve the problem using a systematic, step-by-step approach that addresses these points."
        )
        final_solution = await self.flexible_custom(
            custom_instruction=improved_instruction,
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_profit_formula", "compute_car_profit", "compute_motorcycle_profit", "compare_profits"]
        )

        return final_solution