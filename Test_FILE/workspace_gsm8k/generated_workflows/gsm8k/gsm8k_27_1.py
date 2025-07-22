# Workflow ID: gsm8k_27_1
# Benchmark: gsm8k
# Data Indices: [681, 553, 88]

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
        Reflect and Regenerate Workflow: 
        This pattern uses meta-cognition — first generate a solution, then critically reflect on it to uncover flaws or improvements, 
        and finally regenerate a superior answer guided by that reflection. 
        This is fundamentally different from iterative refinement because it explicitly leverages self-aware critique before re-solving.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with greater accuracy, addressing the issues raised in the reflection."
        )

        return final_solution