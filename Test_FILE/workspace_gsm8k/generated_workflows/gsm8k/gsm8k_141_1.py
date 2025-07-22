# Workflow ID: gsm8k_141_1
# Benchmark: gsm8k
# Data Indices: [737, 964]

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
        This is a diverse workflow using Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions in parallel (fan-out).
        Step 2: Use ScEnsemble to pick the best one.
        Step 3: Critically reflect on that solution's potential flaws or missed assumptions.
        Step 4: Use the reflection to guide a new Custom call for final refinement.
        This combines two distinct patterns: Parallel Ensemble and Reflect-and-Regenerate.
        """
        # Step 1: Generate multiple solutions independently using different reasoning styles
        solution_a = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into steps and checking each step for logical consistency.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        solution_b = await self.flexible_custom(
            custom_instruction="Approach this as if you're teaching someone else — explain every assumption clearly.",
            reasoning_pattern="sequential",
            steps=["understand", "identify_knowns", "formulate_plan", "execute", "explain"]
        )

        solution_c = await self.flexible_custom(
            custom_instruction="Use estimation first, then precise calculation. Show how you verify your answer.",
            reasoning_pattern="iterative",
            steps=["estimate", "calculate", "check"],
            max_iterations=2
        )

        # Step 2: Ensembling - select the most accurate among the three
        all_solutions = [solution_a, solution_b, solution_c]
        best_solution = await self.sc_ensemble(solutions=all_solutions)

        # Step 3: Reflect on the best solution — identify possible weaknesses
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final improved solution based on the reflection
        final_answer = await self.custom(
            instruction=f"Given the following solution: {best_solution}\n\nAnd the reflection on its limitations: {reflection}\n\nNow provide a revised, more robust solution."
        )

        return final_answer