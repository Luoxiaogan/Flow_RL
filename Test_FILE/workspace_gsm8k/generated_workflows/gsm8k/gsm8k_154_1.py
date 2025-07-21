# Workflow ID: gsm8k_154_1
# Benchmark: gsm8k
# Data Indices: [740, 771, 961]

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
        This workflow uses a novel 'Parallel Ensemble + Reflective Refinement' pattern.
        It generates multiple initial solutions in parallel, selects the best one,
        then applies a reflective critique to guide a final improved solution.
        This combines robustness (from ensembling) with meta-cognitive improvement (from reflection).
        """

        # Step 1: Generate 3 independent solutions using flexible custom with sequential reasoning
        # Each solution is based on a slightly different prompt to encourage diverse approaches
        solutions = []
        for i in range(3):
            instruction = f"Approach the problem from a different perspective. For example, focus on identifying variables first, or assume a variable and solve backwards. Be precise."
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="sequential",
                steps=["identify_knowns", "define_variables", "formulate_equation", "solve"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate of the three initial attempts
        best_initial = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best initial solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use that reflection to guide a final, refined solution via a new Custom call
        final_solution = await self.custom(
            instruction=f"Given the following initial solution: {best_initial}. "
                        f"And here is a critical reflection on it: {reflection}. "
                        f"Based on this analysis, provide a logically complete and error-free final answer."
        )

        return final_solution