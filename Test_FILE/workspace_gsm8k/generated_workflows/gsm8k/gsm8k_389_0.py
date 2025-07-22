# Workflow ID: gsm8k_389_0
# Benchmark: gsm8k
# Data Indices: [417, 303, 361]

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
        Generates 3 different solutions via varied instructions, ensembles them,
        then performs a final review for consistency and clarity.
        """
        # --- STEP 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solution_list = []
        instructions = [
            "Solve step-by-step by identifying known quantities first, then setting up equations.",
            "Break the problem into smaller sub-problems. Solve each one independently before combining.",
            "Use a structured approach: define variables, write relationships, solve systematically."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # --- STEP 2: Enforce consensus via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final refinement with Review to improve clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer