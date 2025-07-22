# Workflow ID: gsm8k_341_0
# Benchmark: gsm8k
# Data Indices: [513, 621, 132]

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
        Robust parallel ensemble workflow with iterative refinement and final review.
        Uses three diverse reasoning strategies to generate solutions, then selects the best one.
        """
        # Step 1: Generate multiple candidate solutions using different reasoning patterns
        solution_list = []
        
        # Candidate 1: Sequential decomposition (step-by-step breakdown)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )
        solution_list.append(seq_solution)

        # Candidate 2: Iterative refinement (start rough, improve over passes)
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "adjust"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Candidate 3: Parallel exploration (multiple perspectives)
        par_solution = await self.flexible_custom(
            custom_instruction="Consider multiple valid approaches simultaneously.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_and_select"]
        )
        solution_list.append(par_solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review for polish and error-checking
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer