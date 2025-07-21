# Workflow ID: gsm8k_24_1
# Benchmark: gsm8k
# Data Indices: [940, 729, 565]

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
        This is a diverse workflow using the 'Iterative Refinement' pattern with a twist:
        - Generate an initial solution via FlexibleCustom in iterative mode
        - Use Reflect to critique it after each iteration
        - Then, use Review to refine the solution based on reflection
        - Finally, apply ScEnsemble across multiple independent attempts for robustness
        """
        # Step 1: Run an iterative refinement loop using FlexibleCustom
        # This simulates how humans might improve their reasoning over time
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with a rough estimate and refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "analyze", "refine", "verify"],
            max_iterations=3
        )

        # Step 2: Critically reflect on the iterative result
        reflection = await self.reflect(pre_solution=iterative_solution)

        # Step 3: Use the reflection to guide a targeted review
        refined_solution = await self.review(pre_solution=iterative_solution)

        # Step 4: Generate 3 independent solutions using parallel approach
        parallel_solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem from scratch using a different method or perspective.")
            parallel_solutions.append(sol)

        # Step 5: Ensemble the best solution from the parallel set
        final_answer = await self.sc_ensemble(solutions=parallel_solutions)

        return final_answer