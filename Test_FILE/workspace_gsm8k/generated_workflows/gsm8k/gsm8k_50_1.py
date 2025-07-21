# Workflow ID: gsm8k_50_1
# Benchmark: gsm8k
# Data Indices: [785, 438]

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
        This workflow uses the Iterative Refinement pattern with a loop-based approach.
        It generates an initial solution, then applies Review at least twice to progressively improve it.
        This is different from the existing workflow because it avoids reflection and instead relies on iterative feedback via Review.
        The structure is simple yet effective: initial solution → review × 2 → final answer.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using systematic reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Apply iterative refinement — review the solution twice to improve clarity, logic, and accuracy
        current_solution = initial_solution
        for i in range(2):  # Apply review exactly twice as required
            current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Return the refined solution after two rounds of improvement
        return current_solution