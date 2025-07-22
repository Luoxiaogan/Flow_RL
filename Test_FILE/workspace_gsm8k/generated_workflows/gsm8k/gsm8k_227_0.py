# Workflow ID: gsm8k_227_0
# Benchmark: gsm8k
# Data Indices: [175, 967, 507]

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
        It generates 3 distinct solutions via different reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # Generate multiple solutions using varied approaches (Parallel Ensemble)
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step decomposition
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into clear, logical steps.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "formulate_relations", "compute", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine step-by-step.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Problem-specific structure (but generic instruction)
                solution = await self.flexible_custom(
                    custom_instruction="Apply a structured approach: define variables, set up equations, solve.",
                    reasoning_pattern="sequential",
                    steps=["define_variables", "write_equations", "solve_system", "check_solution"]
                )
            solutions.append(solution)

        # Select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final refinement to ensure clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer