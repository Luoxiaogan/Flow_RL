# Workflow ID: gsm8k_255_1
# Benchmark: gsm8k
# Data Indices: [551, 93, 450]

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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and efficient workflow using a Reflect-and-Regenerate strategy with parallel ensemble.
        It first generates an initial solution, then reflects on its weaknesses, and uses that reflection to guide
        a new, improved solution. Finally, it ensembles multiple such reflections to ensure robustness — a fundamentally
        different logic from iterative refinement or single-step generation.
        
        Key differences from the existing workflow:
        - Uses 'Reflect' to generate meta-cognitive critique before regenerating (not just reviewing).
        - Employs parallel ensemble (fan-out/fan-in) by generating 3 solutions based on different reflections.
        - Avoids iteration; instead, uses structured reflection + regeneration in one pass per solution.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on potential flaws or assumptions in the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a fresh solution attempt
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a new, improved solution that addresses these concerns."
        )

        # Step 4: Generate two more solutions using different reflective prompts (parallel ensemble)
        # This introduces diversity through varied reflection angles
        solution_list = [refined_solution]
        for i in range(2):
            alt_reflection = await self.reflect(pre_solution=initial_solution)
            alt_solution = await self.custom(
                instruction=f"Based on this alternative reflection: '{alt_reflection}', "
                            "generate a revised solution focusing on addressing those points."
            )
            solution_list.append(alt_solution)

        # Step 5: Ensemble the three solutions to pick the best one
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer