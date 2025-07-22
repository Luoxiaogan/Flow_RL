# Workflow ID: gsm8k_235_1
# Benchmark: gsm8k
# Data Indices: [401, 92]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Parallel Ensemble.
        It generates 3 solutions via different reasoning strategies, then uses reflection to guide a final refinement.
        This structure introduces meta-cognition (reflection) before final review, making it fundamentally different from the existing logic.
        """

        # Step 1: Generate 3 diverse initial solutions using varied instructions
        solution_list = []
        instructions = [
            "Solve this math problem by first identifying all costs and their patterns over time.",
            "Break the problem into smaller sub-problems: one for each month or cost type, then combine.",
            "Apply algebraic modeling: define variables for known quantities and set up equations."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Critically reflect on the selected solution — identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new custom generation for an improved answer
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        f"Re-solve the problem while addressing these points. Provide a clear, step-by-step explanation."
        )

        # Step 5: Final review to polish clarity, correctness, and logical flow
        polished_answer = await self.review(pre_solution=final_answer)

        return polished_answer