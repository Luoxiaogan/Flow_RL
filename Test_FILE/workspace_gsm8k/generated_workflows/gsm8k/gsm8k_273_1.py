# Workflow ID: gsm8k_273_1
# Benchmark: gsm8k
# Data Indices: [127, 155, 715]

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
        This is a diverse and efficient workflow using a Parallel Ensemble + Reflective Regeneration strategy.
        It first generates multiple independent solutions (fan-out), selects the best one (fan-in via ScEnsemble),
        then critically reflects on that winner to uncover hidden assumptions or gaps, and finally regenerates
        a superior solution guided by that reflection — combining robustness with meta-cognitive refinement.
        """
        # Step 1: Generate 3 parallel solutions using different reasoning patterns
        parallel_solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction="Solve this problem using a structured approach. Focus on clarity and logical flow."
            )
            parallel_solutions.append(solution)

        # Step 2: Use ensemble to pick the best candidate from the parallel attempts
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Critically reflect on the best solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate a new, improved solution — not just a fix, but a rethinking
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        f"Re-evaluate the problem from scratch using insights from the reflection. Provide a clear, precise, and logically sound answer."
        )

        return final_solution