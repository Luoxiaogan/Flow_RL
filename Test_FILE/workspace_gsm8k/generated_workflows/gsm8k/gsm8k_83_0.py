# Workflow ID: gsm8k_83_0
# Benchmark: gsm8k
# Data Indices: [885, 311, 968]

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
        It generates three independent solutions with different reasoning strategies,
        then selects the best one via ensemble. A final review ensures clarity and correctness.
        """

        # --- Step 1: Generate multiple solutions using varied approaches ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential approach: break down into steps
                solution = await self.flexible_custom(
                    custom_instruction="Solve step-by-step with clear reasoning",
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "compute", "verify"]
                )
            elif i == 1:
                # Iterative approach: refine progressively
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine twice",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Flexible Custom with structured output for consistency
                solution = await self.flexible_custom(
                    custom_instruction="Use structured reasoning: state assumptions, calculate, check",
                    reasoning_pattern="sequential",
                    use_structured_output=True
                )
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for clarity and error detection ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer