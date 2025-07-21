# Workflow ID: gsm8k_168_1
# Benchmark: gsm8k
# Data Indices: [413, 505, 445]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 independent solutions.
        2. Reflect and Regenerate: Critique the best solution, then use that reflection to guide a final refinement.
        
        This approach combines robustness (multiple starting points) with meta-cognition (reflection-driven improvement),
        mimicking how expert problem solvers explore alternatives before refining their choice.
        """
        # Step 1: Generate 3 independent solutions via parallel ensemble
        solution_list = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step using a different method each time. Be creative in your approach."
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect critically on the best solution — identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to generate a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a revised and improved answer based on this critique."
        )

        return final_answer