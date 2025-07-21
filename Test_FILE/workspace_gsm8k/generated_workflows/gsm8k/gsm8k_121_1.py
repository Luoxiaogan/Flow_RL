# Workflow ID: gsm8k_121_1
# Benchmark: gsm8k
# Data Indices: [706, 175, 948]

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
        Diverse parallel ensemble workflow using Reflect to guide a single final solution.
        Generates 3 independent solutions via FlexibleCustom with different reasoning patterns,
        then uses Reflect on the best one to identify weaknesses before a final review.
        This approach combines robustness (via parallel generation) with meta-cognitive refinement.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Branching logic: explore multiple interpretations early
                solution = await self.flexible_custom(
                    custom_instruction="Consider multiple possible ways to interpret the problem and solve each.",
                    reasoning_pattern="branching",
                    steps=["interpret", "solve_interpretation_1", "solve_interpretation_2", "compare"]
                )
            elif i == 1:
                # Sequential logic: methodical step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve this by identifying key elements first, then applying logical steps.",
                    reasoning_pattern="sequential",
                    steps=["identify_key_elements", "formulate_plan", "execute", "verify"]
                )
            else:
                # Iterative logic: start rough, refine progressively
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an approximate solution, then improve it through iterative refinement.",
                    reasoning_pattern="iterative",
                    steps=["initial_approximation", "refine", "finalize"],
                    max_iterations=2
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Final review guided by reflection — use the reflection to inform a targeted revision
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution