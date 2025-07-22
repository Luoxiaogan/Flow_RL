# Workflow ID: gsm8k_0_1
# Benchmark: gsm8k
# Data Indices: [232, 432]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out): Generate multiple independent solutions.
        2. Reflect-and-Regenerate: Critically reflect on the best solution and regenerate it for improved quality.

        Unlike the existing workflow, this one first explores multiple reasoning paths in parallel before refining the winner — introducing both diversity in initial approaches and meta-cognitive refinement.
        """

        # Step 1: Generate 3 different solutions using flexible custom with varying reasoning strategies
        # Each uses a different "reasoning_pattern" to encourage diverse thinking
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            sol = await self.flexible_custom(
                custom_instruction="Solve the problem carefully, focusing on clear logic and step-by-step justification.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most accurate solution from the parallel set
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution — identify assumptions, potential gaps, or unclear parts
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final refined version of the solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution:\n{reflection}\n\n"
                        f"Reconstruct the answer with greater precision, clarity, and logical rigor. "
                        f"Ensure every step is justified and all assumptions are explicitly stated."
        )

        return final_solution