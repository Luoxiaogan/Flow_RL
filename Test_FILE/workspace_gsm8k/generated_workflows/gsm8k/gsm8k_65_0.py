# Workflow ID: gsm8k_65_0
# Benchmark: gsm8k
# Data Indices: [946, 447]

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
        Robust parallel ensemble workflow with iterative refinement and reflection.
        Uses three distinct reasoning strategies to generate diverse solutions,
        then selects the best one via ensemble, followed by a final review for polish.
        """
        # Step 1: Generate 3 different solutions using varied reasoning patterns
        solution_list = []
        
        # Solution 1: Sequential breakdown (like solving equations step-by-step)
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem systematically.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "formulate_equations", "solve", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Parallel approach — consider multiple interpretations
        par_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations or methods.",
            reasoning_pattern="parallel",
            steps=["interpret_problem", "generate_approaches", "evaluate_options"]
        )
        solution_list.append(par_solution)

        # Solution 3: Iterative refinement — start rough, improve progressively
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_consistency", "refine"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to polish and ensure clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer