# Workflow ID: gsm8k_120_1
# Benchmark: gsm8k
# Data Indices: [674, 9, 953]

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
        This is a novel workflow combining Iterative Refinement + Flexible Custom with Branching Logic.
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution and refine it twice.
        2. If the reflection from the final iteration suggests uncertainty, trigger a parallel ensemble for robustness.
        3. Otherwise, return the refined solution directly.
        """
        # Step 1: Initial iterative refinement using FlexibleCustom (Iterative Refinement pattern)
        flexible_iter = operator.FlexibleCustom(
            self.config, self.problem,
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Start with a clear breakdown of knowns and unknowns."
        )
        iterated_solution = await flexible_iter()

        # Step 2: Reflect on the final iterative solution to assess confidence
        reflection = await self.reflect(pre_solution=iterated_solution)

        # Step 3: Conditional logic based on reflection content — if uncertain, use Parallel Ensemble
        if "uncertain" in reflection.lower() or "not confident" in reflection.lower():
            # Generate multiple solutions via parallel ensemble as fallback
            solutions = []
            for i in range(3):
                sol = await self.custom(instruction="Solve this math problem independently using a different approach.")
                solutions.append(sol)
            final_answer = await self.sc_ensemble(solutions=solutions)
        else:
            # If confident, just return the refined solution
            final_answer = iterated_solution

        return final_answer