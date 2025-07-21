# Workflow ID: gsm8k_60_1
# Benchmark: gsm8k
# Data Indices: [869, 440, 564]

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
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 diverse initial solutions.
        2. Reflect and Regenerate: Critically reflect on the best solution, then regenerate a superior one.

        It's designed to be robust against single-point failures (via parallelism) and meta-cognitively refined (via reflection).
        """
        # Step 1: Generate multiple independent solutions using flexible custom with different reasoning strategies
        solution_list = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            steps = {
                "sequential": ["understand", "break_down", "compute", "verify"],
                "iterative": ["initial_approach", "refine", "finalize"],
                "branching": ["analyze", "consider_alternatives", "decide"]
            }[pattern]

            solution = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step with clear logic.",
                reasoning_pattern=pattern,
                steps=steps
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best among the three diverse approaches
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the selected best solution — identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        f"Use this insight to produce a revised, more accurate, and logically sound answer."
        )

        return final_solution