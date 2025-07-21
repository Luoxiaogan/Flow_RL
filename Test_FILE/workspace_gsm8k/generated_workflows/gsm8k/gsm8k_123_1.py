# Workflow ID: gsm8k_123_1
# Benchmark: gsm8k
# Data Indices: [245, 262, 352]

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
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. A final review ensures clarity
        and correctness — enhancing robustness against individual reasoning errors.
        """
        # Step 1: Generate multiple solutions using varied approaches
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step breakdown with explicit arithmetic
                solution = await self.flexible_custom(
                    custom_instruction="Break down the problem into clear steps and solve each part systematically.",
                    reasoning_pattern="sequential",
                    steps=["identify", "compute", "combine", "validate"]
                )
            elif i == 1:
                # Strategy 2: Estimate first, then refine (iterative thinking)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate or intuitive guess, then refine your answer through logical checks.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "check", "adjust"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Multiple perspectives — think like a student, teacher, and expert
                solution = await self.custom(
                    instruction="Solve the problem from three perspectives: as a beginner (explain clearly), as a teacher (highlight key concepts), and as an expert (optimize logic). Then synthesize."
                )
            solutions.append(solution)

        # Step 2: Use ensemble to pick the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish — improve clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer