# Workflow ID: gsm8k_371_0
# Benchmark: gsm8k
# Data Indices: [719, 97, 13]

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
        Generates 3 distinct solutions via FlexibleCustom with different reasoning patterns,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning strategies
        solution_list = []
        
        # Solution 1: Sequential reasoning (step-by-step breakdown)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically in steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "formulate_equation", "solve"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Iterative refinement (start simple, improve)
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine it through multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "adjust"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Parallel approach (multiple angles)
        par_solution = await self.flexible_custom(
            custom_instruction="Consider multiple interpretations of the problem simultaneously.",
            reasoning_pattern="parallel",
            steps=["interpret_a", "interpret_b", "synthesize"]
        )
        solution_list.append(par_solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to polish and ensure clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer