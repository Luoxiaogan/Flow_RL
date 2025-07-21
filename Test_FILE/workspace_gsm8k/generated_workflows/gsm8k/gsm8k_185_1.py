# Workflow ID: gsm8k_185_1
# Benchmark: gsm8k
# Data Indices: [568, 234, 439]

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
        This workflow combines two powerful patterns:
        1. Parallel Ensemble: Generate multiple independent solutions to reduce error risk.
        2. Reflect-and-Regenerate: Critically reflect on the best solution and use that insight to refine it further.
        
        It avoids single-point failure by starting with diverse reasoning paths, then uses meta-cognition for final polish.
        """
        # Step 1: Generate 3 independent solutions using FlexibleCustom in parallel (via loop)
        solutions = []
        for i in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step with clear reasoning.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic based on reflection content — if reflection suggests a flaw, regenerate; otherwise return best
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "alternative" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the following reflection on the best solution: '{reflection}'. "
                            f"Generate a new, improved solution that addresses any identified issues."
            )
        else:
            final_solution = best_solution

        return final_solution