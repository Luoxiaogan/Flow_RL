# Workflow ID: gsm8k_209_1
# Benchmark: gsm8k
# Data Indices: [421, 358]

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
        This workflow uses a parallel ensemble strategy with iterative refinement — 
        a fundamentally different logic from the existing single-reflection approach.
        It generates multiple independent solutions, then refines the best one.
        """
        # Step 1: Generate 3 diverse initial solutions using FlexibleCustom in parallel mode
        solution_list = []
        for _ in range(3):
            sol = await self.flexible_custom(
                reasoning_pattern="parallel",
                steps=["analyze", "formulate", "solve"],
                custom_instruction="Solve the problem by exploring different approaches independently."
            )
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to select the most accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Review the best solution once to polish it further — no reflection needed here
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution