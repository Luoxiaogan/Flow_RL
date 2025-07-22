# Workflow ID: gsm8k_143_1
# Benchmark: gsm8k
# Data Indices: [428, 829]

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
        This is a diverse and complex workflow combining Iterative Refinement + Reflect-and-Regenerate.
        Step 1: Generate an initial solution using FlexibleCustom in iterative mode (3 iterations).
        Step 2: Use the final result from that iteration to generate a reflection.
        Step 3: Based on the reflection, use a new FlexibleCustom call with branching logic to explore alternative approaches if the reflection suggests ambiguity or error.
        Step 4: If branching was used, select the best path via ScEnsemble; otherwise return the refined solution directly.
        """

        # --- ITERATIVE REFINEMENT WITH FLEXIBLECUSTOM ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by iteratively refining your approach.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "execute", "review"],
            max_iterations=3,
            use_structured_output=True
        )

        # --- REFLECT ON THE FINAL ITERATION RESULT ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- BRANCHING LOGIC BASED ON REFLECTION ---
        if "assumption" in reflection.lower() or "uncertainty" in reflection.lower():
            # Branching strategy: Explore multiple interpretations
            branch_solutions = []
            for i in range(2):  # Two different interpretations based on reflection
                instruction = f"Given this reflection: '{reflection}'. Now solve the problem considering potential alternative assumptions."
                branch_sol = await self.custom(instruction=instruction)
                branch_solutions.append(branch_sol)

            # Select best among branches
            final_answer = await self.sc_ensemble(solutions=branch_solutions)
        else:
            # No major issues found — just refine one more time
            final_answer = await self.flexible_custom(
                custom_instruction=f"Based on the following reflection: '{reflection}'. Now provide a final, polished answer.",
                reasoning_pattern="sequential",
                steps=["analyze", "rethink", "finalize"],
                use_structured_output=True
            )

        return final_answer