# Workflow ID: gsm8k_25_1
# Benchmark: gsm8k
# Data Indices: [550, 724, 310]

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
        This is a diverse and efficient workflow using a parallel ensemble followed by reflective regeneration.
        It leverages multiple reasoning strategies simultaneously and then uses meta-cognition to refine the best result.
        """

        # Step 1: Generate 3 different solutions using distinct reasoning patterns (Parallel Ensemble)
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve this problem step-by-step with clear logical progression."
        )
        
        solution2 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then refine your approach through two iterations."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["identify_knowns", "consider_alternatives", "choose_best_path", "compute"],
            custom_instruction="Explore multiple possible interpretations of the problem before selecting the most valid path."
        )

        solutions = [solution1, solution2, solution3]

        # Step 2: Use ScEnsemble to select the best candidate from the parallel approaches
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the selected solution to uncover hidden assumptions or missed details
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, regenerate a new solution that addresses the identified weaknesses
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        f"Generate a revised solution that improves upon it by addressing these points."
        )

        return final_solution