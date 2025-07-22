# Workflow ID: gsm8k_356_1
# Benchmark: gsm8k
# Data Indices: [459, 424, 8]

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
        This is a diverse and complex workflow based on the Iterative Refinement pattern.
        Step 1: Generate an initial solution using Custom with a clear step-by-step instruction.
        Step 2: Apply Review twice in sequence to progressively refine the solution — first for clarity, then for accuracy.
        Step 3: Use Reflect to critique the final refined solution and generate a new version via FlexibleCustom in iterative mode to ensure robustness.
        
        This structure emphasizes deep, multi-stage improvement rather than parallel exploration or ensemble selection.
        """

        # --- INITIAL SOLUTION ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each step clearly."
        )

        # --- ITERATIVE REFINEMENT: Two rounds of Review ---
        first_refinement = await self.review(pre_solution=initial_solution)
        second_refinement = await self.review(pre_solution=first_refinement)

        # --- REFLECT ON FINAL REFINED SOLUTION ---
        reflection = await self.reflect(pre_solution=second_refinement)

        # --- FINAL IMPROVEMENT USING FLEXIBLECUSTOM IN ITERATIVE MODE ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: '{reflection}'. Now solve the problem again using iterative refinement to ensure completeness and correctness.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return final_solution