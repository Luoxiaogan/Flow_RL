# Workflow ID: gsm8k_57_0
# Benchmark: gsm8k
# Data Indices: [894, 44, 502]

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
        Robust parallel ensemble workflow with iterative refinement.
        Generates 3 diverse solutions using different reasoning patterns,
        then selects the best one via ScEnsemble. Final review ensures clarity.
        """
        # Generate 3 different solutions using varied reasoning strategies
        solutions = []
        
        # Solution 1: Sequential reasoning (step-by-step breakdown)
        solution1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "apply_formula", "compute"]
        )
        solutions.append(solution1)

        # Solution 2: Iterative refinement (start simple, improve)
        solution2 = await self.flexible_custom(
            custom_instruction="Begin with an estimate, then refine your answer through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "validate_assumptions", "adjust"],
            max_iterations=2
        )
        solutions.append(solution2)

        # Solution 3: Parallel exploration (multiple approaches at once)
        solution3 = await self.flexible_custom(
            custom_instruction="Consider multiple valid interpretations of the problem and synthesize a final answer.",
            reasoning_pattern="parallel",
            steps=["analyze_perspective_a", "analyze_perspective_b", "synthesize"]
        )
        solutions.append(solution3)

        # Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final review for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer