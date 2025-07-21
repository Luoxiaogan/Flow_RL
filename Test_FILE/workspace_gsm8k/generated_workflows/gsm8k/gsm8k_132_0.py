# Workflow ID: gsm8k_132_0
# Benchmark: gsm8k
# Data Indices: [73, 61]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        Generates 3 distinct solutions via varied instructions, then ensembles them.
        Final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math problem by breaking it into clear steps: identify what is given, what needs to be found, and apply logical operations one at a time."
            elif i == 1:
                instruction = "Approach the problem as if you're teaching someone who is new to math. Use simple language and explain each calculation explicitly."
            else:
                instruction = "Use a structured reasoning pattern: first analyze the problem context, then plan your solution, execute the steps, and finally verify your answer."

            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_list.append(solution)

        # --- STEP 2: Enforce consistency with ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final refinement via Review for polish and clarity ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer