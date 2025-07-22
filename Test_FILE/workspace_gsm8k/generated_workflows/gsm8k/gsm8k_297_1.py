# Workflow ID: gsm8k_297_1
# Benchmark: gsm8k
# Data Indices: [208, 198]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 distinct solutions via different FlexibleCustom configurations,
        then selects the best one using ScEnsemble. Final review ensures clarity and correctness.
        This structure is fundamentally different from iterative refinement—it explores multiple paths first,
        then consolidates the most consistent answer—a more resilient approach to reasoning errors.
        """

        # Step 1: Generate 3 independent solutions using different reasoning patterns
        solution_list = []
        for i in range(3):
            # Varying reasoning patterns per attempt for diversity
            pattern = ["sequential", "iterative", "branching"][i % 3]
            steps = ["analyze", "plan", "solve", "verify"] if pattern == "sequential" else ["initial_guess", "refine", "validate"]
            
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem with clear, logical steps.",
                reasoning_pattern=pattern,
                steps=steps,
                use_structured_output=True
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish clarity and catch any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer