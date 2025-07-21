# Workflow ID: gsm8k_3_1
# Benchmark: gsm8k
# Data Indices: [945, 267]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern for robustness.
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        A final review ensures clarity and correctness before returning.
        """

        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different reasoning patterns
        solution_list = []
        reasoning_patterns = ["sequential", "iterative", "branching"]
        
        for i, pattern in enumerate(reasoning_patterns):
            instruction = (
                f"Use {pattern} reasoning to solve this problem. Break it down into clear steps."
                if pattern == "sequential"
                else f"Apply iterative refinement starting from an initial estimate using {pattern} logic."
                if pattern == "iterative"
                else f"Explore multiple possible paths based on different interpretations of the problem using {pattern} reasoning."
            )
            
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution among the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution — ensures logical soundness and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer