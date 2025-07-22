# Workflow ID: gsm8k_89_1
# Benchmark: gsm8k
# Data Indices: [713, 29, 66]

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
        It generates multiple independent solutions in parallel (via loop), then selects the best one — 
        enhancing robustness by avoiding single-point reasoning failures. This approach is efficient 
        because it leverages diversity without requiring complex reflection or iterative refinement.
        """
        # Step 1: Generate 3 independent solutions using flexible custom with different reasoning patterns
        solution_list = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by focusing on clear, logical steps.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution