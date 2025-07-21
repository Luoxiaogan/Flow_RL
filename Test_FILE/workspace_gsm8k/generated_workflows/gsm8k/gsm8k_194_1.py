# Workflow ID: gsm8k_194_1
# Benchmark: gsm8k
# Data Indices: [331, 236, 72]

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
        This workflow combines two powerful patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate multiple independent solutions to reduce single-point failure.
        2. Reflect and Regenerate: Critically analyze the best solution and refine it using meta-cognition.

        Step-by-step logic:
        - Generate 3 different initial solutions via parallel reasoning.
        - Use ScEnsemble to pick the strongest one.
        - Reflect on that winner to uncover hidden assumptions or errors.
        - Finally, regenerate a new solution informed by the reflection — this is the true final answer.
        
        This hybrid approach ensures robustness (from ensembling) and depth (from reflection).
        """
        # Step 1: Generate 3 diverse initial solutions using FlexibleCustom in "parallel" mode
        solution_list = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Approach the problem from a unique perspective.",
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve"]
            )
            solution_list.append(solution)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Critically reflect on the selected solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a regenerated solution — now with deeper insight
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: {reflection}. "
                        f"Provide a refined, improved version of the solution that addresses the identified issues."
        )

        return final_solution