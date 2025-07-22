# Workflow ID: gsm8k_347_1
# Benchmark: gsm8k
# Data Indices: [301, 487, 159]

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
        This is a diverse and efficient workflow using the Parallel Ensemble pattern.
        It generates multiple independent solutions to reduce reliance on any single reasoning path,
        then selects the best one — a fundamentally different approach from the existing Reflect-and-Regenerate logic.
        """
        # Step 1: Generate 3 independent solutions using different prompts (parallel ensemble)
        solution1 = await self.custom(instruction="Solve the problem step-by-step, starting with identifying all given percentages or quantities.")
        solution2 = await self.custom(instruction="Break down the problem into parts: what is known, what needs to be found, and how they relate. Solve logically.")
        solution3 = await self.custom(instruction="Assume the problem involves percentages of a total. Calculate each segment first, then find the remaining part.")

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution