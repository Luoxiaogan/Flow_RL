# Workflow ID: gsm8k_115_1
# Benchmark: gsm8k
# Data Indices: [384, 647, 135]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        A final Review step ensures clarity and correctness before returning.
        """
        # Step 1: Generate multiple independent solutions using varied reasoning approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (step-by-step logic)
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into clear steps: identify knowns, unknowns, operations needed, and compute systematically.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_solution"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start simple, improve)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate or rough calculation, then refine it through logical adjustments.",
                    reasoning_pattern="iterative",
                    steps=["initial_estimate", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Parallel exploration (multiple interpretations)
                solution = await self.flexible_custom(
                    custom_instruction="Consider alternative interpretations of the problem statement. Solve each path independently and compare results.",
                    reasoning_pattern="parallel",
                    steps=["interpret_alternatives", "solve_each", "compare_results"]
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer