# Workflow ID: gsm8k_177_1
# Benchmark: gsm8k
# Data Indices: [26, 338, 396]

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
        This workflow uses a novel 'Parallel Ensemble with Reflective Guidance' pattern.
        It generates multiple initial solutions in parallel, then uses reflection on the best one to guide a final refined solution.
        This approach combines robustness (from ensembling) with meta-cognitive improvement (from reflection).
        """
        # Step 1: Generate 3 independent solutions using flexible custom in parallel (fan-out)
        solution_list = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by first identifying all relationships and then applying logical deduction.",
                reasoning_pattern="sequential",
                steps=["parse_problem", "extract_relations", "build_equations", "solve"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate of the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to generate a superior final answer
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: '{reflection}'. "
                       f"Reconstruct the answer with improved clarity, precision, and completeness."
        )

        return final_solution