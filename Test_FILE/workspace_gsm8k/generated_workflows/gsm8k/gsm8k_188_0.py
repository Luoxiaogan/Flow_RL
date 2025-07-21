# Workflow ID: gsm8k_188_0
# Benchmark: gsm8k
# Data Indices: [130, 11, 167]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 different solutions via varied approaches, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 distinct solutions ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step breakdown with explicit arithmetic
                instruction = "Solve the problem by breaking it into clear steps: identify total seats, compute allowed occupancy, then find unoccupied seats. Show all calculations."
            elif i == 1:
                # Strategy 2: Algebraic modeling (e.g., equations or formulas)
                instruction = "Model the problem using mathematical expressions. Define variables, write equations, solve them, and interpret the result clearly."
            else:
                # Strategy 3: Unit-based reasoning (think in terms of units like rows, seats per row, etc.)
                instruction = "Approach this as a unit conversion or scaling problem: start from one row, scale up to the whole plane, and compute unused seats."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- SCENSEMBLE: Select the most consistent solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- FINAL REVIEW: Improve clarity and catch any subtle errors ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer