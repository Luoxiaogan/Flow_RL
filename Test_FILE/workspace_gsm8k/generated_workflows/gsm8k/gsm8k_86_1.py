# Workflow ID: gsm8k_86_1
# Benchmark: gsm8k
# Data Indices: [790, 57]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        This approach first explores multiple reasoning paths (parallel), selects the best one,
        then critically reflects on it to guide a final, refined solution—leveraging both robustness and meta-cognition.
        Total steps: 6 operators, with loop for parallelism and conditional reflection logic.
        """

        # Step 1: Generate 3 independent solutions using flexible custom with different reasoning patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            sol = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate of the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution to uncover potential blind spots or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic based on reflection content
        # If reflection indicates uncertainty or ambiguity, regenerate; otherwise, return best_solution
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "ambiguous" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. "
                            f"Re-solve the problem with improved clarity and deeper analysis."
            )
        else:
            final_solution = best_solution

        return final_solution