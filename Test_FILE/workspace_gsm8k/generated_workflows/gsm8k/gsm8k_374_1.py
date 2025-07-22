# Workflow ID: gsm8k_374_1
# Benchmark: gsm8k
# Data Indices: [517, 241]

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
        This is a diverse and robust workflow using:
        1. Iterative Refinement (generate → review → repeat until stable)
        2. Reflect-and-Regenerate (after first iteration, reflect on the solution to guide next step)
        3. FlexibleCustom with iterative reasoning pattern for structured refinement

        Key differences from existing:
        - Uses feedback loop via reflection + regeneration instead of ensemble
        - Starts with a single solution, refines it iteratively
        - Leverages new `Reflect` operator to critique assumptions before regenerating
        - Avoids parallel generation entirely — focuses on depth over breadth
        """

        # --- STEP 1: Initial solution via flexible custom in iterative mode ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying all quantities involved. Then compute their sum.",
            reasoning_pattern="iterative",
            steps=["identify_inputs", "sum_quantities", "verify_result"],
            max_iterations=2
        )

        # --- STEP 2: Reflect on the initial solution to uncover hidden flaws or missed logic ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate solution using reflection as guidance ---
        guided_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. "
                        f"Re-solve the problem now, paying special attention to any identified weaknesses or missing considerations."
        )

        # --- STEP 4: Final Review to polish clarity and correctness ---
        final_answer = await self.review(pre_solution=guided_solution)

        return final_answer