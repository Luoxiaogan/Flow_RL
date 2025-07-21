# Workflow ID: gsm8k_11_1
# Benchmark: gsm8k
# Data Indices: [693, 8, 48]

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
        Diverse workflow using Parallel Ensemble + Iterative Refinement.
        This approach first explores multiple reasoning paths in parallel (fan-out), 
        then applies iterative refinement to the best candidate to improve accuracy.
        Unlike the existing solution, this uses a structured iterative loop instead of conditional regeneration.
        """

        # Step 1: Generate 3 diverse initial solutions using different reasoning styles
        solution_pool = []
        instructions = [
            "Solve step-by-step by identifying variables and relationships.",
            "Break the problem into smaller sub-problems and solve each independently.",
            "Use a formulaic or algebraic approach—define unknowns explicitly."
        ]
        
        for instr in instructions:
            sol = await self.custom(instruction=instr)
            solution_pool.append(sol)

        # Step 2: Select the most consistent solution via ScEnsemble
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Apply iterative refinement — review and improve up to 2 times
        current_solution = best_initial
        for iteration in range(2):  # Max 2 refinement passes
            revised = await self.review(pre_solution=current_solution)
            # Check if the revision made meaningful changes (heuristic: compare length or detect placeholder text)
            if len(revised) <= len(current_solution) and "step" not in revised.lower() and "solution" not in revised.lower():
                break  # No improvement detected, stop refining
            current_solution = revised

        # Final step: One last review to polish the result
        final_solution = await self.review(pre_solution=current_solution)

        return final_solution