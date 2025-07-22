# Workflow ID: gsm8k_14_1
# Benchmark: gsm8k
# Data Indices: [637, 407]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate multiple solutions in parallel (fan-out).
        2. Select the best one using ScEnsemble.
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom.
        
        This combines two powerful patterns:
        - Parallel Ensemble for robustness against flawed reasoning paths
        - Reflect-and-Regenerate for meta-cognitive refinement
        
        The logic is fundamentally different from iterative refinement — here we don't repeatedly fix the same solution but instead explore diverse paths first, then intelligently regenerate based on critique.
        """
        # Step 1: Generate 3 independent solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by defining variables and setting up equations."
            elif i == 1:
                instruction = "Break the problem into smaller parts and solve each part sequentially."
            else:
                instruction = "Use proportional reasoning to compare rates and scale accordingly."

            solution = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction=instruction
            )
            solutions.append(solution)

        # Step 2: Choose the best among them using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify potential flaws, missing assumptions, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, refined solution with more targeted reasoning
        final_answer = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["understand_reflection", "rethink_assumptions", "refine_solution", "validate"],
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now provide a corrected and improved solution.",
            max_iterations=2
        )

        return final_answer