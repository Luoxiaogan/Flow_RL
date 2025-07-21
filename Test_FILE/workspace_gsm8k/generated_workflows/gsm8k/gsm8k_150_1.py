# Workflow ID: gsm8k_150_1
# Benchmark: gsm8k
# Data Indices: [404, 637]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions with different reasoning styles,
        then selects the most consistent one using ScEnsemble. A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions in parallel using varied approaches
        solutions = []
        for i in range(3):
            if i == 0:
                # First solution: Use flexible custom with sequential steps (structured logic)
                sol = await self.flexible_custom(
                    custom_instruction="Break down the problem into clear logical steps.",
                    reasoning_pattern="sequential",
                    steps=["identify", "model", "compute", "validate"]
                )
            elif i == 1:
                # Second solution: Use flexible custom with iterative refinement
                sol = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine your answer through iterations.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2
                )
            else:
                # Third solution: Use basic Custom with open-ended step-by-step reasoning
                sol = await self.custom(
                    instruction="Solve this math problem by thinking through it step-by-step."
                )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the selected solution for clarity and accuracy
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer