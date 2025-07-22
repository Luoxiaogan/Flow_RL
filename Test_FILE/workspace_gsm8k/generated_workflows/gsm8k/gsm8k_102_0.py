# Workflow ID: gsm8k_102_0
# Benchmark: gsm8k
# Data Indices: [67, 69]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions via different reasoning strategies,
        then selects the best one using ScEnsemble. A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential approach: break down step-by-step
                solution = await self.flexible_custom(
                    custom_instruction="Solve this math problem by following a clear, sequential reasoning path.",
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "calculate", "verify"]
                )
            elif i == 1:
                # Iterative approach: start with estimation, refine
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an approximate strategy, then refine your answer through iterations.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Parallel-inspired (but not full ensemble): use flexible custom with structured output
                solution = await self.flexible_custom(
                    custom_instruction="Use structured reasoning to explore multiple interpretations of the problem.",
                    reasoning_pattern="branching",
                    steps=["interpret", "evaluate", "conclude"],
                    use_structured_output=True
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer