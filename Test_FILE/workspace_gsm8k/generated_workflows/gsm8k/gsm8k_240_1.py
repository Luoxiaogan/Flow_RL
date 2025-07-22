# Workflow ID: gsm8k_240_1
# Benchmark: gsm8k
# Data Indices: [625, 10, 847]

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
        Diverse and robust workflow using Parallel Ensemble + Iterative Refinement.
        This approach first explores multiple solution paths in parallel (fan-out),
        then selects the best one via ensemble — but crucially, it applies iterative refinement
        to that top candidate until it converges on a high-confidence answer.
        Unlike the existing workflow, this uses a loop-based refinement strategy
        rather than conditional regeneration based on reflection — making it more systematic
        and less reliant on interpretive judgment of reflection text.
        """

        # Step 1: Generate three diverse initial solutions using different reasoning styles
        solutions = []
        for i in range(3):
            instructions = [
                "Solve by identifying all quantities step-by-step, then compute sequentially.",
                "Use a visual model or diagram to represent relationships before calculating.",
                "Break the problem into smaller sub-problems, solve each independently, then combine."
            ]
            sol = await self.custom(instruction=instructions[i])
            solutions.append(sol)

        # Step 2: Select the most consistent solution via ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Apply iterative refinement — review and improve the selected solution multiple times
        current_solution = best_solution
        for iteration in range(2):  # Two rounds of refinement
            revised = await self.review(pre_solution=current_solution)
            # If no improvement is detected, stop early (heuristic to avoid infinite loops)
            if revised == current_solution:
                break
            current_solution = revised

        return current_solution