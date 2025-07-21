# Workflow ID: gsm8k_94_0
# Benchmark: gsm8k
# Data Indices: [738, 837]

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
        Generates 3 diverse solutions using different reasoning patterns, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solutions = []
        
        # Solution 1: Sequential pattern – structured, step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "model", "solve", "verify"]
        )
        solutions.append(seq_solution)

        # Solution 2: Parallel pattern – consider multiple interpretations simultaneously
        par_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible approaches to the problem at once.",
            reasoning_pattern="parallel",
            steps=["identify_approaches", "evaluate", "compare"]
        )
        solutions.append(par_solution)

        # Solution 3: Iterative pattern – start rough, refine progressively
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with an estimate, then improve it through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review for clarity, logic, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer