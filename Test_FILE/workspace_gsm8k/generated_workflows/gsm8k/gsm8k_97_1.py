# Workflow ID: gsm8k_97_1
# Benchmark: gsm8k
# Data Indices: [868, 942]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 diverse solutions via parallel approach (fan-out).
        2. Use ScEnsemble to pick the best one.
        3. Critically reflect on the winner to identify potential blind spots.
        4. Regenerate a final solution using the reflection as guidance — this mimics meta-cognition and deliberate improvement.
        This combines robustness (multiple perspectives) with reflective reasoning for higher accuracy.
        """

        # Step 1: Generate 3 different initial solutions using flexible custom with varied reasoning patterns
        solution_list = []
        patterns = ["sequential", "iterative", "branching"]
        for pattern in patterns:
            solution = await self.flexible_custom(
                custom_instruction="Approach the problem using a step-by-step breakdown.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            solution_list.append(solution)

        # Step 2: Use ensemble to select the most coherent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to uncover assumptions, logic gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, improved solution — now informed by critical self-awareness
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem with that insight in mind. Be precise and avoid repeating the same mistakes."
        )

        return final_answer